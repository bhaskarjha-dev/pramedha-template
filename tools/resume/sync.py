#!/usr/bin/env python3
"""
Identity to Master Resume Synchronizer — Syncs verified facts from identity/ to tools/resume/master.yaml.

Reads:
  - identity/experience.yaml             → master.yaml experience pool
  - identity/projects.yaml               → master.yaml projects pool
  - identity/credentials.yaml            → master.yaml education, publications, certs & awards
  - identity/speaking-and-community.yaml → master.yaml achievements (hackathons)
  - identity/skills.yaml                 → master.yaml technologies

Usage:
    py tools/resume/sync.py                 # Sync all sections (safe merge, preserves existing)
    py tools/resume/sync.py --dry-run       # Preview changes without modifying master.yaml
    py tools/resume/sync.py --section exp   # Sync specific section (exp, proj, edu, pubs, skills, ach, all)
    py tools/resume/sync.py --force         # Overwrite existing keys with identity values
"""

import argparse
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
    print("ERROR: PyYAML required. Install: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# ============================================================================
# YAML Helpers (Order-preserving) — Imported from _yaml_utils
# ============================================================================

try:
    from tools.resume._yaml_utils import OrderedDumper, dump_yaml, load_yaml
except ImportError:
    try:
        from _yaml_utils import OrderedDumper, dump_yaml, load_yaml
    except ImportError:
        from resume._yaml_utils import OrderedDumper, dump_yaml, load_yaml


# ============================================================================
# Slug & Key Generation
# ============================================================================

STOP_WORDS = {
    'a', 'an', 'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'with',
    'of', 'by', 'from', 'up', 'down', 'out', 'over', 'into', 'built', 'created'
}


def slugify(text: str) -> str:
    """Convert text into a snake_case slug (Unicode-aware)."""
    text = (text or '').strip().lower()
    text = re.sub(r'[^\w]+', '_', text, flags=re.UNICODE)
    return text.strip('_')


def generate_role_key(company: str, position: str, existing_keys: set) -> str:
    """Generate a unique snake_case key for an employer role."""
    comp_slug = slugify(company) or 'company'
    pos_slug = slugify(position) or 'role'
    base = f"{comp_slug}_{pos_slug}"
    key = base
    counter = 2
    while key in existing_keys:
        key = f"{base}_{counter}"
        counter += 1
    return key


def generate_project_key(name: str, existing_keys: set) -> str:
    """Generate a unique snake_case key for a project."""
    base = slugify(name) or 'project'
    key = base
    counter = 2
    while key in existing_keys:
        key = f"{base}_{counter}"
        counter += 1
    return key


def generate_bullet_key(bullet_text: str, existing_keys: set, fallback_idx: int = 1) -> str:
    """Extract 2-4 keywords from a bullet to create an informative snake_case key."""
    # Remove bracketed tags like [measured], [estimated]
    cleaned = re.sub(r'\[.*?\]', '', bullet_text)
    words = [w.lower() for w in re.findall(r'[\w]+', cleaned, flags=re.UNICODE)]
    meaningful = [w for w in words if w not in STOP_WORDS]
    if meaningful:
        base = "_".join(meaningful[:3])
    else:
        base = f"bullet_{fallback_idx}"

    key = base
    counter = 2
    while key in existing_keys:
        key = f"{base}_{counter}"
        counter += 1
    return key


def generate_achievement_key(name: str, existing_keys: set, prefix: str = "") -> str:
    """Generate a unique snake_case key for an achievement."""
    base_slug = slugify(name)
    if prefix and not base_slug.startswith(prefix):
        base = f"{prefix}_{base_slug}"
    else:
        base = base_slug or prefix or 'achievement'
    key = base
    counter = 2
    while key in existing_keys:
        key = f"{base}_{counter}"
        counter += 1
    return key


# ============================================================================
# Sync Logic
# ============================================================================

def is_blank_str(val) -> bool:
    return val is None or (isinstance(val, str) and not val.strip())


def sync_experience(id_data: dict, master_data: dict, force: bool = False):
    """
    Sync identity/experience.yaml into master.yaml['experience'].
    Flattens projects -> deliverables -> bullets.
    """
    exp_entries = id_data.get('experience', []) or []
    master_exp = master_data.get('experience', {}) or {}
    if not isinstance(master_exp, dict):
        master_exp = {}

    stats = {'added_roles': 0, 'added_bullets': 0, 'updated_roles': 0, 'skipped': 0}
    existing_keys = set(master_exp.keys())

    for entry in exp_entries:
        if not isinstance(entry, dict):
            continue

        company = (entry.get('company') or entry.get('client') or entry.get('organization') or entry.get('institution') or entry.get('employer') or entry.get('practice') or '').strip()
        position = (entry.get('position') or entry.get('title') or entry.get('role') or '').strip()
        start_date = entry.get('start_date', '').strip()
        end_date = entry.get('end_date', 'present')
        location = entry.get('location', '').strip()

        # Skip empty template scaffolding
        if not company and not position and not start_date:
            stats['skipped'] += 1
            continue

        # Look for matching existing role by company + position + start_date
        matching_key = None
        for k, v in master_exp.items():
            if isinstance(v, dict):
                same_comp = v.get('company', '').lower() == company.lower()
                same_pos = v.get('position', '').lower() == position.lower()
                same_start = str(v.get('start_date', '')).strip() == str(start_date).strip()
                if same_comp and same_pos and (same_start or not v.get('start_date')):
                    matching_key = k
                    break

        if not matching_key:
            role_key = generate_role_key(company, position, existing_keys)
            existing_keys.add(role_key)
            master_exp[role_key] = {
                'company': company,
                'position': position,
                'start_date': start_date,
                'end_date': end_date or 'present',
                'location': location,
                'bullets': {}
            }
            stats['added_roles'] += 1
            matching_key = role_key
        else:
            role_key = matching_key
            if force:
                master_exp[role_key]['start_date'] = start_date
                master_exp[role_key]['end_date'] = end_date or 'present'
                if location:
                    master_exp[role_key]['location'] = location
                stats['updated_roles'] += 1

        # Extract bullets from deliverables
        role_bullets = master_exp[role_key].setdefault('bullets', {})
        if not isinstance(role_bullets, dict):
            role_bullets = {}
            master_exp[role_key]['bullets'] = role_bullets

        existing_bullet_keys = set(role_bullets.keys())
        bullet_idx = 1

        projects = entry.get('projects', []) or []
        for p in projects:
            if not isinstance(p, dict):
                continue
            client = str(p.get('client') or '').strip()
            deliverables = p.get('deliverables', []) or []
            for d in deliverables:
                if not isinstance(d, dict):
                    continue
                bullets = d.get('bullets', []) or []
                for b in bullets:
                    b_text = str(b).strip()
                    if not b_text:
                        continue

                    # If project has a specific client attribute, preserve attribution in default bullet
                    if client and not b_text.lower().startswith(f"[{client.lower()}]"):
                        final_text = f"[{client}] {b_text}"
                    else:
                        final_text = b_text

                    # Check if text already exists under any phrasing
                    already_present = False
                    for b_data in role_bullets.values():
                        if isinstance(b_data, str) and (b_data == final_text or b_data == b_text):
                            already_present = True
                            break
                        elif isinstance(b_data, dict) and (final_text in b_data.values() or b_text in b_data.values()):
                            already_present = True
                            break

                    if not already_present:
                        b_key = generate_bullet_key(b_text, existing_bullet_keys, bullet_idx)
                        existing_bullet_keys.add(b_key)
                        role_bullets[b_key] = {'default': final_text}
                        stats['added_bullets'] += 1
                        bullet_idx += 1

    # Sync career breaks as archived roles (available for variants to select)
    career_breaks = id_data.get('career_breaks', []) or []
    for b in career_breaks:
        if not isinstance(b, dict):
            continue
        b_title = str(b.get('title') or '').strip()
        b_start = str(b.get('start_date') or '').strip()
        if not b_title and not b_start:
            continue

        break_slug = slugify(b_title)[:20].strip('_') or 'transition'
        break_key = f"career_break_{break_slug}"
        if break_key not in master_exp:
            desc = str(b.get('description') or '').strip()
            bullets = {'summary': {'default': desc}} if desc else {'summary': {'default': b_title}}
            master_exp[break_key] = {
                'company': b_title,
                'position': 'Career Transition / Sabbatical',
                'start_date': b_start,
                'end_date': str(b.get('end_date') or 'present').strip(),
                'location': '',
                'archived': True,
                'bullets': bullets
            }
            stats['added_roles'] += 1
            stats['added_bullets'] += len(bullets)

    master_data['experience'] = master_exp
    return stats


def sync_projects(id_data: dict, master_data: dict, force: bool = False):
    """
    Sync public and internal projects from identity/projects.yaml into master.yaml['projects'].
    """
    master_proj = master_data.get('projects', {}) or {}
    if not isinstance(master_proj, dict):
        master_proj = {}

    stats = {'added': 0, 'updated': 0, 'skipped': 0}
    existing_keys = set(master_proj.keys())

    all_projects = []
    for p in (id_data.get('public', []) or []):
        if isinstance(p, dict):
            all_projects.append(p)
    for p in (id_data.get('internal', []) or []):
        if isinstance(p, dict):
            all_projects.append(p)

    for p in all_projects:
        name = p.get('name', '').strip()
        if not name:
            stats['skipped'] += 1
            continue

        repo = p.get('repo', '').strip()
        live_url = p.get('live_url', '').strip()
        location = repo or live_url or p.get('context', '').strip()

        start = p.get('start_date', '').strip()
        end = p.get('end_date', '').strip()
        if start and end:
            date_str = f"{start} – {end}"
        elif start:
            date_str = start
        elif end:
            date_str = end
        else:
            date_str = ""

        # Find or create key
        proj_key = None
        for k, v in master_proj.items():
            if isinstance(v, dict) and v.get('name', '').lower() == name.lower():
                proj_key = k
                break

        if not proj_key:
            proj_key = generate_project_key(name, existing_keys)
            existing_keys.add(proj_key)
            highlights = p.get('highlights', []) or []
            bullets_dict = {}
            if highlights:
                first_bullet = str(highlights[0]).strip()
                if first_bullet:
                    bullets_dict['default'] = first_bullet
                if len(highlights) > 1:
                    tech_bullet = str(highlights[1]).strip()
                    if tech_bullet:
                        bullets_dict['technical'] = tech_bullet
            else:
                tagline = p.get('tagline', '').strip()
                if tagline:
                    bullets_dict['default'] = tagline

            master_proj[proj_key] = {
                'name': name,
                'date': date_str,
                'location': location,
                'bullets': bullets_dict
            }
            stats['added'] += 1
        elif force:
            if date_str:
                master_proj[proj_key]['date'] = date_str
            if location:
                master_proj[proj_key]['location'] = location
            stats['updated'] += 1

    master_data['projects'] = master_proj
    return stats


def sync_education(id_data: dict, master_data: dict, force: bool = False):
    """
    Sync education from identity/credentials.yaml into master.yaml['education'].
    """
    edu_list = id_data.get('education', []) or []
    master_edu = master_data.get('education', []) or []
    if not isinstance(master_edu, list):
        master_edu = []

    stats = {'added': 0, 'skipped': 0}

    for item in edu_list:
        if not isinstance(item, dict):
            continue
        institution = item.get('institution', '').strip()
        degree = item.get('degree', '').strip()
        field = item.get('field', '').strip()
        year = str(item.get('year', '')).strip()

        if not institution and not degree:
            stats['skipped'] += 1
            continue

        # Check if already present
        exists = any(
            isinstance(e, dict) and
            e.get('institution', '').lower() == institution.lower() and
            e.get('degree', '').lower() == degree.lower()
            for e in master_edu
        )

        if not exists:
            highlights = []
            score = item.get('score', '').strip() if item.get('score') else ''
            if score:
                highlights.append(f"Score: {score}")
            for honor in (item.get('honors', []) or []):
                h_str = str(honor).strip()
                if h_str:
                    highlights.append(h_str)

            start_date = str(item.get('start_date') or '').strip()
            end_date = str(item.get('end_date') or item.get('year') or '').strip()

            entry = {
                'institution': institution,
                'area': field,
                'degree': degree,
            }
            if start_date:
                entry['start_date'] = start_date
            if end_date:
                entry['end_date'] = end_date
            if highlights:
                entry['highlights'] = highlights

            master_edu.append(entry)
            stats['added'] += 1

    master_data['education'] = master_edu
    return stats


def sync_publications(id_data: dict, master_data: dict, force: bool = False):
    """
    Sync publications from identity/credentials.yaml into master.yaml['publications'].
    """
    pubs_list = id_data.get('publications', []) or []
    master_pubs = master_data.get('publications', []) or []
    if not isinstance(master_pubs, list):
        master_pubs = []

    stats = {'added': 0, 'skipped': 0}

    for item in pubs_list:
        if not isinstance(item, dict):
            continue
        title = (item.get('title') or item.get('name') or '').strip()
        if not title:
            stats['skipped'] += 1
            continue

        exists = any(
            isinstance(p, dict) and p.get('title', '').lower() == title.lower()
            for p in master_pubs
        )

        if not exists:
            entry = {
                'title': title,
                'authors': [str(a).strip() for a in (item.get('authors', []) or []) if str(a).strip()],
                'date': str(item.get('year') or item.get('date') or '').strip(),
                'journal': (item.get('publisher') or item.get('journal') or '').strip(),
            }
            if item.get('url'):
                entry['url'] = str(item['url']).strip()
            if item.get('doi'):
                entry['doi'] = str(item['doi']).strip()

            master_pubs.append(entry)
            stats['added'] += 1

    master_data['publications'] = master_pubs
    return stats


def sync_skills(id_data: dict, master_data: dict, force: bool = False):
    """
    Sync skills from identity/skills.yaml into master.yaml['technologies']
    using RenderCV OneLineEntry format (label: Category, details: "Skill1, Skill2").
    """
    master_tech = master_data.get('technologies', []) or []
    if not isinstance(master_tech, list):
        master_tech = []

    stats = {'added': 0, 'updated': 0, 'skipped': 0}
    if not isinstance(id_data, dict):
        return stats

    for cat_name, skills in id_data.items():
        if cat_name in ('last_updated',) or not isinstance(skills, list):
            continue

        skill_names = []
        for s in skills:
            if isinstance(s, dict):
                name = str(s.get('name') or '').strip()
                if name:
                    skill_names.append(name)
            elif isinstance(s, str) and s.strip():
                skill_names.append(s.strip())

        if not skill_names:
            stats['skipped'] += 1
            continue

        cat_label = cat_name.replace('_', ' ').title()
        details_str = ", ".join(skill_names)

        # Check if category label already exists in master technologies
        existing_idx = None
        for idx, entry in enumerate(master_tech):
            if isinstance(entry, dict) and entry.get('label', '').lower() == cat_label.lower():
                existing_idx = idx
                break

        if existing_idx is not None:
            if force:
                master_tech[existing_idx]['details'] = details_str
                stats['updated'] += 1
        else:
            master_tech.append({
                'label': cat_label,
                'details': details_str
            })
            stats['added'] += 1

    master_data['technologies'] = master_tech
    return stats


def sync_achievements(creds_data: dict, community_data: dict, master_data: dict, force: bool = False):
    """
    Sync achievements from identity/credentials.yaml (awards, certifications)
    and identity/speaking-and-community.yaml (hackathons) into master.yaml['achievements'].
    """
    master_ach = master_data.get('achievements', {})
    if not isinstance(master_ach, dict):
        master_ach = {}

    stats = {'added': 0, 'updated': 0, 'skipped': 0}
    existing_keys = set(master_ach.keys())

    # 1. Awards from credentials.yaml
    for item in (creds_data.get('awards', []) or []):
        if not isinstance(item, dict):
            continue
        title = (item.get('title') or '').strip()
        if not title:
            stats['skipped'] += 1
            continue
        awarder = (item.get('awarder') or '').strip()
        year = str(item.get('year') or '').strip()
        if year == '0':
            year = ''
        details = (item.get('details') or '').strip()

        parts = [title]
        meta = []
        if awarder:
            meta.append(awarder)
        if year:
            meta.append(year)
        if meta:
            parts.append(f"({' — '.join(meta)})")
        if details:
            parts.append(f"— {details}")
        text = " ".join(parts)

        ach_key = None
        for k, v in master_ach.items():
            if isinstance(v, dict) and v.get('text', '').lower() == text.lower():
                ach_key = k
                break
            elif isinstance(v, str) and v.lower() == text.lower():
                ach_key = k
                break

        if not ach_key:
            ach_key = generate_achievement_key(title, existing_keys, prefix="award")
            existing_keys.add(ach_key)
            master_ach[ach_key] = {'text': text}
            stats['added'] += 1
        elif force:
            master_ach[ach_key] = {'text': text}
            stats['updated'] += 1

    # 2. Certifications from credentials.yaml
    for item in (creds_data.get('certifications', []) or []):
        if not isinstance(item, dict):
            continue
        name = (item.get('name') or '').strip()
        if not name:
            stats['skipped'] += 1
            continue
        issuer = (item.get('issuer') or '').strip()
        year = str(item.get('year') or '').strip()
        if year == '0':
            year = ''

        parts = [name]
        meta = []
        if issuer:
            meta.append(issuer)
        if year:
            meta.append(year)
        if meta:
            parts.append(f"({' — '.join(meta)})")
        text = " ".join(parts)

        ach_key = None
        for k, v in master_ach.items():
            if isinstance(v, dict) and v.get('text', '').lower() == text.lower():
                ach_key = k
                break
            elif isinstance(v, str) and v.lower() == text.lower():
                ach_key = k
                break

        if not ach_key:
            ach_key = generate_achievement_key(name, existing_keys, prefix="cert")
            existing_keys.add(ach_key)
            master_ach[ach_key] = {'text': text}
            stats['added'] += 1
        elif force:
            master_ach[ach_key] = {'text': text}
            stats['updated'] += 1

    # 3. Hackathons from speaking-and-community.yaml
    for item in (community_data.get('hackathons', []) or []):
        if not isinstance(item, dict):
            continue
        name = (item.get('name') or '').strip()
        if not name:
            stats['skipped'] += 1
            continue
        result = (item.get('result') or '').strip()
        organizer = (item.get('organizer') or '').strip()
        project = (item.get('project') or '').strip()
        prize = (item.get('prize') or '').strip()

        if result:
            text = f"{result} at {name}"
        else:
            text = name
        if organizer:
            text += f" ({organizer})"
        if project:
            text += f" — built {project}"
        if prize:
            text += f" [{prize}]"

        ach_key = None
        for k, v in master_ach.items():
            if isinstance(v, dict) and v.get('text', '').lower() == text.lower():
                ach_key = k
                break
            elif isinstance(v, str) and v.lower() == text.lower():
                ach_key = k
                break

        if not ach_key:
            ach_key = generate_achievement_key(name, existing_keys, prefix="hackathon")
            existing_keys.add(ach_key)
            master_ach[ach_key] = {'text': text}
            stats['added'] += 1
        elif force:
            master_ach[ach_key] = {'text': text}
            stats['updated'] += 1

    # 4. Professional Licenses from credentials.yaml (Medical / Legal / Engineering)
    for item in (creds_data.get('licenses', []) or []):
        if not isinstance(item, dict):
            continue
        name = (item.get('name') or '').strip()
        if not name:
            stats['skipped'] += 1
            continue
        jurisdiction = (item.get('jurisdiction') or '').strip()
        lic_num = (item.get('license_number') or '').strip()
        status = (item.get('status') or '').strip()

        parts = [name]
        meta = []
        if jurisdiction:
            meta.append(jurisdiction)
        if lic_num:
            meta.append(f"License #{lic_num}")
        if status:
            meta.append(status)
        if meta:
            parts.append(f"({' — '.join(meta)})")
        text = " ".join(parts)

        ach_key = None
        for k, v in master_ach.items():
            if isinstance(v, dict) and v.get('text', '').lower() == text.lower():
                ach_key = k
                break
            elif isinstance(v, str) and v.lower() == text.lower():
                ach_key = k
                break

        if not ach_key:
            ach_key = generate_achievement_key(name, existing_keys, prefix="license")
            existing_keys.add(ach_key)
            master_ach[ach_key] = {'text': text}
            stats['added'] += 1
        elif force:
            master_ach[ach_key] = {'text': text}
            stats['updated'] += 1

    # 5. Security Clearances from credentials.yaml (Defense / Government / Aerospace)
    for item in (creds_data.get('clearances', []) or []):
        if not isinstance(item, dict):
            continue
        level = (item.get('level') or '').strip()
        if not level:
            stats['skipped'] += 1
            continue
        agency = (item.get('agency') or '').strip()
        status = (item.get('status') or '').strip()
        poly = (item.get('polygraph') or '').strip()

        parts = [f"{level} Security Clearance"]
        meta = []
        if agency:
            meta.append(agency)
        if status:
            meta.append(status)
        if poly:
            meta.append(f"Polygraph: {poly}")
        if meta:
            parts.append(f"({' — '.join(meta)})")
        text = " ".join(parts)

        ach_key = None
        for k, v in master_ach.items():
            if isinstance(v, dict) and v.get('text', '').lower() == text.lower():
                ach_key = k
                break
            elif isinstance(v, str) and v.lower() == text.lower():
                ach_key = k
                break

        if not ach_key:
            ach_key = generate_achievement_key(level, existing_keys, prefix="clearance")
            existing_keys.add(ach_key)
            master_ach[ach_key] = {'text': text}
            stats['added'] += 1
        elif force:
            master_ach[ach_key] = {'text': text}
            stats['updated'] += 1

    # 6. Patents from credentials.yaml (Intellectual Property / Research)
    for item in (creds_data.get('patents', []) or []):
        if not isinstance(item, dict):
            continue
        title = (item.get('title') or '').strip()
        if not title:
            stats['skipped'] += 1
            continue
        pat_num = str(item.get('patent_number') or item.get('number') or '').strip()
        filing_date = str(item.get('filing_date') or item.get('date') or '').strip()
        status = (item.get('status') or '').strip()

        parts = [f"Patent: {title}"]
        meta = []
        if pat_num:
            meta.append(f"#{pat_num}")
        if status:
            meta.append(status)
        if filing_date:
            meta.append(filing_date)
        if meta:
            parts.append(f"({' — '.join(meta)})")
        text = " ".join(parts)

        ach_key = None
        for k, v in master_ach.items():
            if isinstance(v, dict) and v.get('text', '').lower() == text.lower():
                ach_key = k
                break
            elif isinstance(v, str) and v.lower() == text.lower():
                ach_key = k
                break

        if not ach_key:
            ach_key = generate_achievement_key(title, existing_keys, prefix="patent")
            existing_keys.add(ach_key)
            master_ach[ach_key] = {'text': text}
            stats['added'] += 1
        elif force:
            master_ach[ach_key] = {'text': text}
            stats['updated'] += 1

    # 7. Research Grants from credentials.yaml (Academic / Medical / Scientific)
    for item in (creds_data.get('grants', []) or []):
        if not isinstance(item, dict):
            continue
        title = (item.get('title') or '').strip()
        if not title:
            stats['skipped'] += 1
            continue
        funder = str(item.get('funder') or item.get('agency') or '').strip()
        amount = str(item.get('amount') or '').strip()
        year = str(item.get('year') or '').strip()
        if year == '0':
            year = ''

        parts = [f"Research Grant: {title}"]
        meta = []
        if funder:
            meta.append(funder)
        if amount:
            meta.append(amount)
        if year:
            meta.append(year)
        if meta:
            parts.append(f"({' — '.join(meta)})")
        text = " ".join(parts)

        ach_key = None
        for k, v in master_ach.items():
            if isinstance(v, dict) and v.get('text', '').lower() == text.lower():
                ach_key = k
                break
            elif isinstance(v, str) and v.lower() == text.lower():
                ach_key = k
                break

        if not ach_key:
            ach_key = generate_achievement_key(title, existing_keys, prefix="grant")
            existing_keys.add(ach_key)
            master_ach[ach_key] = {'text': text}
            stats['added'] += 1
        elif force:
            master_ach[ach_key] = {'text': text}
            stats['updated'] += 1

    master_data['achievements'] = master_ach
    return stats


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Sync verified facts from identity/ to tools/resume/master.yaml bullet pool."
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help="Preview changes without modifying tools/resume/master.yaml"
    )
    parser.add_argument(
        '--section',
        choices=['all', 'exp', 'experience', 'proj', 'projects', 'edu', 'education', 'pubs', 'publications', 'skills', 'technologies', 'ach', 'achievements'],
        default='all',
        help="Section to sync (default: all)"
    )
    parser.add_argument(
        '--force', action='store_true',
        help="Overwrite existing metadata with identity values where keys match"
    )

    args = parser.parse_args()

    # Paths
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent  # tools/resume/ → repo root
    master_path = script_dir / 'master.yaml'
    exp_path = repo_root / 'identity' / 'experience.yaml'
    proj_path = repo_root / 'identity' / 'projects.yaml'
    creds_path = repo_root / 'identity' / 'credentials.yaml'
    skills_path = repo_root / 'identity' / 'skills.yaml'
    speaking_path = repo_root / 'identity' / 'speaking-and-community.yaml'

    if not master_path.exists():
        print(f"ERROR: {master_path} not found.", file=sys.stderr)
        sys.exit(1)

    master_data = load_yaml(master_path)
    section = args.section

    print("=" * 60)
    print("🔄 Pramedha Identity → Master Resume Sync")
    if args.dry_run:
        print("   [DRY RUN MODE — No files will be modified]")
    print("=" * 60)

    # Experience
    if section in ('all', 'exp', 'experience'):
        if exp_path.exists():
            exp_data = load_yaml(exp_path)
            stats = sync_experience(exp_data, master_data, force=args.force)
            print(f"💼 Experience:   +{stats['added_roles']} roles, +{stats['added_bullets']} bullets "
                  f"({stats['updated_roles']} updated, {stats['skipped']} blank skipped)")
        else:
            print("💼 Experience:   identity/experience.yaml not found (skipped)")

    # Projects
    if section in ('all', 'proj', 'projects'):
        if proj_path.exists():
            proj_data = load_yaml(proj_path)
            stats = sync_projects(proj_data, master_data, force=args.force)
            print(f"🚀 Projects:     +{stats['added']} projects ({stats['updated']} updated, {stats['skipped']} blank skipped)")
        else:
            print("🚀 Projects:     identity/projects.yaml not found (skipped)")

    # Education
    if section in ('all', 'edu', 'education'):
        if creds_path.exists():
            creds_data = load_yaml(creds_path)
            stats = sync_education(creds_data, master_data, force=args.force)
            print(f"🎓 Education:    +{stats['added']} entries ({stats['skipped']} blank skipped)")
        else:
            print("🎓 Education:    identity/credentials.yaml not found (skipped)")

    # Publications
    if section in ('all', 'pubs', 'publications'):
        if creds_path.exists():
            creds_data = load_yaml(creds_path)
            stats = sync_publications(creds_data, master_data, force=args.force)
            print(f"📚 Publications: +{stats['added']} entries ({stats['skipped']} blank skipped)")
        else:
            print("📚 Publications: identity/credentials.yaml not found (skipped)")

    # Skills / Technologies
    if section in ('all', 'skills', 'technologies'):
        if skills_path.exists():
            skills_data = load_yaml(skills_path)
            stats = sync_skills(skills_data, master_data, force=args.force)
            print(f"🛠️  Skills:       +{stats['added']} categories ({stats['updated']} updated, {stats['skipped']} blank skipped)")
        else:
            print("🛠️  Skills:       identity/skills.yaml not found (skipped)")

    # Achievements (Awards, Certifications, Hackathons)
    if section in ('all', 'ach', 'achievements'):
        creds_data = load_yaml(creds_path) if creds_path.exists() else {}
        speaking_data = load_yaml(speaking_path) if speaking_path.exists() else {}
        if creds_path.exists() or speaking_path.exists():
            stats = sync_achievements(creds_data, speaking_data, master_data, force=args.force)
            print(f"🏆 Achievements: +{stats['added']} entries ({stats['updated']} updated, {stats['skipped']} blank skipped)")
        else:
            print("🏆 Achievements: credentials/speaking YAML not found (skipped)")

    print("-" * 60)

    if args.dry_run:
        print("🔍 Dry run complete. Master file unchanged.")
    else:
        # Create a backup before writing
        bak_path = master_path.with_suffix('.yaml.bak')
        try:
            import shutil
            shutil.copy2(master_path, bak_path)
        except Exception:
            pass

        dump_yaml(master_data, master_path)
        print("✅ tools/resume/master.yaml successfully updated (backup saved to master.yaml.bak).")


if __name__ == '__main__':
    main()
