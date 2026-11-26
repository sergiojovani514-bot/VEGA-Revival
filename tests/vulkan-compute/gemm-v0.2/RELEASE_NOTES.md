# v0.2.0 Compute Kernels — candidate notes

This candidate adds a bounded Vulkan GEMM correctness runner and source for FP32, sequential FP16 accumulation, FP16 input with FP32 accumulation, and paired Packed FP16.

Qualification is intentionally narrow:

- Four single-dispatch N=32 cases passed against the CPU reference on one Radeon VII.
- All four SPIR-V modules compiled and passed Vulkan 1.2 validation.
- The exact Packed FP16 module's driver ISA contains packed half FMA instructions.
- Synchronization validation passed for a representative FP16-input/FP32-accumulation run.
- No performance, repeat-stability, overflow, larger-size, BF16, or cross-device claim is made.

The source is project-authored and covered by the repository MIT license. This is a release candidate prepared for public review; it is not an unattended stress-test package.
