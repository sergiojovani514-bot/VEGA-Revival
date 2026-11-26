# Third-party notices

- `vulkan` Python binding 1.3.275.1 — Apache License 2.0. Upstream: https://github.com/realitix/vulkan. License text: `THIRD_PARTY_LICENSES-vulkan.txt`. Its installed metadata reports an Apache license classifier but incorrectly has `License: UNKNOWN`; the bundled license text is retained here.
- `cffi` 2.1.1 — MIT-0. Upstream: https://github.com/python-cffi/cffi. License text: `THIRD_PARTY_LICENSES-cffi.txt`.
- `pycparser` 3.12 — BSD-3-Clause. Upstream: https://github.com/eliben/pycparser. License text: `THIRD_PARTY_LICENSES-pycparser.txt`.
- Khronos glslang 16.6.0 was used as a build tool and is not redistributed. Its source license is BSD-3-Clause; upstream source and license: https://github.com/KhronosGroup/glslang. The installed executable came from an earlier-phase local archive and was not copied into this release.

These notices describe the smoke-test environment, not a bundling of the dependency implementations. Recheck versions and notices if dependencies change.
