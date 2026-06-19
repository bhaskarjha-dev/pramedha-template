# Importing Into Pramedha

> How to import a filled pramedha-template into the Pramedha platform.

---

## Prerequisites

- Pramedha installed (`pip install pramedha` or running via Docker)
- A filled pramedha-template (at minimum: config.yaml + identity/experience.yaml)

---

## Import Command

```bash
# Import from current directory
pramedha import --from ./

# Import from a specific path
pramedha import --from /path/to/my-career

# Import with dry-run (preview without saving)
pramedha import --from ./ --dry-run

# Import specific layers only
pramedha import --from ./ --layers professional
pramedha import --from ./ --layers professional,personal
```

---

## What Gets Imported

| Template File | → Pramedha Layer | Notes |
|--------------|-----------------|-------|
| `config.yaml` | `professional.identity` | Name, email, profession_type |
| `identity/identity.yaml` | `professional.identity` | Full contact + profiles |
| `identity/experience.yaml` | `professional.experience[]` | Work history + bullets |
| `identity/skills.yaml` | `professional.skills[]` | Auto-normalized to taxonomy |
| `identity/credentials.yaml` | `professional.education[]` + `certifications[]` + `awards[]` | Split into arrays |
| `identity/projects.yaml` | `professional.projects[]` | Public + internal |
| `identity/claims-and-evidence.md` | `meta.claims_registry[]` | Parsed from markdown table |
| `personal/preferences.yaml` | `personal.work_preferences` | Deal-breakers, values |
| `personal/life-goals.md` | `personal.career_goals` | Parsed from markdown |
| `resume/master.yaml` | *(used for artifact generation)* | Bullet phrasings preserved |

---

## What Stays Template-Only

These files are useful in the Git repo but don't import into Pramedha's database:

- `data-corpus/` — Raw evidence (Pramedha has its own intake pipeline)
- `strategy/` — Pramedha has its own tracker and strategy features
- `assets/` — Pramedha generates these from your profile
- `journal/` — Pramedha has its own journal system
- `ops/` — Template maintenance (not needed in platform)

---

## Export Back to Template

```bash
# Export your Pramedha profile back to a template repo
pramedha export --to /path/to/my-career

# This overwrites identity/*.yaml with latest profile data
# Preserves: data-corpus/, strategy/, journal/ (user-managed files)
```

---

## Sync Workflow

For users who maintain both a Git repo and Pramedha platform:

```
Edit in Pramedha → pramedha export → git commit → push
         OR
Edit YAML locally → git commit → pramedha import → verify
```

Pramedha uses `meta.version` (optimistic concurrency) to prevent conflicts.
