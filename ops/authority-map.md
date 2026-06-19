# Source Authority Map

> **Purpose:** Prevents using stale data. When conflicting data exists,
> the AUTHORITATIVE SOURCE always wins.

---

## Authoritative Sources

| Topic | ✅ Authoritative Source | ❌ NOT a Source |
|-------|------------------------|----------------|
| **Name, email, phone, profiles** | `config.yaml` | identity.yaml, old resumes |
| **Demographics, languages, visa** | `identity/identity.yaml` | Old resumes, LinkedIn |
| **Work experience** | `identity/experience.yaml` | Old resume bullets |
| **Skills** | `identity/skills.yaml` | Inflated old resumes |
| **Projects & featured items** | `identity/projects.yaml` | Old project descriptions |
| **Education, certs, awards, orgs** | `identity/credentials.yaml` | Old CVs |
| **Volunteering / OSS** | `identity/volunteering.yaml` | Informal mentions |
| **References** | `identity/references.yaml` | Old reference lists |
| **Claims verification** | `identity/claims-and-evidence.md` | Resume bullets themselves |
| **Professional summary** | `identity/professional-summary.md` | Old LinkedIn about |
| **Resume bullets** | `resume/master.yaml` | Generated files, old YAMLs |
| **Resume design** | `resume/design.yaml` | Design blocks in variants |
| **Variant selection** | `resume/variants/*.yaml` | Manually curated files |
| **Generated YAMLs** | `resume/generated/*.yaml` | Auto-generated — DO NOT EDIT |
| **Network / contacts** | `strategy/networking.md` | Scattered address books |
| **Work preferences & life context** | `personal/preferences.yaml` | Assumptions |
| **Career mission** | `VISION.md` | Old plans, brainstorm docs |
| **Form-fill answers** | `assets/form-fill-cheatsheet.md` | Memory, old applications |

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
     ↓ cascade engine
resume/master.yaml (bullet pool)
     × resume/variants/ (overlays)
     = resume/generated/ (assembled)
     → resume/output/ (PDFs)
```
