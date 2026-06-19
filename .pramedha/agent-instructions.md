# Pramedha Template — Agent Fill Instructions

> **For AI Assistants:** This document tells you how to fill this career template.
> Read this FIRST before modifying any file.

---

## Your Mission

You are filling a **Pramedha Career Template** — a structured career repository.
The user has dumped raw career data in `data-corpus/`. Your job:

1. **Extract** structured facts from raw data
2. **Verify** every claim (tag with ✅/⚠️/❌)
3. **Fill** the template files with structured, accurate data
4. **Generate** resume content, assets, and strategy files
5. **Never fabricate** — if data doesn't exist, leave the field empty

---

## Master File Map

Every file in this template falls into one of these categories:

| Category | AI Can Auto-Fill? | Files |
|----------|:-:|-------|
| **Identity (truth)** | ✅ From data-corpus | experience.yaml, skills.yaml, credentials.yaml, projects.yaml, identity.yaml, volunteering.yaml, references.yaml, claims-and-evidence.md, professional-summary.md |
| **Resume (generated)** | ✅ From identity | master.yaml, design.yaml, variants/*.yaml |
| **Assets (generated)** | ✅ From identity | star-stories.md, cover-letters/*.md, linkedin-pack.md, github-readme.md, questions-to-ask.md, form-fill-cheatsheet.md, testimonials.md, project-briefs/*.md, interview-prep/technical.md |
| **Strategy (needs user input)** | ⚠️ Draft from context | target-roles.md, study-plan.md, financial.md, content-plan.md, risk-register.md, networking.md, role-deep-dives.md |
| **Personal (needs user input)** | ⚠️ Draft from text/ | about-me.md, career-narrative.md, life-goals.md, preferences.yaml, reflections.md |
| **Journal (real-time only)** | ❌ User fills over time | wins.md, learning-log.md, feedback.md, work-log/*.md |
| **Ops (don't fill)** | ❌ System files | guide.md, authority-map.md, prompts.md, audit-checklist.md, tooling.md, templates/*.md |
| **Config** | ⚠️ User fills basics, AI enriches | config.yaml, VISION.md |

---

## Step-by-Step Protocol

### Phase A: Foundation (Steps 0-1) — Read Everything First

#### Step 0: Read config.yaml
Start here. Get the user's name, profession type, and preferences.
This shapes everything that follows.

#### Step 1: Scan data-corpus/
Read ALL files in `data-corpus/` subdirectories:
- `resumes/` — Extract work history, skills, education, projects
- `documents/` — Extract certifications, awards, scores with verification
- `exports/` — Parse LinkedIn/GitHub exports for additional data
- `text/` — Extract career context, goals, preferences from freeform text
- `media/` — Note what visual evidence exists (reference in verification tags)

**Build a mental model of the person's complete career before writing anything.**

---

### Phase B: Identity Layer (Steps 2-8) — The Source of Truth

#### Step 2: Fill identity/identity.yaml
- Copy name/email from config.yaml
- Fill location, online presence, languages from extracted data
- Tag every field with verification status

#### Step 3: Fill identity/experience.yaml
This is the most important file. For each employer:
- Reverse chronological order (newest first)
- Capture: company, title, dates, location, industry, department, team_size
- For each project/deliverable: name, period, description, bullets
- Bullets format: "Action verb + what you did + measurable impact"
- Tag metrics: `[measured]` = from real data, `[estimated]` = reasonable guess
- List skills used per deliverable

**Cross-reference across sources.** If resume says "Jan 2023" but LinkedIn says "Feb 2023", note the contradiction in `claims-and-evidence.md`.

#### Step 4: Fill identity/skills.yaml
- Extract skills from experience bullets and project technologies
- Group by category (programming, frameworks, tools, etc.)
- Assign levels based on evidence:
  - `expert` = 5+ years, led others, deep contributions
  - `advanced` = 3+ years, production use, independent
  - `intermediate` = 1-3 years, guided use
  - `beginner` = < 1 year, learning stage
- Set `importance` (0.0-1.0) based on how central to career identity
- Set `skill_type` (hard/soft/tool)
- Every skill needs an evidence reference

#### Step 5: Fill identity/credentials.yaml
- Education: degree, institution, year, score, honors, courses
- Certifications: name, issuer, year, credential ID, URL
- Awards: title, awarder, year
- Test scores: name, score, year
- Publications, patents, grants: if applicable
- Organizations: professional memberships (ACM, IEEE, etc.)
- Only include what's evidenced in data-corpus/documents/

#### Step 6: Fill identity/projects.yaml
- Public projects: name, repo URL, tech stack, highlights, status
- Internal projects: name, context, tech, highlights (no proprietary info)
- Featured items: what to pin on LinkedIn/GitHub/portfolio
- Cross-reference with experience.yaml to avoid duplication

#### Step 7: Fill identity/volunteering.yaml + references.yaml
- Volunteering: community work, open source, mentoring
- References: professional references with contact details (mark ⚠️ PRIVATE)

#### Step 8: Fill identity/claims-and-evidence.md
- Review ALL claims in experience.yaml, skills.yaml, and credentials.yaml
- Assign safety tiers: 🟢 SAFE, 🟡 USE CAREFULLY, 🔴 DO NOT USE
- Log any contradictions found between sources

#### Step 9: Fill identity/professional-summary.md
- Write 3-5 summary variants based on the filled profile
- Tailor to the user's target roles (from config.yaml or strategy/)
- Keep factual — every claim in the summary must exist in experience.yaml

---

### Phase C: Resume Layer (Steps 10-12) — Generated From Identity

#### Step 10: Generate resume/master.yaml
- Convert experience.yaml bullets into the keyed phrasing format:
  ```yaml
  experience:
    role_key:
      company: "..."
      position: "..."
      bullets:
        bullet_key:
          default: "Original bullet text"
          short: "Shorter version"
          technical: "More technical version"
  ```
- Include education, projects, achievements from credentials.yaml

#### Step 11: Generate resume/variants/
- Create one variant per target role (or per profession area)
- Each variant selects relevant bullets from master.yaml
- Include a tailored summary for each variant

#### Step 12: Validate resume pipeline
- Run `python resume/assemble.py --validate` to check references
- Verify every bullet key in variants exists in master.yaml

---

### Phase D: Assets Layer (Steps 13-19) — Generated From Identity + Experience

#### Step 13: Generate assets/star-stories.md
- Extract 5-8 stories from experience.yaml bullets
- Structure each using STAR format: Situation, Task, Action, Result
- Map to competency categories (leadership, problem-solving, collaboration, etc.)
- Every story must reference a verified claim

#### Step 14: Generate assets/cover-letters/
- `standard.md` — Problem-Solution framework (for job board applications)
- `referral.md` — Hook-Value-Ask framework (for warm introductions)
- `cold-outreach.md` — Context-Connection-Request (for cold emails)
- Use professional-summary.md + target-roles for tone

#### Step 15: Fill assets/form-fill-cheatsheet.md
- Extract from config.yaml + identity.yaml: name, email, phone, DOB, address
- Fill education, references, work authorization sections
- Pre-fill common application questions with suggested answers
- **Mark ⚠️ PRIVATE** — this file goes in .gitignore

#### Step 16: Generate assets/linkedin-pack.md
- Headline: 120 chars, keyword-rich
- About section: 3 variants (narrative, technical, leadership)
- Featured section: top 3-5 items from projects.yaml featured
- Experience descriptions: adapted from experience.yaml bullets

#### Step 17: Generate assets/github-readme.md
- Professional intro from professional-summary.md
- Tech stack badges from skills.yaml
- Featured projects from projects.yaml
- Currently learning from study-plan.md (if filled)

#### Step 18: Fill assets/questions-to-ask.md
- Generate role-appropriate questions from target-roles.md
- Include universal questions (culture, growth, team, process)
- Add company-specific question templates

#### Step 19: Generate assets/interview-prep/technical.md
- Extract core technical areas from skills.yaml (advanced/expert level)
- List likely interview topics per target role
- Add system design topics if applicable
- Cross-reference with study-plan.md for gap awareness

---

### Phase E: Strategy Layer (Steps 20-24) — Needs User Input, AI Drafts

> ⚠️ These files require user preferences/goals. If `data-corpus/text/` contains
> career plans, brain dumps, or goals — use them. Otherwise, draft what you can
> and mark sections needing user input with `<!-- USER INPUT NEEDED -->`.

#### Step 20: Draft strategy/target-roles.md
- If career goals exist in text/: evaluate roles against skills
- Otherwise: suggest 3-5 roles based on experience + skills profile
- Mark as draft: `<!-- AI-SUGGESTED — Review and confirm -->`

#### Step 21: Draft strategy/study-plan.md
- Identify gaps between current skills.yaml and target role requirements
- Suggest learning resources and sprint timeline
- Mark as draft

#### Step 22: Draft strategy/financial.md
- If salary data exists in text/ or config.yaml: structure it
- Otherwise: leave fields empty (salary is sensitive)
- Never fabricate salary information

#### Step 23: Draft strategy/content-plan.md
- Suggest content topics based on expertise areas from skills.yaml
- Draft a publishing cadence based on time availability
- Mark as draft

#### Step 24: Draft strategy/risk-register.md
- Identify career transition risks based on the profile
- Suggest mitigation strategies
- Mark as draft

---

### Phase F: Personal Layer (Steps 25-27) — Private, User Input Preferred

> ⚠️ Fill ONLY from `data-corpus/text/` freeform data. Never infer personal
> information. If no personal context exists, leave these empty.

#### Step 25: Draft personal/about-me.md + career-narrative.md
- Extract life context from freeform text (if available)
- Write "walk me through your career" in 3 lengths (30s/2min/5min)
- Career narrative must only use facts from experience.yaml

#### Step 26: Draft personal/life-goals.md
- If career goals exist in text/: structure into short/medium/long term
- Fill non-negotiables and dream role if context available
- Otherwise: leave empty for user

#### Step 27: Draft personal/preferences.yaml
- Extract work preferences from freeform text (if available)
- Fill career_stage, risk_tolerance, time_availability if inferrable
- Otherwise: leave empty

---

### Phase G: Config & Vision (Steps 28-29) — Finalize

#### Step 28: Enrich VISION.md
- Fill mission statement from config.yaml + career goals
- Set success criteria from target-roles + financial
- Update current status based on what's been filled

#### Step 29: Final Validation
```bash
python .pramedha/validate.py           # Check integrity
python resume/assemble.py --validate   # Check cascade references
```
Report:
- Files filled vs. empty
- Claims verified vs. unverified
- Contradictions found
- Items needing user input

---

## Files The AI Does NOT Fill

These are system files, templates, or real-time documents:

| File | Why AI Doesn't Fill It |
|------|----------------------|
| ops/* | System rules — they're already complete |
| journal/wins.md | Real-time — user logs as events happen |
| journal/work-log/* | Real-time — weekly logs |
| journal/learning-log.md | Real-time — courses as completed |
| journal/feedback.md | Real-time — reviews as received |
| personal/reflections.md | Real-time — rejection learning as it happens |
| strategy/job-search/tracker.md | Real-time — applications as sent |
| strategy/offer-comparison.md | Real-time — offers as received |
| strategy/networking.md | Real-time — contacts as met |
| ops/templates/* | Entry templates — already done |
| .pramedha/* | System config — already done |
| resume/assemble.py | Code — already written |

---

## Rules

1. **Never fabricate data.** If no evidence exists, leave the field empty or commented out.
2. **Always tag verification.** Every fact gets ✅, ⚠️, or ❌.
3. **Preserve the user's voice.** Don't rewrite their descriptions beyond clarity fixes.
4. **Cross-reference everything.** If resume and LinkedIn disagree, note it.
5. **Ask when uncertain.** If a claim is ambiguous, ask the user rather than guessing.
6. **Commit incrementally.** Don't try to fill everything at once if context is limited.
7. **Mark AI drafts.** Any AI-generated content the user hasn't confirmed gets:
   `<!-- AI-DRAFTED — Review and confirm -->`
8. **Respect privacy layers:**
   - identity/ → public (can go on resume)
   - personal/ → private (never on resume, never shared)
   - data-corpus/ → raw evidence (never shared externally)

---

## Partial Fill Protocol

If the template is **already partially filled**, adapt the protocol:

1. **Run validation first:** `python .pramedha/validate.py --status`
2. **Identify what's filled vs empty** — don't overwrite existing data
3. **For filled files:** Review for accuracy, add missing verification tags, fix inconsistencies
4. **For empty files:** Follow the relevant step from the protocol above
5. **Cross-reference** new data against existing data for contradictions
6. **After filling:** Run `python .pramedha/validate.py` to verify integrity

### Common Partial Tasks

| Task | What to do |
|------|-----------|
| "Add a new project" | Update identity/projects.yaml + experience.yaml + master.yaml + claims register |
| "Add a new achievement" | Update experience.yaml + master.yaml + journal/wins.md + claims register |
| "Update skills" | Update identity/skills.yaml + resume/master.yaml technologies |
| "Create resume variant" | Read master.yaml, create resume/variants/[name].yaml |
| "Prep for interview" | Read identity/ + assets/star-stories.md, generate prep doc |
| "Fill everything from data-corpus" | Run Phase A → G in order |

See `ops/prompts.md` for ready-to-paste prompts for each of these tasks.

---

## Validation Step

After any fill or update, run:
```bash
python .pramedha/validate.py           # Check integrity
python resume/assemble.py --validate   # Check cascade references
```

---

## Pramedha Import Compatibility

The filled template can be imported directly into Pramedha:
```
identity/*.yaml     →  PramedhaProfile.professional
personal/*          →  PramedhaProfile.personal
claims-and-evidence →  PramedhaProfile.meta.claims_registry
```

Ensure field names match the schema reference for clean import.
