# Changelog

All notable changes to the Pramedha Career Template.

## [2.1.0] — 2026-10-13

### Major: System-Wide Audit, Resilience & Multi-Profession Generalization

Comprehensive audit of all 67+ repository files resolved 34 findings across code, documentation, schemas, and automation.

### Fixed — Code & Cascade Engine
- **`resume/assemble.py`** — Implemented automated header merge from `config.yaml` into empty fields in `resume/master.yaml`, fully realizing the single-source-of-truth architecture. Fixed crash when validating empty template files (`_template.yaml`). Added UTF-8 console reconfigure preventing Windows `charmap` crashes on emojis. Filtered out `_` template files from automatic build discovery.
- **`resume/build.ps1` & `resume/build.sh`** — Made build scripts resilient to Python environments, missing RenderCV installations, and fixed output folder arguments.
- **`.pramedha/validate.py`** — Added validation for all 10 identity files (`speaking-and-community.yaml`, `volunteering.yaml`, `references.yaml`). Refined fill status logic to accurately differentiate real data from template scaffolding (clean clones report 0% instead of false 58%). Added 90-day file freshness detection (`check_freshness`).

### Fixed — Documentation & Cross-Reference Harmony
- **`ops/prompts.md`** — Corrected Prompt #1 protocol reference from obsolete "12-step" to the actual 7-phase, 33-step protocol.
- **`.pramedha/agent-instructions.md`** — Fixed Phase B header from "Steps 2-9" to "Steps 2-10" and Phase D from "Steps 14-20" to "Steps 14-21". Corrected LinkedIn headline limit to 220 characters.
- **`assets/platform-copy.md`** — Updated LinkedIn headline character limit to modern 220 characters (was 120).
- **`ops/session-handoff.md`** — Standardized session log order to newest-at-the-top, resolving contradiction between append rule and prepend template instruction.
- **`.pramedha/manifest.yaml`** — Completed file registry with 17+ previously omitted files across strategy, assets, personal, journal, and ops layers.

### Added — Privacy & Schema Enhancements
- **Privacy Architecture** — Moved sensitive financial figures (`target_salary_range`, `salary_floor`, `current_salary`) from public `config.yaml` into private `personal/preferences.yaml`.
- **`career_type` Support** — Added `career_type` (`employed | freelance | portfolio | academic | military | government | student`) in `config.yaml` with non-linear career hierarchy guidance in `identity/experience.yaml`.
- **Career Gap Handling** — Added `career_breaks: []` schema to `identity/experience.yaml` with verification tagging for sabbaticals, parental leave, caregiving, health, and transitions.
- **Enum Reconciliations** — Added `conversational` to `language_fluency` and unified `career_stage` options in `.pramedha/schema-reference.md` and `personal/preferences.yaml`.
- **`last_updated` Timestamp** — Added standard maintenance metadata field across YAML files.
- **Multi-Profession Examples** — Added 4 domain-specific skill matrix examples in `.pramedha/examples/`: `skills-business.yaml`, `skills-medical.yaml`, `skills-creative.yaml`, and `skills-academic.yaml`.
- **Evidence Locker Documentation** — Added instructional `README.md` files to all `data-corpus/` subdirectories (`resumes/`, `documents/`, `exports/`, `text/`, `media/`).
- **`CONTRIBUTING.md`** — Added open-source contributor guide and pull request standards.
- **Minimal Viable Career System** — Added "Just 3 Files" fast-track path in `GETTING_STARTED.md` to eliminate cognitive barrier for newcomers.

## [2.0.0] — 2026-10-13

### Major: Dogfooding-Driven Template Upgrade

All improvements below were discovered through real-world usage of the template over
4+ months of intensive career transformation work. Changes are strictly generalizable
improvements — no user-specific content.

### Added — New Files
- `identity/speaking-and-community.yaml` — **10th identity file**: speaking, hackathons, community memberships, content metrics. Separate data model from volunteering
- `strategy/master-action-tracker.md` — Central dashboard aggregating all pending work across 5 streams (Claim Debt, Portfolio, Digital Presence, Skill Building, Job Search). The file that turns the repo from a library into an operating system
- `strategy/digital-presence-plan.md` — Strategic plan for digital presence transformation with P0-P3 platform prioritization, phased execution, and metrics tracking
- `strategy/role-analysis.md` — **Optional** comprehensive role universe scan (8 parameters, 20+ roles) before narrowing to target roles. Prevents tunnel vision
- `assets/platform-copy.md` — Copy-paste ready bios at every length/format: email signature, GitHub bio (160 char), LinkedIn headline (120 char), Twitter bio, speaker bio, conference bio, forum signature
- `ops/session-handoff.md` — Session continuity log for AI-assisted workflows. Append-only, never delete. Prevents cold-start problem across sessions

### Changed — Structural Upgrades
- **`identity/claims-and-evidence.md`** — Added Measurement Tags system: `[measured]`, `[estimated]`, `[to-verify]`. Tags drive the master-action-tracker's Claim Debt stream, turning claims from a static audit into a dynamic work queue
- **`strategy/target-roles.md`** — Expanded evaluation from 5 to 8 parameters (+Time to Close Gaps, Interview Readiness, Competition Level). Added ATS keywords field, resume variant mapping table, shared foundation analysis, and positioning statement
- **`AGENTS.md`** — Added "Key Decisions Already Made (Do NOT Re-litigate)" section to prevent AI decision oscillation across sessions. Added session-handoff rule. Updated architecture block, event→file mapping, and quick-context table for all new files
- **`VISION.md`** — Expanded status table from 5 to 8 phases (added Claims Audit, Portfolio Polish, Digital Presence). Replaced stale "What's Pending" checklist with pointer to master-action-tracker. Added content engine to Future Scope. Expanded Quick Start to 9 steps
- **`ops/authority-map.md`** — Added 10 new authority entries for all new files and strategy files
- **`ops/guide.md`** — Added session-handoff to AI session DO/DON'T rules. Added event→file mappings for speaking/hackathon events and data-corpus extraction. Added master-action-tracker to weekly maintenance ritual
- **`.pramedha/agent-instructions.md`** — Expanded from 29-step to 33-step protocol. Added Step 8 (speaking-and-community.yaml), Step 20 (platform-copy.md), Steps 24-25 (master-action-tracker, digital-presence-plan). Updated all downstream step numbers. Added measurement tag instructions to claims step

### Added — Bhavya Dogfooding
- `ops/conversation-context-archive.md` — One-time founding session context preservation. Captures decisions, data gaps, contradictions, and artifacts from the initial fill session. Complementary to session-handoff.md (ongoing) — this is write-once (founding)
- `data-corpus/linkedin/README.md` + `data-corpus/github/README.md` — Pre-created subdirectories for common platform exports, reducing friction during initial data dump
- `VISION.md` Sub-Projects section — Universal pattern for tracking portfolio websites, GitHub profiles, and other spin-off projects spawned by the career system

### Changed — Standalone-First Architecture
- **Template is now fully standalone** — Works as a complete career operating system without any external tools, while remaining fully compatible with the Pramedha platform
- **`README.md`** — "Pramedha Compatibility" → "Pramedha Integration (Optional)" — reframed as standalone-first with optional Pramedha integration
- **`.pramedha/agent-instructions.md`** — Integration section reframed as optional, standalone usage is the default path
- **`.pramedha/schema-reference.md`** — Header rewritten to serve standalone users first, `Maps to:` comments documented as informational
- **`.pramedha/manifest.yaml`** — Added `standalone: true` flag; version bumped to 2.0.0; added all new files to registry
- **All `Maps to:` comments** — Retained throughout template files for schema documentation; explicitly noted as having no functional dependency

### Template Stats
- Files: 58 → 67 (+9 new files total: 6 from Akanksha + 3 from Bhavya)
- Fill protocol: 29 steps → 33 steps across 7 phases
- Identity files: 9 → 10
- Authority map entries: 19 → 31
- External tool dependencies: 0 (fully standalone)

---


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
