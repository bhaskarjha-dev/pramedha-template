# 🎯 Master Action Tracker — Single Source of Next Steps

> **Purpose:** One place to see EVERYTHING you need to do, across all streams.
> This file is the **dashboard**. Details live in their respective strategy/ files.
>
> **How to use:** Work top-to-bottom within each priority band. Check off items as done.
> Cross-references to source files are linked inline.
>
> **Relationship to weekly-tracker.md:** This is the *backlog*. `weekly-tracker.md` is the *sprint*.
> Each week, pick items from here and move them into your weekly tracker.

---

## Stream Legend

| Stream | Color | What |
|--------|:-----:|------|
| 🔴 CLAIM DEBT | Evidence gaps | Making resume claims defensible |
| 🟠 PORTFOLIO | Projects to build/polish | Public proof of technical ability |
| 🔵 DIGITAL PRESENCE | Website, profiles, content | Brand visibility |
| 🟢 SKILL BUILDING | Learning, certifications | Gap-closing for target roles |
| 🟡 JOB SEARCH | Applications, interviews, networking | Getting hired |

---

## 🔴 CLAIM DEBT — Evidence Substantiation Queue

> These are claims on your resume/LinkedIn tagged `[estimated]` or `[to-verify]`.
> Each one needs evidence before you can confidently use them in interviews.
> Source: [claims-and-evidence.md](identity/claims-and-evidence.md)

### Priority 1: Build Projects to Prove Claims

<!-- Fill one row per claim that needs a project as evidence -->

| # | Claim to Prove | Evidence to Create | Effort | Deadline | Status |
|:-:|----------------|-------------------|:------:|:--------:|:------:|
| C1 | *Example: "Built ML pipeline processing 1M records"* | *Build demo pipeline with monitoring dashboard* | *3 days* | *Sprint 1* | ⬜ |

### Priority 2: Collect Internal Evidence (No Coding Needed)

<!-- Claims that just need screenshots, documents, or testimonials -->

| # | Claim to Prove | Evidence to Provide | Effort | Status |
|:-:|----------------|-------------------|:------:|:------:|
| C2 | *Example: "Led team of 5 developers"* | *Org chart screenshot, Jira team page, or email* | *15 min* | ⬜ |

### Priority 3: Post Evidence → Update Files

After collecting evidence for any item above:
1. Add evidence file to `data-corpus/documents/`
2. Update tag in experience.yaml: change `[estimated]`/`[to-verify]` → `[measured]`
3. Update tier in claims-and-evidence.md: change 🟡 → 🟢
4. Regenerate resume variants

---

## 🟠 PORTFOLIO — Project Quality Overhaul

> Source: [projects.yaml](identity/projects.yaml)

### Tier 1: Flagship Projects (Must Be Polished)

<!-- Your 3-5 best projects that deserve full professional treatment -->

| # | Project | Current State | Actions Needed | Status |
|:-:|---------|--------------|----------------|:------:|
| P1 | *Example: project-name* | *Has code, no README* | *Professional README, architecture diagram, demo GIF* | ⬜ |

### Tier 2: Showcase Projects (Good Enough With Polish)

| # | Project | Actions Needed | Status |
|:-:|---------|----------------|:------:|
| P2 | *Example: another-project* | *Add README, badges* | ⬜ |

### Tier 3: New Projects to Build (Filling Claim Gaps)

| # | New Project to Create | Purpose | Proves Claim | Status |
|:-:|----------------------|---------|-------------|:------:|
| P3 | *Example: rag-demo* | *Full pipeline with monitoring* | *C1* | ⬜ |

### Tier 4: Archive/Cleanup

| Action | Projects |
|--------|----------|
| Archive (make private or archive) | *List repos to archive* |
| Keep but don't feature | *List repos to keep but not highlight* |

---

## 🔵 DIGITAL PRESENCE — Brand Building

> **Full strategic plan:** [digital-presence-plan.md](strategy/digital-presence-plan.md)
> **Copy-ready content:** [platform-copy.md](assets/platform-copy.md)
> **Content schedule:** [content-plan.md](strategy/content-plan.md)

### Phase 0: Quick Wins (~1 hour total — DO FIRST)

| # | Action | Platform | Time | Status |
|:-:|--------|----------|:----:|:------:|
| D1 | Update profile bio + website + email | GitHub | 10 min | ⬜ |
| D2 | Update headline (from `assets/platform-copy.md`) | LinkedIn | 5 min | ⬜ |
| D3 | Update About section (from `identity/professional-summary.md`) | LinkedIn | 15 min | ⬜ |
| D4 | Set consistent profile photo across platforms | All | 10 min | ⬜ |

### Website / Portfolio

| # | Action | Effort | Status |
|:-:|--------|:------:|:------:|
| D5 | Design and build portfolio website | 2-4 days | ⬜ |
| D6 | Deploy to custom domain | 1 day | ⬜ |

### Platform Overhaul

| # | Action | Effort | Status |
|:-:|--------|:------:|:------:|
| D7 | Rewrite LinkedIn Experience sections | 1 hour | ⬜ |
| D8 | Add top certifications to LinkedIn | 20 min | ⬜ |
| D9 | Set bio on secondary platforms (from `platform-copy.md`) | 30 min | ⬜ |

### Content Publishing

| # | Article / Post | Platform | Proves | Status |
|:-:|---------------|----------|--------|:------:|
| D10 | *Example: "Building X in Production"* | *Dev.to* | *Relevant claim* | ⬜ |

---

## 🟢 SKILL BUILDING — Role Gap Closing

> Source: [study-plan.md](strategy/study-plan.md) · [target-roles.md](strategy/target-roles.md)

| # | Skill | Current → Target | Unlocks Roles | Priority | Deadline | Status |
|:-:|-------|:-----------------:|:------------:|:--------:|:--------:|:------:|
| S1 | *Example: Kubernetes* | *beginner → intermediate* | *All senior roles* | 🔴 P0 | *Sprint 1* | ⬜ |

---

## 🟡 JOB SEARCH — Application Pipeline

> Source: [job-search/tracker.md](strategy/job-search/tracker.md) · [target-roles.md](strategy/target-roles.md)

### Pre-Search Prep

| # | Action | Status |
|:-:|--------|:------:|
| J1 | Finalize resume variants (1 per target role cluster) | ⬜ |
| J2 | Set up job alerts on target platforms | ⬜ |
| J3 | Prepare company research template | ⬜ |

### Active Search

| # | Action | Status |
|:-:|--------|:------:|
| J4 | Apply to 3-5 roles per week | ⬜ |
| J5 | Warm 2-3 network contacts per week | ⬜ |
| J6 | Review and iterate resume based on response rates | ⬜ |

---

## 📊 Progress Summary

<!-- Update this section periodically -->

| Stream | Total Items | Done | % |
|--------|:-----------:|:----:|:-:|
| 🔴 Claim Debt | 0 | 0 | 0% |
| 🟠 Portfolio | 0 | 0 | 0% |
| 🔵 Digital Presence | 0 | 0 | 0% |
| 🟢 Skill Building | 0 | 0 | 0% |
| 🟡 Job Search | 0 | 0 | 0% |
| **Total** | **0** | **0** | **0%** |
