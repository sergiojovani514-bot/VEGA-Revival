# Compatibility matrix

The published v0.1.0 single-dispatch smoke test passed on one Radeon VII under Windows 10. See [the test record](../SMOKE_TEST.md). This is a functionality check, not a guarantee of application compatibility, performance or sustained-load stability.

| GPU | PCI ID | Environment | Status |
|---|---|---|---|
| Radeon VII | 1002:66AF | Windows 10 Pro build 19045 / Vulkan 1.3.260 | v0.1.0 smoke test passed on one device |
| Radeon Vega 56 | Not recorded | Not recorded | Untested; reports welcome |
| Radeon Vega 64 | Not recorded | Not recorded | Untested; reports welcome |
| Radeon Instinct MI25 | Not recorded | Not recorded | Untested; reports welcome |
| Radeon Instinct MI50 | Not recorded | Not recorded | Untested; reports welcome |
| Radeon Instinct MI60 | Not recorded | Not recorded | Untested; reports welcome |

The smoke test currently accepts only PCI ID 1002:66AF. Other devices need a separately reviewed device-selection change and validation. Linux and other driver configurations are unqualified. A Vulkan API version alone does not establish support for all shader features.
