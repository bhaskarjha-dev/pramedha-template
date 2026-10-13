# Pramedha Career Template — Agent Instructions

> **You are an AI assistant working with a structured career repository.**
> Read this file completely before modifying anything.

## What This Repository Is

A **career operating system** stored as YAML + Markdown files. It has 3 layers:

1. **Identity** (`identity/`) — Verified career facts. THE source of truth.
2. **Strategy** (`strategy/`) + **Assets** (`assets/`) — Plans and materials derived from identity.
3. **Personal** (`personal/`) + **Journal** (`journal/`) — Private context, never shared externally.

Plus: **Resume** (`resume/`) — A cascade engine that generates role-specific PDFs from identity.

## Architecture at a Glance

```
config.yaml          ← User's name, email, profession type
identity/*.yaml      ← Career facts (experience, skills, credentials, projects, speaking)
resume/master.yaml   ← Bullet pool → assemble.py → variants → RenderCV → PDF
strategy/            ← Target roles, study plan, action tracker, digital presence, financial
assets/              ← STAR stories, cover letters, outreach copy, LinkedIn pack, interview prep
personal/            ← Private: life goals, preferences, reflections (⚠️ NEVER on resumes)
journal/             ← Ongoing: wins, learning log, work log, feedback
ops/                 ← Maintenance guide, authority map, session handoff, prompts
.pramedha/           ← AI fill protocol, schema reference, examples, validator
data-corpus/         ← Raw career evidence (resumes, certs, exports, brain dumps)
```

---

## 🎯 Minimum Context Router (Load ONLY What You Need)

> To preserve LLM context window quality, prevent hallucinations, and eliminate token waste,
> **NEVER read the entire repo.** Route directly to the 2–4 files needed for your specific objective:

| Objective / Task | 🎯 Minimum Files to Read & Edit | Context Budget |
|------------------|---------------------------------|:--------------:|
| **Tailor Resume for a Job Posting** | `resume/master.yaml`, `identity/experience.yaml`, `identity/skills.yaml`, `resume/variants/<target>.yaml` (or copy `_template.yaml`) | ~2,500 tokens |
| **Prepare for Behavioral Interview** | `assets/star-stories.md`, `assets/interview-prep/behavioral.md` | ~2,800 tokens |
| **Prepare for Technical / Domain Interview** | `identity/skills.yaml`, `assets/interview-prep/technical.md`, `identity/projects.yaml` | ~3,200 tokens |
| **Rapid ATS Application Form Fill** | `assets/form-fill-cheatsheet.md`, `strategy/job-tracker.md`, `assets/cover-letters/standard.md` | ~2,100 tokens |
| **Cold Outreach / Referral Request** | `assets/outreach-messages.md`, `identity/professional-summary.md` | ~1,500 tokens |
| **Friday 5-Minute Weekly Review** | `strategy/weekly-tracker.md`, `journal/wins.md`, `journal/work-log/_template.md` | ~1,400 tokens |
| **Target Role & Pivot Evaluation** | `strategy/target-roles.md`, `identity/skills.yaml` | ~2,200 tokens |
| **Offer Evaluation & Comp Negotiation** | `strategy/financial.md`, `strategy/offer-comparison.md`, `personal/preferences.yaml` | ~2,000 tokens |
| **Log New Win or Shipped Feature** | `journal/wins.md`, `identity/experience.yaml`, `resume/master.yaml`, `identity/claims-and-evidence.md` | ~2,600 tokens |
| **Quarterly Audit & System Health** | `ops/guide.md`, `ops/authority-map.md`, `config.yaml` | ~2,000 tokens |

---

## Critical Rules

1. **`ops/authority-map.md`** is the source-of-truth reference. When in doubt about which file owns a piece of data, check there.
2. **Never fabricate data.** If evidence doesn't exist, leave the field empty.
3. **Every claim gets a verification tag:** ✅ (verified), ⚠️ (estimated), ❌ (unverified).
4. **`personal/` content NEVER appears on resumes or public assets.** (It guides private interview coaching, transition narratives, and role evaluation, but is never copied verbatim into outward materials).
   - `identity/references.yaml` is strictly confidential — only extract individual contact details when specifically required by a formal application or background check.
5. **`identity/` is the single source.** All outward materials (resume, LinkedIn, cover letters) derive from identity — never the reverse.
6. **Anti-inflation:** Don't upgrade skill levels, metrics, or titles without evidence. See `ops/guide.md` for the 6 anti-inflation rules.
7. **Check `ops/session-handoff.md`** at the start of each session for prior context.

## Key Decisions Already Made (Do NOT Re-litigate)

> When working across multiple AI sessions, certain decisions get settled.
> Once recorded here, they should NOT be questioned or re-debated unless
> the user explicitly asks to revisit them.

| Decision | Context | Date |
|----------|---------|------|
| *Example: Job title uses "SDE" on portfolio* | *Official HR title is different but role is development* | *YYYY-MM-DD* |

## What To Do When Asked to Fill the Template

Read `.pramedha/agent-instructions.md` — it contains the complete **33-step, 7-phase protocol**:

| Phase | Steps | What Happens |
|:-----:|:-----:|-------------|
| A | 0-1 | Read config.yaml + scan data-corpus/ |
| B | 2-10 | Fill identity/ (10 files — career facts + speaking + claims) |
| C | 11-13 | Generate resume master + variants |
| D | 14-21 | Generate assets (STAR stories, cover letters, LinkedIn, platform copy) |
| E | 22-28 | Draft strategy (target roles, action tracker, digital presence, study plan) |
| F | 29-31 | Draft personal (about-me, life-goals, preferences) |
| G | 32-33 | Finalize VISION.md + validate |

## What To Do When Asked to Update/Maintain

Read `ops/guide.md` — it contains event→file mapping:

| Event | Files to Update |
|-------|----------------|
| New job/role | experience.yaml → skills.yaml → master.yaml → claims → professional-summary |
| New certification | credentials.yaml → claims → study-plan → master.yaml |
| New project | projects.yaml → experience.yaml → master.yaml → claims |
| Job application | strategy/job-tracker.md → (optional) resume/jd/[company].yaml |
| Interview scheduled | strategy/company-research/[company].md → interview-prep → star-stories review |
| Achievement/win | journal/wins.md → experience.yaml → master.yaml → claims |
| Speaking / hackathon | speaking-and-community.yaml → claims → professional-summary → platform-copy |
| New raw data in data-corpus | Extract facts → identity/*.yaml → claims-and-evidence.md → downstream |

## Key Files for Quick Context

| Need | Read This |
|------|-----------|
| Who is this person? | `config.yaml` + `identity/professional-summary.md` |
| What's their career mission? | `VISION.md` |
| What are they good at? | `identity/skills.yaml` + `identity/experience.yaml` |
| What roles are they targeting? | `strategy/target-roles.md` |
| What's verified vs estimated? | `identity/claims-and-evidence.md` |
| Speaking, hackathons, events? | `identity/speaking-and-community.yaml` |
| What actions are pending? | `strategy/master-action-tracker.md` |
| Previous session context? | `ops/session-handoff.md` |
| Sub-projects (websites, etc.)? | `VISION.md` (Sub-Projects section) |
| How to maintain this repo? | `ops/guide.md` |
| Complete field-by-field schema? | `.pramedha/schema-reference.md` |
| Ready-to-use AI prompts? | `ops/prompts.md` |
