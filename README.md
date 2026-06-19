# Pramedha Career Template

> **Your career data — portable, version-controlled, AI-readable, and yours.**

A structured career repository that works standalone (generate resumes immediately) or as the data layer for [Pramedha](https://github.com/pramedha) — the AI-first career platform.

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
| Import into Pramedha | Get AI matching, portfolio generation, and career intelligence |

---

## Quick Start

**→ [Read GETTING_STARTED.md](GETTING_STARTED.md) for the full 30-minute walkthrough.**

```bash
# 1. Clone this template
git clone https://github.com/pramedha/pramedha-template my-career
cd my-career

# 2. Fill config.yaml with your name + basics
# 3. Dump raw career data into data-corpus/
# 4. Let AI fill the rest (see .pramedha/agent-instructions.md)
# 5. Generate resumes:
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

## Pramedha Compatibility

This template's schema aligns 1:1 with [PramedhaProfile](https://github.com/pramedha):

```
identity/*.yaml     →  PramedhaProfile.professional
personal/*          →  PramedhaProfile.personal
claims-and-evidence →  PramedhaProfile.meta.claims_registry
```

Import: `pramedha import --from ./my-career`
Export: `pramedha export --to ./my-career`

---

## Security & Privacy

> ⚠️ **Before making this repo public**, review these rules:

| File/Folder | Contains | Public Repo Safe? |
|------------|----------|:-----------------:|
| `config.yaml` | Name, email, phone | ⚠️ Remove phone if public |
| `identity/` (most files) | Career facts | ✅ Yes (resume-level info) |
| `identity/references.yaml` | Contact details of references | ❌ **Never public** |
| `personal/` | Life context, salary, deal-breakers, reflections | ❌ **Never public** |
| `data-corpus/documents/` | Offer letters, tax docs, IDs | ❌ **Never public** |
| `strategy/financial.md` | Current salary, targets | ❌ **Never public** |
| `strategy/networking.md` | Contact details, relationship notes | ❌ **Never public** |
| `assets/form-fill-cheatsheet.md` | DOB, address, phone, references | ❌ **Never public** |
| `journal/feedback.md` | Performance review data | ❌ **Never public** |
| `resume/output/` | Generated PDFs | ⚠️ Depends on content |

**If your repo is public**, uncomment the private file exclusions in `.gitignore`:
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

## Use as GitHub Template

1. Push this repo to GitHub
2. Go to Settings → check "Template repository"
3. Others can click "Use this template" to create their own copy

---

## License

MIT — Your career data is yours.
