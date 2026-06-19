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


def assemble_variant(master: dict, design: dict, variant: dict) -> dict:
    """
    Assemble a complete RenderCV YAML from master data + variant overlay.
    Returns the full dict ready to be dumped as YAML.
    """
    variant_name = variant.get('variant_name', 'unknown')

    # --- Header ---
    header = copy.deepcopy(master['header'])

    # --- Sections ---
    sections = {}

    # Summary
    sections['summary'] = [variant['summary']]

    # Experience
    experience_entries = []
    master_exp = master['experience']
    for exp_key, bullet_refs in variant['experience'].items():
        if exp_key not in master_exp:
            available = list(master_exp.keys())
            raise AssemblyError(
                f"[{variant_name}] Experience key '{exp_key}' not found in master.\n"
                f"  Available: {available}"
            )

        exp_data = master_exp[exp_key]
        highlights = []
        for ref in bullet_refs:
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

        if 'location' in exp_data:
            entry['location'] = exp_data['location']

        entry['highlights'] = highlights
        experience_entries.append(entry)

    sections['experience'] = experience_entries

    # Projects
    project_entries = []
    for proj_ref in variant['projects']:
        entry = resolve_project(master['projects'], proj_ref, variant_name)
        project_entries.append(entry)
    sections['projects'] = project_entries

    # Technologies (verbatim from variant)
    sections['technologies'] = variant['technologies']

    # Education (from master, shared)
    sections['education'] = copy.deepcopy(master['education'])

    # Achievements (resolve keys)
    achievement_texts = []
    master_achievements = master['achievements']
    for ach_key in variant['achievements']:
        if ach_key not in master_achievements:
            available = list(master_achievements.keys())
            raise AssemblyError(
                f"[{variant_name}] Achievement key '{ach_key}' not found in master.\n"
                f"  Available: {available}"
            )
        achievement_texts.append(master_achievements[ach_key]['text'])
    sections['achievements'] = achievement_texts

    # --- Assemble final structure ---
    cv_data = copy.deepcopy(header)
    cv_data['sections'] = sections

    result = {
        'cv': cv_data,
        'design': copy.deepcopy(design['design']),
    }

    return result


# ============================================================================
# Validation
# ============================================================================

def validate_variant(master: dict, variant: dict) -> list[str]:
    """Validate a variant overlay against master. Returns list of error messages."""
    errors = []
    variant_name = variant.get('variant_name', 'unknown')

    # Check experience keys and bullets
    for exp_key, bullet_refs in variant.get('experience', {}).items():
        if exp_key not in master.get('experience', {}):
            errors.append(f"[{variant_name}] Experience '{exp_key}' not in master")
            continue
        exp_data = master['experience'][exp_key]
        for ref in bullet_refs:
            try:
                resolve_bullet(exp_data, exp_key, ref, variant_name)
            except AssemblyError as e:
                errors.append(str(e))

    # Check project keys
    for proj_ref in variant.get('projects', []):
        try:
            resolve_project(master.get('projects', {}), proj_ref, variant_name)
        except AssemblyError as e:
            errors.append(str(e))

    # Check achievement keys
    for ach_key in variant.get('achievements', []):
        if ach_key not in master.get('achievements', {}):
            errors.append(f"[{variant_name}] Achievement '{ach_key}' not in master")

    return errors


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Resume Cascade Assembler')
    parser.add_argument('--variant', '-v', help='Build only this variant (matches filename prefix, e.g. "A")')
    parser.add_argument('--jd', help='Build from a JD-specific overlay file')
    parser.add_argument('--validate', action='store_true', help='Validate only, no output')
    parser.add_argument('--diff', action='store_true', help='Show what would change vs existing generated files')
    args = parser.parse_args()

    # Resolve paths relative to this script
    script_dir = Path(__file__).parent
    master_path = script_dir / 'master.yaml'
    design_path = script_dir / 'design.yaml'
    variants_dir = script_dir / 'variants'
    generated_dir = script_dir / 'generated'

    # Load master and design
    if not master_path.exists():
        print(f"ERROR: {master_path} not found", file=sys.stderr)
        sys.exit(1)
    if not design_path.exists():
        print(f"ERROR: {design_path} not found", file=sys.stderr)
        sys.exit(1)

    master = load_yaml(master_path)
    design = load_yaml(design_path)

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
        overlay_files = sorted(variants_dir.glob('*.yaml'))
        if args.variant:
            overlay_files = [f for f in overlay_files if f.stem.upper().startswith(args.variant.upper())]
            if not overlay_files:
                print(f"ERROR: No variant matching '{args.variant}' found in {variants_dir}", file=sys.stderr)
                sys.exit(1)

    # Read user name from config.yaml once (for default output filenames)
    config_path = script_dir.parent / 'config.yaml'
    default_name = 'Resume'
    if config_path.exists():
        config_data = load_yaml(config_path)
        user_name = ((config_data or {}).get('user', {}) or {}).get('name', '')
        if user_name:
            default_name = user_name.replace(' ', '_')

    # Process each overlay
    total_errors = 0
    built = 0

    for overlay_path in overlay_files:
        variant = load_yaml(overlay_path)
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
            result = assemble_variant(master, design, variant)
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
