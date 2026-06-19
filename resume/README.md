# Resume Cascade System

> **One source of truth → Multiple tailored resumes**

Edit your bullets in `master.yaml` once. Create thin overlay files in `variants/` to
select which bullets appear for each target role. Run `assemble.py` to generate
RenderCV-compatible YAML files. Render to PDF.

---

## How It Works

```
master.yaml          →  ALL your bullets, keyed by role + phrasing
  × variants/*.yaml  →  Thin overlays selecting bullets per target role
  = generated/*.yaml →  Complete RenderCV YAML files (auto-generated)
  → output/*.pdf     →  Final PDFs via `rendercv render`
```

---

## Quick Start

```bash
# 1. Fill master.yaml with your resume content
# 2. Create a variant for each target role
# 3. Assemble:
python assemble.py

# 4. Render PDFs:
pip install rendercv
rendercv render generated/Your_Name_Variant_CV.yaml
```

---

## File Reference

| File | Edit? | Purpose |
|------|:-----:|---------|
| `master.yaml` | ✏️ YES | All bullets with keyed phrasings |
| `design.yaml` | ✏️ YES | Visual theme (margins, fonts) |
| `variants/*.yaml` | ✏️ YES | Role-specific bullet selection |
| `assemble.py` | ❌ NO | Cascade engine (reads config.yaml) |
| `generated/*.yaml` | ❌ NO | Auto-generated. DO NOT EDIT. |
| `output/*.pdf` | ❌ NO | Rendered PDFs |

---

## Master YAML Structure

```yaml
# master.yaml — Keyed bullet pool
header:
  name: "Your Name"           # Auto-filled from ../config.yaml
  # ... contact info

experience:
  role_key:                    # Unique key for this role/position
    company: "Company Name"
    position: "Job Title"
    start_date: "2023-06"
    end_date: "present"
    location: "City, State"
    bullets:
      bullet_key:              # Unique key for this bullet
        default: "Full bullet text"
        short: "Shortened version"
        technical: "Tech-focused phrasing"
        # Add as many phrasings as needed per target audience
```

## Variant YAML Structure

```yaml
# variants/genai.yaml — Selects from master for GenAI roles
variant_name: "GenAI Engineer"
output_filename: "Your_Name_GenAI_CV"
summary: "One-paragraph summary for this variant"
experience:
  role_key:                    # Must match a key in master.yaml
    - [bullet_key, default]    # [key, phrasing] or just [key]
    - [other_bullet_key]       # Uses "default" phrasing
projects:
  - project_key               # Keys from master.yaml projects section
technologies:
  - label: "GenAI"
    details: "RAG, LLM APIs, ..."
```
