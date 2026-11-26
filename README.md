# VEGA Revival — Compute Foundation

Independent, community-driven Vulkan compute research for AMD Vega GPUs, starting with Radeon VII (gfx906).

**Status: v0.1 release candidate — not yet publicly released.** This is a research project, not an AMD driver replacement or a complete ROCm/CUDA alternative.

## What has been demonstrated

On one Radeon VII under Windows 10, project experiments verified Vulkan compute, CPU-reference-checked GEMM, packed FP16 instructions and an experimental PyTorch Vulkan inference path. The included smoke test checks a staged host-to-device-to-host computation (41 → 42). It intentionally accepts only Radeon VII PCI 1002:66AF; other devices are not yet qualified.

See [research results](docs/results.md) for measured numbers and limitations. The full GEMM and PyTorch harnesses are not included in this initial candidate.

The candidate smoke test passed on a Radeon VII. See the [test record](SMOKE_TEST.md) for the exact environment and output.

## Quick start (Windows, Radeon VII)

Use a working vendor Vulkan driver, a 64-bit Python virtual environment, and the official Khronos glslang 16.6.0 compiler (https://github.com/KhronosGroup/glslang/releases/tag/16.6.0; Windows executable `glslang.exe`). No driver modifications or administrator privileges are intended.

From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r smoke/requirements.txt
glslang -V --target-env vulkan1.1 -S comp -o smoke/add_one.spv smoke/add_one.comp
.\.venv\Scripts\python.exe smoke/vulkan_add_one.py
```

Use the full path to the official compiler if it is not on PATH. Expected output includes result=42 and PASS. If a device, compiler or Vulkan dependency is missing, report the error rather than bypassing checks.

## Help wanted

We welcome reproducibility reports from Radeon VII, Vega 56/64 and Instinct MI50/MI60 owners. Support for devices other than the tested Radeon VII is a research goal, not a claim. See [contributing](CONTRIBUTING.md).

## Roadmap

- Vulkan compute and memory architecture research.
- Quantized inference and llama.cpp Vulkan optimization.
- Experimental PyTorch integration.
- Exploratory geometry, meshlet and upscaling research.

No FSR, mesh shader emulation, Nanite acceleration or production LLM support is included in this candidate.

## Licensing

The project intends to use MIT for its own code, subject to owner approval and provenance review before public release. No license grant is made by this private candidate. Third-party dependencies keep their respective licenses. This project is independent of AMD.
