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

## Step 1: Fill `config.yaml` (3 min)

Open `config.yaml` and fill in your basic identity:

```yaml
user:
  name: "Your Full Name"
  email: "you@example.com"
  phone: "+91-9876543210"
  headline: "Software Engineer | Your Specialization"

profession_type: "engineering"    # or: creative, medical, business, academic, legal

location:
  city: "Bangalore"
  country_code: "IN"
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
| LinkedIn export, GitHub JSON | `data-corpus/exports/` |
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

> **No AI assistant?** Fill the identity files manually. Start with `identity/experience.yaml` — it's the most important file.

---

## Step 5: Generate Your First Resume (5 min)

After identity/ is filled:

```bash
# 1. Fill resume/master.yaml with your best bullets
#    (AI can do this from experience.yaml)

# 2. Create a variant
cp resume/variants/_template.yaml resume/variants/my-role.yaml
# Edit my-role.yaml to select which bullets to include

# 3. Generate
cd resume
python assemble.py
rendercv render generated/my-role.yaml
# Your PDF is in resume/output/
```

> **Don't have RenderCV?** Install it: `pip install rendercv`
> **Don't have Python?** Skip this step — the identity/ data is still valuable on its own.

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
- [ ] `assets/star-stories.md` — Write 3-5 STAR stories for interviews
- [ ] `assets/cover-letters/standard.md` — Customize the cover letter template
- [ ] `assets/form-fill-cheatsheet.md` — Pre-fill common application fields

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
| "What tools do I need?" | `ops/tooling.md` |

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
