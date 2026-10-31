#!/usr/bin/env python3
"""
Resume Cascade Assembler — Merges master.yaml + variant overlays into RenderCV YAMLs.

Usage:
    python assemble.py                          # Build all variants
    python assemble.py --variant backend        # Build only matching variant
    python assemble.py --jd jd/company_role.yaml  # Build from JD-specific overlay
    python assemble.py --validate               # Validate all references without building
    python assemble.py --diff                   # Show what changed vs existing generated files
    python assemble.py --orphans                # Report unreferenced master bullets/roles
"""

import argparse
import copy
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# PyYAML is required — same environment as RenderCV (pip install pyyaml)
import yaml


# ============================================================================
# YAML Helpers — Imported from _yaml_utils with RenderCV schema header
# ============================================================================

try:
    from tools.resume._yaml_utils import OrderedDumper, PresentLiteral, dump_yaml as _base_dump_yaml, load_yaml
except ImportError:
    try:
        from _yaml_utils import OrderedDumper, PresentLiteral, dump_yaml as _base_dump_yaml, load_yaml
    except ImportError:
        from resume._yaml_utils import OrderedDumper, PresentLiteral, dump_yaml as _base_dump_yaml, load_yaml

try:
    from tools.resume.sync import identity_sources
except ImportError:
    try:
        from sync import identity_sources
    except ImportError:
        from resume.sync import identity_sources

RENDERCV_SCHEMA_HEADER = (
    "# yaml-language-server: $schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/v2.8/schema.json\n\n"
)


def dump_yaml(data: dict, path: Path):
    """Write a dict to a YAML file with clean formatting and RenderCV JSON schema directive."""
    _base_dump_yaml(data, path, header=RENDERCV_SCHEMA_HEADER)


LOCALE_MAP = {
    'en': 'english',
    'hi': 'hindi',
    'fr': 'french',
    'de': 'german',
    'es': 'spanish',
    'it': 'italian',
    'ja': 'japanese',
    'ko': 'korean',
    'zh': 'mandarin_chinese',
    'pt': 'portuguese',
    'ru': 'russian',
    'tr': 'turkish',
    'ar': 'arabic',
    'da': 'danish',
    'nl': 'dutch',
    'he': 'hebrew',
    'hu': 'hungarian',
    'id': 'indonesian',
    'fa': 'persian',
    'vi': 'vietnamese',
}


# ============================================================================
# Core Assembly Logic
# ============================================================================

class AssemblyError(Exception):
    """Raised when a variant references something that doesn't exist in master."""
    pass


SAFE_NAME_RE = re.compile(r'[\w][\w.\-]*')
TEMPLATE_PLACEHOLDERS = ('Write a 2-3 line summary', 'Tailored summary matching this specific JD')


def output_name(variant: dict, variant_name: str, default_name: str) -> str:
    """File name (without .yaml) this variant writes inside generated/; AssemblyError if unsafe."""
    raw = str(variant.get('output_filename') or '').strip()
    if raw.endswith(('.yaml', '.yml')):
        raw = raw.rsplit('.', 1)[0]
    if not raw:
        return re.sub(r'[^\w.\-]+', '_', f'{default_name}_{variant_name}_CV').strip('_')
    if not SAFE_NAME_RE.fullmatch(raw) or '..' in raw:
        raise AssemblyError(f"[{variant_name}] output_filename '{raw}' must be a plain file name "
                            f"(letters, digits, '.', '_' or '-'); files are written inside generated/")
    return raw


def clean_bullet_tags(text: str) -> str:
    """
    Strip internal verification tags ([measured], [estimated], [to-verify], [unverified], etc.)
    and internal verification emoji (✅, ⚠️, ❌) so outward-facing resumes remain clean and professional.
    """
    if not text:
        return ""
    # Strip bracketed verification tags, including optional notes e.g. [estimated: 10%]
    cleaned = re.sub(
        r'\s*\[(measured|estimated|to-verify|unverified|partially-verified)(?::[^\]]*)?\]',
        '',
        str(text),
        flags=re.IGNORECASE
    )
    # Strip any stray leading verification emoji if pasted from notes (including multi-code-point emoji like ⚠️)
    cleaned = re.sub(r'^[✅❌\u26a0\ufe0f]+\s*', '', cleaned)
    # Clean up double spaces or spaces before punctuation
    cleaned = re.sub(r'\s+([,.;])', r'\1', cleaned)
    cleaned = re.sub(r'  +', ' ', cleaned)
    return cleaned.strip()


def resolve_bullet(master_exp: dict, exp_key: str, bullet_ref, variant_name: str, keep_tags: bool = False) -> str:
    """
    Resolve a bullet reference to its text.
    bullet_ref can be:
      - "bullet_key"           → uses 'default' phrasing
      - ["bullet_key"]         → uses 'default' phrasing
      - ["bullet_key", "phrasing"] → uses specified phrasing
    """
    if isinstance(bullet_ref, str):
        if '.' in bullet_ref and bullet_ref not in master_exp.get('bullets', {}):
            bullet_key, phrasing = bullet_ref.split('.', 1)
        else:
            bullet_key = bullet_ref
            phrasing = "default"
    elif isinstance(bullet_ref, list):
        bullet_key = bullet_ref[0]
        phrasing = bullet_ref[1] if len(bullet_ref) > 1 else "default"
    else:
        raise AssemblyError(f"[{variant_name}] Invalid bullet reference format: {bullet_ref}")

    bullets = master_exp.get('bullets', {})
    if bullet_key not in bullets:
        available = list(bullets.keys())
        raise AssemblyError(
            f"[{variant_name}] Bullet key '{bullet_key}' not found in experience '{exp_key}'.\n"
            f"  Available bullets: {available}"
        )

    bullet_data = bullets[bullet_key]
    if isinstance(bullet_data, str):
        raw_text = bullet_data
    elif phrasing not in bullet_data or str(phrasing).startswith('_'):
        available = [k for k in bullet_data.keys() if not str(k).startswith('_')]
        raise AssemblyError(
            f"[{variant_name}] Phrasing '{phrasing}' not found for bullet '{bullet_key}' in '{exp_key}'.\n"
            f"  Available phrasings: {available}"
        )
    else:
        raw_text = bullet_data[phrasing]

    return raw_text if keep_tags else clean_bullet_tags(raw_text)


def resolve_project(master_projects: dict, project_ref, variant_name: str, keep_tags: bool = False) -> dict:
    """
    Resolve a project reference to a RenderCV project entry.
    project_ref can be:
      - "project_key"                              → uses 'default' bullet
      - ["project_key", "phrasing"]                → uses specified bullet phrasing
      - ["project_key", ["phrasing1", "phrasing2"]]→ uses multiple bullet phrasings
      - {"project_key": "phrasing"}                → dict syntax with phrasing
      - {"project_key": ["p1", "p2"]}              → dict syntax with multiple phrasings
      - {"project": "project_key", "bullets": [...]}→ explicit dict syntax
    """
    if isinstance(project_ref, str):
        proj_key = project_ref
        phrasings = ["default"]
    elif isinstance(project_ref, list):
        proj_key = project_ref[0]
        if len(project_ref) > 1:
            raw_p = project_ref[1]
            phrasings = raw_p if isinstance(raw_p, list) else [raw_p]
        else:
            phrasings = ["default"]
    elif isinstance(project_ref, dict):
        if 'project' in project_ref or 'name' in project_ref:
            proj_key = project_ref.get('project') or project_ref.get('name')
            if 'bullets' in project_ref:
                raw_b = project_ref['bullets']
                phrasings = raw_b if isinstance(raw_b, list) else [raw_b]
            elif 'bullet' in project_ref:
                phrasings = [project_ref['bullet']]
            elif 'phrasing' in project_ref:
                phrasings = [project_ref['phrasing']]
            else:
                phrasings = ["default"]
        else:
            proj_key = list(project_ref.keys())[0]
            val = project_ref[proj_key]
            phrasings = val if isinstance(val, list) else [val]
    else:
        raise AssemblyError(f"[{variant_name}] Invalid project reference: {project_ref}")

    if proj_key not in master_projects:
        available = list(master_projects.keys())
        raise AssemblyError(
            f"[{variant_name}] Project '{proj_key}' not found in master.\n"
            f"  Available projects: {available}"
        )

    proj = master_projects[proj_key]
    bullet_data = proj.get('bullets', {})

    highlights = []
    if isinstance(bullet_data, str):
        highlights.append(bullet_data if keep_tags else clean_bullet_tags(bullet_data))
    elif isinstance(bullet_data, list):
        for b in bullet_data:
            highlights.append(b if keep_tags else clean_bullet_tags(b))
    elif isinstance(bullet_data, dict):
        for phrasing in phrasings:
            if phrasing in bullet_data:
                b = bullet_data[phrasing]
                highlights.append(b if keep_tags else clean_bullet_tags(b))
            else:
                available = list(bullet_data.keys())
                raise AssemblyError(
                    f"[{variant_name}] Phrasing '{phrasing}' not found for project '{proj_key}'.\n"
                    f"  Available phrasings: {available}"
                )

    entry = {
        'name': proj.get('name', proj_key),
        'highlights': highlights,
    }
    date_val = proj.get('date')
    if not date_val:
        s_date = proj.get('start_date')
        e_date = proj.get('end_date')
        if s_date and e_date:
            date_val = f"{s_date} \u2013 {e_date}" if s_date != e_date else str(s_date)
        elif s_date:
            date_val = str(s_date)
    if date_val:
        entry['date'] = str(date_val)
    if 'location' in proj:
        entry['location'] = proj['location']
    if 'url' in proj:
        entry['url'] = proj['url']

    return entry


def merge_header(header: dict, config: dict = None, identity: dict = None) -> dict:
    """
    Merge contact info and profiles into empty master header fields.
    Precedence:
      1. master.yaml (existing non-empty header values)
      2. identity/identity.yaml (primary profile)
      3. config.yaml (fallback profile)
    """
    config = config or {}
    identity = identity or {}

    id_user = identity.get('user', {}) if isinstance(identity.get('user'), dict) else {}
    id_contact = identity.get('contact', {}) if isinstance(identity.get('contact'), dict) else {}
    id_loc = identity.get('location', {}) if isinstance(identity.get('location'), dict) else {}
    id_profiles = identity.get('profiles', {}) if isinstance(identity.get('profiles'), dict) else (
        identity.get('online_presence', {}) if isinstance(identity.get('online_presence'), dict) else {}
    )

    cfg_user = config.get('user', {}) if isinstance(config.get('user'), dict) else {}
    cfg_loc = config.get('location', {}) if isinstance(config.get('location'), dict) else {}
    cfg_profiles = config.get('profiles', {}) if isinstance(config.get('profiles'), dict) else {}

    # Name
    if not header.get('name'):
        name = (
            identity.get('name')
            or id_user.get('name')
            or cfg_user.get('name')
            or ''
        )
        if name:
            header['name'] = name

    # Headline
    if not header.get('headline'):
        headline = (
            identity.get('professional_headline')
            or identity.get('headline')
            or cfg_user.get('headline')
            or ''
        )
        if headline:
            header['headline'] = str(headline).strip()

    # Email
    if not header.get('email'):
        email = (
            identity.get('email')
            or id_contact.get('email')
            or cfg_user.get('email')
            or ''
        )
        if email:
            header['email'] = email

    # Phone
    if not header.get('phone'):
        phone = (
            identity.get('phone')
            or id_contact.get('phone')
            or cfg_user.get('phone')
            or ''
        )
        if phone:
            header['phone'] = phone

    # Website / portfolio
    if not header.get('website'):
        website = (
            identity.get('website')
            or id_profiles.get('website')
            or id_profiles.get('portfolio')
            or cfg_user.get('website')
            or cfg_profiles.get('portfolio')
            or ''
        )
        if website:
            header['website'] = website

    # Location (e.g. "Bangalore, Karnataka, IN" or "Bangalore, IN")
    if not header.get('location'):
        if isinstance(identity.get('location'), str) and identity.get('location').strip():
            header['location'] = identity.get('location').strip()
        else:
            loc_data = id_loc if id_loc else cfg_loc
            if isinstance(loc_data, dict):
                loc_parts = [p for p in [loc_data.get('city') or loc_data.get('current_city'), loc_data.get('region'), loc_data.get('country_code')] if p]
                if loc_parts:
                    header['location'] = ", ".join(loc_parts)

    # Social network mappings for RenderCV v2.8
    # RenderCV strictly allows: 'LinkedIn', 'GitHub', 'GitLab', 'IMDB', 'Instagram',
    # 'ORCID', 'Mastodon', 'StackOverflow', 'ResearchGate', 'YouTube', 'Google Scholar',
    # 'Telegram', 'WhatsApp', 'Leetcode', 'X', 'Bluesky', 'Reddit'
    NETWORK_MAPPINGS = {
        'linkedin': 'LinkedIn',
        'github': 'GitHub',
        'gitlab': 'GitLab',
        'twitter': 'X',
        'x': 'X',
        'bluesky': 'Bluesky',
        'mastodon': 'Mastodon',
        'stackoverflow': 'StackOverflow',
        'leetcode': 'Leetcode',
        'researchgate': 'ResearchGate',
        'orcid': 'ORCID',
        'google_scholar': 'Google Scholar',
        'googlescholar': 'Google Scholar',
        'youtube': 'YouTube',
        'instagram': 'Instagram',
        'reddit': 'Reddit',
        'telegram': 'Telegram',
        'whatsapp': 'WhatsApp',
        'imdb': 'IMDB',
    }

    social_networks = header.get('social_networks') or []
    if social_networks:
        normalized_nets = []
        for net in social_networks:
            if isinstance(net, dict):
                n_dict = copy.deepcopy(net)
                raw_net = str(n_dict.get('network', '')).strip().lower()
                if raw_net in ('twitter', 'x'):
                    n_dict['network'] = 'X'
                elif raw_net in NETWORK_MAPPINGS:
                    n_dict['network'] = NETWORK_MAPPINGS[raw_net]
                if 'username' in n_dict and isinstance(n_dict['username'], str):
                    u = n_dict['username'].strip()
                    clean_u = u.split('?')[0].split('#')[0].rstrip('/')
                    n_dict['username'] = clean_u.split('/')[-1] if '/' in clean_u else clean_u
                normalized_nets.append(n_dict)
            else:
                normalized_nets.append(net)
        header['social_networks'] = normalized_nets
    else:
        profiles = id_profiles if id_profiles else cfg_profiles
        if profiles and isinstance(profiles, dict):
            new_networks = []
            for prof_key, net_name in NETWORK_MAPPINGS.items():
                if prof_key in profiles and profiles[prof_key]:
                    url = str(profiles[prof_key]).strip()
                    if url:
                        clean_url = url.split('?')[0].split('#')[0].rstrip('/')
                        if 'scholar.google' in url.lower():
                            m_user = re.search(r'[?&]user=([^&]+)', url)
                            username = m_user.group(1) if m_user else (clean_url.split('/')[-1] if '/' in clean_url else clean_url)
                        else:
                            username = clean_url.split('/')[-1] if '/' in clean_url else clean_url
                        new_networks.append({'network': net_name, 'username': username})
            if new_networks:
                header['social_networks'] = new_networks

    return header


# Alias for backward compatibility
merge_header_from_config = merge_header


def assemble_variant(master: dict, design: dict, variant: dict, config: dict = None, identity: dict = None, keep_tags: bool = False) -> dict:
    """
    Assemble a complete RenderCV YAML from master data + variant overlay.
    Returns the full dict ready to be dumped as YAML.
    """
    variant_name = variant.get('variant_name', 'unknown')

    # --- Header ---
    raw_header = master.get('header', {}) or {}
    header = copy.deepcopy(raw_header)
    header = merge_header(header, config=config, identity=identity)
    if variant.get('headline'):
        header['headline'] = str(variant['headline']).strip()

    # --- Sections ---
    sections = {}

    # Summary
    if 'summary' in variant and variant['summary']:
        s_text = variant['summary']
        if not keep_tags and isinstance(s_text, str):
            s_text = clean_bullet_tags(s_text)
        sections['summary'] = [s_text]

    # Experience
    experience_entries = []
    master_exp = master.get('experience', {}) or {}
    variant_exp = variant.get('experience', {}) or {}
    for exp_key, bullet_refs in variant_exp.items():
        if exp_key not in master_exp:
            available = list(master_exp.keys())
            raise AssemblyError(
                f"[{variant_name}] Experience key '{exp_key}' not found in master.\n"
                f"  Available: {available}"
            )

        exp_data = master_exp[exp_key]
        highlights = []
        for ref in (bullet_refs or []):
            text = resolve_bullet(exp_data, exp_key, ref, variant_name, keep_tags=keep_tags)
            highlights.append(text)

        company = (
            exp_data.get('company')
            or exp_data.get('organization')
            or exp_data.get('client')
            or exp_data.get('institution')
            or exp_data.get('practice')
            or exp_data.get('employer')
        )
        if not company:
            raise AssemblyError(
                f"[{variant_name}] Experience entry '{exp_key}' missing required 'company'/'organization' field."
            )
        position = (
            exp_data.get('position')
            or exp_data.get('role')
            or exp_data.get('title')
        )
        if not position:
            raise AssemblyError(
                f"[{variant_name}] Experience entry '{exp_key}' missing required 'position'/'role' field."
            )
        start_date = exp_data.get('start_date')
        if not start_date:
            raise AssemblyError(
                f"[{variant_name}] Experience entry '{exp_key}' missing required 'start_date' field."
            )

        entry = {
            'company': str(company),
            'position': str(position),
            'start_date': str(start_date) if hasattr(start_date, 'isoformat') else start_date,
        }

        end_date = exp_data.get('end_date', 'present')
        if end_date == 'present' or end_date is None:
            entry['end_date'] = PresentLiteral('present')
        else:
            entry['end_date'] = str(end_date) if hasattr(end_date, 'isoformat') else end_date

        if 'location' in exp_data and exp_data['location']:
            entry['location'] = str(exp_data['location'])

        entry['highlights'] = highlights
        experience_entries.append(entry)

    if experience_entries:
        sections['experience'] = experience_entries

    # Projects
    project_entries = []
    variant_projects = variant.get('projects', []) or []
    master_projects = master.get('projects', {}) or {}
    for proj_ref in variant_projects:
        entry = resolve_project(master_projects, proj_ref, variant_name, keep_tags=keep_tags)
        project_entries.append(entry)
    if project_entries:
        sections['projects'] = project_entries

    # Technologies (variant overrides master; falls back to master shared technologies)
    if 'technologies' in variant and variant['technologies'] is not None:
        if variant['technologies']:
            sections['technologies'] = copy.deepcopy(variant['technologies'])
    elif master.get('technologies'):
        sections['technologies'] = copy.deepcopy(master['technologies'])

    # Education (variant overrides master; falls back to master shared education)
    if 'education' in variant and variant['education'] is not None:
        if variant['education']:
            sections['education'] = copy.deepcopy(variant['education'])
    elif master.get('education'):
        sections['education'] = [{k: v for k, v in e.items() if not str(k).startswith('_')}
                                 if isinstance(e, dict) else e for e in copy.deepcopy(master['education'])]

    # Achievements (resolve keys)
    achievement_texts = []
    master_achievements = master.get('achievements', {}) or {}
    for ach_key in (variant.get('achievements', []) or []):
        if ach_key not in master_achievements:
            available = list(master_achievements.keys())
            raise AssemblyError(
                f"[{variant_name}] Achievement key '{ach_key}' not found in master.\n"
                f"  Available: {available}"
            )
        ach_data = master_achievements[ach_key]
        if isinstance(ach_data, dict) and 'text' in ach_data:
            t = ach_data['text']
        else:
            t = str(ach_data)
        achievement_texts.append(t if keep_tags else clean_bullet_tags(t))
    if achievement_texts:
        sections['achievements'] = achievement_texts

    # Publications (RenderCV PublicationEntry)
    if 'publications' in variant and variant['publications']:
        if isinstance(variant['publications'], list):
            sections['publications'] = copy.deepcopy(variant['publications'])
        elif variant['publications'] is True and 'publications' in master:
            sections['publications'] = copy.deepcopy(master['publications'])
    elif 'publications' in master and master.get('publications') and variant.get('include_publications', False):
        sections['publications'] = copy.deepcopy(master['publications'])

    # Section ordering: variant can specify custom section_order, else default sequence
    default_order = ['summary', 'experience', 'projects', 'technologies', 'education', 'achievements', 'publications']
    custom_order = variant.get('section_order')
    if custom_order is not None:
        ordered_sections = {sec: sections[sec] for sec in custom_order if sec in sections}
    else:
        ordered_sections = {}
        for sec in default_order:
            if sec in sections:
                ordered_sections[sec] = sections[sec]
        for sec, val in sections.items():
            if sec not in ordered_sections:
                ordered_sections[sec] = val

    # --- Assemble final structure ---
    # RenderCV v2.8 strictly limits Cv fields to avoid extra_forbidden validation errors
    ALLOWED_CV_FIELDS = {
        'name', 'headline', 'location', 'email', 'phone', 'website',
        'social_networks', 'custom_connections', 'photo'
    }
    cv_data = {}
    for k, v in header.items():
        if k in ALLOWED_CV_FIELDS and v not in ("", None, []):
            cv_data[k] = copy.deepcopy(v)
    if 'name' not in cv_data:
        cv_data['name'] = header.get('name') or "Your Name"
    cv_data['sections'] = ordered_sections

    design_data = copy.deepcopy(design.get('design', {}) if design else {})
    if 'design' in variant and isinstance(variant['design'], dict):
        variant_design = copy.deepcopy(variant['design'])
        for k, v in variant_design.items():
            if isinstance(v, dict) and isinstance(design_data.get(k), dict):
                design_data[k].update(v)
            else:
                design_data[k] = v

    result = {
        'cv': cv_data,
        'design': design_data,
    }

    # Locale passthrough (config.yaml locale / variant locale)
    raw_locale = str(variant.get('locale') or (config.get('locale') if config else '') or '').strip().lower()
    if raw_locale:
        base_locale = raw_locale.split('-')[0].split('_')[0].strip()
        lang_name = LOCALE_MAP.get(base_locale, LOCALE_MAP.get(raw_locale, raw_locale))
        result['locale'] = {'language': lang_name}

    # Settings block (RenderCV v2.8)
    settings = copy.deepcopy(master.get('settings', {}) or {})
    if 'settings' in variant and isinstance(variant['settings'], dict):
        settings.update(variant['settings'])
    if settings:
        result['settings'] = settings

    return result


# ============================================================================
# Validation
# ============================================================================

def validate_variant(master: dict, variant: dict) -> list[str]:
    """Validate a variant overlay against master. Returns list of error messages."""
    errors = []
    if not variant:
        return ["Variant file is empty"]
    variant_name = variant.get('variant_name', 'unknown')

    summary = ' '.join(str(variant.get('summary') or '').split())
    if summary.startswith(TEMPLATE_PLACEHOLDERS):
        errors.append(f"[{variant_name}] summary still holds the template placeholder text; "
                      f"write a real summary or leave it empty")

    # Check experience keys and bullets
    variant_exp = variant.get('experience') or {}
    master_exp = master.get('experience') or {}
    for exp_key, bullet_refs in variant_exp.items():
        if exp_key not in master_exp:
            errors.append(f"[{variant_name}] Experience '{exp_key}' not in master")
            continue
        exp_data = master_exp[exp_key]
        if isinstance(exp_data, dict) and exp_data.get('archived') is True:
            print(f"   ℹ️ [{variant_name}] References role '{exp_key}' marked archived: true")
        for ref in (bullet_refs or []):
            try:
                resolve_bullet(exp_data, exp_key, ref, variant_name)
            except AssemblyError as e:
                errors.append(str(e))

    # Check project keys
    for proj_ref in (variant.get('projects') or []):
        try:
            resolve_project(master.get('projects') or {}, proj_ref, variant_name)
        except AssemblyError as e:
            errors.append(str(e))

    # Check achievement keys
    master_achievements = master.get('achievements') or {}
    for ach_key in (variant.get('achievements') or []):
        if ach_key not in master_achievements:
            errors.append(f"[{variant_name}] Achievement '{ach_key}' not in master")

    return errors


UNVERIFIED_RE = re.compile(r'\[(?:unverified|to-verify)(?::[^\]]*)?\]|\u274c', re.IGNORECASE)
ESTIMATED_RE = re.compile(r'\[(?:estimated|partially-verified)(?::[^\]]*)?\]|\u26a0', re.IGNORECASE)
STATUS_UNVERIFIED_RE = re.compile(r'\u274c|\bUNVERIFIED\b|\bto-verify\b', re.IGNORECASE)
STATUS_ESTIMATED_RE = re.compile(r'\u26a0|\bESTIMATED\b|\bpartially[- ]verified\b', re.IGNORECASE)


def _all_text(value) -> str:
    """Every string inside a bullet (all phrasings, including _source) joined into one string."""
    if isinstance(value, dict):
        return ' '.join(_all_text(v) for v in value.values())
    if isinstance(value, list):
        return ' '.join(_all_text(v) for v in value)
    return '' if value is None else str(value)


def project_key(ref) -> str:
    """The master.yaml project key a variant's project reference points to (same rules as resolve_project)."""
    if isinstance(ref, str):
        return ref
    if isinstance(ref, list) and ref:
        return str(ref[0])
    if isinstance(ref, dict) and ref:
        return str(ref.get('project') or ref.get('name') or next(iter(ref)))
    return ''


def selected_claims(master: dict, variant: dict):
    """Yield (label, raw text, status) for every claim a variant puts on the resume, before tags are stripped.
    status is the bullet's `_verification` (copied by sync.py from identity/), or ''."""
    master_exp = master.get('experience') or {}
    for exp_key, refs in (variant.get('experience') or {}).items():
        bullets = (master_exp.get(exp_key) or {}).get('bullets') or {}
        for ref in (refs or []):
            key = ref[0] if isinstance(ref, list) and ref else str(ref)
            if key not in bullets and '.' in key:
                key = key.split('.', 1)[0]
            if key in bullets:
                bullet = bullets[key]
                status = str(bullet.get('_verification') or '') if isinstance(bullet, dict) else ''
                yield f"{exp_key}.{key}", _all_text(bullet), status
    master_projects = master.get('projects') or {}
    for ref in (variant.get('projects') or []):
        try:
            entry = resolve_project(master_projects, ref, '', keep_tags=True)
        except AssemblyError:
            continue  # reported by validate_variant
        project = master_projects.get(project_key(ref)) or {}
        status = str(project.get('_verification') or '') if isinstance(project, dict) else ''
        for highlight in entry.get('highlights', []):
            yield f"project {entry.get('name')}", str(highlight), status
    achievements = master.get('achievements') or {}
    for key in (variant.get('achievements') or []):
        if key in achievements:
            ach = achievements[key]
            status = str(ach.get('_verification') or '') if isinstance(ach, dict) else ''
            yield f"achievement {key}", _all_text(ach), status
    custom_order = variant.get('section_order')
    if variant.get('education') is None and (custom_order is None or 'education' in custom_order):
        for entry in (master.get('education') or []):
            if isinstance(entry, dict):
                label = f"education {entry.get('degree') or ''} {entry.get('institution') or ''}".rstrip()
                shown = {k: v for k, v in entry.items() if not str(k).startswith('_')}
                yield label, _all_text(shown), str(entry.get('_verification') or '')
    if variant.get('summary'):
        yield 'summary', str(variant['summary']), ''


def check_unverified(master: dict, variant: dict):
    """Return (errors, warnings): errors for unverified claims, warnings for estimated ones."""
    name = variant.get('variant_name', 'unknown')
    errors, warnings = [], []
    for label, text, status in selected_claims(master, variant):
        if UNVERIFIED_RE.search(text) or STATUS_UNVERIFIED_RE.search(status):
            errors.append(f"[{name}] {label}: unverified claim (❌, [unverified] or [to-verify]); "
                          f"recommended to verify in identity/ before submitting")
        elif ESTIMATED_RE.search(text) or STATUS_ESTIMATED_RE.search(status):
            warnings.append(f"[{name}] {label}: estimated claim; use carefully")
    return errors, warnings


def check_sources(master: dict, variant: dict, sources: dict):
    """Return (stale, unsourced) errors for selected roles and bullets, judged against identity/experience.yaml."""
    name = variant.get('variant_name', 'unknown')
    stale, unsourced = [], []
    master_exp = master.get('experience') or {}
    for exp_key, refs in (variant.get('experience') or {}).items():
        role = master_exp.get(exp_key)
        if not isinstance(role, dict):
            continue  # reported by validate_variant
        source = role.get('_source')
        if source is None:
            unsourced.append(f"[{name}] {exp_key}: unsourced role (not created by sync.py from identity/experience.yaml); "
                             f"add it to identity/ and run sync.py")
            continue
        if source not in sources:
            stale.append(f"[{name}] {exp_key}: stale role; identity/experience.yaml no longer has '{source}'. "
                         f"Run sync.py and select the current role key")
            continue
        bullets = role.get('bullets') or {}
        for ref in (refs or []):
            key = ref[0] if isinstance(ref, list) and ref else str(ref)
            if key not in bullets and '.' in key:
                key = key.split('.', 1)[0]
            bullet = bullets.get(key)
            if bullet is None:
                continue  # reported by validate_variant
            b_source = bullet.get('_source') if isinstance(bullet, dict) else None
            if b_source is None:
                unsourced.append(f"[{name}] {exp_key}.{key}: unsourced bullet (typed into master.yaml); "
                                 f"add it to identity/experience.yaml and run sync.py")
            elif b_source not in sources[source]:
                stale.append(f"[{name}] {exp_key}.{key}: stale bullet; its text in identity/experience.yaml "
                             f"changed or was removed. Run sync.py and select the current bullet")
    return stale, unsourced


def check_orphans(master: dict, overlay_paths: list[Path]) -> bool:
    """Analyze master.yaml for entries never referenced in any variant or JD overlay."""
    if not overlay_paths:
        print("ℹ️  No active variants found in tools/resume/variants/ or tools/resume/jd/ to check against.")
        print("   Create a variant (e.g. tools/resume/variants/A_Role.yaml) first.")
        return True

    referenced_roles = set()
    referenced_bullets = {}  # exp_key -> set of bullet keys
    referenced_projects = set()
    referenced_achievements = set()

    for p in overlay_paths:
        data = load_yaml(p) or {}
        # Experience
        for exp_key, bullet_refs in (data.get('experience') or {}).items():
            referenced_roles.add(exp_key)
            if exp_key not in referenced_bullets:
                referenced_bullets[exp_key] = set()
            for ref in (bullet_refs or []):
                if isinstance(ref, str):
                    b_key = ref.split('.', 1)[0] if ('.' in ref and ref not in (master.get('experience', {}).get(exp_key, {}).get('bullets', {}) or {})) else ref
                    referenced_bullets[exp_key].add(b_key)
                elif isinstance(ref, list) and ref:
                    referenced_bullets[exp_key].add(ref[0])

        # Projects
        for proj_ref in (data.get('projects') or []):
            if isinstance(proj_ref, str):
                referenced_projects.add(proj_ref)
            elif isinstance(proj_ref, list) and proj_ref:
                referenced_projects.add(proj_ref[0])
            elif isinstance(proj_ref, dict):
                for k in proj_ref.keys():
                    referenced_projects.add(k)

        # Achievements
        for ach_ref in (data.get('achievements') or []):
            if isinstance(ach_ref, str):
                referenced_achievements.add(ach_ref)

    master_exp = master.get('experience') or {}
    master_proj = master.get('projects') or {}
    master_ach = master.get('achievements') or {}

    unref_roles = []
    unref_bullets = {}
    for role_key, role_data in master_exp.items():
        if role_key == '_example_role_':
            continue
        is_archived = bool(isinstance(role_data, dict) and role_data.get('archived') is True)
        if role_key not in referenced_roles:
            unref_roles.append((role_key, is_archived))
        else:
            bullets = (role_data.get('bullets') or {}) if isinstance(role_data, dict) else {}
            used = referenced_bullets.get(role_key, set())
            unused = [b for b in bullets if b not in used]
            if unused:
                unref_bullets[role_key] = unused

    unref_projects = [p for p in master_proj.keys() if p not in referenced_projects]
    unref_achievements = [a for a in master_ach.keys() if a not in referenced_achievements]

    print(f"🔍 Orphan Analysis across {len(overlay_paths)} active variant overlay(s):\n")

    has_orphans = False

    if unref_roles:
        has_orphans = True
        print(f"💼 Unreferenced Experience Roles ({len(unref_roles)}):")
        for r, is_arch in unref_roles:
            tag = " [archived]" if is_arch else ""
            print(f"   - {r}{tag}")
        print()

    if unref_bullets:
        has_orphans = True
        total_unused_b = sum(len(b) for b in unref_bullets.values())
        print(f"📝 Unreferenced Bullets in Referenced Roles ({total_unused_b}):")
        for r, b_list in unref_bullets.items():
            print(f"   • {r}:")
            for b in b_list:
                print(f"       - {b}")
        print()

    if unref_projects:
        has_orphans = True
        print(f"🚀 Unreferenced Projects ({len(unref_projects)}):")
        for p in unref_projects:
            print(f"   - {p}")
        print()

    if unref_achievements:
        has_orphans = True
        print(f"🏆 Unreferenced Achievements ({len(unref_achievements)}):")
        for a in unref_achievements:
            print(f"   - {a}")
        print()

    if not has_orphans:
        print("✅ No orphaned master entries found. All master roles, projects, and achievements are referenced!")

    return not has_orphans


# ============================================================================
# CLI Driver
# ============================================================================

def main():
    # Ensure UTF-8 output on Windows consoles
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description='Resume Cascade Assembler')
    parser.add_argument('--variant', '-v', help='Build only this variant (matches filename prefix, e.g. "A")')
    parser.add_argument('--jd', help='Build from a JD-specific overlay file')
    parser.add_argument('--render', '-r', action='store_true', help='Immediately render assembled YAML files to PDF with RenderCV')
    parser.add_argument('--keep-tags', action='store_true', help='Keep verification tags ([measured], [estimated]) in output')
    parser.add_argument('--validate', action='store_true', help='Validate only, no output')
    parser.add_argument('--diff', action='store_true', help='Show what would change vs existing generated files')
    parser.add_argument('--orphans', action='store_true', help='Detect and report unreferenced master.yaml bullets, roles, projects, and achievements')
    parser.add_argument('--no-autofill', action='store_true', help='Disable auto-filling header from config.yaml')
    parser.add_argument('--allow-unverified', action='store_true',
                        help='Build even when a selected claim is marked ❌, [unverified] or [to-verify]')
    parser.add_argument('--allow-unsourced', action='store_true',
                        help='Build even when a selected role or bullet was typed into master.yaml instead of synced from identity/')
    args = parser.parse_args()

    # Paths relative to this script
    script_dir = Path(__file__).resolve().parent
    master_path = script_dir / 'master.yaml'
    design_path = script_dir / 'design.yaml'
    variants_dir = script_dir / 'variants'
    generated_dir = script_dir / 'generated'

    # Validate prerequisites
    if not master_path.exists():
        print(f"ERROR: {master_path} not found", file=sys.stderr)
        sys.exit(1)
    if not design_path.exists():
        print(f"ERROR: {design_path} not found", file=sys.stderr)
        sys.exit(1)

    master = load_yaml(master_path) or {}
    design = load_yaml(design_path) or {}

    if args.orphans:
        all_overlays = []
        if variants_dir.exists():
            all_overlays.extend([f for f in sorted(variants_dir.glob('*.yaml')) if not f.name.startswith('_')])
        jd_dir = script_dir / 'jd'
        if jd_dir.exists():
            all_overlays.extend([f for f in sorted(jd_dir.glob('*.yaml')) if not f.name.startswith('_')])
        check_orphans(master, all_overlays)
        return

    # Read identity/identity.yaml and config.yaml for header auto-fill and filenames
    repo_root = script_dir.parent.parent  # tools/resume/ → repo root
    identity_path = repo_root / 'identity' / 'identity.yaml'
    config_path = repo_root / 'config.yaml'
    identity_data = {}
    config_data = {}
    default_name = 'Resume'

    if identity_path.exists():
        identity_data = load_yaml(identity_path) or {}

    if config_path.exists():
        config_data = load_yaml(config_path) or {}

    experience_path = repo_root / 'identity' / 'experience.yaml'
    sources = identity_sources(load_yaml(experience_path) if experience_path.exists() else {})

    user_name = (
        identity_data.get('name')
        or (identity_data.get('user', {}) or {}).get('name')
        or ((config_data.get('user', {}) or {}).get('name', ''))
        or ''
    )
    if user_name.strip():
        default_name = user_name.strip().replace(' ', '_')

    if args.no_autofill:
        config_for_assembly = None
        identity_for_assembly = None
    else:
        config_for_assembly = config_data
        identity_for_assembly = identity_data

    # Check if master.yaml is currently only the template placeholder
    master_exp = master.get('experience') or {}
    if list(master_exp.keys()) == ['_example_role_']:
        print("ℹ️  Note: tools/resume/master.yaml currently contains the '_example_role_' placeholder.")
        print("   Remember to add your real experience to master.yaml before generating final resumes.\n")

    # Determine which overlays to process
    if args.jd:
        jd_path = Path(args.jd)
        if not jd_path.is_absolute():
            if jd_path.exists():
                jd_path = jd_path.resolve()
            elif (script_dir / jd_path).exists():
                jd_path = (script_dir / jd_path).resolve()
            elif (repo_root / jd_path).exists():
                jd_path = (repo_root / jd_path).resolve()
            else:
                jd_path = (script_dir / jd_path).resolve()
        if not jd_path.exists():
            print(f"ERROR: JD overlay {jd_path} not found", file=sys.stderr)
            sys.exit(1)
        overlay_files = [jd_path]
    else:
        if not variants_dir.exists():
            print(f"ERROR: {variants_dir} directory not found", file=sys.stderr)
            sys.exit(1)
        all_variants = sorted(variants_dir.glob('*.yaml'))
        if args.variant:
            overlay_files = [f for f in all_variants if f.stem.upper().startswith(args.variant.upper())]
            if not overlay_files:
                print(f"ERROR: No variant matching '{args.variant}' found in {variants_dir}", file=sys.stderr)
                sys.exit(1)
        else:
            # Exclude template scaffolding files starting with '_'
            overlay_files = [f for f in all_variants if not f.name.startswith('_')]
            if not overlay_files:
                print(
                    "ℹ️  No active variants found in tools/resume/variants/ (found _template.yaml).\n"
                    "   To create your first variant, copy tools/resume/variants/_template.yaml:\n"
                    "     cp tools/resume/variants/_template.yaml tools/resume/variants/A_RoleName.yaml\n"
                    "   Then edit A_RoleName.yaml with your bullet selections and run assemble.py again."
                )
                if args.validate:
                    print("✅ master.yaml and design.yaml are valid.")
                    return
                return

    # Pre-pass: check output filename collisions
    planned = {}
    for overlay_path in overlay_files:
        overlay = load_yaml(overlay_path) or {}
        overlay_name = (overlay.get('variant_name') or '').strip() or overlay_path.stem
        try:
            planned.setdefault(output_name(overlay, overlay_name, default_name), []).append(overlay_path.name)
        except AssemblyError:
            pass  # reported below for that overlay
    collisions = {name: files for name, files in planned.items() if len(files) > 1}
    if collisions:
        for name, files in collisions.items():
            print(f"❌ {', '.join(files)} all write generated/{name}.yaml; give each variant its own output_filename")
        sys.exit(1)

    # Process each overlay
    total_errors = 0
    built = 0

    for overlay_path in overlay_files:
        variant = load_yaml(overlay_path) or {}
        variant_name = (variant.get('variant_name') or '').strip() or overlay_path.stem

        # Validate
        errors = validate_variant(master, variant)
        if not errors:
            claim_errors, claim_warnings = check_unverified(master, variant)
            for warning in claim_warnings:
                print(f"   ⚠️  {warning}")
            for error in claim_errors:
                print(f"   ⚠️  unverified: {error}")
            stale, unsourced = check_sources(master, variant, sources)
            for warning in unsourced:
                print(f"   ⚠️  unsourced: {warning}")
            order = variant.get('section_order')
            for section in ('technologies', 'education'):
                if variant.get(section) == [] and master.get(section) and (order is None or section in order):
                    print(f"   ⚠️  [{variant_name}] {section}: [] hides master.yaml's {section} in this variant. Delete "
                          f"the line to show it; to hide it on purpose, leave {section} out of section_order instead "
                          f"(variants copied from the v0.1.0 template carry technologies: [])")
            errors = stale

        if errors:
            print(f"\n❌ {variant_name} — {len(errors)} error(s):")
            for e in errors:
                print(f"   {e}")
            total_errors += len(errors)
            continue

        if args.validate:
            print(f"✅ {variant_name} — all references valid")
            continue

        # Assemble
        try:
            result = assemble_variant(
                master, design, variant,
                config=config_for_assembly,
                identity=identity_for_assembly,
                keep_tags=args.keep_tags
            )
        except AssemblyError as e:
            print(f"\n❌ {variant_name} — Assembly error:\n   {e}")
            total_errors += 1
            continue

        # Output filename: from variant or auto-generated from config.yaml name
        try:
            output_filename = output_name(variant, variant_name, default_name)
        except AssemblyError as e:
            print(f"\n❌ {variant_name} — {e}")
            total_errors += 1
            continue
        output_path = generated_dir / f'{output_filename}.yaml'

        if args.diff and output_path.exists():
            existing = output_path.read_text(encoding='utf-8')
            import io
            buf = io.StringIO()
            buf.write("# yaml-language-server: $schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/v2.8/schema.json\n\n")
            yaml.dump(result, buf, Dumper=OrderedDumper, default_flow_style=False,
                      allow_unicode=True, width=200, sort_keys=False)
            new_content = buf.getvalue()
            if existing == new_content:
                print(f"✅ {variant_name} — no changes")
            else:
                print(f"🔄 {variant_name} — content would change")
            continue

        dump_yaml(result, output_path)
        built += 1
        print(f"✅ {variant_name} → {output_path.relative_to(script_dir)}")

    # Summary
    print()
    if args.validate:
        if total_errors:
            print(f"Validation FAILED — {total_errors} error(s) found")
            sys.exit(1)
        else:
            print(f"Validation PASSED — all {len(overlay_files)} variant(s) valid")
    elif not args.diff:
        if total_errors:
            print(f"Built {built}/{len(overlay_files)} variant(s) — {total_errors} error(s)")
            sys.exit(1)
        else:
            print(f"Built {built} variant(s) successfully → generated/")

        if args.render and built > 0:
            print(f"\n🎨 Rendering {built} variant(s) to PDF via RenderCV...")
            output_base_dir = (script_dir / 'output').resolve()
            output_base_dir.mkdir(parents=True, exist_ok=True)
            render_env = os.environ.copy()
            render_env["PYTHONUTF8"] = "1"
            render_env["PYTHONIOENCODING"] = "utf-8"

            # Check if rendercv is available via current python interpreter or CLI
            rc_cmd = None
            test_proc = subprocess.run(
                [sys.executable, "-m", "rendercv", "--version"],
                capture_output=True, env=render_env, stdin=subprocess.DEVNULL
            )
            if test_proc.returncode == 0:
                rc_cmd = [sys.executable, "-m", "rendercv"]
            elif shutil.which("rendercv"):
                rc_cmd = ["rendercv"]

            if not rc_cmd:
                print("  ❌ RenderCV not found (it needs Python 3.12+). Install it in the virtual environment: "
                      "python -m pip install -r tools/resume/requirements.txt")
                sys.exit(1)
            else:
                render_errors = 0
                for overlay_path in overlay_files:
                    variant = load_yaml(overlay_path) or {}
                    variant_name = (variant.get('variant_name') or '').strip() or overlay_path.stem
                    try:
                        output_filename = output_name(variant, variant_name, default_name)
                    except AssemblyError:
                        continue
                    gen_yaml = (generated_dir / f'{output_filename}.yaml').resolve()
                    if not gen_yaml.exists():
                        continue

                    var_out_dir = (output_base_dir / output_filename).resolve()
                    var_out_dir.mkdir(parents=True, exist_ok=True)

                    full_cmd = rc_cmd + ["render", str(gen_yaml), "-o", str(var_out_dir)]
                    res = subprocess.run(full_cmd, capture_output=True, text=True,
                                         encoding='utf-8', errors='replace', env=render_env, stdin=subprocess.DEVNULL)
                    if res.returncode == 0:
                        pdf_files = list(var_out_dir.glob("*.pdf"))
                        if pdf_files:
                            target_pdf = output_base_dir / f"{output_filename}.pdf"
                            shutil.copy2(pdf_files[0], target_pdf)
                            print(f"  ✅ Rendered: {variant_name} → tools/resume/output/{output_filename}.pdf")
                        else:
                            print(f"  ✅ Rendered: {variant_name} (in tools/resume/output/{output_filename}/)")
                    else:
                        render_errors += 1
                        err_out = (res.stderr or res.stdout or "").strip()
                        print(f"  ❌ RenderCV failed for {variant_name}:\n{err_out}")
                if render_errors:
                    sys.exit(1)


if __name__ == '__main__':
    main()
