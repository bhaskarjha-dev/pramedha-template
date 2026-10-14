# Source Authority Map

> **Purpose:** Prevents using stale data. When conflicting data exists,
> the AUTHORITATIVE SOURCE always wins.

---

## Authoritative Sources

| Topic | ✅ Authoritative Source | ❌ NOT a Source |
|-------|------------------------|----------------|
| **Name, email, phone, profiles** | `identity/identity.yaml` (fallback: `config.yaml`) | Old resumes, LinkedIn |
| **Demographics, languages, visa** | `identity/identity.yaml` | Old resumes, LinkedIn |
| **Work experience** | `identity/experience.yaml` | Old resume bullets |
| **Skills** | `identity/skills.yaml` | Inflated old resumes |
| **Projects & featured items** | `identity/projects.yaml` | Old project descriptions |
| **Education, certs, awards, orgs** | `identity/credentials.yaml` | Old CVs |
| **Speaking, hackathons, events, communities** | `identity/speaking-and-community.yaml` | LinkedIn posts, event photos |
| **Volunteering / OSS** | `identity/volunteering.yaml` | Informal mentions |
| **References** | `identity/references.yaml` | Old reference lists |
| **Claims verification & debt** | `identity/claims-and-evidence.md` | Resume bullets themselves |
| **Professional summary** | `identity/professional-summary.md` | Old LinkedIn about |
| **Behavioral STAR story bank** | `stories/star-stories.md` | Memory, improvised interview answers |
| **Interview prep & talk tracks** | `stories/interview-prep/behavioral.md`, `technical.md` | Ad-hoc prep sheets, generic online lists |
| **Social proof & endorsements** | `stories/testimonials.md` | Scattered recommendation letters |
| **Resume bullets & phrasings** | `tools/resume/master.yaml` | Generated files, old YAMLs |
| **Resume design** | `tools/resume/design.yaml` | Design blocks in variants |
| **Variant selection** | `tools/resume/variants/*.yaml` | Manually curated files |
| **Generated YAMLs** | `tools/resume/generated/*.yaml` | Auto-generated — DO NOT EDIT |
| **Target roles, scoring & evaluation**| `strategy/target-roles.md` | Old role wish lists |
| **Application pipeline & tracker** | `strategy/job-tracker.md` | Scattered spreadsheets |
| **Compensation targets & runway** | `strategy/financial.md` | Guesses, recruiter-anchored numbers |
| **Offer evaluation & decision matrix** | `strategy/offer-comparison.md` | Mental math, impulsive decisions |
| **Learning roadmap & study sprints** | `strategy/study-plan.md` | Scattered study notes |
| **Network & contacts** | `strategy/networking.md` | Scattered address books |
| **Work preferences & life context** | `personal/preferences.yaml` | Assumptions |
| **Personal narrative & core identity** | `personal/about-me.md` | Public marketing copy |
| **Long-term life & personal vision** | `personal/life-goals.md` | Short-term task lists |
| **Career narrative & pivots** | `personal/career-narrative.md` | Scattered cover letters |
| **Private reflections & notes** | `personal/reflections.md` | Scattered journals |
| **Form-fill answers** | `personal/form-fill-cheatsheet.md` | Memory, old applications |
| **Shipped wins & achievements log** | `journal/wins.md` | Memory during annual reviews |
| **Course & learning log** | `journal/learning-log.md` | Forgotten course history |
| **Performance reviews & feedback** | `journal/feedback.md` | Scattered 1:1 notes |
| **Weekly work logs** | `journal/work-log/*.md` | Vague timesheets |
| **Career mission** | `VISION.md` | Old plans, brainstorm docs |
| **Session context & handoff** | `ops/session-handoff.md` | Old conversation transcripts |
| **Operations, maintenance & audit** | `ops/guide.md` | Ad-hoc maintenance notes |
| **External tools & third-party integrations** | `tools/external/README.md` | Ad-hoc tool clones |
| **Sub-project registry** | `VISION.md` (Sub-Projects section) | Scattered project folders |

---

## Evidence Hierarchy

```
1. Official document (cert, offer letter, scorecard)     ← HIGHEST
2. Screenshot / award record / email
3. Detailed work log (journal/work-log/)
4. Structured YAML (identity/)
5. Older resume
6. Brainstorming doc / freeform notes                    ← LOWEST
```

---

## Data Flow

```
data-corpus/ (raw evidence)
     ↓ AI extraction
identity/ (structured truth)
     ↓ cascade engine (tools/resume/)
tools/resume/master.yaml (bullet pool)
     × tools/resume/variants/ (overlays)
     = tools/resume/generated/ (assembled)
     → tools/resume/output/ (PDFs)

tools/external/ (mounted third-party tools)
     ↑ AI agents read identity/ and bridge to tools
```
