# Third-party notices

- `vulkan` Python binding 1.3.275.1 — Apache License 2.0. Upstream: https://github.com/realitix/vulkan. License text: `THIRD_PARTY_LICENSES-vulkan.txt`. Its installed metadata reports an Apache license classifier but incorrectly has `License: UNKNOWN`; the bundled license text is retained here.
- `cffi` 2.1.1 — MIT-0. Upstream: https://github.com/python-cffi/cffi. License text: `THIRD_PARTY_LICENSES-cffi.txt`.
- `pycparser` 3.12 — BSD-3-Clause. Upstream: https://github.com/eliben/pycparser. License text: `THIRD_PARTY_LICENSES-pycparser.txt`.
- NumPy 2.5.5 — BSD 3-Clause. Upstream: https://numpy.org/. License text from the installed distribution is retained at tests/vulkan-compute/gemm-v0.2/THIRD_PARTY_LICENSES-numpy.txt.
- Khronos glslang 16.6.0 was used for the v0.1.0 smoke test. v0.2.0 kernel qualification used glslang 16.0.0 and SPIRV-Tools v2025.5 from Vulkan SDK 1.4.335.0; both tools use BSD-3-Clause licensing and are not redistributed. Upstream: https://github.com/KhronosGroup/glslang and https://github.com/KhronosGroup/SPIRV-Tools.

These notices describe the smoke-test environment, not a bundling of the dependency implementations. Recheck versions and notices if dependencies change.

