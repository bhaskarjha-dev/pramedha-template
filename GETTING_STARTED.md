# Getting Started — Your First 30 Minutes

> **You just got this template. Here's exactly what to do, step by step.**
> Don't try to fill everything at once. This guide gets you a working career system in 30 minutes.

---

## Step 0: Create Your Private Repo (2 min)

> ⚠️ **DO NOT FORK.** GitHub forks of public repos cannot be made private.
> Your salary, DOB, references, and career strategy would be exposed.

**Option A (Recommended):** On the template repo page, click **"Use this template"** →
**"Create a new repository"** → name it `my-career` → set to **Private** ✅ → clone locally.

**Option B:** Clone + disconnect:
```bash
git clone https://github.com/bhaskarjha-dev/pramedha-template my-career
cd my-career
git remote remove origin
# Create a private repo on GitHub, then:
git remote add origin git@github.com:YOUR-USERNAME/my-career.git
git push -u origin main
```

---

## ⚡ Fast Track: Minimal Viable Career System (Just 3 Files)

> **Feeling intimidated by 60+ files? You don't need to fill everything!**
> Most career changers and job seekers only need **3 core files** to get 80% of the value:
>
> 1. [config.yaml](config.yaml) — Who you are (name, contact, profession type)
> 2. [identity/experience.yaml](identity/experience.yaml) — What you've done (career facts and measured achievements)
> 3. [tools/resume/master.yaml](tools/resume/master.yaml) — Your resume bullet pool
>
> Once these 3 files are filled, you already have an uninflated, single-source career engine. You can copy bullets directly into any resume builder, or let Python assemble them automatically. Every other file (strategy, assets, journal) can be adopted gradually when you need it.
>
> 💡 **Pivoting or Career Changer?**
> If you're switching domains (e.g., non-tech → tech, clinical → healthtech, military/law → corporate):
> - Focus on **transferable outcomes** in [identity/experience.yaml](identity/experience.yaml) (leadership, stakeholder management, optimization).
> - Showcase self-directed proof (portfolio projects, open-source, case studies) in [identity/projects.yaml](identity/projects.yaml).
> - Map out your transition story in [personal/career-narrative.md](personal/career-narrative.md) before applying.
>
> 🚀 **Applying to Jobs Right Away?**
> Keep [personal/form-fill-cheatsheet.md](personal/form-fill-cheatsheet.md) open in a side window. It centralizes your standard URLs, address formats, visa details, and recurring application question answers so you can breeze through lengthy ATS forms (Workday, Greenhouse, Lever) without repetitive typing.

---

## Step 1: Fill `config.yaml` (3 min)

Open `config.yaml` and fill in your basic identity:

```yaml
user:
  name: "Your Full Name"
  email: "you@example.com"
  phone: "+1-555-0100"
  headline: "Software Engineer | Your Specialization"

profession_type: "engineering"    # or: creative, medical, business, academic, legal

location:
  city: "San Francisco"           # or your city
  country_code: "US"              # ISO code (US, IN, GB, DE, etc.)
```

> **Don't overthink it.** You can change everything later. Just get the basics in.

---

## Step 2: Write Your Mission in `VISION.md` (2 min)

Open `VISION.md` and replace the `[brackets]` with your actual information:

```markdown
**Priya Sharma** is a Software Engineer at Infosys transitioning to
a Senior Backend Engineer role within 6 months.
```

> This is YOUR north star. Be specific about what you want and by when.

---

## Step 3: Dump Raw Career Data (5 min)

Drop everything career-related into `data-corpus/`:

| What You Have | Where To Put It |
|--------------|----------------|
| Old resumes (PDF/DOCX) | `data-corpus/resumes/` |
| Certificates, degrees, awards | `data-corpus/documents/` |
| LinkedIn data export (ZIP / CSVs) | `data-corpus/linkedin/` |
| GitHub profile / repository exports | `data-corpus/github/` |
| Other data archives & exports | `data-corpus/exports/` |
| Brain dumps, career notes | `data-corpus/text/` |
| Screenshots of projects/metrics | `data-corpus/media/` |

**Don't have LinkedIn export?** Go to LinkedIn → Settings → Data Privacy → Get a copy of your data.

**Don't have certificates?** That's fine. Drop whatever you have. Even a phone photo of a certificate counts.

---

## Step 4: Let AI Fill Everything (15 min)

Copy this prompt into your AI assistant (ChatGPT, Gemini, Claude, etc.):

```
Read the file .pramedha/agent-instructions.md in my career repository.
Then scan all files in data-corpus/ and fill ALL template files
following the 7-phase protocol (A through G). For each file:
- Auto-fill from data-corpus evidence
- Tag every claim with verification status (✅/⚠️/❌)
- Mark anything you drafted without evidence as <!-- AI-DRAFTED -->
- Leave empty what needs real-time user input (journal/, reflections)
```

The AI will fill **~40 files automatically**:
- ✅ All identity/ YAML files (from your raw data)
- ✅ Resume master + variants (from identity)
- ✅ STAR stories, cover letters, LinkedIn pack (from experience)
- ⚠️ Strategy files (drafted, needs your review)
- ❌ Journal files (you fill these over time)

> 💡 **Phased Execution Tip (Avoid Context Limits):** If your AI chat interface has token output constraints, ask it to fill in two stages:
> 1. **Stage 1:** Execute **Phase A & B** (scan `data-corpus/` → generate `identity/*.yaml` and `claims-and-evidence.md`). Review the facts.
> 2. **Stage 2:** Execute **Phase C through G** (generate resume variants, STAR stories, strategy, and platform copy from the verified identity).
>
> **No AI assistant?** Fill the identity files manually. Start with `identity/experience.yaml` — it's the most important file.

---

## Step 5: Generate Your First Resume (5 min)

### Prerequisites

Ensure you have Python 3.10+ and the required packages installed:
```bash
pip install pyyaml rendercv
```

### Resume Generation Workflow

After `identity/` is filled:

```bash
# Option A (Windows PowerShell 1-Click):
.\tools\resume\build.ps1

# Option B (Manual CLI in any terminal):
# 1. Sync verified career facts into master resume bullet pool:
py tools/resume/sync.py

# 2. Create a tailored variant overlay (copy template):
cp tools/resume/variants/_template.yaml tools/resume/variants/my-role.yaml
# Edit my-role.yaml to select which bullets to include

# 3. Assemble and render PDF:
py tools/resume/assemble.py --validate    # Verify all references
py tools/resume/assemble.py               # Assembles to tools/resume/generated/
rendercv render tools/resume/generated/my-role.yaml -o ../output
# (Or simply run .\tools\resume\build.ps1 on Windows / ./tools/resume/build.sh on Linux/Mac)
# (On Windows PowerShell if encoding errors occur: $env:PYTHONUTF8 = "1")
# Your PDF is compiled in tools/resume/output/ in <1s via Typst (no LaTeX needed!)
```

> 💡 **Modern Workflows & Web Preview:**
> - **Web App:** Prefer a browser GUI? Upload your assembled YAML from `tools/resume/generated/` to [rendercv.com](https://rendercv.com) for instant live rendering and visual adjustments.
> - **AI Agent Skill:** Using Claude Code, Cursor, or AGY agents? Run `npx skills add rendercv/rendercv-skill` so your AI has official AST-verified schema knowledge.
> - **No Python?** The `identity/` data and markdown assets are completely standalone and work with any resume builder.

---

## What You Now Have

After 30 minutes, you have:

| ✅ What's Done | What It Gets You |
|---------------|-----------------|
| `config.yaml` filled | Your identity is defined |
| `VISION.md` written | Your career mission is clear |
| `data-corpus/` loaded | Raw evidence is stored permanently |
| `identity/` filled | A verified career fact database |
| First resume generated | A tailored, ATS-ready PDF |

---

## What To Do Next (When You're Ready)

Fill these at your own pace. Each layer adds value independently:

### Week 1: Strategy
- [ ] `strategy/target-roles.md` — What roles are you targeting?
- [ ] `strategy/study-plan.md` — What skills gaps need filling?
- [ ] `strategy/financial.md` — What's your salary target?

### Week 2: Assets
- [ ] `stories/star-stories.md` — Write 3-5 STAR stories for interviews
- [ ] `stories/interview-prep/behavioral.md` — Customize the cover letter template
- [ ] `personal/form-fill-cheatsheet.md` — Pre-fill common application fields

### Week 3: Personal (Private)
- [ ] `personal/about-me.md` — Your life story and values
- [ ] `personal/life-goals.md` — What does success look like?
- [ ] `personal/preferences.yaml` — Deal-breakers and work preferences

### Ongoing: Journal
- [ ] `journal/wins.md` — Log every achievement as it happens
- [ ] `journal/work-log/` — Weekly work log
- [ ] `journal/learning-log.md` — Track courses and skills development

---

## Need Help?

| Question | Where To Look |
|---------|--------------|
| "How do I fill a specific file?" | `.pramedha/agent-instructions.md` |
| "What fields does each file have?" | `.pramedha/schema-reference.md` |
| "What's an example of a filled template?" | `.pramedha/examples/` |
| "What AI prompts can I use?" | `ops/prompts.md` |
| "What's the source of truth for X?" | `ops/authority-map.md` |
| "How do I maintain this system?" | `ops/guide.md` |
| "What tools do I need?" | `ops/guide.md` (Tool Stack section) |

---

## Privacy Reminder

> ⚠️ **Before pushing to GitHub**, ensure your repo is **Private**.
> If it must be public, uncomment the private file exclusions in `.gitignore`.
> ```bash
> git status  # Verify personal/, financial.md, etc. are NOT staged
> ```

See `README.md → Security & Privacy` for the complete sensitivity map.

---

## Receiving Template Updates

Your repo is disconnected from the template. To receive future updates (new files,
bug fixes, schema improvements):

```bash
# One-time: add the template as upstream
git remote add upstream https://github.com/bhaskarjha-dev/pramedha-template.git

# When you want to check for updates:
git fetch upstream
git log --oneline upstream/main --not main   # See what's new

# Pull updates:
#   Fresh/unfilled template → use -X theirs (template wins)
#   Filled with your data  → use -X ours   (your data wins)
git merge upstream/main --allow-unrelated-histories -X theirs  # or -X ours
```

See `README.md → Staying Updated` for the full guide with examples.
