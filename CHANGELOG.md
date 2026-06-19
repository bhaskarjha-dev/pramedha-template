# Changelog

All notable changes to the Pramedha Career Template.

## [1.1.0] — 2026-06-19

### Added
- `LICENSE` — MIT license file
- `ops/prompts.md` — 15 copy-paste AI prompts for day-to-day operations
- `ops/audit-checklist.md` — 10-area systematic freshness check
- `.pramedha/validate.py` — Template validator (syntax, fill status, integrity)
- `.pramedha/manifest.yaml` — Machine-readable metadata for CLI auto-detection
- `strategy/role-deep-dives.md` — Detailed interview prep per target role
- `strategy/offer-comparison.md` — Weighted offer comparison matrix
- `strategy/weekly-tracker.md` — Current week's checklist
- `strategy/job-search/platforms.md` — Where to apply + strategies
- `.gitattributes` — LFS hints, line endings, generated file markers
- Security & Privacy section in README
- Validation section in README
- Partial Fill Protocol in agent-instructions.md

### Changed
- `resume/assemble.py` — Generalized config handling, moved config read outside loop
- `.pramedha/schema-reference.md` — Documented experience schema flattening on import
- `.pramedha/agent-instructions.md` — Added partial fill protocol + common tasks

### Fixed
- assemble.py docstring referenced hardcoded variant names
- Config.yaml read happened inside variant loop (N reads instead of 1)

## [1.0.0] — 2026-06-19

### Added
- Initial template: 58 files across 8 folders
- Schema aligned with PramedhaProfile (4-layer architecture)
- Resume cascade engine (generalized for any profession)
- Agent fill instructions (universal protocol for any AI)
- Progressive disclosure (Layer 0-4)
- Verification system (✅/⚠️/❌)
- Source authority map
- Example data in .pramedha/examples/
