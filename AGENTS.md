# Pramedha Career Template — Agent Instructions

> **You are an AI assistant working with a structured career repository.**
> Read this file completely before modifying anything.

## What This Repository Is

A **personal career knowledge base** stored as YAML + Markdown files. It has 4 layers:

1. **Identity** (`identity/`) — Verified career facts. THE source of truth.
2. **Stories** (`stories/`) — Authored narratives for interviews (STAR stories, testimonials, prep).
3. **Strategy** (`strategy/`) — Strategic decisions (target roles, financials, job tracking).
4. **Personal** (`personal/`) + **Journal** (`journal/`) — Private context, never shared externally.

Plus: **Tools** (`tools/resume/`) — Optional resume cascade engine (decoupled from data).

## Architecture at a Glance

```
config.yaml          ← User's name, email, profession type
identity/*.yaml      ← Career facts (experience, skills, credentials, projects, speaking)
stories/             ← Authored STAR stories, testimonials, interview prep
strategy/            ← Target roles, study plan, financial, job tracking, networking
personal/            ← Private: life goals, preferences, reflections (⚠️ NEVER on resumes)
journal/             ← Ongoing: wins, learning log, work log, feedback
ops/                 ← Maintenance guide, authority map, session handoff, prompts
.pramedha/           ← AI fill protocol, schema reference, examples, validator
data-corpus/         ← Raw career evidence (resumes, certs, exports, brain dumps)
tools/resume/        ← Optional: bullet pool → assemble.py → variants → RenderCV → PDF
tools/external/      ← Mount point for third-party career tools (gitignored)
```

---

## 🎯 Minimum Context Router (Load ONLY What You Need)

> To preserve LLM context window quality, prevent hallucinations, and eliminate token waste,
> **NEVER read the entire repo.** Route directly to the 2–4 files needed for your specific objective:

| Objective / Task | 🎯 Minimum Files to Read & Edit | Context Budget |
|------------------|---------------------------------|:--------------:|
| **Tailor Resume for a Job Posting** | `tools/resume/master.yaml`, `identity/experience.yaml`, `identity/skills.yaml`, `tools/resume/variants/<target>.yaml` (or copy `_template.yaml`) | ~2,500 tokens |
| **Prepare for Behavioral Interview** | `stories/star-stories.md`, `stories/interview-prep/behavioral.md` | ~2,800 tokens |
| **Prepare for Technical / Domain Interview** | `identity/skills.yaml`, `stories/interview-prep/technical.md`, `identity/projects.yaml` | ~3,200 tokens |
| **Rapid ATS Application Form Fill** | `personal/form-fill-cheatsheet.md`, `strategy/job-tracker.md` | ~1,800 tokens |
| **Cold Outreach / Referral Request** | `identity/professional-summary.md`, `strategy/networking.md` | ~1,500 tokens |
| **Target Role & Pivot Evaluation** | `strategy/target-roles.md`, `identity/skills.yaml` | ~2,200 tokens |
| **Offer Evaluation & Comp Negotiation** | `strategy/financial.md`, `strategy/offer-comparison.md`, `personal/preferences.yaml` | ~2,000 tokens |
| **Log New Win or Shipped Feature** | `journal/wins.md`, `identity/experience.yaml`, `identity/claims-and-evidence.md` | ~2,600 tokens |
| **Use External Career Tool** | `tools/external/README.md`, `identity/experience.yaml`, `identity/skills.yaml`, `strategy/target-roles.md` | ~3,000 tokens |
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

Read `.pramedha/agent-instructions.md` — it contains the complete **34-step, 7-phase protocol (Steps 0–33)**:

| Phase | Steps | What Happens |
|:-----:|:-----:|-------------|
| A | 0-1 | Read config.yaml + scan data-corpus/ |
| B | 2-10 | Fill identity/ (10 files — career facts + speaking + claims) |
| C | 11-13 | Generate resume master + variants (in tools/resume/) |
| D | 14-18 | Generate stories (STAR stories, testimonials, interview prep) |
| E | 19-24 | Draft strategy (target roles, study plan, financial) |
| F | 25-27 | Draft personal (about-me, life-goals, preferences) |
| G | 28-29 | Finalize VISION.md + validate |

## What To Do When Asked to Update/Maintain

Read `ops/guide.md` — it contains event→file mapping:

| Event | Files to Update |
|-------|----------------|
| New job/role | experience.yaml → skills.yaml → tools/resume/master.yaml → claims → professional-summary |
| New certification | credentials.yaml → claims → study-plan → tools/resume/master.yaml |
| New project | projects.yaml → experience.yaml → tools/resume/master.yaml → claims |
| Job application | strategy/job-tracker.md → (optional) tools/resume/jd/[company].yaml |
| Interview scheduled | strategy/company-research/[company].md → stories/interview-prep → stories/star-stories review |
| Achievement/win | journal/wins.md → experience.yaml → tools/resume/master.yaml → claims |
| Speaking / hackathon | speaking-and-community.yaml → claims → professional-summary |
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
| What claim debt is pending? | `identity/claims-and-evidence.md` (Claim Debt Queue section) |
| Previous session context? | `ops/session-handoff.md` |
| Sub-projects (websites, etc.)? | `VISION.md` (Sub-Projects section) |
| How to maintain this repo? | `ops/guide.md` |
| Complete field-by-field schema? | `.pramedha/schema-reference.md` |
| Ready-to-use AI prompts? | `ops/prompts.md` |
