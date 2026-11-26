# Radeon VII Vulkan smoke test

## Result

**PASS — one bounded compute dispatch.** The test stages one signed 32-bit integer from host memory to device-local storage, dispatches one workgroup that adds one, copies the value back, waits for a fence, and verifies `42`.

## Environment

- OS: Windows 10 Pro, build 19045
- GPU: AMD Radeon VII, PCI vendor/device `1002:66AF`
- Python: 3.15.2, 64-bit
- Python Vulkan binding: `vulkan==1.3.275.1`
- Shader compiler: Khronos glslang 16.6.0
- Requested Vulkan API: 1.1; physical device reported API version 1.3.260

## Reproduction

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r smoke/requirements.txt
glslang -V --target-env vulkan1.1 -S comp -o smoke/add_one.spv smoke/add_one.comp
.\.venv\Scripts\python.exe smoke/vulkan_add_one.py
```

Observed output (driver version is printed as the Vulkan integer encoding):

```text
device=AMD Radeon VII vendor=0x1002 device=0x66af
apiVersion=4206852 driverVersion=8388887 queueFamily=0 queueFlags=0xf queueCount=1
input=41 result=42 expected=42 transfer_copy=host_to_device_and_device_to_host fence_signaled=true
PASS
```

This is a minimal functionality check, not a stability, performance, or thermal qualification. No extended load was run.
