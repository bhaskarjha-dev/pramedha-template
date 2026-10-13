#!/usr/bin/env python3
"""
Resume Cascade Assembler — Merges master.yaml + variant overlays into RenderCV YAMLs.

Usage:
    python assemble.py                          # Build all variants
    python assemble.py --variant backend        # Build only matching variant
    python assemble.py --jd jd/company_role.yaml  # Build from JD-specific overlay
    python assemble.py --validate               # Validate all references without building
    python assemble.py --diff                   # Show what changed vs existing generated files
"""

import argparse
import copy
import sys
from pathlib import Path

# PyYAML is required — same environment as RenderCV (pip install pyyaml)
import yaml


# ============================================================================
# YAML Helpers — Preserve key order, handle RenderCV's 'present' literal
# ============================================================================

class OrderedDumper(yaml.SafeDumper):
    """Dump YAML preserving insertion order and using block style."""
    pass

def _dict_representer(dumper, data):
    return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items())

def _str_representer(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    if len(data) > 80:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

def _present_representer(dumper, data):
    """Handle the bare word 'present' (no quotes) for RenderCV end_date."""
    if data == 'present':
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

OrderedDumper.add_representer(dict, _dict_representer)


class PresentLiteral(str):
    """Marker class for the bare word 'present' in YAML output."""
    pass

def _present_literal_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', str(data), style='')

OrderedDumper.add_representer(PresentLiteral, _present_literal_representer)


def load_yaml(path: Path) -> dict:
    """Load a YAML file, returning its contents as a dict."""
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def dump_yaml(data: dict, path: Path):
    """Write a dict to a YAML file with clean formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, Dumper=OrderedDumper, default_flow_style=False,
                  allow_unicode=True, width=200, sort_keys=False)


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


def merge_header_from_config(header: dict, config: dict) -> dict:
    """
    Merge contact info and profiles from config.yaml into empty master header fields.
    Master values always take precedence if already non-empty.
    """
    if not config:
        return header

    user = config.get('user', {}) or {}
    loc = config.get('location', {}) or {}
    profiles = config.get('profiles', {}) or {}

    # Name
    if not header.get('name') and user.get('name'):
        header['name'] = user['name']

    # Email
    if not header.get('email') and user.get('email'):
        header['email'] = user['email']

    # Phone
    if not header.get('phone') and user.get('phone'):
        header['phone'] = user['phone']

    # Website / portfolio
    if not header.get('website'):
        website = user.get('website') or profiles.get('portfolio') or ''
        if website:
            header['website'] = website

    # Location (e.g. "Bangalore, Karnataka, IN" or "Bangalore, IN")
    if not header.get('location'):
        loc_parts = [p for p in [loc.get('city'), loc.get('region'), loc.get('country_code')] if p]
        if loc_parts:
            header['location'] = ", ".join(loc_parts)

    # Social networks (RenderCV format: list of dicts with network and username)
    social_networks = header.get('social_networks') or []
    if not social_networks and profiles:
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


def assemble_variant(master: dict, design: dict, variant: dict, config: dict = None) -> dict:
    """
    Assemble a complete RenderCV YAML from master data + variant overlay.
    Returns the full dict ready to be dumped as YAML.
    """
    variant_name = variant.get('variant_name', 'unknown')

    # --- Header ---
    raw_header = master.get('header', {}) or {}
    header = copy.deepcopy(raw_header)
    if config:
        header = merge_header_from_config(header, config)

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

    # Technologies (verbatim from variant)
    if 'technologies' in variant and variant['technologies']:
        sections['technologies'] = variant['technologies']

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

    # --- Assemble final structure ---
    cv_data = copy.deepcopy(header)
    cv_data['sections'] = sections

    design_data = design.get('design', {}) if design else {}
    result = {
        'cv': cv_data,
        'design': copy.deepcopy(design_data),
    }

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

    # Read config.yaml for header auto-fill and filenames
    config_path = script_dir.parent / 'config.yaml'
    config_data = {}
    default_name = 'Resume'
    if config_path.exists():
        config_data = load_yaml(config_path) or {}
        user_name = ((config_data.get('user', {}) or {}).get('name', '')) or ''
        if user_name.strip():
            default_name = user_name.strip().replace(' ', '_')

    if args.no_autofill:
        config_for_assembly = None
    else:
        config_for_assembly = config_data

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
        variant_name = variant.get('variant_name', overlay_path.stem)

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
            result = assemble_variant(master, design, variant, config=config_for_assembly)
        except AssemblyError as e:
            print(f"\n❌ {variant_name} — Assembly error:\n   {e}")
            total_errors += 1
            continue

        # Output filename: from variant or auto-generated from config.yaml name
        output_filename = variant.get('output_filename', f'{default_name}_{variant_name}_CV')
        output_path = generated_dir / f'{output_filename}.yaml'

        if args.diff and output_path.exists():
            existing = output_path.read_text(encoding='utf-8')
            import io
            buf = io.StringIO()
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
