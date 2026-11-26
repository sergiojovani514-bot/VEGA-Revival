# v0.2.0 Compute Kernels — qualification report

## Outcome

PASS for the four listed correctness cases at N=32 on one AMD Radeon VII (PCI 1002:66AF). This does not qualify N=64/128/256, performance, repeatability, overflow behavior, other devices, or other operating systems.

The test runner performs one dispatch per case, waits for a fence, reads the output, and checks it against an FP64 CPU matrix product of the same quantized input values. It requires finite outputs and applies the stated per-mode tolerances.

| Mode | GPU timestamp (ms) | Max absolute error | atol / rtol | Near-run Hotspot |
|---|---:|---:|---:|---:|
| FP32 / FP32 | 0.02304 | 1.2395e-7 | 2e-5 / 2e-4 | 29 °C |
| FP16 / FP16 | 0.03632 | 8.3971e-4 | 0.003 / 0.02 | 29 °C |
| FP16 / FP32 | 0.03216 | 6.6357e-8 | 2e-5 / 2e-4 | 30 °C |
| Paired Packed FP16 | 0.02992 | 6.1506e-4 | 0.003 / 0.02 | 30 °C |

Each case ran once; the single-sample timestamp is not a performance result. No claim of repeat stability is made. FP16 overflow was not exercised; the tested N=32 inputs produced zero non-finite outputs and zero reference outputs outside the FP16 finite range.

Full machine-readable rows are in qualification-results.json and qualification-results.csv. Source and generated SPIR-V SHA-256 hashes are in shader-hashes.csv. SPIR-V binaries are excluded from the public export.

## Static code audit

- The runner rejects devices other than PCI 1002:66AF, requires Vulkan 1.2, a compute queue with valid timestamp bits, and timestampComputeAndGraphics.
- FP16 paths query VkPhysicalDeviceFeatures2 → VkPhysicalDeviceVulkan12Features → VkPhysicalDevice16BitStorageFeatures; they require and then enable shaderFloat16 and storageBuffer16BitAccess. FP32 does not enable unnecessary 16-bit features.
- Fixed sizes are multiples of the 32×32 output tile and K tile 32. This avoids the source shader's unguarded edge-tile input loads for all accepted sizes. Only N=32 was exercised for this qualification.
- Host staging memory is explicitly required to be HOST_VISIBLE and HOST_COHERENT. Inputs are copied into device-local storage buffers. The command buffer uses transfer-write→compute-read, compute-write→transfer-read, and transfer-read→compute-write dependencies for the output. A fence is awaited before query and host readback. Coherent host memory removes the need for explicit flush/invalidate operations.
- The runner uses dedicated bounded allocations, three storage-buffer descriptors, a 4-byte push constant, and a single compute queue. Output coverage is checked through finite values and CPU comparison.
- Resource destruction happens after confirmed fence completion. On an unconfirmed submit/wait path, the runner intentionally avoids explicit destruction and exits; a five-second fence wait is not an execution cancellation mechanism.
- Two report labels were corrected before qualification: wall duration is runner_wall_ms (resource/pipeline setup through validation, excluding process and Vulkan instance/device startup and CPU-reference generation), and single-run output stability is null rather than a misleading true.
- CLI invalid size and invalid packed/precision combinations were confirmed to fail before creating the Vulkan instance.

## Vulkan validation and driver ISA

- An instrumented copy of the runner enabled VK_LAYER_KHRONOS_validation with synchronization validation and a debug callback for an FP16-input/FP32-accumulation run. It emitted zero warning/error messages; the CPU-reference check passed.
- The driver was queried through VK_AMD_shader_info for the exact Packed FP16 SPIR-V. It returned 51 VGPR, 24 SGPR, 4608 bytes LDS use, 0 scratch, workgroup 8×8, and 64 static v_pk_fma_f16 instructions. These are static pipeline resources and ISA, not dynamic counters or a measured occupancy value. Full disassembly is not part of this report.

## Environment and guarded load

- Windows 10 Pro build 19045; Python 3.15.2 x64; NumPy 2.5.5; Python Vulkan binding 1.3.275.1.
- Radeon VII API version reported as 1.3.260 (integer 4206852); Vulkan driver version integer 8388887; timestamp period 40 ns.
- Khronos glslangValidator 16.0.0 compiled four variants for Vulkan 1.2. SPIRV-Tools v2025.5 validated all four modules. The compiler and validator executables are not redistributed.
- The existing fail-closed ADLX guard used persistent sampling, an 80 °C pre-stop and 90 °C absolute cap, and a 100 ms in-flight allowance. Workloads were run sequentially with a cooldown gate at GPU/Hotspot ≤35 °C for three advancing samples. No limit tripped. Adjacent samples were GPU 27–28 °C, Hotspot 29–30 °C and board power 18–19 W; the approximately 0.1 s sensor cadence cannot resolve the 0.023–0.036 ms GPU dispatch itself.
- No system driver, Runtime, clock, voltage, power limit, VBIOS, or thermal protection was changed. No other GPU workload ran concurrently.

## Scope limits

Only N=32 is qualified. There was one correctness sample per mode, so repeatability and throughput are unknown. Larger sizes, deliberate overflow, BF16, and other runtimes remain unqualified. The measured timestamps are retained for reproducibility but must not be compared as a GEMM performance benchmark.
