# Contributing

Start with a reproducibility report: GPU model and PCI device ID, OS and driver versions, Vulkan API version, toolchain versions, exact commands, pass/fail output, and relevant errors. Mark each result as observed, inferred, or unknown.

Do not upload usernames, absolute personal paths, machine serial numbers, tokens, raw memory dumps, vendor driver binaries, or proprietary disassembly. Redact logs locally.

The candidate includes only a single-dispatch smoke test. Do not run extended stress tests, disable thermal protections, change voltages, flash firmware, or modify a system driver. Support for other Vega GPUs requires separately reviewed device-selection changes.

For code, describe provenance and dependencies. Keep changes small and reproducible. The project license and contribution terms must be approved before accepting public contributions.
