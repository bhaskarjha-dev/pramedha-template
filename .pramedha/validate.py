#!/usr/bin/env python3
"""
Pramedha Template Validator — Checks template integrity and fill status.

Usage:
    python validate.py                # Full validation
    python validate.py --status       # Show fill status only
    python validate.py --strict       # Fail on warnings too
"""

import argparse
import sys
from pathlib import Path

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
    "identity/claims-and-evidence.md",
    "identity/professional-summary.md",
    "resume/master.yaml",
    "resume/design.yaml",
    "resume/assemble.py",
]

OPTIONAL_FILES = [
    "personal/about-me.md",
    "personal/life-goals.md",
    "personal/preferences.yaml",
    "strategy/target-roles.md",
    "strategy/study-plan.md",
    "strategy/financial.md",
    "journal/wins.md",
    "journal/learning-log.md",
]

YAML_FILES_TO_VALIDATE = [
    "config.yaml",
    "identity/identity.yaml",
    "identity/experience.yaml",
    "identity/skills.yaml",
    "identity/credentials.yaml",
    "identity/projects.yaml",
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
    name = user.get('name', '')
    email = user.get('email', '')

    if not name:
        result.warn("config.yaml: user.name is empty")
    if not email:
        result.warn("config.yaml: user.email is empty")

    profession = config.get('profession_type', '')
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

        company = entry.get('company', '')
        title = entry.get('title', '')
        start = entry.get('start_date', '')

        if not company:
            result.warn(f"experience.yaml: Entry {i} missing company")
        if not title:
            result.warn(f"experience.yaml: Entry {i} missing title")
        if not start:
            result.warn(f"experience.yaml: Entry {i} missing start_date")

        # Check for verification tags
        verification = entry.get('verification', '')
        if not verification:
            result.warn(f"experience.yaml: Entry {i} ({company}) missing verification tag")


def check_verification_tags(result: ValidationResult):
    """Check that identity files use verification tags."""
    files_to_check = [
        "identity/identity.yaml",
        "identity/experience.yaml",
        "identity/credentials.yaml",
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
        real_variants = [v for v in variants if v.stem != '_template']
        if not real_variants:
            result.note("No resume variants created yet (only _template.yaml)")
        else:
            result.note(f"{len(real_variants)} resume variant(s) found")


def compute_fill_status(result: ValidationResult):
    """Compute and report template fill percentage."""
    filled = 0
    total = 0
    status_lines = []

    checks = [
        ("config.yaml", "config.yaml", lambda d: bool(((d or {}).get('user') or {}).get('name', ''))),
        ("identity/identity.yaml", "identity.yaml", lambda d: bool((d or {}).get('name', ''))),
        ("identity/experience.yaml", "experience.yaml", lambda d: bool((d or {}).get('experience', []))),
        ("identity/skills.yaml", "skills.yaml", lambda d: d is not None and any(
            isinstance(v, list) and len(v) > 0 for v in (d or {}).values()
        )),
        ("identity/credentials.yaml", "credentials.yaml", lambda d: bool(
            (d or {}).get('education', []) or (d or {}).get('certifications', [])
        )),
        ("identity/projects.yaml", "projects.yaml", lambda d: bool(
            (d or {}).get('public', []) or (d or {}).get('internal', [])
        )),
        ("resume/master.yaml", "master.yaml", lambda d: bool((d or {}).get('experience', {}))),
        ("personal/preferences.yaml", "preferences.yaml", lambda d: bool(
            (d or {}).get('career_anchor', '') or (d or {}).get('work_values', [])
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

    # Check markdown files by content length
    md_checks = [
        ("identity/claims-and-evidence.md", "claims-and-evidence.md", 500),
        ("identity/professional-summary.md", "professional-summary.md", 200),
        ("personal/about-me.md", "about-me.md", 100),
        ("strategy/target-roles.md", "target-roles.md", 300),
    ]

    for filepath, label, min_bytes in md_checks:
        total += 1
        path = TEMPLATE_ROOT / filepath
        if path.exists() and path.stat().st_size > min_bytes:
            filled += 1
            status_lines.append(f"  ✅ {label}")
        else:
            status_lines.append(f"  ⬜ {label} (template only)")

    pct = int(100 * filled / total) if total > 0 else 0
    result.note(f"\n📊 Fill Status: {filled}/{total} ({pct}%)")
    for line in status_lines:
        result.note(line)


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
