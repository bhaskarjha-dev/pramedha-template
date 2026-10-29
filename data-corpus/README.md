# Data Corpus — Your Career Evidence Locker

> **This is the fuel for your entire career system.**
> The more you dump here, the better AI fills your template.
> Even "useless" old files often contain gold (dates, titles, metrics).

---

## Never put these here

- Employer-confidential or internal material: internal documents, wikis, code, RFCs, database schemas,
  dashboards or screenshots of internal systems, customer or colleague data. Describe your work in your
  own words in `text/` instead.
- Government ID scans or numbers (passport, national ID, social security), bank details, payslips.
- Passwords, API keys, tokens.
- Other people's contact details, messages or connection lists, unless they agreed to be your reference.

## What your AI assistant sends

When an AI assistant reads these files, their contents go to that assistant's provider under its terms
(retention, training, human review). Check those terms and your employer's AI policy before you start,
and leave out anything you would not paste into that assistant yourself.

---

## The 8-Folder System

Drop files into the folder that fits. Don't overthink it — wrong folder is
better than not captured at all.

```
data-corpus/
├── inbox/        ← Unsorted intake landing zone (drop raw files here first)
├── resumes/      ← Every resume/CV version you've ever made (PDF, Word, LaTeX)
├── documents/    ← Certificates, degrees, reviews, offer letters, official papers
├── exports/      ← Generic platform data exports (Naukri, Indeed, Kaggle, etc.)
├── linkedin/     ← LinkedIn profile archive and data export files
├── github/       ← GitHub repositories archive and commit metrics
├── text/         ← Brain dumps, notes, transition plans, raw descriptions
└── media/        ← Screenshots of metrics, slides, photos, demo recordings
```

---

## Master Collection Checklist

> **Priority guide:**
> 🔴 **Critical** — Without this, AI can't fill the template accurately
> 🟡 **Important** — Significantly improves quality
> 🟢 **Nice to have** — Adds depth and polish

### 1. Digital Footprint → `exports/`, `linkedin/`, `github/`

Export and download from every platform where you have a professional presence.

| Item | Priority | Destination | How To Get It |
|------|:--------:|:-----------:|---------------|
| LinkedIn export of your own profile | 🔴 | `linkedin/` | Settings → Data privacy → Get a copy of your data → pick Profile, Positions, Education, Skills, Certifications, Honors, Projects, Publications, Recommendations received (not messages or connections) |
| GitHub repos list + contribution graph | 🔴 | `github/` | Settings → Archives → Export account data |
| Naukri / Indeed profile export | 🔴 | `exports/` | Settings → Download profile |
| HuggingFace profile, models, datasets | 🟡 | `exports/` | Screenshot profile + copy model cards |
| Kaggle profile, notebooks, competitions | 🟡 | `exports/` | Screenshot profile + export notebooks |
| Stack Overflow profile + top answers | 🟡 | `exports/` | Copy profile page + top answers |
| Dev.to / Hashnode / Medium articles list | 🟡 | `exports/` | Export or screenshot article list |
| PyPI / npm packages published | 🟡 | `exports/` | Screenshot package pages |
| Twitter/X professional threads | 🟢 | `exports/` | Screenshot or copy thread text |
| Discord/Slack community contributions | 🟢 | `exports/` | Screenshots of notable contributions |
| JSON Resume (if you have one) | 🟢 | `exports/` | Copy the JSON file |

### 2. Prior Resumes & CVs → `resumes/`

Every resume version and CV draft you've ever compiled.

| Item | Priority | Destination | Why It Matters |
|------|:--------:|:-----------:|---------------|
| **Every resume version** — all drafts, oldest to newest | 🔴 | `resumes/` | Shows career progression, catches forgotten roles |
| LaTeX, Typst, Word, or Markdown source files | 🔴 | `resumes/` | Raw text extraction for master bullet pool |

### 3. Career Documents → `documents/`

Every piece of official paperwork. Even expired ones are useful for timeline reconstruction.

| Item | Priority | Destination | Why It Matters |
|------|:--------:|:-----------:|---------------|
| Performance reviews from all employers | 🔴 | `documents/` | Verified metrics + manager assessment of your skills |
| Reference & recommendation letters | 🔴 | `documents/` | Third-party validation of your claims |
| All course/certification certificates | 🔴 | `documents/` | Credential IDs, dates, verification URLs |
| Award citations & recognition documentation | 🔴 | `documents/` | Evidence for claims-and-evidence.md |
| Degree certificates & academic transcripts | 🔴 | `documents/` | Education verification |
| Hackathon & competition result certificates | 🟡 | `documents/` | Project evidence + awards |
| Offer letters (show title & compensation progression) | 🟡 | `documents/` | Timeline + financial.md data |
| Experience letters & relieving letters | 🟡 | `documents/` | Employment date verification |
| Cover letters you've written in the past | 🟡 | `documents/` | Reveals how YOU frame your narrative |
| Patent filings or IP disclosures | 🟡 | `documents/` | If applicable |
| Publications, preprints, co-authored papers | 🟡 | `documents/` | If applicable |

### 4. Project Artifacts → `documents/` or `media/`

Tangible evidence of your actual work. This is what turns "I built X" into a verified claim.

| Item | Priority | Where |
|------|:--------:|:-----:|
| Your own notes describing work you did (no copies of employer documents, code, data or internal screenshots) | 🔴 | `text/` |
| Architecture diagrams of public or personal projects | 🔴 | `media/` |
| Slides you presented publicly (conference, meetup, course) | 🟡 | `documents/` |
| Screen recordings of public or personal projects | 🔴 | `media/` |
| Screenshots of public products or personal projects (no internal dashboards or systems) | 🔴 | `media/` |

### 5. Social Proof → `documents/` or `text/`

What OTHER people say about your work. The most powerful evidence category.

| Item | Priority | Where |
|------|:--------:|:-----:|
| LinkedIn recommendations — full text | 🔴 | `text/` (copy-paste all) |
| Written manager/skip-level performance feedback | 🔴 | `documents/` |
| Thank-you notes about your work, with names and contact details removed | 🟡 | `text/` |
| Client or stakeholder testimonials | 🔴 | `text/` |
| GitHub stars, forks, watchers per repo | 🔴 | `exports/` (screenshot) |
| Peer feedback about you, in your own summary (no names) | 🟡 | `text/` |
| Media, press, or newsletter mentions | 🟡 | `text/` (links + quotes) |
| Podcast or panel appearances | 🟡 | `text/` (links + descriptions) |
| Community shoutouts | 🟢 | `text/` |

### 6. Content You've Created → `text/` or `documents/`

Everything you've written, taught, or presented. Shows expertise depth.

| Item | Priority | Where |
|------|:--------:|:-----:|
| All published blog posts (every platform) | 🔴 | `text/` (links + copy) |
| Open source contributions outside your own repos | 🔴 | `text/` (PR links + descriptions) |
| Conference or meetup talk slides | 🔴 | `documents/` |
| Technical articles or explainers | 🔴 | `text/` |
| Workshop or tutorial materials | 🟡 | `documents/` |
| Internal onboarding guides you authored | 🟡 | `text/` |
| Long-form LinkedIn/Twitter technical threads | 🟡 | `text/` |
| Video tutorials, screencasts, YouTube content | 🟢 | `media/` (or links in `text/`) |

### 7. Impact Numbers → `text/`

Every measurable outcome. If you don't have exact numbers, write your best estimates — AI will tag them as `[estimated]`.

| Item | Priority | Example |
|------|:--------:|---------|
| Users, customers, or teams served per project | 🔴 | "Served 50K daily users" |
| Performance improvements (speed, accuracy, etc.) | 🔴 | "Reduced latency from 2s to 200ms" |
| Revenue generated or directly influenced | 🔴 | "Generated $2M / ₹2Cr pipeline" |
| Cost or time savings achieved | 🔴 | "Saved 40 engineering hours/week" |
| Scale: requests/day, data volume, API calls | 🔴 | "Processed 10M records daily" |
| Team size led or coordinated | 🟡 | "Led 5-person team" |
| Error rate reductions | 🟡 | "Reduced bug rate by 60%" |
| Download/usage counts for published packages | 🟡 | "2K downloads/month on PyPI" |

> **💡 Tip:** Create a file called `text/impact-numbers.md` and just brain-dump
> every number you can remember. Even rough estimates are valuable — AI will
> cross-reference them against your resume bullets.

### 8. Visual Assets → `media/`

Images, recordings, and design files. These feed into portfolio and project briefs.

| Item | Priority |
|------|:--------:|
| Professional headshot (high resolution) | 🔴 |
| Demo recordings of public or personal projects | 🔴 |
| Demo GIFs of working features or outputs | 🔴 |
| Architecture diagram exports (PNG/SVG) | 🔴 |
| Screenshots of public or personal projects (no internal dashboards) | 🔴 |
| Speaking or event photos | 🟡 |
| Certificate scans or photos | 🟡 |
| Award or recognition photos | 🟢 |

### 9. The Hidden Interview → `text/`

> ⭐ **This is the most missed source.** The answers below contain context
> that NO document captures — your motivations, thinking process, and self-awareness.
> Create a file `text/hidden-interview.md` and answer these.

| Question | Priority |
|----------|:--------:|
| Why did you choose your field? (The REAL story, not the polished version) | 🔴 |
| What's the proudest technical achievement of your career? | 🔴 |
| What's the hardest technical problem you've ever solved? | 🔴 |
| What projects were significant but never reached GitHub/public? | 🔴 |
| What do 3 colleagues who know you well say you're uniquely great at? | 🔴 |
| What's your exact mental process when approaching a new problem? | 🔴 |
| What specifically excites you about your target role/domain? | 🔴 |
| What failure or mistake did you learn the most from? | 🔴 |
| What are your unfair advantages? (background, cross-domain skills, perspective) | 🔴 |
| What are your technical principles in 3 sentences? | 🔴 |
| What companies or roles are you specifically targeting? (even if not public) | 🔴 |
| What are you actively learning right now and why? | 🟡 |
| What's your preferred work environment and collaboration style? | 🟡 |

### 10. Domain-Specific Sources → varies

If your field has specialized platforms, add those too:

**For AI/ML Engineers:**
- HuggingFace Spaces (deployed demos)
- Fine-tuning work: base model, dataset, eval metrics
- RAG pipeline implementations with performance data
- Agentic system architectures designed and shipped
- Prompt engineering frameworks or systems built
- Model comparison benchmarks you've run
- Datasets you've created, curated, or annotated

**For Web/Software Engineers:**
- Deployed application URLs with screenshots
- npm/PyPI package download stats
- Open source contribution history
- Code review feedback received

**For Designers:**
- Dribbble/Behance portfolio links
- Case study documents
- User research findings
- Before/after design comparisons

**For Academics:**
- Google Scholar profile export
- Citation counts and h-index
- Grant proposals (funded and unfunded)
- Thesis/dissertation
- Teaching evaluations

---

## Quality Checklist

Before telling AI to fill, check:

- [ ] At least 1 resume version in `resumes/`
- [ ] LinkedIn export in `linkedin/` (or `exports/`)
- [ ] All certificates you can find in `documents/`
- [ ] `text/hidden-interview.md` answered (even partially)
- [ ] At least 3 impact numbers captured somewhere in `text/`
- [ ] At least 2 screenshots of your work in `media/`

> **80% rule:** You don't need everything. 80% of the template quality
> comes from: resumes + LinkedIn export + hidden interview + impact numbers.
> Start there.

---

## How AI Processes This

1. AI reads ALL files in `data-corpus/`
2. Extracts facts: names, dates, roles, skills, achievements
3. Cross-references across sources for accuracy
4. Fills `identity/*.yaml` with structured, verified data
5. Tags each fact with verification status (✅/⚠️/❌)
6. Notes contradictions (different dates in resume vs LinkedIn)
7. Generates interview prep, STAR stories, and summary variants from extracted facts

**Your raw data stays here as evidence.** It's never deleted.
The `identity/` folder becomes the structured, authoritative extraction.

---

## Ready to Extract?

Once you've dumped your files, paste this prompt into your AI assistant:

```
Read the file .pramedha/agent-instructions.md in my career repository.
Then scan all files in data-corpus/ and fill ALL template files
following the 7-phase protocol (A through G). Tag every claim with
verification status. Mark AI-drafted content. Leave journal files empty.
```

Or see `.pramedha/agent-instructions.md` for the full 28-step protocol (Steps 0–27).
