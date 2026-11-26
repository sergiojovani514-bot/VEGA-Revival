# v0.1 candidate export audit

## Export source

- Private source: `sergiojovani514-bot/vega-revival-gfx906`.
- Selected ref: `release/public-v0.1-candidate`.
- Source commit supplied by the project owner: `ccb7810d1f1982ce1b2085deeab54987fbc63cb0`.
- This directory is a clean file export; it contains no source `.git` directory or private commit history.
- GitHub connector content was fetched at the exact commit. Local `git ls-remote` access and authenticated GitHub CLI were unavailable, so the source commit could not be independently verified through local Git.

## Included

- `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md`, `ROADMAP.md`.
- `smoke/add_one.comp`, `smoke/vulkan_add_one.py`, `smoke/requirements.txt`.
- `docs/results.md`, `docs/compatibility.md`.
- Issue and pull request templates under `.github/`.
- `.gitignore`.

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
| Source provenance and third-party license review | BLOCKED | Obtain owner confirmation and verify origins of project-authored and adapted material; audit dependency/license notices |
| MIT license approval | BLOCKED | Owner approval is required; do not add an MIT license or publish until documented |
| Fresh build and GPU smoke test | BLOCKED | Python 3.15.2 syntax compilation passed for `smoke/vulkan_add_one.py`; Vulkan binding is not installed, glslang/glslc are not available, and no GPU smoke run was performed. Install the pinned dependency and official glslang 16.6.0, then run the README commands on a qualified Radeon VII and record sanitized output |
| Safety qualification | PARTIAL | Only the bounded one-dispatch smoke test is included; historical Phase V.7 documents a 95 °C thermal stop at four accumulators. No sustained stress tooling is included |
| New GitHub repository / public visibility | NOT STARTED | Keep `VEGA-Revival` private until all prior gates pass, then create with a clean initial history and confirm permissions |
| v0.1.0 release and announcements | NOT STARTED | After publication gates; draft announcements separately and do not post externally without approval |

## Current limitation

This is a reviewable release-candidate bundle, not a verified build or a published project. The results in `docs/results.md` are historical measurements and are not fresh tests of this export. No license rights are granted by this bundle.

GitHub CLI `gh` was not found and local Git authentication to the private source remote was not confirmed. No remote repository was created or changed.
