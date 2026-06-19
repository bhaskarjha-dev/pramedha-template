# VISION — Career Mission & North Star

> **Read this FIRST.** This is the "why" behind this repository.
> Every other file is the "how."

---

## The Mission

<!-- ⚠️ FILL THIS IN. Replace the [brackets] with your actual information.
     Example: "Priya Sharma is a Software Engineer at Infosys transitioning to
     a Senior Backend Engineer role (₹30+ LPA) within 6 months." -->

**[Your Name]** is [current state/role] transitioning to [target state/role] within [timeframe].

This repository is the **command center** for that transition. It is not a resume folder — it's a verified fact database, strategy engine, and build system that generates all outward-facing career materials from a single source of truth.

---

## What Success Looks Like

```
✅ Land a [Target Role] position
✅ Minimum [salary floor] compensation
✅ At a company that [your criteria]
✅ Within [timeframe]
```

---

## The Three-Layer Architecture

```
IDENTITY (who I am)    → identity/*.yaml — verified facts, never inflated
STRATEGY (what to do)  → strategy/*.md   — plans, targets, timelines
ASSETS   (what to use) → assets/*.md     — copy-paste materials for applications
```

Everything flows from identity → strategy → assets.
If facts change, the identity layer updates first, then everything downstream regenerates.

---

## Current Status

| Phase | Status | What It Covers |
|-------|:------:|----------------|
| 0. Data Intake | ⬜ | Raw career data dumped into `data-corpus/` |
| 1. Identity | ⬜ | Fact database: experience, skills, projects, credentials |
| 2. Strategy + Assets | ⬜ | Target roles, study plan, STAR stories, cover letters |
| 3. Resume Pipeline | ⬜ | Variants generating from YAML → PDF automatically |
| 4. Application Ready | ⬜ | LinkedIn updated, profiles active, tracker running |

---

## What's Pending

### Immediate
- [ ] Fill `config.yaml` with contact info
- [ ] Dump raw career data into `data-corpus/`
- [ ] Fill `identity/` files from data-corpus

### Near-Term
- [ ] Build resume variants
- [ ] Fill strategy files (target-roles, study-plan)
- [ ] Prepare STAR stories and cover letters

### Job Search Phase
- [ ] Start application tracker
- [ ] Activate networking contacts
- [ ] Weekly maintenance rituals

---

## Future Scope

This repository doesn't die after the job search. It becomes:

1. **Ongoing career tracker** — Log achievements, update identity layer
2. **Promotion engine** — Generate materials for internal moves or next job
3. **Knowledge base** — Reference for interview prep, salary negotiation
4. **Portfolio data source** — Portfolio website reads from identity/*.yaml
5. **Maintenance system** — Weekly/monthly rituals prevent career drift

---

## Quick Start

```
1. Read VISION.md (this file)               → Understand the mission
2. Fill config.yaml                         → Your identity + preferences
3. Dump data into data-corpus/              → Raw career materials
4. Read .pramedha/agent-instructions.md     → How AI fills the template
5. Fill identity/ files                     → Structured career facts
6. Build resume variants                    → resume/variants/
```

---

## Key Rules (Non-Negotiable)

1. **`identity/*.yaml` is the source of truth.** Resumes are outputs, not inputs.
2. **`resume/master.yaml` is the resume truth.** Never edit `generated/*.yaml` directly.
3. **Every claim must pass the claims register** before it goes on a resume.
4. **Never disclose current salary** to recruiters. State target range only.
5. **This repo is 100% self-contained.** No external dependencies for the data.
6. **`personal/` data is NEVER shared externally.** It's for AI context only.
