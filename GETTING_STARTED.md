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
> Just **dump your career evidence into `data-corpus/`** and let AI fill the rest.
> The 3 files that matter most are auto-populated by AI from your evidence:
>
> 1. [config.yaml](config.yaml) — Who you are (extracted from resume header)
> 2. [identity/experience.yaml](identity/experience.yaml) — What you've done (extracted from resumes + LinkedIn)
> 3. [tools/resume/master.yaml](tools/resume/master.yaml) — Your resume bullet pool (synced from identity)
>
> Once these 3 files are filled, you already have an uninflated, single-source career engine. You can copy bullets directly into any resume builder, or let Python assemble them automatically. Every other file (strategy, stories, journal) can be adopted gradually when you need it.
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

## Step 1: Dump Raw Career Data (5 min)

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

> ⚠️ **Before you add anything:** read [what never goes here](data-corpus/README.md#never-put-these-here) (employer-confidential material, ID numbers, other people's data) and what your AI assistant sends to its provider.

**Don't have LinkedIn export?** Go to LinkedIn → Settings → Data Privacy → Get a copy of your data.

**Don't have certificates?** That's fine. Drop whatever you have. Even a phone photo of a certificate counts.

> 💡 **This is the only manual step.** Everything else is extracted by AI from what you dump here.

---

## Step 2: Let AI Fill Everything (15 min)

Copy this prompt into your AI assistant (Claude, Gemini, ChatGPT, Antigravity, Cursor, etc.):

```
Read the file .pramedha/agent-instructions.md in my career repository.
Then scan all files in data-corpus/ and fill ALL template files
following the 7-phase protocol (A through G). For each file:
- Auto-fill from data-corpus evidence (including config.yaml)
- Tag every claim with verification status (✅/⚠️/❌)
- Mark anything you drafted without evidence as <!-- AI-DRAFTED -->
- Leave empty what needs real-time user input (journal/, reflections)
```

The AI will fill **~40 files automatically**:
- ✅ `config.yaml` — extracted from your resume header + LinkedIn
- ✅ All `identity/` YAML files — from your raw data
- ✅ Resume master + variants — from identity
- ✅ STAR stories, interview prep, and professional summary variants
- ⚠️ Strategy files — drafted, needs your review
- ❌ Journal files — you fill these over time

> 💡 **Phased Execution Tip (Avoid Context Limits):** If your AI chat interface has token output constraints, ask it to fill in two stages:
> 1. **Stage 1:** Execute **Phase A & B** (scan `data-corpus/` → fill `config.yaml` + generate `identity/*.yaml` and `claims-and-evidence.md`). Review the facts.
> 2. **Stage 2:** Execute **Phase C through G** (generate resume variants, STAR stories, strategy, and platform copy from the verified identity).
>
> **No AI assistant?** Fill the identity files manually. Start with `config.yaml`, then `identity/experience.yaml` — the most important file.

---

## Step 3: Review & Write Your Mission (10 min)

After AI fills everything, review what it extracted:

1. **Check `config.yaml`** — Is your name, email, profession type correct?
2. **Check `identity/experience.yaml`** — Are dates, titles, and bullets accurate?
3. **Check `identity/claims-and-evidence.md`** — Do verification tags (✅/⚠️/❌) look right?
4. **Add private context** the AI couldn't know — salary targets in `strategy/financial.md`, deal-breakers in `personal/preferences.yaml`

Then write your career mission in `VISION.md`:

```markdown
**Priya Sharma** is a Software Engineer at Infosys transitioning to
a Senior Backend Engineer role within 6 months.
```

> This is YOUR north star. Be specific about what you want and by when.

---

## Step 4: Generate Your First Resume (5 min)

### Prerequisites

You need Python 3.12 or newer for PDFs (RenderCV 2.8 requires it); everything else also runs on 3.10 and 3.11.
Check with `python3 --version` (Windows: `py --version`). On macOS and Windows, python.org has installers; on Linux,
use your distribution's package (Ubuntu 24.04+, Debian 13+) or a tool such as pyenv or uv. On Debian/Ubuntu,
also run `sudo apt install python3-venv`. Then create the virtual environment once and install the pinned packages:
```bash
python3 -m venv .venv                       # Windows: py -m venv .venv
source .venv/bin/activate                   # macOS / Linux; again in every new terminal
# Windows PowerShell: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force; .venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate.bat
python -m pip install -r tools/resume/requirements.txt
```
Inside the virtual environment, `python` works on every OS.

### Resume Generation Workflow

After `identity/` is filled:

```bash
# 1. Sync verified career facts into the resume bullet pool:
python tools/resume/sync.py

# 2. Create a variant (copy the template, then select bullets in it):
cp tools/resume/variants/_template.yaml tools/resume/variants/my-role.yaml
# Windows: copy tools\resume\variants\_template.yaml tools\resume\variants\my-role.yaml

# 3. Check the references, then build the PDFs into tools/resume/output/:
python tools/resume/assemble.py --validate
bash tools/resume/build.sh                                        # macOS / Linux
powershell -ExecutionPolicy Bypass -File tools\resume\build.ps1   # Windows
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
| `data-corpus/` loaded | Raw evidence is stored permanently |
| `config.yaml` auto-filled | Your identity is defined (extracted by AI) |
| `identity/` filled | A verified career fact database |
| `VISION.md` written | Your career mission is clear |
| First resume generated | A tailored, ATS-ready PDF |

---

## What To Do Next (When You're Ready)

Fill these at your own pace. Each layer adds value independently:

### Week 1: Strategy
- [ ] `strategy/target-roles.md` — What roles are you targeting?
- [ ] `strategy/study-plan.md` — What skills gaps need filling?
- [ ] `strategy/financial.md` — What's your salary target?

### Week 2: Stories & Preparation
- [ ] `stories/star-stories.md` — Write 3-5 STAR stories for interviews
- [ ] `stories/interview-prep/behavioral.md` — Tailor behavioral talking points
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

## Step 5: External Tools (Optional)

Want to use AI-powered job search, scraping, or matching tools?

1. Browse available tools: `tools/external/README.md`
2. Clone or install any tool into `tools/external/`
3. Point your AI assistant at both your data AND the tool
4. The AI reads your YAML and feeds it to the tool

Example with career-ops:
```bash
cd tools/external/
git clone https://github.com/career-ops-hq/career-ops
# Then ask your AI: "Use career-ops to evaluate this JD against my profile"
```

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

> ⚠️ **Before pushing to GitHub**, make sure your repo is **Private**. Public repositories are not supported: CI fails in a public copy (job `privacy-guard`).

See `README.md → Security & Privacy` for the complete sensitivity map.

---

## Receiving Template Updates

Your repo is disconnected from the template. To receive future updates (new files,
bug fixes, schema improvements):

```bash
# One-time: add the template as upstream
git remote add upstream https://github.com/bhaskarjha-dev/pramedha-template.git

# One-time, if your copy has no tools/update_template.py yet (copies made before this update):
git fetch upstream
git checkout upstream/main -- tools/update_template.py tools/resume/requirements.txt
git commit -m "Add template update script"

# Each time (inside the virtual environment):
git fetch upstream
python tools/update_template.py    # replaces template-owned files only; your data is untouched
git diff --staged                  # review, then commit
```

See `README.md → Staying Updated` for the full guide with examples.
