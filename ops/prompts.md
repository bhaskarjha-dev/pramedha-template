# Prompt Library — Copy-Paste Commands for AI Sessions

> **Purpose:** Each prompt below is a self-contained instruction you paste into a NEW AI session.
> The AI reads the repo files referenced in the prompt and executes the task.
> No conversation history needed.
>
> **How to use:** Copy the prompt. Paste it. The AI does the rest.

---

## Table of Contents

1. [Initial Fill (from raw data)](#1-initial-fill-from-raw-data)
2. [Full System Audit](#2-full-system-audit)
3. [Add New Project](#3-add-new-project)
4. [Add New Work Experience / Achievement](#4-add-new-work-experience--achievement)
5. [Weekly Maintenance](#5-weekly-maintenance)
6. [Generate Tailored Resume for a Job Posting](#6-generate-tailored-resume-for-a-job-posting)
7. [New Resume Variant Creation](#7-new-resume-variant-creation)
8. [Interview Prep for Specific Role](#8-interview-prep-for-specific-role)
9. [Resume Improvement Pass](#9-resume-improvement-pass)
10. [LinkedIn / Job Platform Profile Refresh](#10-linkedin--job-platform-profile-refresh)
11. [Study Plan Progress Update](#11-study-plan-progress-update)
12. [Claims Register Audit](#12-claims-register-audit)
13. [Skills Matrix Refresh](#13-skills-matrix-refresh)
14. [Portfolio Website Content](#14-portfolio-website-content)
15. [Offer Comparison Analysis](#15-offer-comparison-analysis)

---

## 1. Initial Fill (from raw data)

```
TASK: Fill my pramedha-template from raw career data.

CONTEXT: Read these files FIRST:
- .pramedha/agent-instructions.md (master protocol — follow every step)
- .pramedha/schema-reference.md (field mapping)
- config.yaml (my preferences)

Then scan ALL files in data-corpus/ (resumes, documents, exports, text, media).

EXECUTE: Follow the 12-step protocol in agent-instructions.md exactly:
1. Extract structured facts from all raw data
2. Cross-reference across sources for accuracy
3. Fill identity/*.yaml with verified, structured data
4. Tag EVERY claim with ✅/⚠️/❌
5. Generate resume/master.yaml with keyed bullets
6. Create resume variants for my target roles
7. Fill claims-and-evidence.md with contradictions
8. Fill personal/ and strategy/ where data exists

OUTPUT: Commit after each major file with clear messages.
Report: files filled, claims count, contradictions found, gaps remaining.
```

---

## 2. Full System Audit

```
TASK: Comprehensive audit of my pramedha-template career system.

CONTEXT: Read these files FIRST before doing anything:
- ops/guide.md (system rules, maintenance rituals)
- ops/authority-map.md (what's truth for what)
- README.md (architecture overview)

Then read ALL files in identity/ and resume/.

EXECUTE: Audit these 10 areas systematically:
1. CONTACT CONSISTENCY — Does identity.yaml match config.yaml match master.yaml header?
2. EXPERIENCE FRESHNESS — Is experience.yaml up to date? Missing recent work?
3. SKILLS ACCURACY — Do skills.yaml levels match evidence in experience.yaml?
4. CLAIMS INTEGRITY — Pick 5 random bullets from master.yaml. Are they in claims register?
5. RESUME CASCADE — Run: python resume/assemble.py --validate
6. VERIFICATION COVERAGE — What % of facts have ✅ tags? What % are ⚠️ or ❌?
7. CROSS-FILE CONSISTENCY — Do dates, titles, company names match across files?
8. PRIVACY CHECK — Is any personal/ data leaking into identity/ or resume/?
9. COMPLETENESS — What important fields are empty? What's the fill rate?
10. STRATEGY ALIGNMENT — Do resume variants match target roles in strategy/?

OUTPUT: For each area, report PASS/FAIL with specific findings.
For any FAIL, provide the exact fix (file, line, what to change).
Overall score: X/10 areas passing.
```

---

## 3. Add New Project

```
TASK: Add a new project to my career data.

PROJECT DETAILS:
[Paste your project description, what you built, tech used, outcomes]

CONTEXT: Read these files first:
- identity/projects.yaml (existing projects)
- identity/experience.yaml (to see if this project relates to work experience)
- identity/skills.yaml (to update skills if new tech was used)
- identity/claims-and-evidence.md (to register new claims)

EXECUTE:
1. Add project to identity/projects.yaml with proper structure
2. Tag all claims with verification status
3. If this was a work project, add relevant bullets to experience.yaml
4. Update identity/skills.yaml if new technologies were used
5. Add to resume/master.yaml as a keyed project entry
6. Note any new claims in identity/claims-and-evidence.md

OUTPUT: Show exact changes made to each file. Commit with clear message.
```

---

## 4. Add New Work Experience / Achievement

```
TASK: Add a new work achievement/deliverable to my career data.

WHAT HAPPENED:
[Describe what you did, when, what the outcome was, any metrics]

CONTEXT: Read these files first:
- identity/experience.yaml (current experience)
- identity/claims-and-evidence.md (claims register)
- resume/master.yaml (bullet pool)
- ops/authority-map.md (source rules)

EXECUTE:
1. Add the deliverable to the correct employer/project in experience.yaml
2. Write 2-3 bullet variations (default, short, technical)
3. Tag metrics as [measured] or [estimated]
4. Tag verification status (✅/⚠️/❌)
5. Add keyed bullets to resume/master.yaml
6. Register claims in claims-and-evidence.md
7. Log the achievement in journal/wins.md

OUTPUT: Show all changes. Suggest which resume variants should include this.
```

---

## 5. Weekly Maintenance

```
TASK: Weekly maintenance check on my career system.

CONTEXT: Read:
- ops/guide.md (maintenance rituals section)
- ops/authority-map.md

EXECUTE the weekly ritual:
1. Check: Any new work this week to add to journal/work-log/?
2. Check: Any wins to capture in journal/wins.md?
3. Check: Any applications sent? Update strategy/job-search/tracker.md
4. Check: Any new skills learned? Update identity/skills.yaml
5. Run: python resume/assemble.py --validate (cascade health check)
6. Quick scan: Anything in data-corpus/ not yet extracted to identity/?
7. Check git status — any uncommitted changes?

OUTPUT: Checklist with DONE/SKIPPED/NEEDS ACTION for each item.
Commit any changes with message: "weekly: maintenance check [date]"
```

---

## 6. Generate Tailored Resume for a Job Posting

```
TASK: Create a tailored resume for a specific job posting.

JOB POSTING:
[Paste the full job description here]

CONTEXT: Read these files:
- resume/master.yaml (all available bullets)
- resume/design.yaml (theme config)
- identity/experience.yaml (full work history)
- identity/skills.yaml (skill levels)
- resume/jd/_template.yaml (JD overlay structure)

EXECUTE:
1. Analyze the JD: extract required skills, experience, keywords
2. Match against my skills and experience
3. Create a JD-specific overlay in resume/jd/[company]_[role].yaml
4. Select the most relevant bullets from master.yaml
5. Write a tailored summary for this specific role
6. Choose technologies section matching JD requirements
7. Run: python resume/assemble.py --jd jd/[company]_[role].yaml

OUTPUT:
- The JD overlay file (ready to assemble)
- Skills match analysis (what I have vs what they want)
- Gap analysis (skills I should highlight even if not perfect match)
- ATS keyword coverage estimate
```

---

## 7. New Resume Variant Creation

```
TASK: Create a new resume variant for a target role category.

TARGET ROLE: [e.g., "GenAI Engineer", "Backend Lead", "ML Engineer"]

CONTEXT: Read:
- resume/master.yaml (all bullets)
- resume/variants/_template.yaml (variant structure)
- strategy/target-roles.md (role evaluation)
- identity/skills.yaml (current skills)

EXECUTE:
1. Analyze what skills/experience matter most for this role
2. Select the strongest matching bullets from master.yaml
3. Create resume/variants/[role_name].yaml
4. Write a role-specific summary
5. Choose technologies section optimized for ATS
6. Run: python resume/assemble.py --variant [name]
7. Review the generated YAML for quality

OUTPUT: The variant file + analysis of how well my profile matches this role.
```

---

## 8. Interview Prep for Specific Role

```
TASK: Prepare me for an interview for a specific role.

ROLE: [Role title]
COMPANY: [Company name]
INTERVIEW STAGE: [Phone screen / Technical / System design / Behavioral / Final]

CONTEXT: Read:
- identity/experience.yaml (my full work history)
- identity/skills.yaml (my skill levels)
- assets/star-stories.md (behavioral stories)
- assets/questions-to-ask.md (questions for interviewer)
- strategy/role-deep-dives.md (if this role has been analyzed)

EXECUTE:
1. Identify top 5 things this interviewer will probe
2. Map my experience to their likely questions
3. Prepare 3-5 STAR stories relevant to this role
4. Identify potential weak spots and prepare honest answers
5. Prepare 5 specific questions to ask THEM
6. Create a "cheat sheet" with key talking points

OUTPUT: Interview prep document I can review 30 min before the call.
```

---

## 9. Resume Improvement Pass

```
TASK: Improve the quality of my resume bullets.

CONTEXT: Read:
- resume/master.yaml (current bullets)
- identity/experience.yaml (source facts)
- identity/claims-and-evidence.md (what's safe to claim)

EXECUTE for each bullet in master.yaml:
1. Does it start with a strong action verb?
2. Does it include a measurable result?
3. Is the metric tagged [measured] or [estimated]?
4. Is it concise (under 2 lines when rendered)?
5. Does it pass the claims register? (no inflated claims)
6. Can the phrasing be improved for clarity or impact?

OUTPUT:
- Before/after comparison for each improved bullet
- List of bullets that need more information from me
- Overall quality score: X/10
```

---

## 10. LinkedIn / Job Platform Profile Refresh

```
TASK: Update my LinkedIn/Naukri/job platform profiles based on current career data.

CONTEXT: Read:
- identity/identity.yaml (contact info)
- identity/experience.yaml (work history)
- identity/skills.yaml (skill matrix)
- identity/professional-summary.md (summary variants)
- assets/linkedin-pack.md (LinkedIn-specific content)

EXECUTE:
1. Generate optimized headline (max 220 chars)
2. Write About section (personal, story-driven)
3. Map experience entries to platform format
4. Generate skills list ordered by relevance to target roles
5. Suggest Featured section items
6. Check for consistency with resume/master.yaml

OUTPUT: Ready-to-paste content for each profile section.
```

---

## 11. Study Plan Progress Update

```
TASK: Update my learning progress and adjust the study plan.

WHAT I COMPLETED RECENTLY:
[Describe courses, books, projects, practice completed]

CONTEXT: Read:
- strategy/study-plan.md (current plan)
- journal/learning-log.md (learning history)
- identity/skills.yaml (current skills)
- identity/credentials.yaml (certifications)

EXECUTE:
1. Log completed learning in journal/learning-log.md
2. Update skill levels in identity/skills.yaml if improved
3. Add new certifications to identity/credentials.yaml
4. Adjust study-plan.md sprint progress
5. Recalculate skill gaps against target roles

OUTPUT: Updated files + progress summary + next priorities.
```

---

## 12. Claims Register Audit

```
TASK: Audit the integrity of my claims register.

CONTEXT: Read:
- identity/claims-and-evidence.md (claims register)
- identity/experience.yaml (all experience bullets)
- resume/master.yaml (resume-facing bullets)
- data-corpus/ (available evidence)

EXECUTE:
1. For each bullet in experience.yaml, verify a claims entry exists
2. For each ✅ VERIFIED claim, check that evidence actually exists
3. For each ⚠️ ESTIMATED claim, can it be upgraded to ✅?
4. For each ❌ UNVERIFIED claim, is it still in any resume variant?
5. Check for any contradictions between files
6. Check for "claim inflation" — bullets that oversell the reality

OUTPUT:
- Claims coverage: X% of bullets have claims entries
- Verification rate: X% ✅, X% ⚠️, X% ❌
- Action items: specific claims to verify or fix
```

---

## 13. Skills Matrix Refresh

```
TASK: Refresh my skills matrix based on recent work.

CONTEXT: Read:
- identity/skills.yaml (current skills)
- identity/experience.yaml (recent work — check for new tech used)
- journal/learning-log.md (recent learning)
- journal/work-log/ (recent work logs)

EXECUTE:
1. Scan recent experience and learning for new skills
2. Check if any existing skill levels should increase
3. Add any new skills with proper evidence references
4. Remove any skills no longer relevant (or mark as deprecated)
5. Ensure every skill has evidence linking to a project or course
6. Update resume/master.yaml technologies sections if needed

OUTPUT: Diff of changes to skills.yaml + justification for each change.
```

---

## 14. Portfolio Website Content

```
TASK: Generate content for my portfolio/personal website.

CONTEXT: Read:
- identity/professional-summary.md (summary variants)
- identity/projects.yaml (portfolio projects)
- identity/experience.yaml (work highlights)
- assets/github-readme.md (GitHub profile)

EXECUTE:
1. Write homepage hero section (name, headline, 1-liner)
2. Write About page content (professional + personal)
3. Generate project cards (title, tech, 1-line description, link)
4. Write Experience section (condensed timeline)
5. Generate blog topic ideas from expertise areas
6. Create contact page content

OUTPUT: Website content organized by page, ready to implement.
```

---

## 15. Offer Comparison Analysis

```
TASK: Compare job offers to make a data-driven decision.

OFFERS:
[Paste details of each offer: company, role, compensation, benefits, etc.]

CONTEXT: Read:
- strategy/offer-comparison.md (comparison template)
- strategy/financial.md (my salary targets)
- personal/preferences.yaml (work preferences, deal-breakers)
- personal/life-goals.md (career goals)

EXECUTE:
1. Normalize compensation (base + bonus + equity + benefits)
2. Score each offer against my work preferences
3. Check against deal-breakers
4. Evaluate growth potential vs career goals
5. Calculate risk factors (startup stage, visa, relocation)
6. Generate a weighted comparison matrix

OUTPUT: Recommendation with clear reasoning.
```
