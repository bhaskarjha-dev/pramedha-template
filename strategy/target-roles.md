# 🎯 Target Roles — Role Evaluation & Targeting Strategy

> **Purpose:** Evaluate potential target roles, score their viability against your verified profile,
> and define your targeting strategy and resume variant mapping.
>
> **Methodology:** Score each candidate role on 8 objective parameters (1-5 each, max 40).
> High-scoring roles (Tier A) become your primary focus and dictate your resume variants.

---

## Part 1: Your Verified Profile (The Honest Baseline)

> Before scoring ANY role, document what you **actually have** — not what you
> aspire to, not what's on your resume without evidence, but what's verified.
> Ground this in `identity/skills.yaml` and `identity/experience.yaml`.

### Core Technical Identity

| Dimension | Level (⭐1-5) | Evidence |
|-----------|:------------:|---------:|
| *Example: Python engineering* | *⭐⭐⭐⭐ Advanced (5 yrs)* | *Primary language across all employers* |
| | | |
| | | |

### Skill Gaps (Be Honest)

| Dimension | Level (⭐1-5) | Impact on Target Roles |
|-----------|:------------:|-----------------------:|
| *Example: System design at scale* | *⭐ Beginner* | *Blocks Staff/Architect roles* |
| | | |
| | | |

### Domain Context & Soft Strengths

| Asset | Evidence |
|-------|---------|
| *Example: Enterprise delivery* | *3 years at Fortune 500, client-facing* |
| | |

---

## Part 2: Evaluation Criteria & Scoring

Rate each role 1–5 on these 8 dimensions (Max 40 points):

| Parameter | What It Measures | Scoring Guide (1-5) |
|-----------|-----------------|---------------------|
| **P1: Skills Match** | How much of the requirements do you already have? | 5 = 90%+ match · 1 = Critical gap |
| **P2: Interest / Passion** | How excited are you about this work daily? | 5 = Dream work · 1 = Dread it |
| **P3: Market Demand** | How many openings exist? Is demand growing? | 5 = Massive demand · 1 = Dying market |
| **P4: Salary Potential** | Does it meet your financial targets at your YoE? | 5 = Top of band · 1 = Below target |
| **P5: Growth Trajectory** | Where does this role lead in 3-5 years? | 5 = High leverage · 1 = Dead end |
| **P6: Time to Close Gaps** | How long to become competitive? | 5 = Ready now · 1 = 12+ months |
| **P7: Interview Readiness** | Can you pass the interview today? | 5 = Ready today · 1 = No chance |
| **P8: Competition Level** | How crowded is the applicant pool? | 5 = Low competition · 1 = Brutal pool |

---

## Part 3: Master Role Evaluation Table

<!-- Fill one row per role you're considering. Don't pre-filter — let the scores decide.
     Total = sum of P1 through P8 (max 40). -->

| # | Role | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | Total | Tier |
|:-:|------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:-----:|:----:|
| 1 | *Example: ML Engineer* | *4* | *5* | *4* | *5* | *4* | *4* | *4* | *3* | *33* | *A* |
| 2 | | | | | | | | | | | |
| 3 | | | | | | | | | | | |

### Tier Definitions (Max 40 Points)
- **Tier A (32–40):** Primary targets — apply aggressively, create dedicated resume variants
- **Tier B (24–31):** Secondary targets — apply selectively or invest 1–3 months closing gaps
- **Tier C (16–23):** Stretch targets — pursue only if exceptional inbound opportunity
- **Below 16:** Skip — significant foundational gaps, not worth current investment

---

## Part 4: Why Your Target Roles Work Together

<!-- After scoring, find the shared foundation across all Tier A roles.
     This determines your positioning statement and how many resume variants you need. -->

| Shared Foundation (All Tier A Roles) | Role-Specific Additions |
|--------------------------------------|------------------------|
| *Example: Python + SQL + Distributed Systems* | *Role X: Cloud depth, Role Y: Model Serving* |

### Unified Positioning Statement
> Write one sentence covering ALL your Tier A targets:
>
> *"I build [what] — [specialty 1], [specialty 2], and [specialty 3] — at [scale/context]."*

---

## Part 5: Resume Variant Mapping

<!-- Group target roles by which resume variant they share. Aim for 2-4 variants max. -->

| Variant | Target Roles | Key Emphasis | Variant Config |
|:-------:|-------------|-------------|----------------|
| A | *Roles 1, 2* | *Core engineering + architecture* | `tools/resume/variants/variant-a.yaml` |
| B | *Roles 3, 4* | *Applied ML / domain specialization* | `tools/resume/variants/variant-b.yaml` |

---

## Part 6: Detailed Role Deep-Dive (Tier A & B)

<!-- For each Tier A or B role, complete this deep-dive profile: -->

### Role: [Role Name] — Score: [X/40] — Tier [A/B]

| Attribute | Detail |
|-----------|--------|
| **Why this role** | (Personal motivation / career alignment) |
| **Your match** | (Score context — what makes you competitive) |
| **Key skill gaps** | (Specific tools/frameworks missing) |
| **Time to close gaps** | (Weeks/months needed to become fully competitive) |
| **Preparation needed** | (Targeted courses, projects, mock interviews) |
| **Salary range (your YoE)** | (Research-backed range for target market) |
| **Target companies** | **Dream:** [Co A] · **Target:** [Co B, Co C] · **Safety:** [Co D] |
| **ATS keywords** | (Keywords from job descriptions to include on resume/LinkedIn) |
| **Resume variant** | (Maps to `tools/resume/variants/*.yaml`) |
