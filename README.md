# VEGA Revival

**Community-driven Vulkan compute and architecture research for AMD Vega GPUs.**

VEGA Revival explores how older AMD GPUs can remain useful for modern compute, AI inference and graphics workloads using documented APIs and reproducible experiments.

[Early Research Preview v0.1.0](https://github.com/sergiojovani514-bot/VEGA-Revival/releases/tag/v0.1.0) · [Compute Kernels v0.2.0 candidate](tests/vulkan-compute/gemm-v0.2/README.md) · [Research results](docs/results.md) · [Compatibility](docs/compatibility.md) · [Roadmap](ROADMAP.md) · [Discussions](https://github.com/sergiojovani514-bot/VEGA-Revival/discussions)

## Current capabilities

| Capability | Status |
|---|---|
| Radeon VII Vulkan smoke test | Public, verified on Windows 10 |
| Bounded GEMM kernels | v0.2.0 candidate: four modes passed N=32 CPU-reference checks on one Radeon VII; other sizes unqualified |
| Paired Packed FP16 | N=32 correctness passed; the exact pipeline emitted packed half FMA instructions |
| PyTorch Vulkan inference | Experimental, historical small-model results; integration not shipped |
| HBM2, LDS and cache characterization | Planned research direction |
| Quantized LLM inference | Planned research direction |
| Mesh shaders, Nanite and FSR | Exploratory ideas only; no implementation shipped |

## Selected research results

Historical measurements from one Radeon VII (gfx906), not performance claims for the v0.1 smoke test.

| Workload | Result |
|---|---:|
| FP32 GEMM, 8192² | 3.391 TFLOPS |
| FP16 input, FP32 accumulation GEMM, 8192² | 4.496 TFLOPS |
| Packed FP16 GEMM, 8192² | 4.989 TFLOPS |
| Sustained FP32 ALU, two accumulators | 5.4342 TFLOPS (three runs) |
| Experimental mini Transformer | 2,224 parameters, CPU-reference agreement |

GEMM and ALU results are different workloads; do not compare them as equivalent measurements. Read [results and limitations](docs/results.md) and [benchmark methodology](docs/benchmark-methodology.md). Machine-readable historical GEMM summaries are available in [data/gemm-summary.csv](data/gemm-summary.csv).

## Quick start — Windows, Radeon VII

Use a working Vulkan driver, 64-bit Python and the official [Khronos glslang 16.6.0](https://github.com/KhronosGroup/glslang/releases/tag/16.6.0) compiler. The smoke test accepts Radeon VII PCI ID `1002:66AF` only. No driver modifications or administrator privileges are intended.

From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r smoke/requirements.txt
glslang -V --target-env vulkan1.1 -S comp -o smoke/add_one.spv smoke/add_one.comp
.\.venv\Scripts\python.exe smoke/vulkan_add_one.py
```

Use the full path to the official compiler if it is not on PATH. Expected output: `result=42` and `PASS`. See [the verified test record](SMOKE_TEST.md). This single dispatch is a functionality check, not a stress test.

## Compute kernels — v0.2.0 candidate

A bounded Vulkan GEMM runner covers FP32, FP16 accumulation, FP16 input with FP32 accumulation, and paired Packed FP16. All four passed one synchronized N=32 correctness case on Radeon VII. This is not a performance or repeatability qualification; larger sizes are not qualified. See the [package instructions and full test record](tests/vulkan-compute/gemm-v0.2/README.md).

## Join the research

We welcome independent results, particularly from Radeon VII, Vega 56/64 and Instinct MI25/MI50/MI60 owners. Other hardware and operating systems are not yet qualified. If the smoke test rejects your device, do not bypass the device check; share a compatibility report instead.

Read [CONTRIBUTING.md](CONTRIBUTING.md), then browse [open issues](https://github.com/sergiojovani514-bot/VEGA-Revival/issues) or join a discussion. Benchmark reports, documentation fixes and reviewed code contributions are welcome.

## Project scope and license

This is an independent research project, not an AMD driver replacement or a complete ROCm/CUDA alternative. Project-owned code is released under [MIT](LICENSE); see [third-party notices](THIRD_PARTY_NOTICES.md) for dependencies. The published v0.1.0 release remains an early preview.

