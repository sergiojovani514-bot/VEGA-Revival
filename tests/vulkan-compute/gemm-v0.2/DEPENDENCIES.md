# Dependencies and provenance

## Project source

The test runner and shader are project-authored VEGA Revival files, released under the repository MIT license. The package is an independently reviewable source export with no bundled vendor implementation.

## Runtime dependencies

| Dependency | Pin / tested version | License and source | Distribution |
|---|---|---|---|
| NumPy | 2.5.5 | BSD 3-Clause; NumPy project | Installed by requirements, not vendored |
| Python Vulkan binding | 1.3.275.1 | Apache License 2.0; realitix/vulkan | Installed by requirements, not vendored |

The repository-level third-party notice retains the Vulkan binding license. The NumPy license text is included as THIRD_PARTY_LICENSES-numpy.txt.

## Build and validation tools

Khronos glslangValidator 16.0.0 and SPIRV-Tools v2025.5 from the Vulkan SDK 1.4.335.0 were used to compile and validate the four SPIR-V modules. The tools were not copied into this repository. Their upstream projects use BSD 3-Clause licensing.

No AMD DLLs, headers, runtime libraries, driver files, generated SPIR-V binaries, or other third-party implementation code are bundled.
