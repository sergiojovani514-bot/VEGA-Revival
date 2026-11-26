# VEGA Revival v0.2.0 — bounded GEMM kernels

This package contains a small Vulkan GEMM runner and four precision variants. Qualification is limited to one dispatch at N=32 on one Radeon VII (1002:66AF) under Windows 10 Pro. Larger CLI sizes are available but were not GPU-qualified in this release pass.

The four N=32 cases passed synchronized GPU execution and CPU-reference checks:

- FP32 × FP32 with FP32 accumulation.
- FP16 × FP16 with FP16 accumulation.
- FP16 × FP16 with FP32 accumulation.
- Paired Packed FP16 with FP16 output.

This is correctness evidence, not a performance benchmark or stability qualification. Each reported case used one dispatch and one sample. See QUALIFICATION.md and qualification-results.csv.

## Requirements

- Windows x64 and Vulkan 1.2 or newer.
- AMD Radeon VII with PCI ID 1002:66AF; other devices are intentionally rejected.
- Python 3.15.2 x64 was used for the recorded qualification.
- Pinned Python dependencies in requirements.txt.
- Khronos glslangValidator and spirv-val. The recorded build used glslang 16.0.0 and SPIRV-Tools v2025.5 from Vulkan SDK 1.4.335.0. Generated SPIR-V is not committed.

## Build and validate shaders

From PowerShell at the repository root:

```powershell
$glslang = 'C:/path/to/VulkanSDK/Bin/glslangValidator.exe'
$spirvVal = 'C:/path/to/VulkanSDK/Bin/spirv-val.exe'
Push-Location tests/vulkan-compute/gemm-v0.2
try {
    ./build-shaders.ps1 -GlslangExe $glslang
    Get-ChildItem *.spv | ForEach-Object {
        & $spirvVal --target-env vulkan1.2 $_.FullName
        if ($LASTEXITCODE -ne 0) { throw 'SPIR-V validation failed' }
    }
} finally {
    Pop-Location
}
```

## Run one bounded correctness case

Create the environment and install the pinned dependencies:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r tests/vulkan-compute/gemm-v0.2/requirements.txt
```

Run cases sequentially from the test directory:

```powershell
python ./bounded_gemm.py --size 32 --precision fp32
python ./bounded_gemm.py --size 32 --precision fp16_acc16
python ./bounded_gemm.py --size 32 --precision fp16_acc32
python ./bounded_gemm.py --size 32 --precision fp16_acc16 --packed
```

The runner checks the exact PCI ID, compute/timestamp queue, required 16-bit storage and arithmetic features, synchronized result, finite outputs, and an FP64 CPU reference computed from quantized inputs. A missing feature, allocation failure, shader error, timeout, or numerical mismatch is reported as failure. If GPU completion cannot be confirmed within the fence wait, stop and verify the device is idle before retrying.

Only sizes 32, 64, 128 and 256 are accepted because the shader uses a fixed 32×32 output tile and does not use a partial-tile-safe input path. Only N=32 is qualified here. The shader source contains an unused BF16 branch, but the build script and public runner do not expose or qualify BF16.

## License and provenance

Project code is covered by the repository MIT license. This package contains project-authored source and generated test records; it does not include vendor libraries, driver binaries, or generated SPIR-V. See DEPENDENCIES.md for third-party license details.
