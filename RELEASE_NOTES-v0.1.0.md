# VEGA Revival v0.1.0 — Early Research Preview

VEGA Revival is an independent community research project exploring Vulkan compute and architecture optimization on AMD Vega GPUs.

## Included

- One minimal Vulkan compute smoke test for Radeon VII (`1002:66AF`).
- A tested Windows setup path using Python `vulkan==1.3.275.1` and Khronos glslang 16.6.0.
- Historical Radeon VII research measurements with explicit limitations.
- A compatibility matrix, safety guidance, contribution/security/community documents, and issue templates.

## Verification

The included shader was compiled and the one-dispatch test passed on Windows 10 Pro build 19045 with a Radeon VII: `41 → 42`, fence signaled, `PASS`. This is a functionality smoke test, not a sustained-load or thermal qualification.

## Limits

Only Radeon VII `1002:66AF` is accepted by the smoke test. Other GPUs, operating systems, and driver configurations are unqualified. Full GEMM and PyTorch harnesses, stress tools, driver modifications, and undocumented AMD interfaces are not included. Historical performance figures are not new benchmarks from this release.

The project-owned code is released under MIT. Third-party notices and license texts are included for the Python Vulkan binding and its dependencies.
