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
| **Identity (truth)** | ✅ From data-corpus | experience.yaml, skills.yaml, credentials.yaml, projects.yaml, identity.yaml, volunteering.yaml, speaking-and-community.yaml, references.yaml, claims-and-evidence.md, professional-summary.md |
| **Resume (generated)** | ✅ From identity | master.yaml, design.yaml, variants/*.yaml |
| **Assets (generated)** | ✅ From identity | star-stories.md, cover-letters/*.md, linkedin-pack.md, platform-copy.md, github-readme.md, questions-to-ask.md, form-fill-cheatsheet.md, testimonials.md, project-briefs/*.md, interview-prep/technical.md, interview-prep/behavioral.md |
| **Strategy (needs user input)** | ⚠️ Draft from context | target-roles.md, role-analysis.md (optional), study-plan.md, master-action-tracker.md, digital-presence-plan.md, financial.md, content-plan.md, risk-register.md, networking.md (tiers/targets), role-deep-dives.md |
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
- `exports/` — Parse generic data exports for additional background
- `linkedin/` — Extract full profile text, endorsements, and network data
- `github/` — Extract repository history, commit volumes, tech stacks
- `text/` — Extract career context, goals, preferences from freeform text
- `media/` — Note what visual evidence exists (reference in verification tags)

**Build a mental model of the person's complete career before writing anything.**

---

### Phase B: Identity Layer (Steps 2-10) — The Source of Truth

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

#### Step 8: Fill identity/speaking-and-community.yaml
- Speaking engagements: title, event, organizer, date, audience, topics, materials links
- Hackathons: name, result, project built, team size, tech used
- Community memberships: groups joined, role, activity level
- Content metrics: LinkedIn followers, GitHub stars, articles published (update periodically)
- Tag verification status for each entry
- Cross-reference with LinkedIn exports and event certificates in data-corpus/

#### Step 9: Fill identity/claims-and-evidence.md
- Review ALL claims in experience.yaml, skills.yaml, and credentials.yaml
- Assign safety tiers: 🟢 SAFE, 🟡 USE CAREFULLY, 🔴 DO NOT USE
- Assign measurement tags: `[measured]`, `[estimated]`, `[to-verify]`
- Items tagged `[estimated]` or `[to-verify]` will become Claim Debt in master-action-tracker
- Log any contradictions found between sources

#### Step 10: Fill identity/professional-summary.md
- Write 3-5 summary variants based on the filled profile
- Tailor to the user's target roles (from config.yaml or strategy/)
- Keep factual — every claim in the summary must exist in experience.yaml

---

### Phase C: Resume Layer (Steps 11-13) — Generated From Identity

#### Step 11: Populate resume/master.yaml via Bridge Script
- Run the bridge synchronizer to import verified facts from identity into `master.yaml`:
  ```bash
  py resume/sync.py
  ```
  *(Use `py resume/sync.py --dry-run` to preview additions without writing).*
- **Transformation Pipeline:**
  - `identity/experience.yaml` → flattens deliverables into `master.yaml[role_key].bullets[bullet_key].default`.
  - `identity/projects.yaml` → syncs public/internal projects into `master.yaml[projects]`.
  - `identity/credentials.yaml` → syncs education & publications into `master.yaml`.
- **Enrich Bullet Phrasings in master.yaml:**
  For key achievements, craft alternative phrasings tailored for different audiences:
  ```yaml
  experience:
    role_key:
      company: "..."
      position: "..."
      bullets:
        bullet_key:
          default: "Standard phrasing with metric [measured]"
          short: "Concise 1-line version for tight layouts"
          technical: "Deep-dive phrasing highlighting stack/architecture"
          leadership: "Emphasizes team orchestration and business impact"
  ```

#### Step 12: Generate resume/variants/
- Create role-specific overlays in `resume/variants/` (e.g. `A_Backend_Lead.yaml`, `B_Fullstack.yaml`).
- Each variant selects specific bullets and phrasings from `master.yaml`.
- Include a tailored summary and select relevant projects and technologies.

#### Step 13: Validate resume pipeline
- Run `py resume/assemble.py --validate` to verify all bullet and project references.
- Test building output with `py resume/assemble.py`. RenderCV will compile variants into `resume/generated/*.yaml` and output PDFs/Typst documents.

---

### Phase D: Assets Layer (Steps 14-21) — Generated From Identity + Experience

#### Step 14: Generate assets/star-stories.md
- Extract 5-8 stories from experience.yaml bullets
- Structure each using STAR format: Situation, Task, Action, Result
- Map to competency categories (leadership, problem-solving, collaboration, etc.)
- Every story must reference a verified claim

#### Step 15: Generate assets/cover-letters/
- `standard.md` — Problem-Solution framework (for job board applications)
- `referral.md` — Hook-Value-Ask framework (for warm introductions)
- `cold-outreach.md` — Context-Connection-Request (for cold emails)
- Use professional-summary.md + target-roles for tone

#### Step 16: Fill assets/form-fill-cheatsheet.md
- Extract from config.yaml + identity.yaml: name, email, phone, DOB, address
- Fill education, references, work authorization sections
- Pre-fill common application questions with suggested answers
- **Mark ⚠️ PRIVATE** — this file goes in .gitignore

#### Step 17: Generate assets/linkedin-pack.md
- Headline: max 220 chars, keyword-rich
- About section: 3 variants (narrative, technical, leadership)
- Featured section: top 3-5 items from projects.yaml featured
- Experience descriptions: adapted from experience.yaml bullets

#### Step 18: Generate assets/github-readme.md
- Professional intro from professional-summary.md
- Tech stack badges from skills.yaml
- Featured projects from projects.yaml
- Currently learning from study-plan.md (if filled)

#### Step 19: Fill assets/questions-to-ask.md
- Generate role-appropriate questions from target-roles.md
- Include universal questions (culture, growth, team, process)
- Add company-specific question templates

#### Step 20: Generate assets/platform-copy.md
- Email signature (4-5 lines)
- GitHub bio (160 char max)
- LinkedIn headline (220 char max, 2-3 options)
- Twitter/X bio (160 char max)
- Speaker bio (1 paragraph, ~100 words)
- Conference bio (2 paragraphs, ~200 words)
- Short bio (50 words)
- Derive all from professional-summary.md + target-roles.md positioning

#### Step 21: Generate assets/interview-prep/ (technical.md & behavioral.md)
- **technical.md**: Extract core technical competencies from skills.yaml (advanced/expert level); list likely interview topics per target role and add system design topics if applicable. Cross-reference with study-plan.md for gap awareness.
- **behavioral.md**: Map STAR stories from star-stories.md to common behavioral questions, leadership principles (e.g. Amazon LP, ownership, conflict resolution), and situational frameworks. Ensure each target role has at least 3 matching stories.

---

### Phase E: Strategy Layer (Steps 22-28) — Needs User Input, AI Drafts

> ⚠️ These files require user preferences/goals. If `data-corpus/text/` contains
> career plans, brain dumps, or goals — use them. Otherwise, draft what you can
> and mark sections needing user input with `<!-- USER INPUT NEEDED -->`.

#### Step 22: Draft strategy/target-roles.md
- If career goals exist in text/: evaluate roles against skills using 8-parameter framework
- Otherwise: suggest 3-5 roles based on experience + skills profile
- Include ATS keywords per role
- Map roles to resume variants
- Mark as draft: `<!-- AI-SUGGESTED — Review and confirm -->`
- Optional: Fill `strategy/role-analysis.md` first for comprehensive scan

#### Step 23: Draft strategy/study-plan.md
- Identify gaps between current skills.yaml and target role requirements
- Suggest learning resources and sprint timeline
- Mark as draft

#### Step 24: Draft strategy/master-action-tracker.md
- Populate 🔴 Claim Debt from claims-and-evidence.md `[estimated]` / `[to-verify]` items
- Populate 🟠 Portfolio from projects.yaml (repos needing polish)
- Populate 🟢 Skill Building from study-plan.md gaps
- Leave 🔵 Digital Presence and 🟡 Job Search for user to fill
- Update progress summary counts

#### Step 25: Draft strategy/digital-presence-plan.md
- Audit user's current digital presence from config.yaml profiles
- Categorize platforms into P0-P3 priority tiers
- Draft execution phases
- Mark as draft

#### Step 26: Draft strategy/financial.md
- If salary data exists in text/ or config.yaml: structure it
- Otherwise: leave fields empty (salary is sensitive)
- Never fabricate salary information

#### Step 27: Draft strategy/content-plan.md
- Suggest content topics based on expertise areas from skills.yaml
- Draft a publishing cadence based on time availability
- Mark as draft

#### Step 28: Draft strategy/risk-register.md
- Identify career transition risks based on the profile
- Suggest mitigation strategies
- Mark as draft

---

### Phase F: Personal Layer (Steps 29-31) — Private, User Input Preferred

> ⚠️ Fill ONLY from `data-corpus/text/` freeform data. Never infer personal
> information. If no personal context exists, leave these empty.

#### Step 29: Draft personal/career-narrative.md, then personal/about-me.md
- **First, Draft `personal/career-narrative.md`:**
  - Write "walk me through your career" transition arcs in 3 lengths (30s elevator pitch, 2min interview standard, 5min deep dive).
  - Ground every transition strictly in verified facts from `identity/experience.yaml`.
- **Second, Draft `personal/about-me.md`:**
  - Use the career narrative as grounding to articulate life context, personal values, and intellectual motivations (extracted only from `data-corpus/text/` evidence).

#### Step 30: Draft personal/life-goals.md
- If career goals exist in text/: structure into short/medium/long term
- Fill non-negotiables and dream role if context available
- Otherwise: leave empty for user

#### Step 31: Draft personal/preferences.yaml
- Extract work preferences from freeform text (if available)
- Fill career_stage, risk_tolerance, time_availability if inferrable
- Otherwise: leave empty

---

### Phase G: Config & Vision (Steps 32-33) — Finalize

#### Step 32: Enrich VISION.md
- Fill mission statement from config.yaml + career goals
- Set success criteria from target-roles + financial
- Update current status based on what's been filled
- Update "What's Next" pointer to master-action-tracker.md

#### Step 33: Final Validation
```bash
python .pramedha/validate.py           # Check integrity
python resume/assemble.py --validate   # Check cascade references
```
Report:
- Files filled vs. empty
- Claims verified vs. unverified
- Contradictions found
- Items needing user input
- Update `ops/session-handoff.md` with session summary
- **Fill `ops/conversation-context-archive.md`** — this is the one-time founding
  document. Capture: what phases happened, key user decisions discovered,
  data gaps resolved, contradictions found, and artifacts created

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
| strategy/networking.md | Real-time contacts — AI initializes target circles/strategy; user logs individual contacts as met |
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

## Pramedha Integration (Optional)

This template is **fully standalone**. No external tools are required.
If also using the Pramedha platform, the schema mapping is:

```
identity/*.yaml     →  PramedhaProfile.professional
personal/*          →  PramedhaProfile.personal
claims-and-evidence →  PramedhaProfile.meta.claims_registry
```

The `Maps to:` comments in individual template files document this mapping
for reference. They are informational only — removing them has no effect
on standalone usage.
