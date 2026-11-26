import argparse, struct, sys
from pathlib import Path
import vulkan as vk

AMD, RADEON_VII = 0x1002, 0x66AF

def require(ok, message):
    if not ok: raise RuntimeError(message)

def main():
    ap=argparse.ArgumentParser(description='Vulkan staged-buffer compute probe: 41 -> 42')
    ap.add_argument('--spv',type=Path,default=Path(__file__).with_name('add_one.spv'))
    args=ap.parse_args(); spv=args.spv.read_bytes()
    instance=vk.vkCreateInstance(vk.VkInstanceCreateInfo(sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
        pApplicationInfo=vk.VkApplicationInfo(sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,pApplicationName='VEGA Vulkan Compute Qualification',applicationVersion=1,pEngineName='none',engineVersion=1,apiVersion=vk.VK_MAKE_VERSION(1,1,0))),None)
    device=None; buffers=[]; memories=[]; owned={}
    try:
        physical=next((d for d in vk.vkEnumeratePhysicalDevices(instance) if (lambda p:p.vendorID==AMD and p.deviceID==RADEON_VII)(vk.vkGetPhysicalDeviceProperties(d))),None)
        require(physical is not None,'Radeon VII PCI 1002:66AF not enumerated')
        props=vk.vkGetPhysicalDeviceProperties(physical); families=vk.vkGetPhysicalDeviceQueueFamilyProperties(physical)
        qi=next((i for i,q in enumerate(families) if q.queueCount and q.queueFlags&vk.VK_QUEUE_COMPUTE_BIT),None); require(qi is not None,'no compute queue')
        print(f'device={props.deviceName} vendor=0x{props.vendorID:04x} device=0x{props.deviceID:04x}')
        print(f'apiVersion={props.apiVersion} driverVersion={props.driverVersion} queueFamily={qi} queueFlags=0x{families[qi].queueFlags:x} queueCount={families[qi].queueCount}')
        qci=vk.VkDeviceQueueCreateInfo(sType=vk.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,queueFamilyIndex=qi,queueCount=1,pQueuePriorities=[1.0])
        device=vk.vkCreateDevice(physical,vk.VkDeviceCreateInfo(sType=vk.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,queueCreateInfoCount=1,pQueueCreateInfos=[qci]),None); queue=vk.vkGetDeviceQueue(device,qi,0)
        mp=vk.vkGetPhysicalDeviceMemoryProperties(physical)
        def make_buffer(usage, required, preferred=0):
            b=vk.vkCreateBuffer(device,vk.VkBufferCreateInfo(sType=vk.VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,size=4,usage=usage,sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE),None)
            req=vk.vkGetBufferMemoryRequirements(device,b)
            candidates=[i for i in range(mp.memoryTypeCount) if req.memoryTypeBits&(1<<i) and (mp.memoryTypes[i].propertyFlags&required)==required]
            require(bool(candidates),f'no memory type required flags 0x{required:x}')
            i=next((j for j in candidates if mp.memoryTypes[j].propertyFlags&preferred==preferred),candidates[0])
            m=vk.vkAllocateMemory(device,vk.VkMemoryAllocateInfo(sType=vk.VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,allocationSize=req.size,memoryTypeIndex=i),None);vk.vkBindBufferMemory(device,b,m,0)
            buffers.append(b);memories.append(m);return b,m
        host=vk.VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT|vk.VK_MEMORY_PROPERTY_HOST_COHERENT_BIT
        staging_usage=vk.VK_BUFFER_USAGE_TRANSFER_SRC_BIT|vk.VK_BUFFER_USAGE_TRANSFER_DST_BIT
        src,srcmem=make_buffer(staging_usage,host); dst,dstmem=make_buffer(staging_usage,host)
        storage_usage=vk.VK_BUFFER_USAGE_STORAGE_BUFFER_BIT|vk.VK_BUFFER_USAGE_TRANSFER_SRC_BIT|vk.VK_BUFFER_USAGE_TRANSFER_DST_BIT
        data,datamem=make_buffer(storage_usage,vk.VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT)
        mapped=vk.vkMapMemory(device,srcmem,0,4,0);mapped[:]=struct.pack('<i',41);vk.vkUnmapMemory(device,srcmem)
        dsl=vk.vkCreateDescriptorSetLayout(device,vk.VkDescriptorSetLayoutCreateInfo(sType=vk.VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO,bindingCount=1,pBindings=[vk.VkDescriptorSetLayoutBinding(binding=0,descriptorType=vk.VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,descriptorCount=1,stageFlags=vk.VK_SHADER_STAGE_COMPUTE_BIT)]),None);owned['dsl']=dsl
        pl=vk.vkCreatePipelineLayout(device,vk.VkPipelineLayoutCreateInfo(sType=vk.VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,setLayoutCount=1,pSetLayouts=[dsl]),None);owned['pl']=pl
        sm=vk.vkCreateShaderModule(device,vk.VkShaderModuleCreateInfo(sType=vk.VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,codeSize=len(spv),pCode=spv),None);owned['sm']=sm
        stage=vk.VkPipelineShaderStageCreateInfo(sType=vk.VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,stage=vk.VK_SHADER_STAGE_COMPUTE_BIT,module=sm,pName='main')
        pipe=vk.vkCreateComputePipelines(device,vk.VK_NULL_HANDLE,1,[vk.VkComputePipelineCreateInfo(sType=vk.VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO,stage=stage,layout=pl)],None)[0];owned['pipe']=pipe
        pool=vk.vkCreateDescriptorPool(device,vk.VkDescriptorPoolCreateInfo(sType=vk.VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO,maxSets=1,poolSizeCount=1,pPoolSizes=[vk.VkDescriptorPoolSize(type=vk.VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,descriptorCount=1)]),None);owned['pool']=pool
        ds=vk.vkAllocateDescriptorSets(device,vk.VkDescriptorSetAllocateInfo(sType=vk.VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO,descriptorPool=pool,descriptorSetCount=1,pSetLayouts=[dsl]))[0]
        bi=vk.VkDescriptorBufferInfo(buffer=data,offset=0,range=4);wr=vk.VkWriteDescriptorSet(sType=vk.VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET,dstSet=ds,dstBinding=0,descriptorCount=1,descriptorType=vk.VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,pBufferInfo=[bi]);vk.vkUpdateDescriptorSets(device,1,[wr],0,None)
        cpool=vk.vkCreateCommandPool(device,vk.VkCommandPoolCreateInfo(sType=vk.VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO,flags=vk.VK_COMMAND_POOL_CREATE_TRANSIENT_BIT,queueFamilyIndex=qi),None);owned['cpool']=cpool
        cb=vk.vkAllocateCommandBuffers(device,vk.VkCommandBufferAllocateInfo(sType=vk.VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO,commandPool=cpool,level=vk.VK_COMMAND_BUFFER_LEVEL_PRIMARY,commandBufferCount=1))[0]
        vk.vkBeginCommandBuffer(cb,vk.VkCommandBufferBeginInfo(sType=vk.VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,flags=vk.VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT))
        region=vk.VkBufferCopy(srcOffset=0,dstOffset=0,size=4);vk.vkCmdCopyBuffer(cb,src,data,1,[region])
        b1=vk.VkBufferMemoryBarrier(sType=vk.VK_STRUCTURE_TYPE_BUFFER_MEMORY_BARRIER,srcAccessMask=vk.VK_ACCESS_TRANSFER_WRITE_BIT,dstAccessMask=vk.VK_ACCESS_SHADER_READ_BIT|vk.VK_ACCESS_SHADER_WRITE_BIT,srcQueueFamilyIndex=vk.VK_QUEUE_FAMILY_IGNORED,dstQueueFamilyIndex=vk.VK_QUEUE_FAMILY_IGNORED,buffer=data,offset=0,size=4)
        vk.vkCmdPipelineBarrier(cb,vk.VK_PIPELINE_STAGE_TRANSFER_BIT,vk.VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,0,0,None,1,[b1],0,None)
        vk.vkCmdBindPipeline(cb,vk.VK_PIPELINE_BIND_POINT_COMPUTE,pipe);vk.vkCmdBindDescriptorSets(cb,vk.VK_PIPELINE_BIND_POINT_COMPUTE,pl,0,1,[ds],0,None);vk.vkCmdDispatch(cb,1,1,1)
        b2=vk.VkBufferMemoryBarrier(sType=vk.VK_STRUCTURE_TYPE_BUFFER_MEMORY_BARRIER,srcAccessMask=vk.VK_ACCESS_SHADER_WRITE_BIT,dstAccessMask=vk.VK_ACCESS_TRANSFER_READ_BIT,srcQueueFamilyIndex=vk.VK_QUEUE_FAMILY_IGNORED,dstQueueFamilyIndex=vk.VK_QUEUE_FAMILY_IGNORED,buffer=data,offset=0,size=4)
        vk.vkCmdPipelineBarrier(cb,vk.VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,vk.VK_PIPELINE_STAGE_TRANSFER_BIT,0,0,None,1,[b2],0,None)
        vk.vkCmdCopyBuffer(cb,data,dst,1,[region]);vk.vkEndCommandBuffer(cb)
        fence=vk.vkCreateFence(device,vk.VkFenceCreateInfo(sType=vk.VK_STRUCTURE_TYPE_FENCE_CREATE_INFO),None);owned['fence']=fence
        submit=vk.VkSubmitInfo(sType=vk.VK_STRUCTURE_TYPE_SUBMIT_INFO,commandBufferCount=1,pCommandBuffers=[cb]);vk.vkQueueSubmit(queue,1,[submit],fence);vk.vkWaitForFences(device,1,[fence],vk.VK_TRUE,30_000_000_000)
        mapped=vk.vkMapMemory(device,dstmem,0,4,0);result=struct.unpack('<i',bytes(mapped))[0];vk.vkUnmapMemory(device,dstmem)
        print(f'input=41 result={result} expected=42 transfer_copy=host_to_device_and_device_to_host fence_signaled=true')
        require(result==42,f'wrong GPU result {result}');print('PASS')
    finally:
        if device:
            for key,fn in [('fence',vk.vkDestroyFence),('cpool',vk.vkDestroyCommandPool),('pool',vk.vkDestroyDescriptorPool),('pipe',vk.vkDestroyPipeline),('sm',vk.vkDestroyShaderModule),('pl',vk.vkDestroyPipelineLayout),('dsl',vk.vkDestroyDescriptorSetLayout)]:
                if key in owned:fn(device,owned[key],None)
            for b in buffers:vk.vkDestroyBuffer(device,b,None)
            for m in memories:vk.vkFreeMemory(device,m,None)
            vk.vkDestroyDevice(device,None)
        vk.vkDestroyInstance(instance,None)
if __name__=='__main__':
    try:main()
    except Exception as exc:print(f'FAIL: {type(exc).__name__}: {exc}',file=sys.stderr);raise
