# Contributing to Pramedha Career Template

Thank you for helping make Pramedha the best career operating system template in the world.

Whether you're fixing a typo, refining a validator check, adding profession-specific examples, or proposing architectural improvements, we welcome thoughtful contributions.

---

## 🌟 Philosophy & Principles

Before submitting changes, please keep our core tenets in mind:

1. **Standalone-First:** The template must function completely without requiring external servers or proprietary tools. Plain YAML and Markdown files are first-class citizens.
2. **Anti-Inflation:** Never build features or prompts that encourage inflating credentials, skills, or metrics. Every claim must have an evidence path (✅ / ⚠️ / ❌).
3. **Single Source of Truth:** `identity/` is the authoritative source. Outward-facing materials (resumes, cover letters, platform bios) derive from identity — never the reverse.
4. **Privacy-First:** Deeply personal or sensitive financial numbers must never be exposed or co-mingled with public configuration files.
5. **Universal Relevance:** Avoid tech-only bias. The system is designed for professionals across all domains — engineering, healthcare, business, creative, academic, and non-linear careers.

---

## 🛠️ How to Contribute

### 1. Reporting Issues
- Search existing issues to ensure your bug or feature request isn't already documented.
- When filing a bug, include:
  - Your OS (Windows, macOS, Linux) and Python version (`python --version`)
  - The exact command you ran (e.g. `python resume/assemble.py --validate`)
  - Full traceback or error message
  - Which template version you cloned (see `CHANGELOG.md` or `.pramedha/manifest.yaml`)

### 2. Adding Profession-Specific Examples
We actively encourage domain experts to contribute examples to `.pramedha/examples/`:
- `skills-[domain].yaml`
- `experience-[domain].yaml`
Ensure examples are realistic, use standard industry terminology, and follow the verification tagging scheme.

### 3. Improving Scripts & Automation
When modifying `.pramedha/validate.py` or `resume/assemble.py`:
- Use standard library Python 3.10+ features with minimal external dependencies (`pyyaml` is permitted).
- Ensure scripts run cleanly cross-platform (Windows, macOS, Linux).
- Always include UTF-8 console safeguards (`sys.stdout.reconfigure(encoding='utf-8')`).
- Run the validator locally to confirm your changes pass:
  ```bash
  python .pramedha/validate.py
  python resume/assemble.py --validate
  ```

### 4. Proposing Schema Changes
If you propose adding or modifying fields:
- Update `.pramedha/schema-reference.md`
- Update `.pramedha/manifest.yaml`
- Update `ops/authority-map.md` if data ownership is affected
- Update `.pramedha/validate.py` if validation rules change
- Explain the rationale and backward compatibility considerations in your PR description.

---

## 📝 Pull Request Checklist

Before opening your pull request, verify:
- [ ] Code runs on Python 3.10+ without syntax or encoding errors
- [ ] `python .pramedha/validate.py` passes
- [ ] Cross-references between files remain consistent
- [ ] No personal or proprietary private data is included in commit history
- [ ] `CHANGELOG.md` includes a concise note under `[Unreleased]` or the upcoming version

Thank you for contributing to an open, empowering, and disciplined career ecosystem!
