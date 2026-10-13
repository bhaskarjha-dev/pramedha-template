# Changelog

All notable changes to the Pramedha Career Template.

## [0.1.0] — 2026-10-13

### Major: Architectural Streamlining, Minimum Context Router & Directory Flattening

Consolidated redundant and overlapping frameworks across the repository to achieve minimum context consumption with maximum purpose. Embedded a token-budgeted Task-to-Files Routing Matrix in `AGENTS.md` and `README.md`, unified role evaluation in `strategy/target-roles.md`, merged content planning into `strategy/digital-presence-plan.md`, relocated networking outreach copy to `assets/outreach-messages.md`, flattened application tracking to `strategy/job-tracker.md` and `strategy/job-platforms.md`, and integrated operations tooling and audits into `ops/guide.md`. Cleanly reduced repository footprint from 100 to 96 purposeful files with 100% test pass rates across all validation and cascade engines.

### Improved — Schema Harmony, Falsification Hardening & Cascade Robustness
- **Intelligent Scaffold-Aware Fill Detection (`.pramedha/validate.py`)** — Upgraded `compute_fill_status()` to inspect file contents and evaluate comment-only or placeholder templates as unfilled, reporting honest `0/13 (0%)` on clean template clones and eliminating false-positive fill reporting.
- **Target Role Level Enum Validation (`.pramedha/validate.py` & `.pramedha/schema-reference.md`)** — Added enum enforcement for `target_role_level` (`intern`, `junior`, `mid`, `senior`, `staff`, `principal`, `director`, `vp`, `c-level`) and aligned schema reference documentation.
- **Education Chronology & Multi-Domain Generalization (`identity/credentials.yaml`, `resume/sync.py`, `resume/master.yaml`)** — Added `start_date` and `end_date` support to education entries, updated `sync.py` to extract both dates, and broadened master resume education examples to support multi-degree histories, international GPA/CGPA scales (`GPA: 3.8/4.0`, `CGPA: 8.5/10`), and diverse standardized tests (`GRE`, `GMAT`, `GATE`, `USMLE`, `CFA`).
- **Identity Schema Privacy & Delivery Generalization (`identity/experience.yaml`, `identity/projects.yaml`)** — Purged private `# reason_for_leaving` stub from outward experience schema (retained in private `personal/career-narrative.md`), and broadened project comments to support non-code deliverables (`live_url`, case studies, whitepapers) and methodologies (`tech_or_tools`).
- **Asset Harmonization & Formal Application Letters (`assets/cover-letters/`, `assets/outreach-messages.md`)** — Replaced informal short-chat snippets in `referral.md` and `cold-outreach.md` with comprehensive, professional application cover letter documents (Internal Employee Referral application and Letter of Interest / Unsolicited Application), eliminating duplication with `assets/outreach-messages.md`.
- **AI Protocol Harmony (`.pramedha/agent-instructions.md`)** — Added explicit protocol steps and instructions in Phase D for `outreach-messages.md`, `testimonials.md`, and `project-briefs/`, and in Phase E for `networking.md`, while maintaining strict 33-step numbering consistency.
- **Global Inclusivity & Cross-File Integrity (`strategy/financial.md`, `personal/preferences.yaml`, `VISION.md`, `AGENTS.md`)** — Generalized housing comparisons to `1–2 Bed Apartment / Flat`, added cross-reference notes linking `preferences.yaml` compensation dealbreakers to authoritative `strategy/financial.md`, diversified vision mission statement examples across international currency scales ($185K+, ₹35+ LPA, £95K+), added `claims-and-evidence.md` to Context Router row 48, and clarified Rule 4 regarding private interview coaching vs outward publication with strict sandboxing for `identity/references.yaml`.
- **Data-Corpus & Getting Started Alignment (`data-corpus/README.md`, `GETTING_STARTED.md`)** — Separated sections 2 and 3 in `data-corpus/README.md` to avoid internal contradictions, aligned `GETTING_STARTED.md` intake table with all 7 data-corpus subdirectories, and added Windows PowerShell 1-click build guidance (`.\resume\build.ps1`).
- **Enum Parity & Validation in `.pramedha/validate.py`** — Expanded allowed values for `employment_type` (supporting both underscored and hyphenated variants, plus volunteer and freelance), `language_fluency` (adding `elementary`), `career_stage` (supporting student, early_career, mid_career, etc.), and `career_break_type`. Added validation for `work_authorization` (supporting both dict status and string forms) and eliminated false negatives in `identity.yaml` fill status detection.
- **Project Date Safety & Highlights in `resume/assemble.py`** — Eliminated date `KeyError` crash by safely resolving date via `.get()` with fallback to start_date/end_date formatting. Added preservation of project `url` and full support for multi-bullet highlights via list and dict syntax.
- **Variant Education Overrides** — Added ability for variant files to customize or override education entries (`education:`), seamlessly falling back to master shared education when omitted.
- **Manifest & Authority Map Completeness** — Registered cover letters (`assets/cover-letters/*.md`) and `resume/_yaml_utils.py` in `.pramedha/manifest.yaml`. Mapped all assets, financial strategy, personal documents, and journal logs in `ops/authority-map.md`.
- **PowerShell Console Encoding** — Added UTF-8 console output encoding guards to `resume/build.ps1` to prevent Unicode output exceptions across Windows environments.
- **Path Drift & Quick Start Reconciliation** — Fixed legacy paths in `.pramedha/agent-instructions.md`, clarified 8-folder digital footprint destinations in `data-corpus/README.md`, synchronized `ops/prompts.md` TOC with Prompt #17, and aligned `VISION.md` Quick Start steps with the 7-phase model.

### Added — Automation & Bridge Script
- **`resume/_yaml_utils.py`** — Extracted shared YAML utilities module providing order-preserving dumping, block style multiline string formatting, and RenderCV `present` literal handling across cascade tools.
- **`resume/sync.py` Achievements Synchronization** — Added `sync_achievements()` bridging awards and certifications from `identity/credentials.yaml` and hackathons from `identity/speaking-and-community.yaml` into `resume/master.yaml['achievements']`. Added `--section ach` / `achievements` CLI flag and collision-safe slug generation.
- **`resume/assemble.py --orphans` Analysis** — Added `--orphans` flag detecting unreferenced master bullets, roles, projects, and achievements across active variants, with explicit `[archived]` indicators.
- **`data-corpus/inbox/`** — Added zero-friction intake landing zone with `.gitkeep` for unsorted career evidence.
- **`validate.py --json` Mode** — Added machine-readable JSON validation reporting for CI/CD integration.
- **Expanded Identity-Master Parity** — `validate.py` now enforces parity for projects (`projects.yaml`) and education (`credentials.yaml`) against `master.yaml`.
- **Schema Version Tracking** — Added `schema_version: "0.1.0"` to `config.yaml` with automated integrity validation against `.pramedha/manifest.yaml`.
- **Prompt #17 in `ops/prompts.md`** — Added AI prompt for logging speaking engagements and hackathon wins.
- **Career Changer & Fast-Track Callouts** — Added pivoting strategies and ATS application speedup callouts (`assets/form-fill-cheatsheet.md`) to `GETTING_STARTED.md`.
- **`resume/sync.py`** — New cascade bridge script that automatically transforms verified facts in `identity/experience.yaml`, `identity/projects.yaml`, and `identity/credentials.yaml` into keyed pools in `resume/master.yaml`. Safe non-destructive merging with `--dry-run`, `--section`, and `--force` flags.
- **`assets/interview-prep/behavioral.md`** — Dedicated behavioral interview preparation guide mapping STAR stories from `assets/star-stories.md` to common questions, Amazon 16 Leadership Principles, and situational frameworks.
- **`.pramedha/examples/master-filled.yaml`** — Realistic populated master resume bullet pool pairing with `variant-example.yaml` for Alex Chen (Stripe/Twilio), demonstrating multi-phrasing bullets, publications, projects, and education.
- **Prompt #16 in `ops/prompts.md`** — Added "Lite Career Template Audit & Health Check" prompt for rapid AI-assisted validation, freshness checking, and anti-inflation auditing.

### Changed — Schema Unification & RenderCV v2.8 Modernization
- **Unified Experience Schema** — Renamed `title` → `position` and `subtitle` → `role_subtitle` in `identity/experience.yaml` to directly match native RenderCV schema.
- **Identity Precedence in Cascade** — Updated `resume/assemble.py` header loader to read `identity/identity.yaml` as primary profile source, falling back to `config.yaml`.
- **JSON Schema Directive** — `assemble.py` outputs `# yaml-language-server: $schema=...` directive pointing to RenderCV v2.8 schema, enabling immediate IDE autocompletion and linting in VS Code, Cursor, and Neovim.
- **RenderCV v2.8 Themes** — Expanded documented themes in `resume/design.yaml` and `resume/README.md` to all 12 supported themes, including `harvard`, `ink`, `opal`, `ember`, `developer`, `compact`, and `academic`.
- **Publications Support** — Added `PublicationEntry` schema handling in `resume/assemble.py`, `resume/master.yaml`, and `resume/sync.py`.
- **Locale & Settings Passthrough** — Mapped `config.yaml` `locale` to RenderCV `locale: { language: ... }` and supported RenderCV `settings:` block (custom date, pdf title, bold keywords).
- **Archived Roles Convention** — Added `archived: true` convention to `resume/master.yaml` to retain historic career roles in bullet pool while omitting from active variant files.

### Changed — Validator Enhancements (`.pramedha/validate.py`)
- **Skill Level Enum Validation** — Enforces valid skill levels (`beginner`, `intermediate`, `advanced`, `expert`) per `schema-reference.md`.
- **Date Chronology Checks** — Detects anachronisms, negative durations (`start_date > end_date`), and invalid date formats across experience and career breaks.
- **Identity-to-Master Parity** — Checks that filled employers in `identity/experience.yaml` have corresponding representation in `resume/master.yaml`.
- **Cross-File Technology Consistency** — Flags unlisted technologies used in deliverables or projects that are missing from `identity/skills.yaml`.
- **Authority Reconciliation & Optional Files** — Reclassified `speaking-and-community.yaml`, `volunteering.yaml`, and `references.yaml` to optional files, ensuring fresh clones pass strict validation without requiring non-universal community files.

### Fixed — Build Pipeline, Runtime Scripts & Resilience
- **Build Scripts Output Resolution & Windows Console Encoding** — Replaced `--output-folder-name "output"` with `-o $outputDir` / `-o "$OUTPUT_DIR"` in `resume/build.ps1` and `resume/build.sh`, fixing RenderCV output folder resolution. Added `$env:PYTHONIOENCODING = "utf-8"` in `build.ps1` to prevent Windows `charmap` codec crashes on completion checkmarks (`\u2713`).
- **Sync Tool Runtime Fixes & Unicode Support** — Fixed `NameError: generate_slug` in `resume/sync.py`. Upgraded `slugify()` and `generate_bullet_key()` with Unicode-aware regex (`re.UNICODE`) to preserve non-Latin alphabet characters. Disambiguated employment stints by `(company, start_date)` to support non-consecutive tenures at the same employer.
- **Technologies Synchronization & Section Ordering** — Implemented `sync_skills()` in `resume/sync.py` to auto-populate `master.yaml['technologies']` (`OneLineEntry` format) from `identity/skills.yaml`. Added variant `section_order` and fallback technology support in `resume/assemble.py`.
- **Locale Subtag Normalization** — Added BCP-47 / POSIX subtag stripping in `resume/assemble.py` (`raw_locale.split('-')[0].split('_')[0]`), cleanly mapping `en-US`, `en_GB`, etc., to `english` without triggering Pydantic validation errors.
- **RenderCV PublicationEntry & Credential Scaffolds** — Updated publication scaffolding in `identity/credentials.yaml` to native RenderCV v2.8 schema (`title`, `authors`, `date`, `journal`, `doi`, `url`), and added scaffolding for professional licenses and security clearances.
- **Portability & Privacy Sanitization** — Sanitized local workstation absolute links (`file:///d:/dev/...`) in `GETTING_STARTED.md` and `VISION.md`; scrubbed personal domain leak in `VISION.md`.
- **AI Protocol Harmony & Phased Guidance** — Reconciled `interview-prep/behavioral.md` and `networking.md` in `.pramedha/agent-instructions.md`; linked Prompt 16 in `ops/prompts.md` TOC; added phased prompt guidance in `GETTING_STARTED.md` to prevent LLM context limit truncation.
- **Multi-Domain Technical Interview Tracks** — Expanded `assets/interview-prep/technical.md` with structured preparation tracks across 6 professional domains (Engineering, Business & Product, Creative & Design, Medical & Clinical, Academic & Research, Legal & Policy).
- **Mathematical & Structural Consistency** — Reconciled role viability scoring in `strategy/target-roles.md` and `strategy/role-analysis.md` (33 pts for Tier A); aligned `assets/interview-prep/behavioral.md` question matrix with canonical STAR story titles; reconciled `VISION.md` status table to 7-phase model (A through G) and Quick Start sequence to Rule #3.
- **Schema & Validator Rigor** — Added comprehensive enum validation in `.pramedha/validate.py` covering all schema enum types (`profession_type`, `career_type`, `employment_type`, `location_type`, `language_fluency`, `career_stage`, `career_break_type`, `skill_level`). Updated config validation to accept identity defined in `identity/identity.yaml`. Clarified fill metrics reporting.
- **Automated CI Workflow** — Added `.github/workflows/validate.yml` for automated CI matrix testing across Ubuntu, Windows, Python 3.11, and Python 3.12.
- **Client Attribution & Career Breaks in Sync Pipeline** — Preserved freelance client attributions in bullet extraction; added career break synchronization into `resume/master.yaml` (`archived: true`).
- **Internationalization & Multi-Region Platforms** — Defaulted `config.yaml` to `currency: "USD"` with ISO 4217 instructions; neutralized region-specific compensation and housing metrics in `strategy/financial.md`; restructured `strategy/job-search/platforms.md` into Global, Remote, US/Americas, UK/Europe, and India/APAC platform matrices.
- **Relative Markdown Links & Registry Parity** — Fixed broken cross-folder relative links in `strategy/master-action-tracker.md`; updated `strategy/README.md` and `assets/README.md` file registries to cover all tracked files.
- **`CONTRIBUTING.md`** — Added an 8-point schema change checklist ensuring cross-repository synchronization for future contributions.
- **Line Ending Normalization** — Added `* text=auto` in `.gitattributes`.
- **Manifest Registry** — Set template version to 0.1.0 in `.pramedha/manifest.yaml` and registered new tools and interview prep files.

## [0.0.4] — 2026-10-13

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

## [0.0.3] — 2026-10-13

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
- **`.pramedha/manifest.yaml`** — Added `standalone: true` flag; added all new files to registry
- **All `Maps to:` comments** — Retained throughout template files for schema documentation; explicitly noted as having no functional dependency

### Template Stats
- Files: 58 → 67 (+9 new files total: 6 from Akanksha + 3 from Bhavya)
- Fill protocol: 29 steps → 33 steps across 7 phases
- Identity files: 9 → 10
- Authority map entries: 19 → 31
- External tool dependencies: 0 (fully standalone)

---

## [0.0.2] — 2026-06-19

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

## [0.0.1] — 2026-06-19

### Added
- Initial template: 58 files across 8 folders
- Schema aligned with PramedhaProfile (4-layer architecture)
- Resume cascade engine (generalized for any profession)
- Agent fill instructions (universal protocol for any AI)
- Progressive disclosure (Layer 0-4)
- Verification system (✅/⚠️/❌)
- Source authority map
- Example data in .pramedha/examples/
