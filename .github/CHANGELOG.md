# Changelog

All notable changes to the Pramedha Career Template.

## [0.1.0] — 2026-10-30 (Audit Remediation & Cascade Hardening)

### Architecture, Safety & Integrity Hardening
- **Variant Section Omission & Whitelist Ordering (`tools/resume/assemble.py`)** — Fixed section omission logic so specifying `section_order` in a variant acts as an intentional whitelist, cleanly omitting unlisted sections rather than re-appending them. Fixed `technologies: []` and `education: []` to allow explicit section suppression instead of falling back to `master.yaml`.
- **Variant Template Scaffolding Alignment (`tools/resume/variants/_template.yaml`, `tools/resume/jd/_template.yaml`)** — Commented out `# technologies: []` in variant scaffolding templates, aligning with `# education: []` so new variants cleanly inherit master technologies by default while enabling intentional override or suppression.
- **Year-Only Date Chronology Resolution (`.pramedha/validate.py`)** — Upgraded `parse_flexible_date()` with `is_end_date` context, resolving year-only end dates (`YYYY`) to month 12 for chronology checks and eliminating false warnings when start dates contain explicit months (e.g., `2024-05` to `2024`).
- **Speaking & Volunteering Ingestion into Achievements (`tools/resume/sync.py`)** — Added automatic ingestion of public speaking engagements from `identity/speaking-and-community.yaml` and volunteer initiatives from `identity/volunteering.yaml` into `master.yaml['achievements']`.
- **Master Section Banner Preservation (`tools/resume/sync.py`)** — Added deterministic section banner preservation when writing `master.yaml`, maintaining visual section dividers across synchronization cycles.
- **Defensive Path Guard in Template Updater (`tools/update_template.py`)** — Added explicit guard when `paths` is empty before invoking `git status`, preventing false dirty working tree aborts across unrelated repository files.
- **Virtual Environment Setup & Hermetic Resume Build (`tools/resume/requirements.txt`, `tools/resume/build.ps1`, `tools/resume/build.sh`)** — Documented and pinned RenderCV runtime dependencies (`pyyaml==6.0.3` and `rendercv[full]==2.8` for Python 3.12+). Rewrote build runners to activate repository `.venv` or fail with informative diagnostic guidance.
- **Non-Experience Claim Verification Propagation (`tools/resume/sync.py`, `tools/resume/assemble.py`)** — Extended verification status propagation across public talks, volunteering, certifications, awards, hackathons, licenses, clearances, patents, grants, projects, and degrees into `_verification`. `assemble.py` emits warnings when any selected claim is marked `❌` or `UNVERIFIED` (Soft Gate D1=B), while stripping `_verification` from education before compiling RenderCV YAML.
- **User Test Suite Isolation (`pytest.ini`, `.github/CONTRIBUTING.md`, `tests/e2e/test_build_exit_code.py`)** — Restored `testpaths = tools/resume/tests .pramedha/tests tests/e2e` in `pytest.ini`, keeping template document checks (`tests/docs`) in the dedicated CI job `template-checks` so upgrading user repositories never fail on customized template documents. Updated exit code tests to replace active themes via regex rather than assuming `engineeringresumes`.
- **Empty List Section Override Notice (`tools/resume/assemble.py`)** — Added diagnostic notice in `assemble.py` when `technologies: []` or `education: []` hides a master section, alerting users upgrading variants from v0.1.0 templates. Delete the line to inherit from `master.yaml` or leave the section out of `section_order` to hide intentionally.
- **YAML Scalar Crash Regression Suite (`tests/e2e/test_yaml_scalar_regressions.py`)** — Restored full regression suite validating default-mode `validate.py` and `sync.py` on numeric/boolean/null scalars.
- **First Sync Migration Behavior** — The first `sync.py` run after updating writes `_source` and `_verification` into `master.yaml` once (with automatic backup `master.yaml.bak`). Subsequent sync runs remain strictly idempotent ("already up to date").
- **YAML Scalar Coercion Safety (`tools/resume/sync.py`, `.pramedha/validate.py`)** — Enforced safe text coercion via `as_text()` across all synchronizer and validator fields, preventing YAML numeric / boolean coercion crashes on versions, dates, and names.
- **Claim Verification Soft Gate (`tools/resume/sync.py`, `tools/resume/assemble.py`)** — Propagated `verification` status from `identity/` into `master.yaml` as `_verification`. `assemble.py` issues prominent warnings on unverified (`❌` / `[unverified]`) claims while stripping internal markers on output and compiling cleanly.
- **Claim Provenance & Anti-Staleness Tracking (`tools/resume/sync.py`, `tools/resume/assemble.py`)** — Embedded exact `_source` pointer strings on synchronized roles and bullets. `sync.py` back-fills sources on first run; in-place updates are applied for changed dates and locations; stale bullets strictly abort the build (exit 1), and unsourced bullets typed directly into `master.yaml` emit soft warnings until moved into `identity/experience.yaml`. Fixed career-break synchronization position mapping; career-break entries written by the old `sync.py` must be deleted from `master.yaml` and re-synced.
- **Variant Output Collisions & Template Placeholders (`tools/resume/assemble.py`)** — Enforced output filename hygiene with collision detection across multiple variants, sanitized output paths, and rejected template placeholder summaries.
- **Privacy Enforcement & Private-Only Model (`README.md`, `.gitignore`, `.github/workflows/validate.yml`)** — Switched repository model to strictly private-only; removed public override blocks from `.gitignore` (existing copies should delete the "PUBLIC REPOSITORY SAFETY OVERRIDE" block from `.gitignore`). Added `privacy-guard` GitHub Actions workflow to block public repositories.
- **Confidentiality & NDA Guards (`data-corpus/README.md`, `.pramedha/agent-instructions.md`)** — Added explicit guidance on employer confidentiality and intellectual property; excluded internal wikis, RFCs, and schemas; guided LinkedIn exports to profile-only data.
- **Standalone Template Update Mechanism (`tools/update_template.py`, `.pramedha/manifest.yaml`)** — Introduced `tools/update_template.py` with manifest-driven `template_owned` paths, allowing clean zero-merge updates without touching user data or custom configuration. Copies made before this update can bootstrap via:
  ```bash
  git fetch upstream
  git checkout upstream/main -- tools/update_template.py tools/resume/requirements.txt
  git commit -m "Add template update script"
  ```
- **Validator Truth & Integrity (`.pramedha/validate.py`, `.pramedha/tests/test_validate.py`)** — Fixed tag inspection to check parsed values instead of raw text substrings, delegated variant validation to `assemble.validate_variant()`, and removed dead mock tests in `.pramedha/tests`.
- **Traceable Evidence Paths (`.pramedha/validate.py`, `identity/*.yaml`, `.pramedha/examples/*.yaml`)** — Enforced that `✅ VERIFIED` claims reference an existing file under `data-corpus/` or a valid public URL (`http://` / `https://`).
- **Agent Safety Rules (`AGENTS.md`, `.pramedha/agent-instructions.md`, `ops/prompts.md`)** — Added explicit untrusted data boundary rules for AI agents: text in `data-corpus/` and job postings is strictly data, not instructions; agents must prompt the user before sending data off the machine or modifying repository visibility.
- **Front Page Discovery (`README.md`)** — Added "Who it's for", "What you need", "See it" linking to compiled sample PDF (`docs/sample/alex-chen-backend.pdf`), and "Limits" directly to the top screen of `README.md`. Removed invalid releases page links.


## [0.1.0] — 2026-10-16 (Autonomous Quality Audit & Cascade Integrity)

### Fixed — Verification Tag Leakage & Cascade Engine Hardening
- **Verification Tag Stripping on RenderCV Output (`tools/resume/assemble.py`)** — Implemented `clean_bullet_tags()` to automatically strip internal verification tags (`[measured]`, `[estimated]`, `[to-verify]`, `[unverified]`, `[partially-verified]`) and internal emojis (`✅`, `⚠️`, `❌`) so they never leak into candidate-facing resume PDFs. Added `--keep-tags` CLI flag for internal review and verification auditing.
- **Social Network URL Sanitization (`tools/resume/assemble.py`)** — Sanitized usernames extracted from full URLs by stripping tracking queries and URL fragments (`?.*`, `#.*`), and properly extracted Google Scholar user IDs from query parameters (`user=...`).
- **Variant Design Overrides (`tools/resume/assemble.py`)** — Implemented deep-merge of variant-level `design:` block into `design.yaml`, enabling target-specific theme, typography, color, and margin overrides per resume variant.
- **RenderCV PDF Output Alignment (`tools/resume/assemble.py`)** — Aligned `--render` to use `output_filename` rather than `variant_name`, matching the output structure produced by `build.ps1` and `build.sh`.
- **Python Subprocess & Virtualenv Reliability (`tools/resume/assemble.py`)** — Used `[sys.executable, "-m", "rendercv"]` for RenderCV invocations, added missing `import re`, and enforced explicit UTF-8 encoding on subprocess pipelines across Windows and Unix platforms.

### Improved — Synchronizer Non-Destructive Behavior & Cascade Validation
- **Non-Destructive Identity Synchronization (`tools/resume/sync.py`)** — Implemented `extract_master_header()` to preserve top-level documentation comments, and added change detection to skip file writes and backup creation when 0 changes are detected. Added multi-highlight project parsing, coursework extraction from `credentials.yaml`, and complete `--force` update handling for projects, education, and publications.
- **ISO Date Chronology & Format Relaxations (`.pramedha/validate.py`)** — Upgraded `parse_flexible_date()` regex to support ISO dates (`YYYY-MM-DD` and `YYYY-MM`), with month range validation (1–12) eliminating false invalid date warnings on standard date strings.
- **Required Build Files & Verification Coverage (`.pramedha/validate.py`, `.pramedha/manifest.yaml`)** — Added `tools/resume/build.ps1`, `tools/resume/build.sh`, and `.pramedha/manifest.yaml` to `REQUIRED_FILES` in validator and synchronized `files.required` in `manifest.yaml`. Added `identity/projects.yaml` and `identity/volunteering.yaml` to verification tag checks.
- **Deep Cascade Reference Integrity in Validator (`.pramedha/validate.py`)** — Enhanced `check_cascade_consistency()` to validate active resume variants against `master.yaml`, verifying that all referenced roles, bullets, projects, and achievements exist and flagging dangling references before build/render.
- **Operational Alignment & Authority Clarification (`ops/guide.md`, `ops/authority-map.md`)** — Corrected `sync.py` description from two-way to identity → master.yaml forward synchronizer, scoped the tag preservation rule strictly to source data files, and clarified base design ownership vs. variant design overrides in the authority matrix.

## [0.1.0] — 2026-10-15 (Runtime Robustness & Multi-Domain Hardening)

### Fixed — Engine Resilience & Platform Compatibility
- **RenderCV v2.8 Schema & Social Network Hardening (`tools/resume/assemble.py`)** — Normalized social network identifier `'Twitter'` to RenderCV v2.8 canonical `'X'`, expanded auto-detection across all 17 RenderCV networks (`GitLab`, `Google Scholar`, `ORCID`, `Leetcode`, `StackOverflow`, `Bluesky`, `Mastodon`, etc.), and whitelisted allowed `Cv` fields (`name`, `headline`, `location`, `email`, `phone`, `website`, `social_networks`, `custom_connections`, `photo`, `sections`) to prevent strict Pydantic `extra_forbidden` validation crashes.
- **Headline Extraction & Overrides (`tools/resume/assemble.py`)** — Added support for `headline` in `assemble_variant` and `merge_header`, resolving from `variant.yaml` overlays, `master.yaml` header, `identity.professional_headline`, or `config.user.headline`.
- **Flexible Bullet & Experience Resolution (`tools/resume/assemble.py`)** — Added support for dot-notation bullet references (`bullet_key.phrasing`) across `resolve_bullet` and `check_orphans`, safeguarded date conversions with `isoformat()` / `str()` checks, and supported universal employer/role aliases (`organization`, `client`, `institution`, `practice`, `role`, `title`) with explicit `AssemblyError` diagnostics instead of raw unhandled `KeyError` crashes.
- **1-Step Assemble & Render (`tools/resume/assemble.py`)** — Added `--render` (`-r`) CLI flag to `assemble.py`, automatically invoking RenderCV with guaranteed UTF-8 environment settings, absolute output resolution (bypassing RenderCV's nested relative directory behavior), and automatic primary PDF copying to `tools/resume/output/<variant>.pdf`.
- **PowerShell Parameter Binding & Command Array Fix (`tools/resume/build.ps1`)** — Replaced raw string invocation of `$pythonCmd` with a dedicated scriptblock accepting parameter arrays, eliminating PowerShell's ambiguous parameter binding error on `-o` (which collided with `-OutVariable`) and enabling robust multi-token runners (`uv run python`).
- **RenderCV CLI PATH Fallback (`tools/resume/build.sh`)** — Added automatic fallback from `rendercv` binary to `python3 -m rendercv`, `python -m rendercv`, or `uv run python -m rendercv`, ensuring headless CI/CD and non-login shells without `~/.local/bin` in PATH compile PDFs cleanly.
- **PyYAML Date Object Protection in Synchronizer (`tools/resume/sync.py`)** — Defensively stringified date and URL fields in `sync_experience` and `sync_projects` before invoking `.strip()`, preventing `AttributeError` crashes when PyYAML auto-parses unquoted ISO dates as `datetime.date`.
- **Stale Career Contingency Linkage (`VISION.md`, `ops/guide.md`)** — Updated cross-references to point to the canonical Career Contingency & Crisis Readiness checklists in `strategy/job-tracker.md` (Section 6).
- **Parity & Chronology Enhancements (`.pramedha/validate.py`)** — Added publications parity checks between `identity/credentials.yaml` and `tools/resume/master.yaml`, employer alias awareness in identity-master parity, date chronology validation for `identity/volunteering.yaml`, and robust fill detection for `strategy/target-roles.md` supporting both Part 3 evaluation tables and deep-dive headings.
- **PyYAML Multi-Representer Fix (`tools/resume/_yaml_utils.py`)** — Registered `OrderedDumper.add_multi_representer(PresentLiteral, _present_literal_representer)` and defensive type checks in `_str_representer`, preventing `yaml.representer.RepresenterError` when `_yaml_utils` is imported across differing module namespaces.
- **Quickstart Variant Filename Harmony (`tools/resume/variants/_template.yaml`)** — Initialized default `variant_name: "General"` and `output_filename: "my-role_CV"`, ensuring that copying `_template.yaml` to `my-role.yaml` produces `my-role_CV.yaml` matching documentation without file-not-found errors.
- **Cross-Platform CLI Build Commands (`README.md`, `GETTING_STARTED.md`)** — Replaced unsupported shell wildcard `rendercv render generated/*.yaml` with cross-platform automated build scripts (`build.ps1` on Windows, `build.sh` on macOS/Linux), and documented `$env:PYTHONUTF8=1` for raw Windows terminal rendering.
- **Unquoted Date Safety in Validator (`.pramedha/validate.py`)** — Defensively stringified date fields across `validate_experience_yaml`, `parse_flexible_date`, and claim queue checks, preventing `AttributeError: 'int' object has no attribute 'strip'` on unquoted numeric YAML dates.
- **Authority Map Cross-Reference Fix (`ops/authority-map.md`)** — Added missing directory prefix for `stories/interview-prep/technical.md`.

### Improved — Multi-Domain Hardening & Protocol Realignment
- **Academic Patents & Grants Cascade Synchronization (`tools/resume/sync.py`)** — Extended `sync_achievements()` to extract intellectual property (`patents`) and research funding (`grants`) from `identity/credentials.yaml` into `master.yaml['achievements']`.
- **Chronology Validation for Education & Projects (`.pramedha/validate.py`)** — Extended `check_date_chronology` to validate `start_date` and `end_date` bounds within `identity/credentials.yaml` and `identity/projects.yaml`.
- **Non-Speaker Fill Status Neutrality (`.pramedha/validate.py`)** — Classified `speaking-and-community.yaml` as optional in `compute_fill_status()`, ensuring professionals without public speaking engagements are not penalized with capped core fill scores.
- **Protocol Phase Realignment (`.pramedha/agent-instructions.md`, `AGENTS.md`, `ops/prompts.md`)** — Realigned Step 17 (`form-fill-cheatsheet.md`) into Phase F (Personal Layer, as Step 25), enforcing strict layer purity while maintaining the canonical 28-step count (Steps 0–27).
- **Zero-Python Browser Resume Generation Prompt (`ops/prompts.md`)** — Added Prompt 18 for generating a standalone, browser-pasteable RenderCV YAML resume file for instant rendering at `rendercv.com`.

## [0.1.0] — 2026-10-14 (Audit Remediation)

### Fixed — Build Engine, Security, and Cross-File Integrity
- **Evidence Locker & Build Artifact Boundaries (`.gitignore`)** — Configured `.gitignore` to track markdown and text notes in `data-corpus/text/` as part of the private canonical knowledge base, while ignoring heavy video media in `data-corpus/media/` and auto-generated build outputs in `tools/resume/generated/` and `tools/resume/output/`.
- **Step Protocol & Phase Count Harmonization (`ops/guide.md`, `data-corpus/README.md`, `ops/prompts.md`)** — Harmonized all references to the canonical 28-step protocol (Steps 0–27 across 7 phases), eliminating references to the legacy 34-step protocol and removed phantom phases for pruned static assets.
- **Ghost Asset Reference Removal (`GETTING_STARTED.md`, `ops/prompts.md`, `identity/claims-and-evidence.md`, `.pramedha/agent-instructions.md`)** — Removed dangling references to cover letters, LinkedIn packs, and non-existent `master-action-tracker.md`. Replaced cover letter reference in `GETTING_STARTED.md` with behavioral interview prep, and directed claim debt tracking to the local `## Claim Debt Queue` in `claims-and-evidence.md`.
- **Path Consistency Across Tooling (`.github/CONTRIBUTING.md`, `tools/resume/assemble.py`, `tools/resume/sync.py`, `tools/resume/README.md`)** — Replaced all legacy `resume/...` paths with `tools/resume/...`, improved module import handling for `_yaml_utils`, and fixed relative directory paths in documentation.

### Improved — Universal Profession & Multi-Persona Architecture
- **Professional Licenses & Security Clearances in Resume Cascade (`tools/resume/sync.py`, `master.yaml`)** — Extended `sync.py` to extract professional licenses (Medical Board, State Bar, PE) and security clearances (Top Secret / SCI, Polygraphs) from `identity/credentials.yaml` into `master.yaml['achievements']` with prefix `license_` and `clearance_`.
- **Universal Experience Aliases (`tools/resume/sync.py`, `.pramedha/validate.py`)** — Added support for freelance client engagements, medical hospital practices, research institutes, and military commands by accepting `company`, `client`, `organization`, `institution`, `practice`, and `employer` aliases in both the synchronizer and validator.
- **Comprehensive Credentials Fill Validation (`.pramedha/validate.py`)** — Enhanced `compute_fill_status()` to recognize licenses, security clearances, academic publications, and awards as valid credentials, ensuring non-tech and licensed professionals receive honest fill scoring.
- **Core Professional Identity Generalization (`strategy/target-roles.md`)** — Generalized `### Core Technical Identity` to `### Core Professional Identity & Capabilities` with diverse examples across software architecture, clinical research leadership, and corporate compliance.
- **Layer Purity & Crisis Readiness Checklists (`identity/claims-and-evidence.md`, `strategy/job-tracker.md`)** — Relocated the emergency layoff and crisis contingency checklist from `identity/claims-and-evidence.md` to `strategy/job-tracker.md` (Section 6), preserving the `identity/` layer as strictly verified, objective facts.

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
- **Separation of Template Development from Career Runtime State (`ops/session-handoff.md`, `ops/guide.md`)** — Purged internal repository development logs from `ops/session-handoff.md`, establishing a clean career continuity log template with explicit scope guardrails and a new DO/DON'T rule in `ops/guide.md` ensuring AI assistants never confuse template code maintenance with career facts and strategy.
- **Role Hierarchy Enums Expansion (`.pramedha/validate.py`, `.pramedha/schema-reference.md`, `config.yaml`)** — Expanded `VALID_ROLE_LEVELS` to support the full professional hierarchy (`intern`, `entry`, `junior`, `mid`, `senior`, `lead`, `staff`, `principal`, `director`, `vp`, `c-level`, `executive`) across validator checks, schema reference documentation, and configuration comments.
- **Required Utilities & Ops Files in Validator (`.pramedha/validate.py`)** — Added `resume/_yaml_utils.py` to `REQUIRED_FILES` ensuring core shared cascade utilities are always validated, and registered all 4 `ops/` files (`session-handoff.md`, `guide.md`, `authority-map.md`, `prompts.md`) in `OPTIONAL_FILES`.
- **System Architecture Diagram Alignment (`README.md`)** — Updated the master architecture tree in `README.md` to reflect the complete 8-folder `data-corpus/` evidence locker (`inbox/`, `resumes/`, `documents/`, `exports/`, `linkedin/`, `github/`, `text/`, `media/`) and the `resume/sync.py` bridge synchronizer.
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
