#!/usr/bin/env python3
"""
Pramedha Template Validator — Checks template integrity and fill status.

Usage:
    python validate.py                # Full validation
    python validate.py --status       # Show fill status only
    python validate.py --strict       # Fail on warnings too
"""

import argparse
import datetime
import re
import sys
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install: pip install pyyaml")
    sys.exit(1)


# ============================================================================
# Configuration
# ============================================================================

TEMPLATE_ROOT = Path(__file__).parent.parent  # pramedha-template/

REQUIRED_FILES = [
    "config.yaml",
    "identity/identity.yaml",
    "identity/experience.yaml",
    "identity/skills.yaml",
    "identity/credentials.yaml",
    "identity/projects.yaml",
    "identity/speaking-and-community.yaml",
    "identity/volunteering.yaml",
    "identity/references.yaml",
    "identity/claims-and-evidence.md",
    "identity/professional-summary.md",
    "resume/master.yaml",
    "resume/design.yaml",
    "resume/assemble.py",
    "resume/sync.py",
]

OPTIONAL_FILES = [
    "personal/about-me.md",
    "personal/life-goals.md",
    "personal/preferences.yaml",
    "personal/career-narrative.md",
    "personal/reflections.md",
    "strategy/target-roles.md",
    "strategy/master-action-tracker.md",
    "strategy/digital-presence-plan.md",
    "strategy/study-plan.md",
    "strategy/financial.md",
    "strategy/weekly-tracker.md",
    "assets/star-stories.md",
    "assets/linkedin-pack.md",
    "assets/platform-copy.md",
    "assets/form-fill-cheatsheet.md",
    "journal/wins.md",
    "journal/learning-log.md",
    "journal/feedback.md",
]

YAML_FILES_TO_VALIDATE = [
    "config.yaml",
    "identity/identity.yaml",
    "identity/experience.yaml",
    "identity/skills.yaml",
    "identity/credentials.yaml",
    "identity/projects.yaml",
    "identity/speaking-and-community.yaml",
    "identity/volunteering.yaml",
    "identity/references.yaml",
    "personal/preferences.yaml",
    "resume/master.yaml",
    "resume/design.yaml",
]


# ============================================================================
# Validators
# ============================================================================

class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def note(self, msg):
        self.info.append(msg)

    @property
    def passed(self):
        return len(self.errors) == 0


def check_file_exists(result: ValidationResult):
    """Check that all required files exist."""
    for f in REQUIRED_FILES:
        path = TEMPLATE_ROOT / f
        if not path.exists():
            result.error(f"Missing required file: {f}")
        else:
            result.note(f"✅ {f}")

    for f in OPTIONAL_FILES:
        path = TEMPLATE_ROOT / f
        if not path.exists():
            result.warn(f"Optional file missing: {f}")


def check_yaml_valid(result: ValidationResult):
    """Check that all YAML files parse without errors."""
    for f in YAML_FILES_TO_VALIDATE:
        path = TEMPLATE_ROOT / f
        if not path.exists():
            continue
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                data = yaml.safe_load(fh)
            if data is None:
                result.warn(f"{f}: File is empty (no data)")
        except yaml.YAMLError as e:
            result.error(f"{f}: YAML parse error — {e}")


def check_config(result: ValidationResult):
    """Validate config.yaml has minimum required fields."""
    path = TEMPLATE_ROOT / "config.yaml"
    if not path.exists():
        return

    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f) or {}

    user = config.get('user', {}) or {}
    name = (user.get('name') or '').strip()
    email = (user.get('email') or '').strip()

    if not name:
        result.warn("config.yaml: user.name is empty")
    if not email:
        result.warn("config.yaml: user.email is empty")

    profession = (config.get('profession_type') or '').strip()
    if not profession:
        result.warn("config.yaml: profession_type is empty")


def check_experience(result: ValidationResult):
    """Validate experience.yaml structure."""
    path = TEMPLATE_ROOT / "identity" / "experience.yaml"
    if not path.exists():
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}

    experience = data.get('experience', [])
    if not experience:
        result.warn("experience.yaml: No experience entries")
        return

    for i, entry in enumerate(experience):
        if not isinstance(entry, dict):
            result.error(f"experience.yaml: Entry {i} is not a dict")
            continue

        company = (entry.get('company') or '').strip()
        position = (entry.get('position') or entry.get('title') or '').strip()
        start = (entry.get('start_date') or '').strip()

        # If it's a completely blank scaffolding entry, don't spam individual field warnings
        if not company and not position and not start:
            continue

        if not company:
            result.warn(f"experience.yaml: Entry {i} missing company")
        if not position:
            result.warn(f"experience.yaml: Entry {i} missing position")
        if not start:
            result.warn(f"experience.yaml: Entry {i} missing start_date")

        # Check for verification tags
        verification = (entry.get('verification') or '').strip()
        if not verification:
            result.warn(f"experience.yaml: Entry {i} ({company or 'unnamed'}) missing verification tag")


def check_verification_tags(result: ValidationResult):
    """Check that identity files use verification tags."""
    files_to_check = [
        "identity/identity.yaml",
        "identity/experience.yaml",
        "identity/credentials.yaml",
        "identity/speaking-and-community.yaml",
    ]

    for f in files_to_check:
        path = TEMPLATE_ROOT / f
        if not path.exists():
            continue

        content = path.read_text(encoding='utf-8')
        has_verified = '✅' in content or 'VERIFIED' in content
        has_estimated = '⚠️' in content or 'ESTIMATED' in content
        has_unverified = '❌' in content or 'UNVERIFIED' in content

        if not (has_verified or has_estimated or has_unverified):
            # Only warn if the file has real data (not just template)
            data = yaml.safe_load(content)
            if data and not all(v in ('', None, [], {}, 0, False) for v in
                               (data.values() if isinstance(data, dict) else [data])):
                result.warn(f"{f}: No verification tags (✅/⚠️/❌) found")


def check_cascade_consistency(result: ValidationResult):
    """Check that resume cascade files are consistent."""
    master_path = TEMPLATE_ROOT / "resume" / "master.yaml"
    design_path = TEMPLATE_ROOT / "resume" / "design.yaml"

    if not master_path.exists():
        result.error("resume/master.yaml missing — cascade engine won't work")
        return
    if not design_path.exists():
        result.error("resume/design.yaml missing — cascade engine won't work")
        return

    # Check for variants
    variants_dir = TEMPLATE_ROOT / "resume" / "variants"
    if variants_dir.exists():
        variants = list(variants_dir.glob('*.yaml'))
        real_variants = [v for v in variants if not v.name.startswith('_')]
        if not real_variants:
            result.note("No active resume variants created yet (only _template.yaml)")
        else:
            result.note(f"{len(real_variants)} resume variant(s) found")


VALID_SKILL_LEVELS = {"beginner", "intermediate", "advanced", "expert"}


def parse_flexible_date(date_str: str):
    """Parse YYYY-MM or YYYY string into a comparable tuple (year, month). Returns None if unparseable."""
    if not date_str or not isinstance(date_str, str):
        return None
    s = date_str.strip().lower()
    if s in ('present', 'current', 'now'):
        return (9999, 12)
    m = re.match(r'^(\d{4})(?:-(\d{2}))?$', s)
    if m:
        year = int(m.group(1))
        month = int(m.group(2)) if m.group(2) else 1
        return (year, month)
    return None


def check_skill_enums(result: ValidationResult):
    """Validate skill levels against allowed schema enums."""
    path = TEMPLATE_ROOT / "identity" / "skills.yaml"
    if not path.exists():
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        return

    for cat_name, skills in data.items():
        if cat_name in ('last_updated',) or not isinstance(skills, list):
            continue
        for s in skills:
            if not isinstance(s, dict):
                continue
            name = (s.get('name') or '').strip()
            level = (s.get('level') or '').strip()
            if not name:
                continue
            if level and level.lower() not in VALID_SKILL_LEVELS:
                result.warn(
                    f"skills.yaml: Skill '{name}' in '{cat_name}' has invalid level '{level}' "
                    f"(expected: {', '.join(sorted(VALID_SKILL_LEVELS))})"
                )


def check_date_chronology(result: ValidationResult):
    """Check start_date <= end_date and date formats in experience and career breaks."""
    path = TEMPLATE_ROOT / "identity" / "experience.yaml"
    if not path.exists():
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}

    # Experience entries
    experience = data.get('experience', []) or []
    for i, entry in enumerate(experience):
        if not isinstance(entry, dict):
            continue
        company = entry.get('company', '').strip()
        start = str(entry.get('start_date') or '').strip()
        end = str(entry.get('end_date') or '').strip()

        if not company and not start:
            continue

        p_start = parse_flexible_date(start)
        p_end = parse_flexible_date(end)

        if start and p_start is None:
            result.warn(f"experience.yaml: Entry {i} ({company or 'unnamed'}) has invalid start_date '{start}' (expected YYYY-MM)")
        if end and p_end is None:
            result.warn(f"experience.yaml: Entry {i} ({company or 'unnamed'}) has invalid end_date '{end}' (expected YYYY-MM or 'present')")

        if p_start and p_end and p_start > p_end:
            result.warn(f"experience.yaml: Entry {i} ({company or 'unnamed'}) has start_date '{start}' after end_date '{end}'")

    # Career breaks
    breaks = data.get('career_breaks', []) or []
    for i, b in enumerate(breaks):
        if not isinstance(b, dict):
            continue
        title = b.get('title', '').strip()
        start = str(b.get('start_date') or '').strip()
        end = str(b.get('end_date') or '').strip()

        if not title and not start:
            continue

        p_start = parse_flexible_date(start)
        p_end = parse_flexible_date(end)
        if p_start and p_end and p_start > p_end:
            result.warn(f"experience.yaml: Career break {i} ('{title}') has start_date '{start}' after end_date '{end}'")


def check_identity_master_parity(result: ValidationResult):
    """Check parity between identity/experience.yaml and resume/master.yaml."""
    exp_path = TEMPLATE_ROOT / "identity" / "experience.yaml"
    master_path = TEMPLATE_ROOT / "resume" / "master.yaml"

    if not exp_path.exists() or not master_path.exists():
        return

    with open(exp_path, 'r', encoding='utf-8') as f:
        exp_data = yaml.safe_load(f) or {}
    with open(master_path, 'r', encoding='utf-8') as f:
        master_data = yaml.safe_load(f) or {}

    id_companies = []
    for e in (exp_data.get('experience', []) or []):
        if isinstance(e, dict):
            comp = (e.get('company') or '').strip()
            if comp:
                id_companies.append(comp)

    if not id_companies:
        return

    master_exp = master_data.get('experience', {}) or {}
    master_companies = set()
    for k, v in master_exp.items():
        if k != '_example_role_' and isinstance(v, dict):
            comp = (v.get('company') or '').strip()
            if comp:
                master_companies.add(comp.lower())

    for comp in id_companies:
        if comp.lower() not in master_companies:
            result.warn(
                f"Parity: Employer '{comp}' in experience.yaml is not in resume/master.yaml. "
                f"Run 'py resume/sync.py' to synchronize."
            )


def check_cross_file_consistency(result: ValidationResult):
    """Check consistency across files (config vs identity contact info, and skills in deliverables vs skills.yaml)."""
    # 1. Config vs Identity contact info check
    cfg_path = TEMPLATE_ROOT / "config.yaml"
    id_path = TEMPLATE_ROOT / "identity" / "identity.yaml"
    if cfg_path.exists() and id_path.exists():
        with open(cfg_path, 'r', encoding='utf-8') as f:
            cfg_data = yaml.safe_load(f) or {}
        with open(id_path, 'r', encoding='utf-8') as f:
            id_data = yaml.safe_load(f) or {}

        cfg_name = str((cfg_data.get('user', {}) or {}).get('name') or '').strip()
        id_name = str(id_data.get('name') or id_data.get('full_name') or '').strip()
        if cfg_name and id_name and cfg_name.lower() != id_name.lower():
            result.warn(
                f"Contradiction: config.yaml user.name ('{cfg_name}') does not match identity.yaml ('{id_name}'). "
                f"Identity takes precedence, but keeping them synchronized is recommended."
            )

        cfg_email = str((cfg_data.get('user', {}) or {}).get('email') or '').strip()
        id_email = str(id_data.get('email') or '').strip()
        if cfg_email and id_email and cfg_email.lower() != id_email.lower():
            result.warn(
                f"Contradiction: config.yaml user.email ('{cfg_email}') does not match identity.yaml ('{id_email}')."
            )

    # 2. Skills referenced in deliverables/projects vs skills.yaml
    skills_path = TEMPLATE_ROOT / "identity" / "skills.yaml"
    exp_path = TEMPLATE_ROOT / "identity" / "experience.yaml"
    proj_path = TEMPLATE_ROOT / "identity" / "projects.yaml"

    if not skills_path.exists():
        return

    with open(skills_path, 'r', encoding='utf-8') as f:
        skills_data = yaml.safe_load(f) or {}

    known_skills = set()
    if isinstance(skills_data, dict):
        for cat, slist in skills_data.items():
            if cat != 'last_updated' and isinstance(slist, list):
                for s in slist:
                    if isinstance(s, dict) and s.get('name'):
                        known_skills.add(str(s['name']).strip().lower())

    if not known_skills:
        return

    unlisted_skills = set()

    # Check experience deliverables
    if exp_path.exists():
        with open(exp_path, 'r', encoding='utf-8') as f:
            exp_data = yaml.safe_load(f) or {}
        for e in (exp_data.get('experience', []) or []):
            if isinstance(e, dict):
                for p in (e.get('projects', []) or []):
                    if isinstance(p, dict):
                        for d in (p.get('deliverables', []) or []):
                            if isinstance(d, dict):
                                for s in (d.get('skills', []) or []):
                                    s_clean = str(s).strip()
                                    if s_clean and s_clean.lower() not in known_skills:
                                        unlisted_skills.add(s_clean)

    # Check projects
    if proj_path.exists():
        with open(proj_path, 'r', encoding='utf-8') as f:
            proj_data = yaml.safe_load(f) or {}
        for p in ((proj_data.get('public', []) or []) + (proj_data.get('internal', []) or [])):
            if isinstance(p, dict):
                for t in (p.get('tech', []) or []):
                    t_clean = str(t).strip()
                    if t_clean and t_clean.lower() not in known_skills:
                        unlisted_skills.add(t_clean)

    if unlisted_skills:
        sample = sorted(list(unlisted_skills))[:5]
        suffix = f" (+{len(unlisted_skills) - 5} more)" if len(unlisted_skills) > 5 else ""
        result.warn(
            f"Cross-reference: {len(unlisted_skills)} skill(s) referenced in deliverables/projects "
            f"not found in skills.yaml: {', '.join(sample)}{suffix}"
        )


def compute_fill_status(result: ValidationResult):
    """Compute and report template fill percentage."""
    filled = 0
    total = 0
    status_lines = []

    checks = [
        ("config.yaml", "config.yaml", lambda d: bool(((d or {}).get('user') or {}).get('name', '').strip())),
        ("identity/identity.yaml", "identity.yaml", lambda d: bool((d or {}).get('name', '').strip()) or bool((d or {}).get('total_years_experience', 0) > 0)),
        ("identity/experience.yaml", "experience.yaml", lambda d: any(
            isinstance(e, dict) and bool((e.get('company') or '').strip()) for e in ((d or {}).get('experience') or [])
        )),
        ("identity/skills.yaml", "skills.yaml", lambda d: d is not None and any(
            isinstance(v, list) and any(isinstance(s, dict) and bool((s.get('name') or '').strip()) for s in v)
            for v in (d or {}).values() if isinstance(v, list)
        )),
        ("identity/credentials.yaml", "credentials.yaml", lambda d: any(
            isinstance(e, dict) and bool((e.get('degree') or '').strip()) for e in ((d or {}).get('education') or [])
        ) or any(
            isinstance(c, dict) and bool((c.get('name') or '').strip()) for c in ((d or {}).get('certifications') or [])
        )),
        ("identity/projects.yaml", "projects.yaml", lambda d: any(
            isinstance(p, dict) and bool((p.get('name') or '').strip()) for p in ((d or {}).get('public') or [])
        ) or any(
            isinstance(p, dict) and bool((p.get('name') or '').strip()) for p in ((d or {}).get('internal') or [])
        )),
        ("identity/speaking-and-community.yaml", "speaking-and-community.yaml", lambda d: any(
            isinstance(s, dict) and bool((s.get('title') or '').strip()) for s in ((d or {}).get('speaking') or [])
        ) or any(
            isinstance(h, dict) and bool((h.get('name') or '').strip()) for h in ((d or {}).get('hackathons') or [])
        )),
        ("resume/master.yaml", "master.yaml", lambda d: any(
            k != '_example_role_' and isinstance(v, dict) for k, v in ((d or {}).get('experience') or {}).items()
        )),
        ("personal/preferences.yaml", "preferences.yaml", lambda d: bool(
            str((d or {}).get('career_stage') or '').strip() or str((d or {}).get('career_anchor') or '').strip() or (d or {}).get('work_values')
        )),
    ]

    for filepath, label, check_fn in checks:
        total += 1
        path = TEMPLATE_ROOT / filepath
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                if check_fn(data):
                    filled += 1
                    status_lines.append(f"  ✅ {label}")
                else:
                    status_lines.append(f"  ⬜ {label} (empty)")
            except Exception:
                status_lines.append(f"  ❌ {label} (parse error)")
        else:
            status_lines.append(f"  ⬜ {label} (not created)")

    # Check markdown files for real user data beyond template scaffolding
    def check_claims(text: str) -> bool:
        if "## Claims Register" not in text:
            return False
        reg = text.split("## Claims Register")[-1].split("## Contradictions Log")[0]
        return any(
            line.strip().startswith('|') and not line.strip().startswith(('| Claim', '|---', '|:---', '| *Example'))
            for line in reg.splitlines()
        )

    def check_summary(text: str) -> bool:
        clean = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        content_lines = [
            l.strip() for l in clean.splitlines()
            if l.strip() and not l.strip().startswith(('#', '>', '---'))
        ]
        return len(content_lines) > 0

    def check_about(text: str) -> bool:
        clean = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        content_lines = [
            l.strip() for l in clean.splitlines()
            if l.strip() and not l.strip().startswith(('#', '>', '---')) and l.strip() not in ('-', '1.', '2.', '3.')
        ]
        return len(content_lines) > 0

    def check_roles(text: str) -> bool:
        for line in text.splitlines():
            s = line.strip()
            if s.startswith('### Role') and '[' not in s:
                return True
        return False

    md_checks = [
        ("identity/claims-and-evidence.md", "claims-and-evidence.md", check_claims),
        ("identity/professional-summary.md", "professional-summary.md", check_summary),
        ("personal/about-me.md", "about-me.md", check_about),
        ("strategy/target-roles.md", "target-roles.md", check_roles),
    ]

    for filepath, label, check_fn in md_checks:
        total += 1
        path = TEMPLATE_ROOT / filepath
        if path.exists():
            try:
                content = path.read_text(encoding='utf-8')
                if check_fn(content):
                    filled += 1
                    status_lines.append(f"  ✅ {label}")
                else:
                    status_lines.append(f"  ⬜ {label} (template only)")
            except Exception:
                status_lines.append(f"  ❌ {label} (read error)")
        else:
            status_lines.append(f"  ⬜ {label} (not created)")

    pct = int(100 * filled / total) if total > 0 else 0
    result.note(f"\n📊 Fill Status: {filled}/{total} ({pct}%)")
    for line in status_lines:
        result.note(line)


def check_freshness(result: ValidationResult):
    """Check freshness of YAML files with last_updated fields."""
    stale_files = []
    for f in YAML_FILES_TO_VALIDATE:
        path = TEMPLATE_ROOT / f
        if not path.exists():
            continue
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                data = yaml.safe_load(fh)
            if isinstance(data, dict) and data.get('last_updated'):
                raw_date = str(data['last_updated']).strip()
                try:
                    dt = datetime.datetime.strptime(raw_date, "%Y-%m-%d").date()
                    days = (datetime.date.today() - dt).days
                    if days > 90:
                        stale_files.append((f, raw_date, days))
                except ValueError:
                    result.warn(f"{f}: Invalid last_updated date format '{raw_date}' (expected YYYY-MM-DD)")
        except Exception:
            pass

    if stale_files:
        for f, d, days in stale_files:
            result.warn(f"{f}: Last updated {days} days ago ({d}) — review during quarterly audit")


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Pramedha Template Validator')
    parser.add_argument('--status', action='store_true', help='Show fill status only')
    parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')
    args = parser.parse_args()

    # Ensure UTF-8 output on Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    result = ValidationResult()

    print("\n🔍 Pramedha Template Validator")
    print(f"   Root: {TEMPLATE_ROOT}\n")

    if args.status:
        compute_fill_status(result)
        for msg in result.info:
            print(msg)
        return

    # Run all checks
    print("── File Structure ──")
    check_file_exists(result)

    print("\n── YAML Syntax ──")
    check_yaml_valid(result)

    print("\n── Config Validation ──")
    check_config(result)

    print("\n── Experience Validation ──")
    check_experience(result)

    print("\n── Verification Tags ──")
    check_verification_tags(result)

    print("\n── Resume Cascade ──")
    check_cascade_consistency(result)

    print("\n── Skill Enums ──")
    check_skill_enums(result)

    print("\n── Date Chronology ──")
    check_date_chronology(result)

    print("\n── Identity-Master Parity ──")
    check_identity_master_parity(result)

    print("\n── Cross-File Consistency ──")
    check_cross_file_consistency(result)

    print("\n── Freshness Check ──")
    check_freshness(result)

    print("\n── Fill Status ──")
    compute_fill_status(result)

    # Report
    print("\n" + "=" * 50)

    for msg in result.info:
        print(msg)

    if result.warnings:
        print(f"\n⚠️  {len(result.warnings)} warning(s):")
        for w in result.warnings:
            print(f"   ⚠️  {w}")

    if result.errors:
        print(f"\n❌ {len(result.errors)} error(s):")
        for e in result.errors:
            print(f"   ❌ {e}")

    print()
    if result.errors:
        print("❌ VALIDATION FAILED")
        sys.exit(1)
    elif result.warnings and args.strict:
        print("⚠️  VALIDATION FAILED (strict mode)")
        sys.exit(1)
    else:
        print("✅ VALIDATION PASSED")


if __name__ == '__main__':
    main()
