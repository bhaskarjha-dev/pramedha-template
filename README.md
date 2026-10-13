# Pramedha Career Template

> **Your career data — portable, version-controlled, AI-readable, and yours.**

A structured career repository that works as a **complete career operating system** out of the box.
Fill the YAML + Markdown files with any AI assistant or text editor — no external tools required.
Optionally compatible with [Pramedha](https://github.com/bhaskarjha-dev/pramedha-template) for AI-powered career intelligence.

---

## What You Get

| After Filling... | You Can... |
|-----------------|-----------|
| `config.yaml` + `identity/` | Generate a tailored resume in 30 seconds for any role |
| `assets/star-stories.md` | Walk into any behavioral interview prepared with 8 stories |
| `strategy/target-roles.md` | Know exactly which roles to apply to and why |
| `strategy/job-search/tracker.md` | Track 50+ applications with follow-up reminders |
| `assets/form-fill-cheatsheet.md` | Fill any job application form in 2 minutes flat |
| `journal/` | Have a brag document ready for performance reviews and promotions |

---

## Quick Start

> ⚠️ **DO NOT FORK this repo.** GitHub forks inherit the parent's visibility —
> a fork of a public repo **cannot be made private**. Your salary, DOB, references,
> and career strategy would be exposed. Use one of the methods below instead.

**→ [Read GETTING_STARTED.md](GETTING_STARTED.md) for the full 30-minute walkthrough.**

### Option A: GitHub "Use this template" (Recommended)

1. Click the green **"Use this template"** button at the top of this repo
2. Select **"Create a new repository"**
3. Set visibility to **Private** ✅
4. Clone your new private repo locally

### Option B: Clone + fresh private repo

```bash
# 1. Clone (this does NOT create a fork)
git clone https://github.com/bhaskarjha-dev/pramedha-template my-career
cd my-career

# 2. Disconnect from the template repo
git remote remove origin

# 3. Connect to YOUR private repo
git remote add origin git@github.com:YOUR-USERNAME/my-career.git
git push -u origin main
```

### Option C: Download ZIP

Download the ZIP from the releases page → extract → `git init` in the folder.

### Then:

```bash
# Fill config.yaml with your name + basics
# Dump raw career data into data-corpus/
# Let AI fill the rest (see .pramedha/agent-instructions.md)
# Generate resumes:
cd resume && python assemble.py && rendercv render generated/*.yaml
```

---

## Progressive Layers

Fill at your own pace. Each layer adds value independently.

| Layer | What You Fill | What You Get |
|:-----:|---------------|--------------|
| **0** | `config.yaml` (name + email) | Repo initialized |
| **1** | `identity/` (experience + skills) | Working resume via cascade engine |
| **2** | `strategy/` + `assets/` | Job search execution system |
| **3** | `personal/` + `journal/` | Full career operating system |
| **→** | Import into Pramedha | AI matching, portfolio, career intelligence |

---

## Architecture

```
pramedha-template/
│
├── VISION.md                  ← READ FIRST: career mission & north star
├── AGENTS.md                  ← AI agent instructions (universal standard)
├── GETTING_STARTED.md         ← 30-minute setup walkthrough
├── config.yaml                ← Your identity + preferences
│
├── data-corpus/               ← Phase 0: Dump raw career data
│   ├── resumes/                  Old resumes, CVs (PDF/DOCX)
│   ├── documents/                Certificates, transcripts, awards
│   ├── exports/                  LinkedIn CSV, GitHub JSON, Naukri
│   ├── text/                     Brain dumps, career notes
│   └── media/                    Photos, screenshots
│
├── identity/                  ← Phase 1: Structured career facts
│   ├── identity.yaml             Demographics, languages, work auth
│   ├── experience.yaml           Work history + bullets
│   ├── skills.yaml               Skill matrix with levels
│   ├── credentials.yaml          Education, certs, awards
│   ├── projects.yaml             Portfolio projects
│   ├── volunteering.yaml         Community, open source, mentoring
│   ├── references.yaml           Professional references (⚠️ private)
│   ├── claims-and-evidence.md    Verification registry
│   └── professional-summary.md   Elevator pitches (5 variants)
│
├── resume/                    ← Resume cascade system
│   ├── master.yaml               Bullet pool (keyed phrasings)
│   ├── design.yaml               Visual theme
│   ├── assemble.py               Cascade engine
│   ├── variants/                 Role-specific overlays
│   ├── jd/                       Per-job-description overlays
│   └── output/                   Generated PDFs
│
├── strategy/                  ← Phase 2: Career strategy
│   ├── target-roles.md           Role evaluation framework
│   ├── study-plan.md             Learning roadmap
│   ├── financial.md              Compensation & runway (⚠️ private)
│   ├── networking.md             Professional network CRM (⚠️ private)
│   ├── content-plan.md           Thought leadership plan
│   ├── risk-register.md          Career risk assessment
│   ├── offer-comparison.md       Multi-offer comparison
│   ├── company-research/         Per-company research files
│   └── job-search/               Tracker, outreach, salary
│
├── assets/                    ← Phase 2: Application materials
│   ├── star-stories.md           8 STAR behavioral stories
│   ├── questions-to-ask.md       Prepared interviewer questions
│   ├── form-fill-cheatsheet.md   Copy-paste job application answers (⚠️)
│   ├── testimonials.md           Social proof & endorsements
│   ├── linkedin-pack.md          LinkedIn profile optimization
│   ├── github-readme.md          GitHub profile README
│   ├── cover-letters/            3 named frameworks
│   ├── interview-prep/           Technical + behavioral prep
│   └── project-briefs/           Detailed project write-ups
│
├── personal/                  ← Phase 3: Private (never shared)
│   ├── about-me.md               Life story, values, strengths
│   ├── career-narrative.md       "Walk me through your career" script
│   ├── life-goals.md             Goals, non-negotiables, dream role
│   ├── reflections.md            Rejection learning & decision patterns
│   └── preferences.yaml          Work prefs, deal-breakers, life context
│
├── journal/                   ← Phase 3: Chronological logs
│   ├── wins.md                   Achievement log (brag document)
│   ├── learning-log.md           Courses, books, growth
│   ├── feedback.md               Performance reviews & feedback
│   └── work-log/                 Fiscal year logs + quarterly summaries
│
├── ops/                       ← System maintenance
│   ├── guide.md                  Session rules + maintenance rituals
│   ├── authority-map.md          Source of truth reference
│   ├── prompts.md                AI operation prompts
│   ├── audit-checklist.md        Template integrity audit
│   ├── tooling.md                Tool stack reference
│   └── templates/                Entry templates
│
└── .pramedha/                 ← Pramedha ecosystem
    ├── agent-instructions.md     How ANY AI fills this template
    ├── schema-reference.md       Field-by-field schema docs
    ├── import-guide.md           Import into Pramedha platform
    ├── validate.py               Template integrity validator
    └── examples/                 Example filled data
```

---

## Verification System

Every fact in this repo carries a verification tag:

| Tag | Meaning | Use In Resumes? |
|-----|---------|:---------------:|
| `✅ VERIFIED` | Evidence exists (cert, screenshot, doc) | ✅ Safe |
| `⚠️ ESTIMATED` | Reasonable but unverified | ⚠️ Use carefully |
| `❌ UNVERIFIED` | Aspiration or uncertain claim | ❌ Do not use |

This maps directly to Pramedha's `ClaimStatus` enum for import.

---

## For AI Assistants

If you're an AI helping fill this template, read `.pramedha/agent-instructions.md` first.
It contains the complete protocol for extracting, structuring, and verifying career data.

---

## Pramedha Integration (Optional)

This template is **fully standalone** — it works as a complete career operating system
without any external tools. Just fill the YAML/Markdown files with any AI assistant
or text editor.

If you also use the [Pramedha](https://github.com/bhaskarjha-dev/pramedha-template)
platform, this template's schema is designed for seamless integration:

```
identity/*.yaml     →  PramedhaProfile.professional
personal/*          →  PramedhaProfile.personal
claims-and-evidence →  PramedhaProfile.meta.claims_registry
```

The `Maps to:` comments throughout the template files document this mapping.
They are informational only — removing them has no effect on standalone usage.

---

## Security & Privacy

> 🔴 **Rule #1: Use a PRIVATE repository.**
> This template stores sensitive career data (salary, DOB, references, deal-breakers).
> A private repo is the only safe default.

> 🔴 **Rule #2: NEVER fork a public repo.**
> GitHub forks inherit the parent's visibility. A fork of a public repo **cannot be
> made private**. Use "Use this template" or clone instead (see Quick Start above).

### Sensitivity Map

| File/Folder | Contains | Public Repo Safe? |
|------------|----------|:-----------------:|
| `config.yaml` | Name, email, phone | ⚠️ Remove phone if public |
| `identity/` (most files) | Career facts | ✅ Yes (resume-level info) |
| `identity/references.yaml` | Contact details of references | ❌ **Never public** |
| `personal/` | Life context, salary, deal-breakers, reflections | ❌ **Never public** |
| `data-corpus/` | Raw evidence — certs, offer letters, IDs | ❌ **Never public** |
| `strategy/financial.md` | Current salary, targets | ❌ **Never public** |
| `strategy/networking.md` | Contact details, relationship notes | ❌ **Never public** |
| `assets/form-fill-cheatsheet.md` | DOB, address, phone, references | ❌ **Never public** |
| `journal/feedback.md` | Performance review data | ❌ **Never public** |
| `resume/output/` | Generated PDFs | ⚠️ Depends on content |

### If you MUST use a public repo

Uncomment the private file exclusions in `.gitignore`:
```bash
# In .gitignore, remove the # from these lines:
personal/
data-corpus/documents/
strategy/financial.md
strategy/networking.md
identity/references.yaml
assets/form-fill-cheatsheet.md
journal/feedback.md
```

---

## Validation

Check your template's integrity and fill status:

```bash
python .pramedha/validate.py            # Full validation
python .pramedha/validate.py --status   # Fill percentage only
python .pramedha/validate.py --strict   # Fail on warnings too
```

---

## Staying Updated

> GitHub's "Use this template" creates a **disconnected copy** — there's no
> upstream link. If the template adds new files, fixes bugs, or improves schemas,
> your copy won't know. Set up an upstream remote to pull updates.

### One-time setup (after creating your repo)

```bash
# Add the template as a secondary remote called "upstream"
git remote add upstream https://github.com/bhaskarjha-dev/pramedha-template.git

# Verify
git remote -v
# origin    git@github.com:YOU/my-career.git (your private repo)
# upstream  https://github.com/bhaskarjha-dev/pramedha-template.git (template)
```

### Pulling template updates

**Choose the right strategy based on your repo state:**

#### If you HAVEN'T filled your data yet (fresh template):

```bash
# Template is authoritative — accept all upstream changes
git fetch upstream
git merge upstream/main --allow-unrelated-histories -X theirs
```

#### If you HAVE filled your data (active career repo):

```bash
# 1. Fetch latest template changes
git fetch upstream

# 2. See what changed
git log --oneline upstream/main --not main

# 3. Merge (your filled data wins on conflicts)
git merge upstream/main --allow-unrelated-histories -X ours

# 4. Review what came in (new files, bug fixes)
git diff HEAD~1 --stat

# 5. Check for template improvements you might want to adopt manually
git diff upstream/main -- .pramedha/ ops/ resume/assemble.py
```

### Why two strategies?

| Your repo state | Strategy | Why |
|----------------|----------|-----|
| **Unfilled** (just created) | `-X theirs` | Template is authoritative — you have no data to protect |
| **Filled** (has your career data) | `-X ours` | Your data is authoritative — template can't overwrite your career facts |

### What merges cleanly vs. what conflicts

| Template Change | Your Filled Repo | Result |
|----------------|-----------------|--------|
| New file added (e.g., `assets/new-template.md`) | Doesn't exist | ✅ Auto-merges |
| Bug fix in `resume/assemble.py` | You didn't edit it | ✅ Auto-merges |
| Updated `ops/guide.md` | You didn't edit it | ✅ Auto-merges |
| New fields in `identity/skills.yaml` | You filled it with your data | ⚠️ `-X ours` keeps YOUR version |
| Updated `.pramedha/agent-instructions.md` | You didn't edit it | ✅ Auto-merges |

> **After merging with `-X ours`**, review what the template changed in files you've filled:
> ```bash
> git diff upstream/main -- identity/ personal/ strategy/
> ```
> Manually adopt any improvements (new fields, better comments) you want.

### Checking for updates without merging

```bash
git fetch upstream
git log --oneline upstream/main --not main
# Shows template commits you don't have yet
```

---

## License

MIT — Your career data is yours.
