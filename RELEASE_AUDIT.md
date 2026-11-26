# v0.1 candidate export audit

## Export source

- Private source: `sergiojovani514-bot/vega-revival-gfx906`.
- Selected ref: `release/public-v0.1-candidate`.
- Source commit supplied by the project owner: `ccb7810d1f1982ce1b2085deeab54987fbc63cb0`.
- This directory is a clean file export; it contains no source `.git` directory or private commit history.
- GitHub API verified the staging commit SHA, author, message, timestamp, and parent. The source `smoke/PROVENANCE.md` states the Python runner, shader, and build files are project-authored for Phase V.1; its parent commit's `SOURCE-MANIFEST.sha256` matches the exported `add_one.comp`, `vulkan_add_one.py`, and `requirements.txt` byte-for-byte. The owner separately confirmed authorship/license authority for project-owned code and approved MIT on 2026-11-26.

## Included

- `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md`, `ROADMAP.md`.
- `smoke/add_one.comp`, `smoke/vulkan_add_one.py`, `smoke/requirements.txt`.
- `docs/results.md`, `docs/compatibility.md`.
- Issue and pull request templates under `.github/`.
- `.gitignore`.
- `LICENSE` (MIT, copyright 2026 VEGA Revival project contributors).
- `THIRD_PARTY_NOTICES.md` and upstream license texts for the Python binding and its dependencies.
- `SMOKE_TEST.md` with the fresh Radeon VII test result.

## Excluded

- Full GEMM and PyTorch harnesses: the candidate README says they are not included in the candidate; no provenance-ready public exports were identified.
- Research worktrees, private SKILL.md/knowledge bases, PAL and undocumented AMD interface research, driver binaries/disassembly, raw diagnostics, and machine-specific outputs.
- Compiled SPIR-V and generated artifacts.
- `LICENSE`: no license grant is present in the source candidate. The README explicitly conditions the intended MIT license on owner approval and provenance review. This export is not licensed for redistribution until written approval and review are recorded.

## Release gates

| Gate | Status | Evidence / next action |
|---|---|---|
| Clean export; no private Git history | PASS | Standalone Git root commit `456d05b`; no source `.git` history imported; working tree clean |
| File and secret/path review | PASS, pattern-based | Scanned all included source/docs for common credential and absolute path patterns; matches were explanatory policy text and this audit only. Repeat a human review before remote publication |
| Source provenance and third-party license review | PASS for included files | Source commit verified with GitHub API; the three executable/dependency source files match the prior source manifest SHA-256. Owner authorized project-owned code. Full GEMM/PyTorch and internal research outputs excluded. Dependencies: `vulkan` 1.3.275.1 (Apache-2.0; bundled license, metadata field says UNKNOWN), `cffi` 2.1.1 (MIT-0), `pycparser` 3.12 (BSD-3-Clause); glslang 16.6.0 build tool (BSD-3-Clause, not redistributed). See `THIRD_PARTY_NOTICES.md`. |
| MIT license approval | PASS | Owner explicitly confirmed MIT selection and publication authorization on 2026-11-26; `LICENSE` added |
| Fresh build and GPU smoke test | PASS | Windows 10 build 19045, Radeon VII 1002:66AF; glslang 16.6.0 compiled for Vulkan 1.1; Python 3.15.2 + vulkan 1.3.275.1; output `result=42`, fence signaled, `PASS`. One bounded dispatch only |
| Safety qualification | PARTIAL | Only the bounded one-dispatch smoke test is included; historical Phase V.7 documents a 95 °C thermal stop at four accumulators. No sustained stress tooling is included |
| New GitHub repository / public visibility | IN PROGRESS | Create separate repository `VEGA-Revival` with a clean initial history; keep source private |
| v0.1.0 release and announcements | IN PROGRESS | Publish Early Research Preview and release notes. Announcements may be drafted; do not post externally without approval |

## Current limitation

The smoke test was freshly run and passed. Historical results in `docs/results.md` are not new measurements. Only the code/data authorized by the owner and the small candidate subset are included; no internal study harnesses are included.

GitHub CLI installation was attempted from the official GitHub CLI 2.106.0 MSI; winget verified its hash but Windows Installer returned 1618 because another installation is active. Resume installation after that installer finishes, authenticate with the connected GitHub account, then create the independent repository and publish the verified commit. Never change visibility of or push to the source repository.
