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
import sys
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# PyYAML is required — same environment as RenderCV (pip install pyyaml)
import yaml


# ============================================================================
# YAML Helpers — Imported from _yaml_utils with RenderCV schema header
# ============================================================================

try:
    from resume._yaml_utils import OrderedDumper, PresentLiteral, dump_yaml as _base_dump_yaml, load_yaml
except ImportError:
    from _yaml_utils import OrderedDumper, PresentLiteral, dump_yaml as _base_dump_yaml, load_yaml

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


def resolve_bullet(master_exp: dict, exp_key: str, bullet_ref, variant_name: str) -> str:
    """
    Resolve a bullet reference to its text.
    bullet_ref can be:
      - "bullet_key"           → uses 'default' phrasing
      - ["bullet_key"]         → uses 'default' phrasing
      - ["bullet_key", "phrasing"] → uses specified phrasing
    """
    if isinstance(bullet_ref, str):
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
        return bullet_data

    if phrasing not in bullet_data:
        available = list(bullet_data.keys())
        raise AssemblyError(
            f"[{variant_name}] Phrasing '{phrasing}' not found for bullet '{bullet_key}' in '{exp_key}'.\n"
            f"  Available phrasings: {available}"
        )

    return bullet_data[phrasing]


def resolve_project(master_projects: dict, project_ref, variant_name: str) -> dict:
    """
    Resolve a project reference to a RenderCV project entry.
    project_ref can be:
      - "project_key"                    → uses 'default' bullet
      - ["project_key", "phrasing"]      → uses specified bullet phrasing
      - {"project_key": "phrasing"}      → alternate dict syntax (not used currently)
    """
    if isinstance(project_ref, str):
        proj_key = project_ref
        phrasing = "default"
    elif isinstance(project_ref, list):
        proj_key = project_ref[0]
        phrasing = project_ref[1] if len(project_ref) > 1 else "default"
    elif isinstance(project_ref, dict):
        proj_key = list(project_ref.keys())[0]
        phrasing = project_ref[proj_key]
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

    if isinstance(bullet_data, str):
        bullet_text = bullet_data
    elif phrasing not in bullet_data:
        available = list(bullet_data.keys())
        raise AssemblyError(
            f"[{variant_name}] Phrasing '{phrasing}' not found for project '{proj_key}'.\n"
            f"  Available phrasings: {available}"
        )
    else:
        bullet_text = bullet_data[phrasing]

    entry = {
        'name': proj['name'],
        'date': proj['date'],
        'highlights': [bullet_text],
    }
    if 'location' in proj:
        entry['location'] = proj['location']

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

    # Social networks (RenderCV format: list of dicts with network and username)
    social_networks = header.get('social_networks') or []
    if not social_networks:
        profiles = id_profiles if id_profiles else cfg_profiles
        if profiles:
            new_networks = []
            if profiles.get('linkedin'):
                url = str(profiles['linkedin']).strip()
                if url:
                    username = url.rstrip('/').split('/')[-1] if '/' in url else url
                    new_networks.append({'network': 'LinkedIn', 'username': username})
            if profiles.get('github'):
                url = str(profiles['github']).strip()
                if url:
                    username = url.rstrip('/').split('/')[-1] if '/' in url else url
                    new_networks.append({'network': 'GitHub', 'username': username})
            if profiles.get('twitter'):
                url = str(profiles['twitter']).strip()
                if url:
                    username = url.rstrip('/').split('/')[-1] if '/' in url else url
                    new_networks.append({'network': 'Twitter', 'username': username})
            if new_networks:
                header['social_networks'] = new_networks

    return header


# Alias for backward compatibility
merge_header_from_config = merge_header


def assemble_variant(master: dict, design: dict, variant: dict, config: dict = None, identity: dict = None) -> dict:
    """
    Assemble a complete RenderCV YAML from master data + variant overlay.
    Returns the full dict ready to be dumped as YAML.
    """
    variant_name = variant.get('variant_name', 'unknown')

    # --- Header ---
    raw_header = master.get('header', {}) or {}
    header = copy.deepcopy(raw_header)
    header = merge_header(header, config=config, identity=identity)

    # --- Sections ---
    sections = {}

    # Summary
    if 'summary' in variant and variant['summary']:
        sections['summary'] = [variant['summary']]

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
            text = resolve_bullet(exp_data, exp_key, ref, variant_name)
            highlights.append(text)

        entry = {
            'company': exp_data['company'],
            'position': exp_data['position'],
            'start_date': exp_data['start_date'],
        }

        end_date = exp_data.get('end_date', 'present')
        if end_date == 'present':
            entry['end_date'] = PresentLiteral('present')
        else:
            entry['end_date'] = end_date

        if 'location' in exp_data and exp_data['location']:
            entry['location'] = exp_data['location']

        entry['highlights'] = highlights
        experience_entries.append(entry)

    if experience_entries:
        sections['experience'] = experience_entries

    # Projects
    project_entries = []
    variant_projects = variant.get('projects', []) or []
    master_projects = master.get('projects', {}) or {}
    for proj_ref in variant_projects:
        entry = resolve_project(master_projects, proj_ref, variant_name)
        project_entries.append(entry)
    if project_entries:
        sections['projects'] = project_entries

    # Technologies (variant overrides master; falls back to master shared technologies)
    technologies = variant.get('technologies') or master.get('technologies', [])
    if technologies:
        sections['technologies'] = copy.deepcopy(technologies)

    # Education (from master, shared)
    if 'education' in master and master['education']:
        sections['education'] = copy.deepcopy(master['education'])

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
            achievement_texts.append(ach_data['text'])
        else:
            achievement_texts.append(str(ach_data))
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
    section_order = variant.get('section_order') or default_order
    ordered_sections = {}
    for sec in section_order:
        if sec in sections:
            ordered_sections[sec] = sections[sec]
    for sec, val in sections.items():
        if sec not in ordered_sections:
            ordered_sections[sec] = val

    # --- Assemble final structure ---
    cv_data = {}
    for k, v in header.items():
        if v not in ("", None, []):
            cv_data[k] = copy.deepcopy(v)
    if 'name' not in cv_data:
        cv_data['name'] = header.get('name') or "Your Name"
    cv_data['sections'] = ordered_sections

    design_data = design.get('design', {}) if design else {}
    result = {
        'cv': cv_data,
        'design': copy.deepcopy(design_data),
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


def check_orphans(master: dict, overlay_paths: list[Path]) -> bool:
    """Analyze master.yaml for entries never referenced in any variant or JD overlay."""
    if not overlay_paths:
        print("ℹ️  No active variants found in resume/variants/ or resume/jd/ to check against.")
        print("   Create a variant (e.g. resume/variants/A_Role.yaml) first.")
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
                    referenced_bullets[exp_key].add(ref)
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
    parser.add_argument('--validate', action='store_true', help='Validate only, no output')
    parser.add_argument('--diff', action='store_true', help='Show what would change vs existing generated files')
    parser.add_argument('--orphans', action='store_true', help='Detect and report unreferenced master.yaml bullets, roles, projects, and achievements')
    parser.add_argument('--no-autofill', action='store_true', help='Disable auto-filling header from config.yaml')
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
    identity_path = script_dir.parent / 'identity' / 'identity.yaml'
    config_path = script_dir.parent / 'config.yaml'
    identity_data = {}
    config_data = {}
    default_name = 'Resume'

    if identity_path.exists():
        identity_data = load_yaml(identity_path) or {}

    if config_path.exists():
        config_data = load_yaml(config_path) or {}

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
        print("ℹ️  Note: resume/master.yaml currently contains the '_example_role_' placeholder.")
        print("   Remember to add your real experience to master.yaml before generating final resumes.\n")

    # Determine which overlays to process
    if args.jd:
        jd_path = Path(args.jd)
        if not jd_path.is_absolute():
            jd_path = script_dir / jd_path
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
                    "ℹ️  No active variants found in resume/variants/ (found _template.yaml).\n"
                    "   To create your first variant, copy resume/variants/_template.yaml:\n"
                    "     cp resume/variants/_template.yaml resume/variants/A_RoleName.yaml\n"
                    "   Then edit A_RoleName.yaml with your bullet selections and run assemble.py again."
                )
                if args.validate:
                    print("✅ master.yaml and design.yaml are valid.")
                    return
                return

    # Process each overlay
    total_errors = 0
    built = 0

    for overlay_path in overlay_files:
        variant = load_yaml(overlay_path) or {}
        variant_name = (variant.get('variant_name') or '').strip() or overlay_path.stem

        # Validate
        errors = validate_variant(master, variant)
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
            result = assemble_variant(master, design, variant, config=config_for_assembly, identity=identity_for_assembly)
        except AssemblyError as e:
            print(f"\n❌ {variant_name} — Assembly error:\n   {e}")
            total_errors += 1
            continue

        # Output filename: from variant or auto-generated from config.yaml name
        output_filename = (variant.get('output_filename') or '').strip()
        if not output_filename:
            output_filename = f'{default_name}_{variant_name}_CV' if default_name else f'{variant_name}_CV'
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


if __name__ == '__main__':
    main()
