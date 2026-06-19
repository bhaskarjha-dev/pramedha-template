# Tooling Reference — Career System Stack

> **Purpose:** Tool stack for maintaining this career system.
> Update as you adopt/drop tools.

---

## Core Stack

| Tool | Purpose | Status |
|------|---------|:------:|
| **Git** | Version control for all career data | ✅ Required |
| **RenderCV** | Resume rendering from YAML → PDF | ✅ Required |
| **assemble.py** | Resume cascade engine (master → variants) | ✅ Included |
| **VS Code / Editor** | Primary editor for YAML/MD files | ✅ Required |
| **Python 3.10+** | Running assemble.py and validate.py | ✅ Required |

---

## Resume Pipeline

```
identity/*.yaml → resume/master.yaml → assemble.py → generated/*.yaml → RenderCV → PDFs
                  resume/design.yaml ↗
                  resume/variants/*.yaml ↗
```

| Component | Tool | Notes |
|-----------|------|-------|
| Career data | `identity/*.yaml` | Source of truth |
| Resume bullets | `resume/master.yaml` | Keyed bullets with phrasing variants |
| Design config | `resume/design.yaml` | Shared fonts, margins, spacing |
| Variant overlays | `resume/variants/*.yaml` | Per-role bullet selection |
| Cascade engine | `resume/assemble.py` | Validates + assembles |
| Renderer | RenderCV | `pip install rendercv` |
| Build scripts | `resume/build.ps1` / `build.sh` | Full pipeline |
| Output | `resume/output/*.pdf` | ATS-friendly PDFs |

---

## Job Search Platforms

| Platform | Purpose | Region |
|----------|---------|--------|
| LinkedIn | Primary search + networking | Global |
| Indeed | High volume listings | Global |
| Glassdoor | Reviews + salary data | Global |
| <!-- Add platforms for your region --> | | |

---

## Learning & Prep

| Tool | Purpose |
|------|---------|
| Anki (desktop + mobile) | Spaced repetition for interview prep |
| LeetCode / NeetCode | Coding practice |
| Pramp / Interviewing.io | Mock interviews |
| <!-- Add your learning tools --> | |

---

## Content & Publishing

| Platform | Purpose |
|----------|---------|
| Medium / Dev.to | Technical blog |
| LinkedIn Articles | Native content |
| GitHub | Portfolio + open source |
| <!-- Add your platforms --> | |

---

## Infrastructure

| Tool | Purpose |
|------|---------|
| GitHub / GitLab | Code hosting for projects |
| Cloud provider | Deployment for portfolio projects |
| Personal domain | Portfolio website |
