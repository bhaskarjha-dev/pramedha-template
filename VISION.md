# VISION — Career Mission & North Star

> **Your Career Mission & North Star.** This is the "why" behind this repository.
> Every other file is the "how." Follow [GETTING_STARTED.md](GETTING_STARTED.md) for initial setup.

---

## The Mission

<!-- ⚠️ FILL THIS IN. Replace the [brackets] with your actual information.
     Examples:
     - Tech: "Alex Chen is a Software Engineer at Acme transitioning to Staff Backend Engineer ($185K+) within 6 months."
     - Domain Pivot: "Priya Sharma is a Data Analyst at Infosys transitioning to Lead AI/ML Engineer (₹35+ LPA) within 4 months."
     - Non-Tech: "Elena Rostova is a Marketing Lead transitioning to VP of Growth (£95K+) within 9 months." -->

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

## The Four-Layer Architecture

```
IDENTITY (who I am)    → identity/*.yaml — verified facts, never inflated
STORIES  (what I say)  → stories/*.md    — authored narratives for interviews
STRATEGY (what to do)  → strategy/*.md   — plans, targets, decisions
PERSONAL (who I am)    → personal/*.md   — private context, never shared
```

Plus: `tools/resume/` — optional cascade engine for deterministic PDF generation.

Everything flows from identity → stories/strategy → tools.
If facts change, the identity layer updates first, then everything downstream regenerates.

---

## Current Status

| Phase | Status | What It Covers |
|-------|:------:|----------------|
| Phase A: Foundation | ⬜ | Identity config + raw evidence in `data-corpus/` |
| Phase B: Identity Layer | ⬜ | Fact database: experience, skills, credentials, projects, claims |
| Phase C: Resume Pipeline | ⬜ | tools/resume/ master.yaml bullet pool + role-specific variants → RenderCV PDF |
| Phase D: Stories & Narratives | ⬜ | STAR stories, testimonials, interview prep |
| Phase E: Strategy Layer | ⬜ | Target roles, study plan, job tracking, financial |
| Phase F: Personal Context | ⬜ | About me, career narrative, preferences, reflections |
| Phase G: Governance & Vision | ⬜ | VISION.md, validation, maintenance rituals |

---

## What's Next

> **Action items are tracked in the Claim Debt Queue within:**
> 📋 **[Claims & Evidence Registry](identity/claims-and-evidence.md)**
>
> That file tracks:
> - 🔴 **Claim Debt** — evidence needed for resume claims
> - 🟢 **Career Contingency** — emergency preparedness checklists
>
> Active job search tasks are tracked in [job-tracker.md](strategy/job-tracker.md).

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

## Ecosystem & Future Scope

### The Data Gravity Thesis

In a world of abundant AI career tools, the scarce resource is not the tool —
it's **accurate, verified, structured personal data**. This template is the
canonical data layer. Tools orbit around it.

### The Three Layers

1. **This Template** — Your career data in portable YAML/Markdown.
   Works standalone with any AI assistant. Zero dependencies.

2. **External Tools** (`tools/external/`) — Clone any career tool.
   career-ops for job search, JobSpy for scraping, anything you want.
   AI agents bridge between your data and the tool.

3. **Pramedha Platform** (optional) — Full Career OS with AI intake,
   7-dimension JD matching, resume tailoring, career graph intelligence,
   MCP server, and plugin SDK. Import this template with one command.

### Lifecycle

This repository doesn't die after the job search. It becomes:

1. **Ongoing career tracker** — Log achievements, update identity layer
2. **Promotion engine** — Generate materials for internal moves or next job
3. **Knowledge base** — Reference for interview prep, salary negotiation
4. **Portfolio data source** — Portfolio website reads from identity/*.yaml
5. **External tool substrate** — Any new career tool reads from your data
6. **Pramedha import source** — `pramedha import --format template` when ready

---

## Quick Start

```
1. Read VISION.md (this file)               → Understand the mission
2. Dump data into data-corpus/              → Raw career evidence (the ONLY manual step)
3. Let AI fill everything                   → AI extracts config, identity, resume, stories, strategy
4. Review & write your mission              → Correct errors, add private context, write VISION
5. Build resume master & variants           → tools/resume/master.yaml + variants
6. Validate & render PDFs                   → py .pramedha/validate.py & tools/resume/build
```

---

## Key Rules (Non-Negotiable)

1. **`identity/*.yaml` is the source of truth.** Resumes are outputs, not inputs.
2. **`tools/resume/master.yaml` is the resume truth.** Never edit `generated/*.yaml` directly.
3. **Every claim must pass the claims register** before it goes on a resume.
4. **Never disclose current salary** to recruiters. State target range only.
5. **This repo is 100% self-contained.** No external dependencies for the data.
6. **`personal/` data is NEVER shared externally.** It's for AI context only.
