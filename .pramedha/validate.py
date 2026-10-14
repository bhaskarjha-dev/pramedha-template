#!/usr/bin/env python3
"""
Pramedha Template Validator — Checks template integrity and fill status.

Usage:
    python validate.py                # Full validation
    python validate.py --status       # Show fill status only
    python validate.py --strict       # Fail on warnings too
    python validate.py --json         # Output JSON summary for CI
"""

import argparse
import datetime
import json
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
    "identity/claims-and-evidence.md",
    "identity/professional-summary.md",
    "tools/resume/master.yaml",
    "tools/resume/design.yaml",
    "tools/resume/assemble.py",
    "tools/resume/sync.py",
    "tools/resume/_yaml_utils.py",
]

OPTIONAL_FILES = [
    "identity/speaking-and-community.yaml",
    "identity/volunteering.yaml",
    "identity/references.yaml",
    "personal/about-me.md",
    "personal/life-goals.md",
    "personal/preferences.yaml",
    "personal/career-narrative.md",
    "personal/reflections.md",
    "personal/form-fill-cheatsheet.md",
    "stories/star-stories.md",
    "stories/testimonials.md",
    "stories/interview-prep/behavioral.md",
    "stories/interview-prep/technical.md",
    "strategy/target-roles.md",
    "strategy/study-plan.md",
    "strategy/financial.md",
    "strategy/job-tracker.md",
    "strategy/networking.md",
    "strategy/offer-comparison.md",
    "journal/wins.md",
    "journal/learning-log.md",
    "journal/feedback.md",
    "ops/session-handoff.md",
    "ops/guide.md",
    "ops/authority-map.md",
    "ops/prompts.md",
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
    "tools/resume/master.yaml",
    "tools/resume/design.yaml",
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
        if path.exists():
            result.note(f"✅ {f} (optional)")


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

    # Resolve effective contact details across config.yaml and identity/identity.yaml
    id_path = TEMPLATE_ROOT / "identity" / "identity.yaml"
    id_data = {}
    if id_path.exists():
        try:
            with open(id_path, 'r', encoding='utf-8') as id_f:
                id_data = yaml.safe_load(id_f) or {}
        except Exception:
            pass

    effective_name = name or (id_data.get('name') or '').strip()
    effective_email = email or (id_data.get('email') or '').strip()

    if not effective_name:
        result.warn("config.yaml / identity.yaml: user name is empty in both files")
    if not effective_email:
        result.warn("config.yaml / identity.yaml: user email is empty in both files")

    profession = (config.get('profession_type') or '').strip()
    if not profession:
        result.warn("config.yaml: profession_type is empty")

    # Schema version validation against manifest.yaml
    manifest_path = TEMPLATE_ROOT / ".pramedha" / "manifest.yaml"
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r', encoding='utf-8') as mf:
                mdata = yaml.safe_load(mf) or {}
            expected_ver = (mdata.get('template') or {}).get('schema_version', '0.1.0')
            config_ver = config.get('schema_version')
            if config_ver is not None:
                if str(config_ver).strip() != str(expected_ver).strip():
                    result.warn(
                        f"config.yaml: schema_version '{config_ver}' does not match "
                        f"manifest schema_version '{expected_ver}'"
                    )
            else:
                result.note(f"config.yaml: schema_version not specified (manifest: {expected_ver})")
        except Exception:
            pass


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
    master_path = TEMPLATE_ROOT / "tools" / "resume" / "master.yaml"
    design_path = TEMPLATE_ROOT / "tools" / "resume" / "design.yaml"

    if not master_path.exists():
        result.error("tools/resume/master.yaml missing — cascade engine won't work")
        return
    if not design_path.exists():
        result.error("tools/resume/design.yaml missing — cascade engine won't work")
        return

    # Check for variants
    variants_dir = TEMPLATE_ROOT / "tools" / "resume" / "variants"
    if variants_dir.exists():
        variants = list(variants_dir.glob('*.yaml'))
        real_variants = [v for v in variants if not v.name.startswith('_')]
        if not real_variants:
            result.note("No active resume variants created yet (only _template.yaml)")
        else:
            result.note(f"{len(real_variants)} resume variant(s) found")


VALID_SKILL_LEVELS = {"beginner", "intermediate", "advanced", "expert"}
VALID_PROFESSION_TYPES = {"engineering", "creative", "medical", "business", "academic", "legal", "freelance", "executive", "other"}
VALID_CAREER_TYPES = {"employed", "freelance", "portfolio", "academic", "military", "government", "student"}
VALID_EMPLOYMENT_TYPES = {
    "full-time", "part-time", "contract", "freelance", "internship",
    "full_time", "part_time", "self_employed", "volunteer"
}
VALID_LOCATION_TYPES = {"remote", "hybrid", "onsite"}
VALID_LANGUAGE_FLUENCY = {"native", "fluent", "professional", "conversational", "basic", "elementary"}
VALID_CAREER_STAGES = {
    "early", "mid", "senior", "lead", "executive",
    "student", "early_career", "mid_career", "career_changer", "returning", "sabbatical", "freelance"
}
VALID_CAREER_BREAK_TYPES = {
    "parental", "caregiving", "health", "sabbatical", "education", "relocation", "travel", "transition", "other",
    "parental_leave", "career_transition", "layoff"
}
VALID_WORK_AUTHORIZATION = {"citizen", "permanent_resident", "work_visa", "student_visa", "need_sponsorship", "other"}
VALID_ROLE_LEVELS = {
    "intern", "entry", "junior", "mid", "senior", "lead", "staff", "principal", "director", "vp", "c-level", "executive"
}


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


def check_schema_enums(result: ValidationResult):
    """Validate all schema enums against allowed values in schema-reference.md."""
    # 1. Skill levels in skills.yaml
    skills_path = TEMPLATE_ROOT / "identity" / "skills.yaml"
    if skills_path.exists():
        with open(skills_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        if isinstance(data, dict):
            for cat_name, skills in data.items():
                if cat_name in ('last_updated',) or not isinstance(skills, list):
                    continue
                for s in skills:
                    if isinstance(s, dict):
                        name = (s.get('name') or '').strip()
                        level = (s.get('level') or '').strip()
                        if name and level and level.lower() not in VALID_SKILL_LEVELS:
                            result.warn(
                                f"skills.yaml: Skill '{name}' in '{cat_name}' has invalid level '{level}' "
                                f"(expected: {', '.join(sorted(VALID_SKILL_LEVELS))})"
                            )

    # 2. Config enums (profession_type, career_type, target_role_level)
    cfg_path = TEMPLATE_ROOT / "config.yaml"
    if cfg_path.exists():
        with open(cfg_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f) or {}
        prof = (cfg.get('profession_type') or '').strip().lower()
        if prof and prof not in VALID_PROFESSION_TYPES:
            result.warn(f"config.yaml: profession_type '{prof}' not in allowed enums")
        ctype = (cfg.get('career_type') or '').strip().lower()
        if ctype and ctype not in VALID_CAREER_TYPES:
            result.warn(f"config.yaml: career_type '{ctype}' not in allowed enums")
        rlevel = (cfg.get('target_role_level') or '').strip().lower()
        if rlevel and rlevel not in VALID_ROLE_LEVELS:
            result.warn(f"config.yaml: target_role_level '{rlevel}' not in allowed enums")

    # 3. Identity languages & work authorization
    id_path = TEMPLATE_ROOT / "identity" / "identity.yaml"
    if id_path.exists():
        with open(id_path, 'r', encoding='utf-8') as f:
            id_data = yaml.safe_load(f) or {}
        for lang in (id_data.get('languages') or []):
            if isinstance(lang, dict):
                lvl = (lang.get('level') or '').strip().lower()
                lname = (lang.get('language') or '').strip()
                if lvl and lvl not in VALID_LANGUAGE_FLUENCY:
                    result.warn(f"identity.yaml: Language '{lname}' has invalid fluency '{lvl}'")
        wauth_raw = id_data.get('work_authorization')
        if isinstance(wauth_raw, dict):
            wauth = (wauth_raw.get('status') or '').strip().lower()
        elif isinstance(wauth_raw, str):
            wauth = wauth_raw.strip().lower()
        else:
            wauth = ''
        if wauth and wauth not in VALID_WORK_AUTHORIZATION:
            result.warn(f"identity.yaml: work_authorization status '{wauth}' not in allowed enums")

    # 4. Experience enums (employment_type, location_type, career_break_type)
    exp_path = TEMPLATE_ROOT / "identity" / "experience.yaml"
    if exp_path.exists():
        with open(exp_path, 'r', encoding='utf-8') as f:
            exp_data = yaml.safe_load(f) or {}
        for entry in (exp_data.get('experience') or []):
            if isinstance(entry, dict):
                comp = (entry.get('company') or '').strip()
                etype = (entry.get('employment_type') or '').strip().lower()
                if etype and etype not in VALID_EMPLOYMENT_TYPES:
                    result.warn(f"experience.yaml: Role at '{comp}' has invalid employment_type '{etype}'")
                ltype = (entry.get('location_type') or '').strip().lower()
                if ltype and ltype not in VALID_LOCATION_TYPES:
                    result.warn(f"experience.yaml: Role at '{comp}' has invalid location_type '{ltype}'")
        for brk in (exp_data.get('career_breaks') or []):
            if isinstance(brk, dict):
                btype = (brk.get('type') or '').strip().lower()
                btitle = (brk.get('title') or '').strip()
                if btype and btype not in VALID_CAREER_BREAK_TYPES:
                    result.warn(f"experience.yaml: Career break '{btitle}' has invalid type '{btype}'")

    # 5. Preferences enums (career_stage)
    pref_path = TEMPLATE_ROOT / "personal" / "preferences.yaml"
    if pref_path.exists():
        with open(pref_path, 'r', encoding='utf-8') as f:
            pref_data = yaml.safe_load(f) or {}
        cstage = (pref_data.get('career_stage') or '').strip().lower()
        if cstage and cstage not in VALID_CAREER_STAGES:
            result.warn(f"preferences.yaml: career_stage '{cstage}' not in allowed enums")


# Alias for backward compatibility
check_skill_enums = check_schema_enums


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
    """Check parity between identity/ files and resume/master.yaml (experience, projects, education)."""
    master_path = TEMPLATE_ROOT / "resume" / "master.yaml"
    if not master_path.exists():
        return

    with open(master_path, 'r', encoding='utf-8') as f:
        master_data = yaml.safe_load(f) or {}

    # 1. Experience Parity
    exp_path = TEMPLATE_ROOT / "identity" / "experience.yaml"
    if exp_path.exists():
        with open(exp_path, 'r', encoding='utf-8') as f:
            exp_data = yaml.safe_load(f) or {}

        id_companies = []
        for e in (exp_data.get('experience', []) or []):
            if isinstance(e, dict):
                comp = (e.get('company') or '').strip()
                if comp:
                    id_companies.append(comp)

        if id_companies:
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

    # 2. Projects Parity
    proj_path = TEMPLATE_ROOT / "identity" / "projects.yaml"
    if proj_path.exists():
        with open(proj_path, 'r', encoding='utf-8') as f:
            proj_data = yaml.safe_load(f) or {}

        id_projects = []
        all_projs = (proj_data.get('public', []) or []) + (proj_data.get('internal', []) or []) + (proj_data.get('projects', []) or [])
        for p in all_projs:
            if isinstance(p, dict):
                pname = (p.get('name') or '').strip()
                if pname:
                    id_projects.append(pname)

        if id_projects:
            master_proj = master_data.get('projects', {}) or {}
            master_project_names = set()
            for k, v in master_proj.items():
                if isinstance(v, dict):
                    name = (v.get('name') or k).strip().lower()
                    master_project_names.add(name)
                elif isinstance(k, str):
                    master_project_names.add(k.lower())

            for pname in id_projects:
                if pname.lower() not in master_project_names:
                    result.warn(
                        f"Parity: Project '{pname}' in projects.yaml is not in resume/master.yaml. "
                        f"Run 'py resume/sync.py' to synchronize."
                    )

    # 3. Education Parity
    creds_path = TEMPLATE_ROOT / "identity" / "credentials.yaml"
    if creds_path.exists():
        with open(creds_path, 'r', encoding='utf-8') as f:
            creds_data = yaml.safe_load(f) or {}

        id_institutions = []
        for e in (creds_data.get('education', []) or []):
            if isinstance(e, dict):
                inst = (e.get('institution') or '').strip()
                if inst:
                    id_institutions.append(inst)

        if id_institutions:
            master_edu = master_data.get('education', []) or []
            master_insts = set()
            for e in master_edu:
                if isinstance(e, dict):
                    inst = (e.get('institution') or '').strip().lower()
                    if inst:
                        master_insts.add(inst)

            for inst in id_institutions:
                if inst.lower() not in master_insts:
                    result.warn(
                        f"Parity: Education institution '{inst}' in credentials.yaml is not in resume/master.yaml. "
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
        ("identity/identity.yaml", "identity.yaml", lambda d: (
            bool((d or {}).get('name', '').strip())
            or bool((d or {}).get('total_years_experience', 0) > 0)
            or any(isinstance(l, dict) and bool(l.get('language', '').strip()) for l in ((d or {}).get('languages') or []))
            or bool(str((d or {}).get('nationality', '') or (d or {}).get('citizenship', '')).strip())
            or bool(((d or {}).get('work_authorization') or {}).get('status', '').strip() if isinstance((d or {}).get('work_authorization'), dict) else str((d or {}).get('work_authorization', '')).strip())
        )),
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
    result.note(f"\n📊 Core System Fill Status: {filled}/{total} ({pct}%) [13 Core Identity & Cascade Files]")
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
    parser.add_argument('--json', action='store_true', help='Output JSON summary for CI/tooling')
    args = parser.parse_args()

    # Ensure UTF-8 output on Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    result = ValidationResult()

    if args.json:
        check_file_exists(result)
        check_yaml_valid(result)
        check_config(result)
        check_experience(result)
        check_verification_tags(result)
        check_cascade_consistency(result)
        check_skill_enums(result)
        check_date_chronology(result)
        check_identity_master_parity(result)
        check_cross_file_consistency(result)
        check_freshness(result)
        compute_fill_status(result)

        passed = not bool(result.errors) and not (bool(result.warnings) and args.strict)
        output = {
            "passed": passed,
            "root": str(TEMPLATE_ROOT),
            "error_count": len(result.errors),
            "warning_count": len(result.warnings),
            "errors": result.errors,
            "warnings": result.warnings,
            "info": result.info,
        }
        print(json.dumps(output, indent=2))
        sys.exit(0 if passed else 1)

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
