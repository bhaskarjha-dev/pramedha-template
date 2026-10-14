# Claims & Evidence Registry

> **Purpose:** The gatekeeper between what you THINK you did and what you can PROVE.
> Every outward-facing claim (resume, LinkedIn, interview) must pass through here.
>
> Maps to: `PramedhaProfile.meta.claims_registry`

---

## Claim Safety Tiers

| Tier | Label | Rule |
|:----:|-------|------|
| 🟢 | **SAFE** | Use freely — evidence is strong |
| 🟡 | **USE CAREFULLY** | Technically true but needs context or metric substantiation |
| 🔴 | **DO NOT USE** | Cannot prove, or misleading without context |

## Measurement Tags

> These tags annotate the *evidence type* behind each claim.
> Claims tagged `[estimated]` or `[to-verify]` automatically become items
> in the **Claim Debt Queue** section below.

| Tag | Meaning | Action Required |
|-----|---------|----------------|
| `[measured]` | Exact data from official document (review, letter, dashboard, CSV) | None — claim is substantiated |
| `[estimated]` | Reasonable claim — needs substantiation via project, demo, or benchmark | Build evidence (code, demo, blog) |
| `[to-verify]` | Claim is true but formal evidence not yet on file | Collect evidence (screenshot, doc, testimonial) |

---

## Evidence Hierarchy

When facts conflict, trust sources in this order:

```
1. Official document (certificate, offer letter, scorecard)        ← HIGHEST
2. Dedicated screenshot / award record / email
3. Detailed work log (journal/work-log/)
4. Structured YAML (identity/)
5. Older resume
6. Brainstorming doc / freeform notes                              ← LOWEST
```

> Old resumes are evidence of what was once *claimed*, not proof the claim is *true*.

---

## Claims Register

<!-- Fill this as you verify claims. Format:
| Claim | Source | Tier | Evidence | Tag | Notes |
     Tag values: [measured], [estimated], or [to-verify]
     Claims with [estimated] or [to-verify] feed into the Claim Debt Queue below
-->

| Claim | Source | Tier | Evidence | Tag | Notes |
|-------|--------|:----:|----------|-----|-------|
| *Example: "Led team of 5"* | *resume_2024.pdf* | 🟡 | *No org chart, was informal lead* | *[to-verify]* | *Rephrase to "coordinated with 5 engineers"* |

---

## Contradictions Log

<!-- When two sources disagree about the same fact, log it here.
     Maps to: PramedhaProfile.meta.contradictions[] -->

| Field | Source A | Value A | Source B | Value B | Resolution |
|-------|---------|---------|---------|---------|------------|
| *Example: start date at Company X* | *resume.pdf* | *Jan 2023* | *LinkedIn* | *Feb 2023* | *Checked offer letter: Jan 16, 2023* |

---

## Claim Debt Queue

> Claims tagged `[estimated]` or `[to-verify]` in the register above need evidence.
> Track the evidence-building work here. Check off items as they are substantiated.

### Priority 1: Build Projects to Prove Claims

<!-- Fill one row per claim that needs a project as evidence -->

| # | Claim to Prove | Evidence to Create | Effort | Status |
|:-:|----------------|-------------------|:------:|:------:|
| C1 | *Example: "Built ML pipeline processing 1M records"* | *Build demo pipeline with monitoring dashboard* | *3 days* | ⬜ |

### Priority 2: Collect Internal Evidence (No Coding Needed)

<!-- Claims that just need screenshots, documents, or testimonials -->

| # | Claim to Prove | Evidence to Provide | Effort | Status |
|:-:|----------------|-------------------|:------:|:------:|
| C2 | *Example: "Led team of 5 developers"* | *Org chart screenshot, Jira team page, or email* | *15 min* | ⬜ |

### After Resolving Claim Debt

1. Add evidence file to `data-corpus/documents/`
2. Update tag in `identity/experience.yaml`: change `[estimated]`/`[to-verify]` → `[measured]`
3. Update tier in Claims Register above: change 🟡 → 🟢
4. Regenerate resume variants (if applicable)

---

> 💡 **Emergency Career Contingency & Crisis Checklists:**
> Layoff preparedness and financial runway checklists are maintained in `strategy/job-tracker.md` (Section 6) and `strategy/financial.md`.
