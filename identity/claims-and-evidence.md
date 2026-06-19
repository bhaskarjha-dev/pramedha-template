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
| 🟡 | **USE CAREFULLY** | Technically true but needs context |
| 🔴 | **DO NOT USE** | Cannot prove, or misleading without context |

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
| Claim | Source | Tier | Evidence | Notes |
-->

| Claim | Source | Tier | Evidence | Notes |
|-------|--------|:----:|----------|-------|
| *Example: "Led team of 5"* | *resume_2024.pdf* | 🟡 | *No org chart, was informal lead* | *Rephrase to "coordinated with 5 engineers"* |

---

## Contradictions Log

<!-- When two sources disagree about the same fact, log it here.
     Maps to: PramedhaProfile.meta.contradictions[] -->

| Field | Source A | Value A | Source B | Value B | Resolution |
|-------|---------|---------|---------|---------|------------|
| *Example: start date at Company X* | *resume.pdf* | *Jan 2023* | *LinkedIn* | *Feb 2023* | *Checked offer letter: Jan 16, 2023* |
