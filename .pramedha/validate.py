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
import contextlib
import datetime
import importlib.util
import io
import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

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
    ".pramedha/manifest.yaml",
]

SATELLITE_FILES = [
    "tools/resume/master.yaml",
    "tools/resume/design.yaml",
    "tools/resume/assemble.py",
    "tools/resume/sync.py",
    "tools/resume/_yaml_utils.py",
    "tools/resume/build.ps1",
    "tools/resume/build.sh",
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


def as_text(value) -> str:
    """Safely coerce any YAML scalar (int, float, date, bool, str, None) to stripped string."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


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

    for f in SATELLITE_FILES:
        path = TEMPLATE_ROOT / f
        if path.exists():
            result.note(f"✅ {f} (satellite)")



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
    name = as_text(user.get('name'))
    email = as_text(user.get('email'))

    # Resolve effective contact details across config.yaml and identity/identity.yaml
    id_path = TEMPLATE_ROOT / "identity" / "identity.yaml"
    id_data = {}
    if id_path.exists():
        try:
            with open(id_path, 'r', encoding='utf-8') as id_f:
                id_data = yaml.safe_load(id_f) or {}
        except Exception:
            pass

    effective_name = name or as_text(id_data.get('name'))
    effective_email = email or as_text(id_data.get('email'))

    if not effective_name:
        result.warn("config.yaml / identity.yaml: user name is empty in both files")
    if not effective_email:
        result.warn("config.yaml / identity.yaml: user email is empty in both files")

    profession = as_text(config.get('profession_type'))
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

        company = as_text(entry.get('company') or entry.get('organization') or entry.get('client') or entry.get('institution') or entry.get('employer') or entry.get('practice'))
        position = as_text(entry.get('position') or entry.get('title') or entry.get('role'))
        start = as_text(entry.get('start_date'))

        # If it's a completely blank scaffolding entry, don't spam individual field warnings
        if not company and not position and not start:
            continue

        if not company:
            result.warn(f"experience.yaml: Entry {i} missing company / client / organization")
        if not position:
            result.warn(f"experience.yaml: Entry {i} missing position / title / role")
        if not start:
            result.warn(f"experience.yaml: Entry {i} missing start_date")

        # Check for verification tags
        verification = as_text(entry.get('verification'))
        if not TAG_RE.search(verification):
            result.warn(f"experience.yaml: Entry {i} ({company or 'unnamed'}) verification has no tag (✅/⚠️/❌)")


TAG_RE = re.compile(r'\u2705|\u26a0|\u274c|\b(?:UN)?VERIFIED\b|\bESTIMATED\b')
FILL_KEYS = {'name', 'title', 'company', 'position', 'degree', 'institution', 'language', 'status', 'organization'}


def _strings(value):
    """Every string value inside parsed YAML (comments are not values)."""
    if isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)
    elif isinstance(value, str):
        yield value


def _has_real_data(value) -> bool:
    """True when any name/title/company/... field holds text (template scaffolding leaves them empty)."""
    if isinstance(value, dict):
        return any((k in FILL_KEYS and as_text(v)) or _has_real_data(v) for k, v in value.items())
    if isinstance(value, list):
        return any(_has_real_data(item) for item in value)
    return False


def check_verification_tags(result: ValidationResult):
    """Check that identity files use verification tags."""
    files_to_check = [
        "identity/identity.yaml",
        "identity/experience.yaml",
        "identity/credentials.yaml",
        "identity/projects.yaml",
        "identity/speaking-and-community.yaml",
        "identity/volunteering.yaml",
    ]

    for f in files_to_check:
        path = TEMPLATE_ROOT / f
        if not path.exists():
            continue
        data = yaml.safe_load(path.read_text(encoding='utf-8'))
        if _has_real_data(data) and not any(TAG_RE.search(s) for s in _strings(data)):
            result.warn(f"{f}: No verification tags (✅/⚠️/❌) found in any value")


EVIDENCE_RE = re.compile(r'data-corpus/[^\s;,()"\']+')
URL_RE = re.compile(r'https?://\S+')
VERIFIED_RE = re.compile(r'\u2705|\bVERIFIED\b')


def _verification_values(value, where=''):
    """(location, text) for every `verification` value in parsed YAML."""
    if isinstance(value, dict):
        for key, item in value.items():
            here = f"{where}.{key}" if where else str(key)
            if key == 'verification':
                text_val = as_text(item)
                if text_val:
                    yield here, text_val
            else:
                yield from _verification_values(item, here)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _verification_values(item, f"{where}[{index}]")


def check_evidence_paths(result: ValidationResult):
    """Every ✅ VERIFIED value must name an evidence file under data-corpus/ that exists, or a public URL."""
    for f in ("identity/identity.yaml", "identity/experience.yaml", "identity/credentials.yaml",
              "identity/projects.yaml", "identity/skills.yaml", "identity/speaking-and-community.yaml",
              "identity/volunteering.yaml"):
        path = TEMPLATE_ROOT / f
        if not path.exists():
            continue
        data = yaml.safe_load(path.read_text(encoding='utf-8'))
        for where, text in _verification_values(data):
            if not VERIFIED_RE.search(text):
                continue
            files = [p.rstrip('.') for p in EVIDENCE_RE.findall(text)]
            if not files and not URL_RE.search(text):
                result.warn(f"{f}: {where}: ✅ VERIFIED without evidence (name a data-corpus/ file "
                            f"or a public URL, e.g. data-corpus/documents/offer-letter.pdf)")
            for evidence in files:
                if evidence.endswith('/') or (TEMPLATE_ROOT / evidence).is_dir():
                    result.warn(f"{f}: {where}: evidence must name a file, not a folder: {evidence}")
                elif not (TEMPLATE_ROOT / evidence).is_file():
                    result.warn(f"{f}: {where}: evidence file not found: {evidence} (paths can't contain spaces)")


def _load_assemble():
    """Import tools/resume/assemble.py so --with-resume uses the same reference rules as the builder."""
    if str(TEMPLATE_ROOT) not in sys.path:
        sys.path.insert(0, str(TEMPLATE_ROOT))
    spec = importlib.util.spec_from_file_location('pramedha_assemble', TEMPLATE_ROOT / 'tools' / 'resume' / 'assemble.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_cascade_consistency(result: ValidationResult):
    """Check that resume cascade files are consistent and active variants reference valid keys."""
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
            try:
                with open(master_path, 'r', encoding='utf-8') as mf:
                    master_data = yaml.safe_load(mf) or {}

                assemble = _load_assemble()
                for vfile in real_variants:
                    with open(vfile, 'r', encoding='utf-8') as vf:
                        vdata = yaml.safe_load(vf) or {}
                    with contextlib.redirect_stdout(io.StringIO()):
                        messages = assemble.validate_variant(master_data, vdata)
                    for message in messages:
                        result.error(f"{vfile.name}: {message}")
            except Exception as e:
                result.warn(f"Failed to validate variant references against master: {e}")


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


def parse_flexible_date(date_str, is_end_date: bool = False):
    """Parse YYYY-MM-DD, YYYY-MM, or YYYY string into a comparable tuple (year, month). Returns None if unparseable."""
    if date_str is None or date_str == '':
        return None
    s = str(date_str).strip().lower()
    if not s or s == '0':
        return None
    if s in ('present', 'current', 'now'):
        return (9999, 12)
    m = re.match(r'^(\d{4})(?:-(\d{1,2}))?(?:-(\d{1,2}))?$', s)
    if m:
        year = int(m.group(1))
        month = int(m.group(2)) if m.group(2) else (12 if is_end_date else 1)
        if 1 <= month <= 12:
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
                        name = as_text(s.get('name'))
                        level = as_text(s.get('level'))
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
        prof = as_text(cfg.get('profession_type')).lower()
        if prof and prof not in VALID_PROFESSION_TYPES:
            result.warn(f"config.yaml: profession_type '{prof}' not in allowed enums")
        ctype = as_text(cfg.get('career_type')).lower()
        if ctype and ctype not in VALID_CAREER_TYPES:
            result.warn(f"config.yaml: career_type '{ctype}' not in allowed enums")
        rlevel = as_text(cfg.get('target_role_level')).lower()
        if rlevel and rlevel not in VALID_ROLE_LEVELS:
            result.warn(f"config.yaml: target_role_level '{rlevel}' not in allowed enums")

    # 3. Identity languages & work authorization
    id_path = TEMPLATE_ROOT / "identity" / "identity.yaml"
    if id_path.exists():
        with open(id_path, 'r', encoding='utf-8') as f:
            id_data = yaml.safe_load(f) or {}
        for lang in (id_data.get('languages') or []):
            if isinstance(lang, dict):
                lvl = as_text(lang.get('level')).lower()
                lname = as_text(lang.get('language'))
                if lvl and lvl not in VALID_LANGUAGE_FLUENCY:
                    result.warn(f"identity.yaml: Language '{lname}' has invalid fluency '{lvl}'")
        wauth_raw = id_data.get('work_authorization')
        if isinstance(wauth_raw, dict):
            wauth = as_text(wauth_raw.get('status')).lower()
        else:
            wauth = as_text(wauth_raw).lower()
        if wauth and wauth not in VALID_WORK_AUTHORIZATION:
            result.warn(f"identity.yaml: work_authorization status '{wauth}' not in allowed enums")

    # 4. Experience enums (employment_type, location_type, career_break_type)
    exp_path = TEMPLATE_ROOT / "identity" / "experience.yaml"
    if exp_path.exists():
        with open(exp_path, 'r', encoding='utf-8') as f:
            exp_data = yaml.safe_load(f) or {}
        for entry in (exp_data.get('experience') or []):
            if isinstance(entry, dict):
                comp = as_text(entry.get('company'))
                etype = as_text(entry.get('employment_type')).lower()
                if etype and etype not in VALID_EMPLOYMENT_TYPES:
                    result.warn(f"experience.yaml: Role at '{comp}' has invalid employment_type '{etype}'")
                ltype = as_text(entry.get('location_type')).lower()
                if ltype and ltype not in VALID_LOCATION_TYPES:
                    result.warn(f"experience.yaml: Role at '{comp}' has invalid location_type '{ltype}'")
        for brk in (exp_data.get('career_breaks') or []):
            if isinstance(brk, dict):
                btype = as_text(brk.get('type')).lower()
                btitle = as_text(brk.get('title'))
                if btype and btype not in VALID_CAREER_BREAK_TYPES:
                    result.warn(f"experience.yaml: Career break '{btitle}' has invalid type '{btype}'")

    # 5. Preferences enums (career_stage)
    pref_path = TEMPLATE_ROOT / "personal" / "preferences.yaml"
    if pref_path.exists():
        with open(pref_path, 'r', encoding='utf-8') as f:
            pref_data = yaml.safe_load(f) or {}
        cstage = as_text(pref_data.get('career_stage')).lower()
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
        company = as_text(entry.get('company'))
        start = as_text(entry.get('start_date'))
        end = as_text(entry.get('end_date'))

        if not company and not start:
            continue

        p_start = parse_flexible_date(start)
        p_end = parse_flexible_date(end, is_end_date=True)

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
        title = as_text(b.get('title'))
        start = as_text(b.get('start_date'))
        end = as_text(b.get('end_date'))

        if not title and not start:
            continue

        p_start = parse_flexible_date(start)
        p_end = parse_flexible_date(end, is_end_date=True)
        if p_start and p_end and p_start > p_end:
            result.warn(f"experience.yaml: Career break {i} ('{title}') has start_date '{start}' after end_date '{end}'")

    # Education in credentials.yaml
    creds_path = TEMPLATE_ROOT / "identity" / "credentials.yaml"
    if creds_path.exists():
        with open(creds_path, 'r', encoding='utf-8') as f:
            creds_data = yaml.safe_load(f) or {}
        for i, edu in enumerate(creds_data.get('education', []) or []):
            if not isinstance(edu, dict):
                continue
            inst = as_text(edu.get('institution') or edu.get('degree') or 'unnamed')
            start = as_text(edu.get('start_date'))
            end_val = edu.get('end_date') if edu.get('end_date') not in (None, "") else edu.get('year')
            end = "" if end_val in (0, "0", None) else as_text(end_val)
            if not start and not end:
                continue
            p_start = parse_flexible_date(start)
            p_end = parse_flexible_date(end, is_end_date=True)
            if start and p_start is None:
                result.warn(f"credentials.yaml: Education {i} ('{inst}') has invalid start_date '{start}' (expected YYYY-MM or YYYY)")
            if end and p_end is None:
                result.warn(f"credentials.yaml: Education {i} ('{inst}') has invalid end_date '{end}' (expected YYYY-MM or YYYY)")
            if p_start and p_end and p_start > p_end:
                result.warn(f"credentials.yaml: Education {i} ('{inst}') has start_date '{start}' after end_date '{end}'")

    # Projects in projects.yaml
    proj_path = TEMPLATE_ROOT / "identity" / "projects.yaml"
    if proj_path.exists():
        with open(proj_path, 'r', encoding='utf-8') as f:
            proj_data = yaml.safe_load(f) or {}
        all_projs = (proj_data.get('public', []) or []) + (proj_data.get('internal', []) or [])
        for i, p in enumerate(all_projs):
            if not isinstance(p, dict):
                continue
            pname = as_text(p.get('name') or 'unnamed')
            start = as_text(p.get('start_date'))
            end = as_text(p.get('end_date'))
            if not start and not end:
                continue
            p_start = parse_flexible_date(start)
            p_end = parse_flexible_date(end, is_end_date=True)
            if start and p_start is None:
                result.warn(f"projects.yaml: Project {i} ('{pname}') has invalid start_date '{start}' (expected YYYY-MM)")
            if end and p_end is None:
                result.warn(f"projects.yaml: Project {i} ('{pname}') has invalid end_date '{end}' (expected YYYY-MM or 'present')")
            if p_start and p_end and p_start > p_end:
                result.warn(f"projects.yaml: Project {i} ('{pname}') has start_date '{start}' after end_date '{end}'")

    # Volunteering in volunteering.yaml
    vol_path = TEMPLATE_ROOT / "identity" / "volunteering.yaml"
    if vol_path.exists():
        with open(vol_path, 'r', encoding='utf-8') as f:
            vol_data = yaml.safe_load(f) or {}
        for i, v in enumerate(vol_data.get('volunteering', []) or []):
            if not isinstance(v, dict):
                continue
            org = as_text(v.get('organization') or v.get('role') or 'unnamed')
            start = as_text(v.get('start_date'))
            end = as_text(v.get('end_date'))
            if not start and not end:
                continue
            p_start = parse_flexible_date(start)
            p_end = parse_flexible_date(end, is_end_date=True)
            if start and p_start is None:
                result.warn(f"volunteering.yaml: Entry {i} ('{org}') has invalid start_date '{start}' (expected YYYY-MM)")
            if end and p_end is None:
                result.warn(f"volunteering.yaml: Entry {i} ('{org}') has invalid end_date '{end}' (expected YYYY-MM or 'present')")
            if p_start and p_end and p_start > p_end:
                result.warn(f"volunteering.yaml: Entry {i} ('{org}') has start_date '{start}' after end_date '{end}'")


def check_identity_master_parity(result: ValidationResult):
    """Check parity between identity/ files and tools/resume/master.yaml (experience, projects, education, publications)."""
    master_path = TEMPLATE_ROOT / "tools" / "resume" / "master.yaml"
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
                comp = as_text(e.get('company') or e.get('organization') or e.get('client') or e.get('institution') or e.get('employer') or e.get('practice'))
                if comp:
                    id_companies.append(comp)

        if id_companies:
            master_exp = master_data.get('experience', {}) or {}
            master_companies = set()
            for k, v in master_exp.items():
                if k != '_example_role_' and isinstance(v, dict):
                    comp = as_text(v.get('company') or v.get('organization') or v.get('client'))
                    if comp:
                        master_companies.add(comp.lower())

            for comp in id_companies:
                if comp.lower() not in master_companies:
                    result.warn(
                        f"Parity: Employer '{comp}' in experience.yaml is not in tools/resume/master.yaml. "
                        f"Run 'python tools/resume/sync.py' to synchronize."
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
                pname = as_text(p.get('name'))
                if pname:
                    id_projects.append(pname)

        if id_projects:
            master_proj = master_data.get('projects', {}) or {}
            master_project_names = set()
            for k, v in master_proj.items():
                if isinstance(v, dict):
                    name = as_text(v.get('name') or k).lower()
                    master_project_names.add(name)
                elif isinstance(k, str):
                    master_project_names.add(k.lower())

            for pname in id_projects:
                if pname.lower() not in master_project_names:
                    result.warn(
                        f"Parity: Project '{pname}' in projects.yaml is not in tools/resume/master.yaml. "
                        f"Run 'python tools/resume/sync.py' to synchronize."
                    )

    # 3. Education & Publications Parity
    creds_path = TEMPLATE_ROOT / "identity" / "credentials.yaml"
    if creds_path.exists():
        with open(creds_path, 'r', encoding='utf-8') as f:
            creds_data = yaml.safe_load(f) or {}

        id_institutions = []
        for e in (creds_data.get('education', []) or []):
            if isinstance(e, dict):
                inst = as_text(e.get('institution'))
                if inst:
                    id_institutions.append(inst)

        if id_institutions:
            master_edu = master_data.get('education', []) or []
            master_insts = set()
            for e in master_edu:
                if isinstance(e, dict):
                    inst = as_text(e.get('institution')).lower()
                    if inst:
                        master_insts.add(inst)

            for inst in id_institutions:
                if inst.lower() not in master_insts:
                    result.warn(
                        f"Parity: Education institution '{inst}' in credentials.yaml is not in tools/resume/master.yaml. "
                        f"Run 'python tools/resume/sync.py' to synchronize."
                    )

        # 4. Publications Parity
        id_pubs = []
        for p in (creds_data.get('publications', []) or []):
            if isinstance(p, dict):
                pub_title = as_text(p.get('title') or p.get('name'))
                if pub_title:
                    id_pubs.append(pub_title)

        if id_pubs:
            master_pubs = master_data.get('publications', []) or []
            master_pub_titles = set()
            for p in master_pubs:
                if isinstance(p, dict):
                    t = as_text(p.get('title') or p.get('name')).lower()
                    if t:
                        master_pub_titles.add(t)

            for pub_title in id_pubs:
                if pub_title.lower() not in master_pub_titles:
                    result.warn(
                        f"Parity: Publication '{pub_title}' in credentials.yaml is not in tools/resume/master.yaml. "
                        f"Run 'python tools/resume/sync.py' to synchronize."
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

    # Common engineering deliverables keywords / formats that are implementation details rather than standalone career skills
    UNIVERSAL_ENGINEERING_TERMS = {
        'json', 'yaml', 'markdown', 'regex', 'apis', 'api development', 'rest api', 'rest apis',
        'git internals', '3-way merge', 'ast parsing', 'csv ingestion', 'validation schemas',
        'data modeling', 'data engineering', 'data processing', 'data analysis', 'data ingestion',
        'database normalization', 'etl', 'excel/json etl', 'eda', 'statistical analysis',
        'web interface', 'web terminals', 'websockets', 'streaming i/o', 'oauth 2.0', 'ssh',
        'scaffolding', 'benchmarking', 'load testing', 'leadership', 'team leadership', 'mentorship',
        'technical writing', 'technical interviewing', 'stakeholder communication', 'research',
        'market research', 'curriculum analysis', 'business process analysis', 'contract intelligence',
        'entrepreneurship', 'event management', 'game design', 'content curation', 'marketing automation',
        'product management', 'compliance', 'gri standards', 'sebi brsr', 'cve analysis', 'dast', 'sast',
        'enterprise security standards', 'security', 'security testing', 'security automation', 'security workflows',
        'html/css/js', 'html5 canvas', 'vanilla javascript', 'javascript', 'css3', 'bash 3.2', 'bash/cli',
        'cli/tui', 'faker', 'obs api', 'mkdocs', 'obsidian', 'low-code ui', 'lookml', 'nexpose report parsing',
        'architecture design', 'automation', 'automation design', 'data visualization'
    }

    known_skills = set(UNIVERSAL_ENGINEERING_TERMS)
    if isinstance(skills_data, dict):
        for cat, slist in skills_data.items():
            if cat != 'last_updated' and isinstance(slist, list):
                for s in slist:
                    if isinstance(s, dict):
                        name = str(s.get('name') or '').strip().lower()
                        if name:
                            known_skills.add(name)
                            # Split parenthetical and slash constituent parts
                            for part in re.split(r'[/&()]', name):
                                clean_p = part.strip().lower()
                                if len(clean_p) > 1:
                                    known_skills.add(clean_p)
                        # Support aliases, tools, and keywords
                        for a in (s.get('aliases') or []) + (s.get('tools') or []) + (s.get('keywords') or []):
                            clean_a = str(a).strip().lower()
                            if clean_a:
                                known_skills.add(clean_a)

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
        ("config.yaml", "config.yaml", lambda d: bool(as_text(((d or {}).get('user') or {}).get('name')))),
        ("identity/identity.yaml", "identity.yaml", lambda d: (
            bool(as_text((d or {}).get('name')))
            or bool((d or {}).get('total_years_experience', 0) > 0)
            or any(isinstance(l, dict) and bool(as_text(l.get('language'))) for l in ((d or {}).get('languages') or []))
            or bool(as_text((d or {}).get('nationality') or (d or {}).get('citizenship')))
            or bool(as_text(((d or {}).get('work_authorization') or {}).get('status') if isinstance((d or {}).get('work_authorization'), dict) else (d or {}).get('work_authorization')))
        )),
        ("identity/experience.yaml", "experience.yaml", lambda d: any(
            isinstance(e, dict) and bool(as_text(e.get('company') or e.get('organization') or e.get('client') or e.get('institution') or e.get('employer') or e.get('practice'))) for e in ((d or {}).get('experience') or [])
        )),
        ("identity/skills.yaml", "skills.yaml", lambda d: d is not None and any(
            isinstance(v, list) and any(isinstance(s, dict) and bool(as_text(s.get('name'))) for s in v)
            for v in (d or {}).values() if isinstance(v, list)
        )),
        ("identity/credentials.yaml", "credentials.yaml", lambda d: any(
            isinstance(e, dict) and bool(as_text(e.get('degree'))) for e in ((d or {}).get('education') or [])
        ) or any(
            isinstance(c, dict) and bool(as_text(c.get('name'))) for c in ((d or {}).get('certifications') or [])
        ) or any(
            isinstance(l, dict) and bool(as_text(l.get('name'))) for l in ((d or {}).get('licenses') or [])
        ) or any(
            isinstance(cl, dict) and bool(as_text(cl.get('level'))) for cl in ((d or {}).get('clearances') or [])
        ) or any(
            isinstance(p, dict) and bool(as_text(p.get('title'))) for p in ((d or {}).get('publications') or [])
        ) or any(
            isinstance(a, dict) and bool(as_text(a.get('title') or a.get('name'))) for a in ((d or {}).get('awards') or [])
        )),
        ("identity/projects.yaml", "projects.yaml", lambda d: any(
            isinstance(p, dict) and bool(as_text(p.get('name'))) for p in ((d or {}).get('public') or [])
        ) or any(
            isinstance(p, dict) and bool(as_text(p.get('name'))) for p in ((d or {}).get('internal') or [])
        )),
        ("identity/speaking-and-community.yaml", "speaking-and-community.yaml", lambda d: any(
            isinstance(s, dict) and bool(as_text(s.get('title'))) for s in ((d or {}).get('speaking') or [])
        ) or any(
            isinstance(h, dict) and bool(as_text(h.get('name'))) for h in ((d or {}).get('hackathons') or [])
        ), True),
        ("personal/preferences.yaml", "preferences.yaml", lambda d: bool(
            as_text((d or {}).get('career_stage')) or as_text((d or {}).get('career_anchor')) or (d or {}).get('work_values')
        ), False),
    ]

    for item in checks:
        filepath, label, check_fn = item[0], item[1], item[2]
        is_optional = item[3] if len(item) > 3 else False
        path = TEMPLATE_ROOT / filepath
        is_filled = False
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                if check_fn(data):
                    is_filled = True
            except Exception:
                status_lines.append(f"  ❌ {label} (parse error)")
                total += 1
                continue

        if is_filled:
            filled += 1
            total += 1
            opt_tag = " (optional)" if is_optional else ""
            status_lines.append(f"  ✅ {label}{opt_tag}")
        elif is_optional:
            status_lines.append(f"  ⚪ {label} (optional — skipped)")
        else:
            total += 1
            status_lines.append(f"  ⬜ {label} ({'empty' if path.exists() else 'not created'})")

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
            if s.startswith('### Role') and not s.startswith('### Role: [') and 'Role Name' not in s and '[' not in s:
                return True
            if s.startswith('|') and not s.startswith(('| #', '|:-', '|:--')):
                parts = [p.strip() for p in s.split('|')[1:-1]]
                if len(parts) >= 11 and parts[0].isdigit() and not parts[1].startswith('*Example') and parts[1] != '':
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
    result.note(f"\n📊 Core Career Knowledge Base: {filled}/{total} ({pct}%) [Verified Identity & Context Files]")
    for line in status_lines:
        result.note(line)

    # Satellite Resume Engine Status (On-Demand)
    master_path = TEMPLATE_ROOT / "tools" / "resume" / "master.yaml"
    master_filled = False
    if master_path.exists():
        try:
            with open(master_path, 'r', encoding='utf-8') as f:
                mdata = yaml.safe_load(f) or {}
            master_filled = any(k != '_example_role_' and isinstance(v, dict) for k, v in (mdata.get('experience') or {}).items())
        except Exception:
            pass

    result.note("\n🛰️ Satellite Resume Engine (On-Demand):")
    if master_filled:
        result.note("  ✅ tools/resume (master.yaml populated — ready to render)")
    else:
        result.note("  ⬜ tools/resume (master.yaml clean template — run 'python tools/resume/sync.py' when tailoring a CV)")



def check_freshness(result: ValidationResult, with_resume: bool = False):
    """Check freshness of YAML files with last_updated fields."""
    stale_files = []
    for f in YAML_FILES_TO_VALIDATE:
        if f in SATELLITE_FILES and not with_resume:
            continue
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
    parser.add_argument('--with-resume', action='store_true', help='Include on-demand resume cascade and master parity checks')
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
        check_evidence_paths(result)
        if getattr(args, 'with_resume', False):
            check_cascade_consistency(result)
        check_skill_enums(result)
        check_date_chronology(result)
        if getattr(args, 'with_resume', False):
            check_identity_master_parity(result)
        check_cross_file_consistency(result)
        check_freshness(result, with_resume=getattr(args, 'with_resume', False))
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
    check_evidence_paths(result)

    print("\n── Skill Enums ──")
    check_skill_enums(result)

    print("\n── Date Chronology ──")
    check_date_chronology(result)

    print("\n── Cross-File Consistency ──")
    check_cross_file_consistency(result)

    print("\n── Freshness Check ──")
    check_freshness(result, with_resume=getattr(args, 'with_resume', False))

    if getattr(args, 'with_resume', False):
        print("\n── Resume Cascade (On-Demand) ──")
        check_cascade_consistency(result)

        print("\n── Identity-Master Parity (On-Demand) ──")
        check_identity_master_parity(result)

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
