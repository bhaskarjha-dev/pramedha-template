# VISION — Career Mission & North Star

> **Your Career Mission & North Star.** This is the "why" behind this repository.
> Every other file is the "how." Follow [GETTING_STARTED.md](GETTING_STARTED.md) for initial setup.

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
| Phase A: Foundation | ⬜ | Identity config + raw evidence in `data-corpus/` |
| Phase B: Identity Layer | ⬜ | Fact database: experience, skills, credentials, projects, claims |
| Phase C: Resume Pipeline | ⬜ | master.yaml bullet pool + role-specific variants → RenderCV PDF |
| Phase D: Assets Generation | ⬜ | STAR stories, cover letters, LinkedIn pack, platform copy |
| Phase E: Strategy Layer | ⬜ | Target roles, study plan, master action tracker, digital presence |
| Phase F: Personal Context | ⬜ | About me, career narrative, preferences, reflections |
| Phase G: Governance & Vision | ⬜ | VISION.md, validation, maintenance rituals |

---

## What's Next

> **All action items are tracked in a single file:**
> 📋 **[Master Action Tracker](strategy/master-action-tracker.md)**
>
> That file is the dashboard — organized by stream:
> - 🔴 **Claim Debt** — evidence needed for resume claims
> - 🟠 **Portfolio** — projects to build/polish
> - 🔵 **Digital Presence** — website, profiles, content
> - 🟢 **Skill Building** — learning gaps to close
> - 🟡 **Job Search** — applications, interviews, networking
>
> Weekly picks from the tracker go into [weekly-tracker.md](strategy/weekly-tracker.md).

---

## Sub-Projects

> As your career system grows, you'll likely spawn related sub-projects:
> portfolio websites, GitHub profile READMEs, side-project repos, etc.
> Register them here so the career system stays aware of them.

| Sub-Project | Path | Purpose | Status |
|-------------|------|---------|:------:|
| <!-- Example: Portfolio website --> | <!-- yourname.com/ --> | <!-- Career portfolio --> | <!-- ✅ LIVE --> |
| <!-- Example: GitHub Profile README --> | <!-- github-profile/ --> | <!-- Public GitHub profile --> | <!-- ✅ LIVE --> |

> **Tip:** Sub-projects often have their own git repos but are conceptually
> children of this career system. Use `.gitignore` to exclude their directories
> if they have independent version control.

---

## Future Scope

This repository doesn't die after the job search. It becomes:

1. **Ongoing career tracker** — Log achievements, update identity layer
2. **Promotion engine** — Generate materials for internal moves or next job
3. **Knowledge base** — Reference for interview prep, salary negotiation
4. **Portfolio data source** — Portfolio website reads from identity/*.yaml
5. **Maintenance system** — Weekly/monthly rituals prevent career drift
6. **Content engine** — Technical articles, LinkedIn posts, thought leadership

---

## Quick Start

```
1. Read VISION.md (this file)               → Understand the mission
2. Fill config.yaml                         → Your identity + profession
3. Dump data into data-corpus/              → Raw career evidence
4. Read .pramedha/agent-instructions.md     → AI fill protocol (7 phases)
5. Fill identity/ & audit claims            → Structured facts + claims verification
6. Build resume master & variants           → resume/master.yaml + variants
7. Generate assets/                         → STAR stories, cover letters, platform copy
8. Draft strategy/ & personal/              → Target roles, trackers, career vision
9. Validate & render PDFs                   → py .pramedha/validate.py & resume/build
```

---

## Key Rules (Non-Negotiable)

1. **`identity/*.yaml` is the source of truth.** Resumes are outputs, not inputs.
2. **`resume/master.yaml` is the resume truth.** Never edit `generated/*.yaml` directly.
3. **Every claim must pass the claims register** before it goes on a resume.
4. **Never disclose current salary** to recruiters. State target range only.
5. **This repo is 100% self-contained.** No external dependencies for the data.
6. **`personal/` data is NEVER shared externally.** It's for AI context only.
