import argparse, math, sys, time
from pathlib import Path
import numpy as np
import vulkan as vk

AMD, RADEON_VII = 0x1002, 0x66AF
TILE_M = 32
TILE_N = 32
# The runner selects a precompiled precision variant for each invocation.


class UnconfirmedGPUCompletion(RuntimeError):
    pass


def require(ok, message):
    if not ok: raise RuntimeError(message)

def make_inputs(n, precision, seed):
    rng=np.random.default_rng(seed+n)
    scale=1.0/math.sqrt(n)
    a=(rng.standard_normal((n,n))*scale).astype(np.float32)
    b=(rng.standard_normal((n,n))*scale).astype(np.float32)
    if precision.startswith('fp16'):
        a=a.astype(np.float16); b=b.astype(np.float16)
        out_dtype=np.float16 if precision=='fp16_acc16' else np.float32
    else:
        a=a.astype(np.float32); b=b.astype(np.float32)
        out_dtype=np.float32
    return np.ascontiguousarray(a),np.ascontiguousarray(b),out_dtype

def run_one(physical, device, queue, family, props, memprops, precision, method, n, a, b, reference, out_dtype, warmups, repeats, source, timestamp_bits):
    input_bytes=a.nbytes; output_bytes=n*n*np.dtype(out_dtype).itemsize
    local=True
    spv=(source/f'{method}_{precision}.spv').read_bytes()
    wall0=time.perf_counter()
    buffers=[]; memories=[]; owned={}; in_flight=False
    try:
        def make_buffer(size, usage, required, preferred=0):
            buf=vk.vkCreateBuffer(device,vk.VkBufferCreateInfo(sType=vk.VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,size=size,usage=usage,sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE),None)
            buffers.append(buf)
            req=vk.vkGetBufferMemoryRequirements(device,buf)
            choices=[i for i in range(memprops.memoryTypeCount) if req.memoryTypeBits&(1<<i) and (memprops.memoryTypes[i].propertyFlags&required)==required]
            require(bool(choices),f'no Vulkan memory type for flags 0x{required:x}')
            idx=next((i for i in choices if (memprops.memoryTypes[i].propertyFlags&preferred)==preferred),choices[0])
            alloc=vk.vkAllocateMemory(device,vk.VkMemoryAllocateInfo(sType=vk.VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,allocationSize=req.size,memoryTypeIndex=idx),None)
            memories.append(alloc); vk.vkBindBufferMemory(device,buf,alloc,0)
            return buf,alloc,idx
        host=vk.VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT|vk.VK_MEMORY_PROPERTY_HOST_COHERENT_BIT
        localflag=vk.VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT
        transfer=vk.VK_BUFFER_USAGE_TRANSFER_SRC_BIT|vk.VK_BUFFER_USAGE_TRANSFER_DST_BIT
        stage_a,mem_stage_a,_=make_buffer(input_bytes,transfer,host)
        stage_b,mem_stage_b,_=make_buffer(input_bytes,transfer,host)
        stage_out,mem_stage_out,_=make_buffer(output_bytes*repeats,vk.VK_BUFFER_USAGE_TRANSFER_DST_BIT,host)
        a_usage=vk.VK_BUFFER_USAGE_STORAGE_BUFFER_BIT|vk.VK_BUFFER_USAGE_TRANSFER_DST_BIT
        b_usage=vk.VK_BUFFER_USAGE_STORAGE_BUFFER_BIT|vk.VK_BUFFER_USAGE_TRANSFER_DST_BIT
        c_usage=vk.VK_BUFFER_USAGE_STORAGE_BUFFER_BIT|vk.VK_BUFFER_USAGE_TRANSFER_SRC_BIT
        buf_a,mem_a,idx_a=make_buffer(input_bytes,a_usage,localflag)
        buf_b,mem_b,idx_b=make_buffer(input_bytes,b_usage,localflag)
        buf_c,mem_c,idx_c=make_buffer(output_bytes,c_usage,localflag)
        device_local_bytes=sum(vk.vkGetBufferMemoryRequirements(device,x).size for x in (buf_a,buf_b,buf_c))
        staging_bytes=2*input_bytes+output_bytes*repeats
        mapped=vk.vkMapMemory(device,mem_stage_a,0,input_bytes,0);mapped[:]=a.tobytes();vk.vkUnmapMemory(device,mem_stage_a)
        mapped=vk.vkMapMemory(device,mem_stage_b,0,input_bytes,0);mapped[:]=b.tobytes();vk.vkUnmapMemory(device,mem_stage_b)
        dsl=vk.vkCreateDescriptorSetLayout(device,vk.VkDescriptorSetLayoutCreateInfo(sType=vk.VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO,bindingCount=3,pBindings=[vk.VkDescriptorSetLayoutBinding(binding=i,descriptorType=vk.VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,descriptorCount=1,stageFlags=vk.VK_SHADER_STAGE_COMPUTE_BIT) for i in range(3)]),None);owned['dsl']=dsl
        pcr=vk.VkPushConstantRange(stageFlags=vk.VK_SHADER_STAGE_COMPUTE_BIT,offset=0,size=4)
        pl=vk.vkCreatePipelineLayout(device,vk.VkPipelineLayoutCreateInfo(sType=vk.VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,setLayoutCount=1,pSetLayouts=[dsl],pushConstantRangeCount=1,pPushConstantRanges=[pcr]),None);owned['pl']=pl
        sm=vk.vkCreateShaderModule(device,vk.VkShaderModuleCreateInfo(sType=vk.VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,codeSize=len(spv),pCode=spv),None);owned['sm']=sm
        stageinfo=vk.VkPipelineShaderStageCreateInfo(sType=vk.VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,stage=vk.VK_SHADER_STAGE_COMPUTE_BIT,module=sm,pName='main')
        pipeline=vk.vkCreateComputePipelines(device,vk.VK_NULL_HANDLE,1,[vk.VkComputePipelineCreateInfo(sType=vk.VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO,stage=stageinfo,layout=pl)],None)[0];owned['pipeline']=pipeline
        pool=vk.vkCreateDescriptorPool(device,vk.VkDescriptorPoolCreateInfo(sType=vk.VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO,maxSets=1,poolSizeCount=1,pPoolSizes=[vk.VkDescriptorPoolSize(type=vk.VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,descriptorCount=3)]),None);owned['pool']=pool
        ds=vk.vkAllocateDescriptorSets(device,vk.VkDescriptorSetAllocateInfo(sType=vk.VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO,descriptorPool=pool,descriptorSetCount=1,pSetLayouts=[dsl]))[0]
        infos=[vk.VkDescriptorBufferInfo(buffer=x,offset=0,range=sz) for x,sz in ((buf_a,input_bytes),(buf_b,input_bytes),(buf_c,output_bytes))]
        writes=[vk.VkWriteDescriptorSet(sType=vk.VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET,dstSet=ds,dstBinding=i,descriptorCount=1,descriptorType=vk.VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,pBufferInfo=[infos[i]]) for i in range(3)]
        vk.vkUpdateDescriptorSets(device,3,writes,0,None)
        qpool=vk.vkCreateQueryPool(device,vk.VkQueryPoolCreateInfo(sType=vk.VK_STRUCTURE_TYPE_QUERY_POOL_CREATE_INFO,queryType=vk.VK_QUERY_TYPE_TIMESTAMP,queryCount=2*repeats),None);owned['qpool']=qpool
        cpool=vk.vkCreateCommandPool(device,vk.VkCommandPoolCreateInfo(sType=vk.VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO,flags=vk.VK_COMMAND_POOL_CREATE_TRANSIENT_BIT,queueFamilyIndex=family),None);owned['cpool']=cpool
        cmd_count=1
        cmd=vk.vkAllocateCommandBuffers(device,vk.VkCommandBufferAllocateInfo(sType=vk.VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO,commandPool=cpool,level=vk.VK_COMMAND_BUFFER_LEVEL_PRIMARY,commandBufferCount=cmd_count))[0]
        vk.vkBeginCommandBuffer(cmd,vk.VkCommandBufferBeginInfo(sType=vk.VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,flags=vk.VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT))
        copya=vk.VkBufferCopy(srcOffset=0,dstOffset=0,size=input_bytes);copyc=vk.VkBufferCopy(srcOffset=0,dstOffset=0,size=output_bytes)
        vk.vkCmdCopyBuffer(cmd,stage_a,buf_a,1,[copya]);vk.vkCmdCopyBuffer(cmd,stage_b,buf_b,1,[copya])
        srcbar=[vk.VkBufferMemoryBarrier(sType=vk.VK_STRUCTURE_TYPE_BUFFER_MEMORY_BARRIER,srcAccessMask=vk.VK_ACCESS_TRANSFER_WRITE_BIT,dstAccessMask=vk.VK_ACCESS_SHADER_READ_BIT,srcQueueFamilyIndex=vk.VK_QUEUE_FAMILY_IGNORED,dstQueueFamilyIndex=vk.VK_QUEUE_FAMILY_IGNORED,buffer=x,offset=0,size=input_bytes) for x in (buf_a,buf_b)]
        vk.vkCmdPipelineBarrier(cmd,vk.VK_PIPELINE_STAGE_TRANSFER_BIT,vk.VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,0,0,None,2,srcbar,0,None)
        vk.vkCmdBindPipeline(cmd,vk.VK_PIPELINE_BIND_POINT_COMPUTE,pipeline);vk.vkCmdBindDescriptorSets(cmd,vk.VK_PIPELINE_BIND_POINT_COMPUTE,pl,0,1,[ds],0,None);vk.vkCmdPushConstants(cmd,pl,vk.VK_SHADER_STAGE_COMPUTE_BIT,0,4,vk.ffi.new('uint32_t[1]',[n]))
        gx=math.ceil(n/TILE_N);gy=math.ceil(n/TILE_M)
        compute_waw=vk.VkMemoryBarrier(sType=vk.VK_STRUCTURE_TYPE_MEMORY_BARRIER,srcAccessMask=vk.VK_ACCESS_SHADER_WRITE_BIT,dstAccessMask=vk.VK_ACCESS_SHADER_WRITE_BIT)
        for _ in range(warmups):
            vk.vkCmdDispatch(cmd,gx,gy,1);vk.vkCmdPipelineBarrier(cmd,vk.VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,vk.VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,0,1,[compute_waw],0,None,0,None)
        for i in range(repeats):
            first=2*i;vk.vkCmdResetQueryPool(cmd,qpool,first,2)
            vk.vkCmdWriteTimestamp(cmd,vk.VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,qpool,first)
            vk.vkCmdDispatch(cmd,gx,gy,1)
            vk.vkCmdWriteTimestamp(cmd,vk.VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT,qpool,first+1)
            after_compute=vk.VkBufferMemoryBarrier(sType=vk.VK_STRUCTURE_TYPE_BUFFER_MEMORY_BARRIER,srcAccessMask=vk.VK_ACCESS_SHADER_WRITE_BIT,dstAccessMask=vk.VK_ACCESS_TRANSFER_READ_BIT,srcQueueFamilyIndex=vk.VK_QUEUE_FAMILY_IGNORED,dstQueueFamilyIndex=vk.VK_QUEUE_FAMILY_IGNORED,buffer=buf_c,offset=0,size=output_bytes)
            vk.vkCmdPipelineBarrier(cmd,vk.VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,vk.VK_PIPELINE_STAGE_TRANSFER_BIT,0,0,None,1,[after_compute],0,None)
            copyout=vk.VkBufferCopy(srcOffset=0,dstOffset=i*output_bytes,size=output_bytes);vk.vkCmdCopyBuffer(cmd,buf_c,stage_out,1,[copyout])
            if i+1<repeats:
                back=vk.VkBufferMemoryBarrier(sType=vk.VK_STRUCTURE_TYPE_BUFFER_MEMORY_BARRIER,srcAccessMask=vk.VK_ACCESS_TRANSFER_READ_BIT,dstAccessMask=vk.VK_ACCESS_SHADER_WRITE_BIT,srcQueueFamilyIndex=vk.VK_QUEUE_FAMILY_IGNORED,dstQueueFamilyIndex=vk.VK_QUEUE_FAMILY_IGNORED,buffer=buf_c,offset=0,size=output_bytes)
                vk.vkCmdPipelineBarrier(cmd,vk.VK_PIPELINE_STAGE_TRANSFER_BIT,vk.VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,0,0,None,1,[back],0,None)
        vk.vkEndCommandBuffer(cmd)
        fence=vk.vkCreateFence(device,vk.VkFenceCreateInfo(sType=vk.VK_STRUCTURE_TYPE_FENCE_CREATE_INFO),None);owned['fence']=fence
        in_flight=True
        try:
            vk.vkQueueSubmit(queue,1,[vk.VkSubmitInfo(sType=vk.VK_STRUCTURE_TYPE_SUBMIT_INFO,commandBufferCount=1,pCommandBuffers=[cmd])],fence)
            wait_result=vk.vkWaitForFences(device,1,[fence],vk.VK_TRUE,5_000_000_000)
            require(wait_result is None or wait_result==vk.VK_SUCCESS,'fence did not signal')
        except Exception as exc:
            raise UnconfirmedGPUCompletion('GPU completion unconfirmed; stop and inspect system before retrying') from exc
        in_flight=False
        qdata=vk.ffi.new(f'uint64_t[{2*repeats}]')
        vk.vkGetQueryPoolResults(device,qpool,0,2*repeats,16*repeats,qdata,8,vk.VK_QUERY_RESULT_64_BIT|vk.VK_QUERY_RESULT_WAIT_BIT)
        times=[]
        for i in range(repeats):
            delta=(int(qdata[2*i+1])-int(qdata[2*i])) if timestamp_bits>=64 else ((int(qdata[2*i+1])-int(qdata[2*i]))&((1<<timestamp_bits)-1))
            times.append(delta*float(props.limits.timestampPeriod)/1e6)
        mapped=vk.vkMapMemory(device,mem_stage_out,0,output_bytes*repeats,0)
        raw=bytes(mapped);vk.vkUnmapMemory(device,mem_stage_out)
        outs=[np.frombuffer(raw[i*output_bytes:(i+1)*output_bytes],dtype=out_dtype).reshape(n,n).astype(np.float64) for i in range(repeats)]
        stable=all(np.array_equal(outs[0],x,equal_nan=True) for x in outs[1:])
        result=outs[-1]
        abs_err=np.abs(result-reference); rel_mask=np.abs(reference)>1e-6
        rel_err=np.zeros_like(abs_err);np.divide(abs_err,np.abs(reference),out=rel_err,where=rel_mask)
        rel_mask_report=np.abs(reference)>1e-3
        rel_report=np.zeros_like(abs_err);np.divide(abs_err,np.abs(reference),out=rel_report,where=rel_mask_report)
        ref_norm=float(np.linalg.norm(reference));relative_fro=float(np.linalg.norm(abs_err)/ref_norm) if ref_norm else 0.0
        flops=2.0*n*n*n;mean_gpu=float(np.mean(times));require(math.isfinite(mean_gpu) and mean_gpu>0,'invalid timestamp duration');gflops=flops/(mean_gpu/1000.0)/1e9
        half_nonfinite=int(np.count_nonzero(~np.isfinite(result))) if precision=='fp16_acc16' else 0
        expected_over=int(np.count_nonzero(np.abs(reference)>65504)) if precision=='fp16_acc16' else 0
        atol,rtol=(0.003,0.02) if precision=='fp16_acc16' else (0.00002,0.0002)
        passed=bool(np.all(np.isfinite(result)) and np.allclose(result,reference,atol=atol,rtol=rtol))
        return {'size':n,'precision':precision,'kernel':method,'status':'PASS' if passed else 'FAIL','atol':atol,'rtol':rtol,'warmups':warmups,'repeats':repeats,
            'gpu_timestamp_ms_mean':mean_gpu,'gpu_timestamp_ms_median':float(np.median(times)),'gpu_timestamp_ms_min':float(np.min(times)),'gpu_timestamp_ms_max':float(np.max(times)),
            'gpu_timestamp_cv_pct':float(np.std(times)/mean_gpu*100) if mean_gpu else 0.0,'gflops':gflops,'tflops':gflops/1000.0,
            'runner_wall_ms':(time.perf_counter()-wall0)*1000.0,'device_local_alloc_bytes':int(device_local_bytes),'host_staging_bytes':int(staging_bytes),
            'max_abs_error':float(np.max(abs_err)),'max_rel_error_eps1e-6':float(np.max(rel_err)),'max_rel_error_ref_gt1e-3':float(np.max(rel_report)),'relative_fro_error':relative_fro,'relative_error_sample_count':int(np.count_nonzero(rel_mask_report)),'rms_abs_error':float(np.sqrt(np.mean(abs_err*abs_err))),
            'fp16_nonfinite_output_count':half_nonfinite,'fp16_expected_out_of_range_count':expected_over,'stable_repeat_outputs':stable if len(outs)>1 else None,
            'cpu_reference_ms':None,'notes':f'config={method}; tile={TILE_M}x{TILE_N}; shader={method}_{precision}.spv'}
    finally:
        if device and not in_flight:
            for key,fn in [('fence',vk.vkDestroyFence),('qpool',vk.vkDestroyQueryPool),('cpool',vk.vkDestroyCommandPool),('pool',vk.vkDestroyDescriptorPool),('pipeline',vk.vkDestroyPipeline),('sm',vk.vkDestroyShaderModule),('pl',vk.vkDestroyPipelineLayout),('dsl',vk.vkDestroyDescriptorSetLayout)]:
                if key in owned: fn(device,owned[key],None)
            for x in buffers: vk.vkDestroyBuffer(device,x,None)
            for x in memories: vk.vkFreeMemory(device,x,None)


def main():
    import json
    ap=argparse.ArgumentParser(description='Bounded Radeon VII GEMM correctness candidate')
    ap.add_argument('--size',type=int,choices=(32,64,128,256),default=32)
    ap.add_argument('--precision',choices=('fp32','fp16_acc16','fp16_acc32'),default='fp32')
    ap.add_argument('--packed',action='store_true',help='separate two-partial-sum FP16 numerical contract')
    args=ap.parse_args()
    require(not args.packed or args.precision=='fp16_acc16','packed requires fp16_acc16')
    source=Path(__file__).resolve().parent
    method='packed' if args.packed else 'bounded'
    instance=vk.vkCreateInstance(vk.VkInstanceCreateInfo(sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,pApplicationInfo=vk.VkApplicationInfo(sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,pApplicationName='VEGA GEMM correctness candidate',applicationVersion=1,pEngineName='VEGA Revival',engineVersion=1,apiVersion=vk.VK_MAKE_VERSION(1,2,0))),None)
    device=None
    cleanup=True
    try:
        phys=next((d for d in vk.vkEnumeratePhysicalDevices(instance) if (lambda p:p.vendorID==AMD and p.deviceID==RADEON_VII)(vk.vkGetPhysicalDeviceProperties(d))),None)
        require(phys is not None,'AMD Radeon VII 1002:66AF not enumerated')
        props=vk.vkGetPhysicalDeviceProperties(phys)
        require(props.apiVersion>=vk.VK_MAKE_VERSION(1,2,0),'Vulkan 1.2 required')
        families=vk.vkGetPhysicalDeviceQueueFamilyProperties(phys)
        family=next((i for i,q in enumerate(families) if q.queueCount and q.queueFlags&vk.VK_QUEUE_COMPUTE_BIT and q.timestampValidBits),None)
        require(family is not None,'no compute queue with timestamps')
        require(bool(props.limits.timestampComputeAndGraphics),'compute timestamps unsupported')
        enabled12=None
        if args.precision!='fp32':
            feat16=vk.VkPhysicalDevice16BitStorageFeatures(sType=vk.VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_16BIT_STORAGE_FEATURES)
            feat12=vk.VkPhysicalDeviceVulkan12Features(sType=vk.VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_FEATURES,pNext=feat16)
            feats2=vk.VkPhysicalDeviceFeatures2(sType=vk.VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2,pNext=feat12)
            vk.vkGetPhysicalDeviceFeatures2(phys,feats2)
            require(bool(feat16.storageBuffer16BitAccess),'storageBuffer16BitAccess unsupported')
            require(bool(feat12.shaderFloat16),'shaderFloat16 unsupported')
            enabled16=vk.VkPhysicalDevice16BitStorageFeatures(sType=vk.VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_16BIT_STORAGE_FEATURES,storageBuffer16BitAccess=vk.VK_TRUE)
            enabled12=vk.VkPhysicalDeviceVulkan12Features(sType=vk.VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_FEATURES,pNext=enabled16,shaderFloat16=vk.VK_TRUE)
        qci=vk.VkDeviceQueueCreateInfo(sType=vk.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,queueFamilyIndex=family,queueCount=1,pQueuePriorities=[1.0])
        device=vk.vkCreateDevice(phys,vk.VkDeviceCreateInfo(sType=vk.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,pNext=enabled12,queueCreateInfoCount=1,pQueueCreateInfos=[qci]),None)
        queue=vk.vkGetDeviceQueue(device,family,0)
        memprops=vk.vkGetPhysicalDeviceMemoryProperties(phys)
        a,b,outdtype=make_inputs(args.size,args.precision,20261126)
        reference=a.astype(np.float64)@b.astype(np.float64)
        try:
            row=run_one(phys,device,queue,family,props,memprops,args.precision,method,args.size,a,b,reference,outdtype,0,1,source,int(families[family].timestampValidBits))
        except UnconfirmedGPUCompletion:
            cleanup=False
            raise
        row.update({'device':str(props.deviceName),'pci':'1002:66af','api_version':int(props.apiVersion),'driver_version':int(props.driverVersion),'timestamp_period_ns':float(props.limits.timestampPeriod),'seed':20261126+args.size,'scope':'single_dispatch_correctness_not_throughput_qualification','wall_time_scope':'run_one resource setup, dispatch, fence, readback and validation; excludes process startup, instance/device setup and CPU reference generation'})
        print(json.dumps(row,allow_nan=False),flush=True)
        require(row['status']=='PASS','GPU output failed CPU reference tolerance')
    finally:
        if cleanup:
            if device: vk.vkDestroyDevice(device,None)
            vk.vkDestroyInstance(instance,None)

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print(f'FAIL: {type(exc).__name__}: {exc}',file=sys.stderr,flush=True)
        sys.exit(1)

