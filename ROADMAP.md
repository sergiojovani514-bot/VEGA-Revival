# Roadmap

The following milestones are proposed, not delivery dates or claims of existing support.

## v0.1 — Compute Foundation (released)

- [x] Minimal Vulkan compute smoke test on Radeon VII (1002:66AF).
- [x] Historical research measurements with limitations.
- [x] Contribution guidance, compatibility matrix and issue templates.
- [ ] Independent reproduction reports.

## Proposed v0.2 — Compute Kernels

- Review provenance, license and error paths of existing GEMM source.
- Package bounded FP32/FP16 correctness examples and build instructions.
- Reproduce the exported code on Radeon VII; document exact environment and numerical contracts.
- Add machine-readable results, distinguish fresh measurements from historical ones.
- Keep unqualified sustained-load tools out of the release.

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
