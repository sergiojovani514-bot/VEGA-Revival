# Contributing

Start with a reproducibility report: GPU model and PCI device ID, OS and driver versions, Vulkan API version, toolchain versions, exact commands, pass/fail output, and relevant errors. Mark each result as observed, inferred, or unknown.

Choose an existing [issue](https://github.com/sergiojovani514-bot/VEGA-Revival/issues) or propose a small reproducible experiment. For comparisons, follow the [benchmark methodology](docs/benchmark-methodology.md). A failed or unsupported experiment is useful evidence when documented accurately.

Do not upload usernames, absolute personal paths, machine serial numbers, tokens, raw memory dumps, vendor driver binaries, or proprietary disassembly. Redact logs locally.

The current release includes only a single-dispatch smoke test. Do not run extended stress tests, disable thermal protections, change voltages, flash firmware, or modify a system driver. Support for other Vega GPUs requires separately reviewed device-selection changes.

For code, describe provenance and dependencies. Keep changes small and reproducible. Identify third-party code and its license. Project-owned code uses MIT (see [LICENSE](LICENSE)); do not submit material you lack permission to distribute.
