# Roadmap

The following milestones are proposed, not delivery dates or claims of existing support.

## v0.1 — Compute Foundation (released)

- [x] Minimal Vulkan compute smoke test on Radeon VII (1002:66AF).
- [x] Historical research measurements with limitations.
- [x] Contribution guidance, compatibility matrix and issue templates.
- [ ] Independent reproduction reports.

## v0.2 — Compute Kernels (qualification passed; public review pending)

- [x] Review source provenance, license, Vulkan feature chains, synchronization and error paths.
- [x] Package bounded FP32 and FP16 examples with build instructions.
- [x] Qualify four N=32 correctness cases on one Radeon VII and record CPU-reference results.
- [x] Validate all four Vulkan 1.2 SPIR-V modules and capture packed FP16 driver ISA summary.
- [ ] Complete public review and tag the release.

Only N=32 is qualified. Larger sizes, performance, stability, overflow and BF16 remain unqualified.

## Subsequent research directions

| Area | Next deliverable |
|---|---|
| VEGA Compute | Reviewed GEMM/GEMV code and reference comparisons |
| VEGA Memory | Qualified HBM2, LDS and cache probes, sanitized results |
| VEGA AI | Reviewed experimental PyTorch integration and baseline llama.cpp Vulkan results |
| VEGA Research | Architecture findings with evidence and device-specific limitations |
| VEGA Geometry | Small compute-based geometry prototypes |
| VEGA Gaming | Feasibility studies of upscaling and frame generation |

Geometry and gaming are exploratory; no mesh shader emulation, Nanite acceleration or FSR implementation is shipped. Production LLM support and cross-device compatibility require independent qualification.

