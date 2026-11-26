# Benchmark methodology

This guide describes proposed reporting standards, not new measured results. The historical numbers are in [results.md](results.md). The public v0.1.0 release ships only the bounded smoke test.

## Evidence and comparisons

Record device and PCI ID, OS, driver and Vulkan API version, toolchain and exact source revision. Record shape, precision of inputs, accumulation and outputs, workgroup configuration, repeat count and validation tolerances. Distinguish observed measurements, hypotheses and unknowns.

Use GPU timestamps for kernel timing when available; separately report end-to-end wall time, transfers and synchronization. For square GEMM, the conventional useful-work estimate is 2*N^3 operations divided by GPU time. For ALU microbenchmarks, count the intended arithmetic and verify that the compiler retained it before reporting an estimated throughput. Static instruction counts are not dynamic hardware counters.

Report individual samples, repeat statistics, CPU reference checks, and failures. Do not present BF16 storage as native BF16 arithmetic or treat different rounding contracts as bitwise equivalent. Do not infer bottlenecks from theoretical peak bandwidth or register counts alone.

## Safety and reproducibility

Start with small bounded workloads; never disable hardware or OS protections. Record telemetry availability and distinguish measured temperatures from unknown values. A software watchdog is not proof against rapid thermal overshoot. Do not distribute or run extended load tests on behalf of this project until the workload and monitoring are separately qualified.

Keep raw personal or proprietary diagnostic material local. Publish only reviewed source, reproducible instructions and sanitized measurements.

## Historical summary dataset

[data/gemm-summary.csv](../data/gemm-summary.csv) transcribes the 16 Phase V.3 summary values already published in results.md. It is not raw per-run data and does not supply missing clocks, temperatures, or repeat statistics. Separate packed-FP16 results remain in the report because they use a different numerical contract.
