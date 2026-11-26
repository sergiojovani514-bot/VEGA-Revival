# Recorded research results

Historical results from a single Radeon VII (gfx906), Windows 10 build 19045, Vulkan API 1.3.260. These are not new tests of this export and are not cross-device benchmarks.

## Phase V.3 — GEMM

GPU timestamp throughput in TFLOPS, calculated as 2*N^3 / dispatch time. All 16 main cases passed FP64 CPU-reference checks within expected precision; repeats were byte-identical.

| Square N | FP32 | FP16 accumulation | FP16 input / FP32 accumulation | BF16 storage / FP32 |
|---:|---:|---:|---:|---:|
|1024|1.191|1.151|1.409|0.921|
|2048|3.314|3.082|4.040|2.009|
|4096|3.389|3.618|4.421|2.200|
|8192|3.391|3.641|4.496|2.623|

Separate packed-FP16 kernels reached 4.929 and 4.989 TFLOPS at N=4096 and 8192 respectively. They use two partial half sums and different rounding order. BF16 storage is not native BF16 arithmetic. No clock, hotspot or power telemetry was captured for V.3, and performance counters were not available.

## Phase V.6 — experimental torchvulkan

Small strict-mode Vulkan operations and a randomly initialized 2,224-parameter mini Transformer matched CPU references. 17 of 19 audited cases passed; BF16 matmul and BF16-to-FP32 cast were rejected. No production LLM, training or comprehensive PyTorch support was established.

## Phase V.7 — sustained FP32 ALU

At 8192 workgroups, one independent accumulator reached 4.5537 TFLOPS. Two accumulators averaged 5.4342 TFLOPS across three approximately five-second series, sample SD 0.0058 TFLOPS, maximum sampled hotspot 75 C. The rate is estimated from FMA counts and Vulkan timestamps, not instruction-retirement counters.

Four accumulators triggered a thermal stop during warmup (95 C sampled hotspot); no valid throughput was obtained. Heavy tests are not included or recommended. Static packed FP16 instructions were confirmed; no new sustained packed-FP16 runtime result was obtained. DOT2 instruction lowering was not established on the installed Vulkan driver.
