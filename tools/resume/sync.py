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
    python tools/resume/sync.py                 # Sync all sections (safe merge, preserves existing)
    python tools/resume/sync.py --dry-run       # Preview changes without modifying master.yaml
    python tools/resume/sync.py --section exp   # Sync specific section (exp, proj, edu, pubs, skills, ach, all)
    python tools/resume/sync.py --force         # Also overwrite start dates of matched roles (end dates and locations always follow identity/)
"""

import argparse
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

CAREER_BREAK_POSITION = 'Career Transition / Sabbatical'


def role_source(company: str, position: str, start_date: str) -> str:
    """The identity fact a master.yaml role comes from, stored in its `_source` key."""
    return f"{company} | {position} | {start_date}"


def identity_sources(exp_data: dict) -> dict:
    """Map every role in identity/experience.yaml to its bullet texts: {role_source: {text, ...}}."""
    sources = {}
    for entry in (exp_data or {}).get('experience', []) or []:
        if not isinstance(entry, dict):
            continue
        company = as_text(entry.get('company') or entry.get('client') or entry.get('organization')
                          or entry.get('institution') or entry.get('employer') or entry.get('practice'))
        position = as_text(entry.get('position') or entry.get('title') or entry.get('role'))
        start = as_text(entry.get('start_date'))
        if not company and not position and not start:
            continue
        texts = sources.setdefault(role_source(company, position, start), set())
        for project in entry.get('projects', []) or []:
            if not isinstance(project, dict):
                continue
            for deliverable in project.get('deliverables', []) or []:
                if not isinstance(deliverable, dict):
                    continue
                for bullet in deliverable.get('bullets', []) or []:
                    if as_text(bullet):
                        texts.add(as_text(bullet))
    for brk in (exp_data or {}).get('career_breaks', []) or []:
        if not isinstance(brk, dict):
            continue
        title, start = as_text(brk.get('title')), as_text(brk.get('start_date'))
        if title or start:
            sources[role_source(title, CAREER_BREAK_POSITION, start)] = {as_text(brk.get('description')) or title}
    return sources


def stale_entries(master_exp: dict, sources: dict) -> list:
    """master.yaml roles and bullets whose `_source` no longer exists in identity/experience.yaml."""
    stale = []
    for key, role in master_exp.items():
        if not isinstance(role, dict) or role.get('_source') is None:
            continue
        if role['_source'] not in sources:
            stale.append(key)
            continue
        for b_key, bullet in (role.get('bullets') or {}).items():
            if isinstance(bullet, dict) and bullet.get('_source') is not None \
                    and bullet['_source'] not in sources[role['_source']]:
                stale.append(f"{key}.{b_key}")
    return stale


def is_blank_str(val) -> bool:
    return val is None or (isinstance(val, str) and not val.strip())


def as_text(value) -> str:
    """Any YAML scalar as a stripped string: None -> '', 3.8 -> '3.8', True -> 'True'."""
    if value is None:
        return ''
    return str(value).strip()


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

    # Prune template placeholder scaffolding if real experience entries exist
    has_real_entries = any(
        isinstance(e, dict) and bool(as_text(e.get('company') or e.get('position') or e.get('title') or ''))
        for e in exp_entries
    )
    if has_real_entries and '_example_role_' in master_exp:
        del master_exp['_example_role_']
        existing_keys.discard('_example_role_')

    for entry in exp_entries:
        if not isinstance(entry, dict):
            continue

        company = as_text(entry.get('company') or entry.get('client') or entry.get('organization') or entry.get('institution') or entry.get('employer') or entry.get('practice') or '')
        position = as_text(entry.get('position') or entry.get('title') or entry.get('role') or '')
        start_date = as_text(entry.get('start_date') or '')
        end_date = as_text(entry.get('end_date') or 'present')
        location = as_text(entry.get('location') or '')

        # Skip empty template scaffolding
        if not company and not position and not start_date:
            stats['skipped'] += 1
            continue

        # Look for matching existing role by company + position + start_date
        matching_key = None
        for k, v in master_exp.items():
            if isinstance(v, dict):
                same_comp = as_text(v.get('company')).lower() == company.lower()
                same_pos = as_text(v.get('position')).lower() == position.lower()
                same_start = as_text(v.get('start_date')) == start_date
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
                '_source': role_source(company, position, start_date),
                'bullets': {}
            }
            stats['added_roles'] += 1
            matching_key = role_key
        else:
            role_key = matching_key
            role = master_exp[role_key]
            fresh = {'end_date': end_date or 'present', '_source': role_source(company, position, start_date)}
            if location:
                fresh['location'] = location
            if force:
                fresh['start_date'] = start_date
            changed = {k: v for k, v in fresh.items() if str(role.get(k) or '') != v}
            if changed:
                role.update(changed)
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
            client = as_text(p.get('client'))
            deliverables = p.get('deliverables', []) or []
            for d in deliverables:
                if not isinstance(d, dict):
                    continue
                status = (as_text(d.get('verification') or '') or as_text(p.get('verification') or '')
                          or as_text(entry.get('verification') or ''))
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

                    # Check if text already exists under any phrasing; keep its source and status current
                    already_present = False
                    for k, b_data in list(role_bullets.items()):
                        if isinstance(b_data, str) and (b_data == final_text or b_data == b_text):
                            role_bullets[k] = b_data = {'default': b_data}
                        if isinstance(b_data, dict) and (final_text in b_data.values() or b_text in b_data.values()):
                            fresh = {'_source': b_text, '_verification': status}
                            changed = {f: v for f, v in fresh.items() if (b_data.get(f) or '') != v}
                            for f, v in changed.items():
                                if v:
                                    b_data[f] = v
                                else:
                                    b_data.pop(f, None)
                            if changed:
                                stats['updated_roles'] += 1
                            already_present = True
                            break

                    if not already_present:
                        b_key = generate_bullet_key(b_text, existing_bullet_keys, bullet_idx)
                        existing_bullet_keys.add(b_key)
                        role_bullets[b_key] = {'default': final_text, '_source': b_text,
                                               **({'_verification': status} if status else {})}
                        stats['added_bullets'] += 1
                        bullet_idx += 1

    # Sync career breaks as archived roles (available for variants to select)
    career_breaks = id_data.get('career_breaks', []) or []
    for b in career_breaks:
        if not isinstance(b, dict):
            continue
        b_title = as_text(b.get('title'))
        b_start = as_text(b.get('start_date'))
        if not b_title and not b_start:
            continue

        break_slug = slugify(b_title)[:20].strip('_') or 'transition'
        break_key = f"career_break_{break_slug}"
        if break_key not in master_exp:
            desc = as_text(b.get('description'))
            b_content = desc or b_title
            bullets = {'summary': {'default': b_content, '_source': b_content}}
            master_exp[break_key] = {
                'company': b_title,
                'position': CAREER_BREAK_POSITION,
                'start_date': b_start,
                'end_date': as_text(b.get('end_date') or 'present'),
                'location': '',
                'archived': True,
                '_source': role_source(b_title, CAREER_BREAK_POSITION, b_start),
                'bullets': bullets
            }
            stats['added_roles'] += 1
            stats['added_bullets'] += len(bullets)

    stats['stale'] = stale_entries(master_exp, identity_sources(id_data))
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
        name = as_text(p.get('name'))
        if not name:
            stats['skipped'] += 1
            continue

        repo = as_text(p.get('repo'))
        live_url = as_text(p.get('live_url'))
        location = repo or live_url or as_text(p.get('context'))

        start = as_text(p.get('start_date'))
        end = as_text(p.get('end_date'))
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
            if isinstance(v, dict) and as_text(v.get('name')).lower() == name.lower():
                proj_key = k
                break

        highlights = p.get('highlights', []) or []

        if not proj_key:
            proj_key = generate_project_key(name, existing_keys)
            existing_keys.add(proj_key)
            bullets_dict = {}
            existing_bkeys = set()
            if highlights:
                first_bullet = str(highlights[0]).strip()
                if first_bullet:
                    bullets_dict['default'] = first_bullet
                    existing_bkeys.add('default')
                if len(highlights) > 1:
                    tech_bullet = str(highlights[1]).strip()
                    if tech_bullet:
                        bullets_dict['technical'] = tech_bullet
                        existing_bkeys.add('technical')
                for i in range(2, len(highlights)):
                    h_text = str(highlights[i]).strip()
                    if h_text:
                        b_k = generate_bullet_key(h_text, existing_bkeys, i + 1)
                        existing_bkeys.add(b_k)
                        bullets_dict[b_k] = h_text
            else:
                tagline = as_text(p.get('tagline'))
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
            updated_any = False
            if date_str and master_proj[proj_key].get('date') != date_str:
                master_proj[proj_key]['date'] = date_str
                updated_any = True
            if location and master_proj[proj_key].get('location') != location:
                master_proj[proj_key]['location'] = location
                updated_any = True

            role_b = master_proj[proj_key].setdefault('bullets', {})
            if isinstance(role_b, dict) and highlights:
                existing_texts = set()
                for b_val in role_b.values():
                    if isinstance(b_val, str):
                        existing_texts.add(b_val.strip())
                    elif isinstance(b_val, dict):
                        for sub_v in b_val.values():
                            if isinstance(sub_v, str):
                                existing_texts.add(sub_v.strip())

                for i, h in enumerate(highlights):
                    h_text = str(h).strip()
                    if not h_text:
                        continue
                    if i == 0 and 'default' not in role_b:
                        role_b['default'] = h_text
                        updated_any = True
                    elif i == 1 and 'technical' not in role_b:
                        role_b['technical'] = h_text
                        updated_any = True
                    elif h_text not in existing_texts:
                        b_k = generate_bullet_key(h_text, set(role_b.keys()), i + 1)
                        role_b[b_k] = h_text
                        existing_texts.add(h_text)
                        updated_any = True

            if updated_any:
                stats['updated'] += 1

    master_data['projects'] = master_proj
    return stats


def sync_education(id_data: dict, master_data: dict, force: bool = False):
    """
    Sync education from identity/credentials.yaml into master.yaml['education'].
    Includes degree, institution, area, dates, score, honors, and coursework.
    """
    edu_list = id_data.get('education', []) or []
    master_edu = master_data.get('education', []) or []
    if not isinstance(master_edu, list):
        master_edu = []

    stats = {'added': 0, 'updated': 0, 'skipped': 0}

    for item in edu_list:
        if not isinstance(item, dict):
            continue
        institution = as_text(item.get('institution'))
        degree = as_text(item.get('degree'))
        field = as_text(item.get('field'))

        if not institution and not degree:
            stats['skipped'] += 1
            continue

        # Check if already present
        existing_idx = None
        for idx, e in enumerate(master_edu):
            if isinstance(e, dict) and (
                as_text(e.get('institution')).lower() == institution.lower() and
                as_text(e.get('degree')).lower() == degree.lower()
            ):
                existing_idx = idx
                break

        highlights = []
        score = as_text(item.get('score'))
        if score:
            highlights.append(f"Score: {score}")
        for honor in (item.get('honors', []) or []):
            h_str = as_text(honor)
            if h_str:
                highlights.append(h_str)
        courses = [as_text(c) for c in (item.get('courses', []) or []) if as_text(c)]
        if courses:
            highlights.append(f"Coursework: {', '.join(courses)}")

        start_date = as_text(item.get('start_date'))
        year_val = item.get('year')
        raw_end = item.get('end_date') if item.get('end_date') not in (None, '') else (year_val if year_val and year_val != 0 else '')
        end_date = '' if raw_end in (0, '0') else as_text(raw_end)

        if existing_idx is None:
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
        elif force:
            entry = master_edu[existing_idx]
            updated_any = False
            if field and entry.get('area') != field:
                entry['area'] = field
                updated_any = True
            if start_date and entry.get('start_date') != start_date:
                entry['start_date'] = start_date
                updated_any = True
            if end_date and entry.get('end_date') != end_date:
                entry['end_date'] = end_date
                updated_any = True
            if highlights and entry.get('highlights') != highlights:
                entry['highlights'] = highlights
                updated_any = True
            if updated_any:
                stats['updated'] += 1

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

    stats = {'added': 0, 'updated': 0, 'skipped': 0}

    for item in pubs_list:
        if not isinstance(item, dict):
            continue
        title = as_text(item.get('title') or item.get('name') or '')
        if not title:
            stats['skipped'] += 1
            continue

        existing_idx = None
        for idx, p in enumerate(master_pubs):
            if isinstance(p, dict) and as_text(p.get('title')).lower() == title.lower():
                existing_idx = idx
                break

        authors = [as_text(a) for a in (item.get('authors', []) or []) if as_text(a)]
        year_val = item.get('year')
        raw_date = item.get('date') if item.get('date') not in (None, '') else (year_val if year_val and year_val != 0 else '')
        date_str = '' if raw_date in (0, '0') else as_text(raw_date)
        journal_str = as_text(item.get('publisher') or item.get('journal') or '')
        url_str = as_text(item.get('url'))
        doi_str = as_text(item.get('doi'))

        if existing_idx is None:
            entry = {
                'title': title,
                'authors': authors,
                'date': date_str,
                'journal': journal_str,
            }
            if url_str:
                entry['url'] = url_str
            if doi_str:
                entry['doi'] = doi_str

            master_pubs.append(entry)
            stats['added'] += 1
        elif force:
            entry = master_pubs[existing_idx]
            updated_any = False
            if authors and entry.get('authors') != authors:
                entry['authors'] = authors
                updated_any = True
            if date_str and entry.get('date') != date_str:
                entry['date'] = date_str
                updated_any = True
            if journal_str and entry.get('journal') != journal_str:
                entry['journal'] = journal_str
                updated_any = True
            if url_str and entry.get('url') != url_str:
                entry['url'] = url_str
                updated_any = True
            if doi_str and entry.get('doi') != doi_str:
                entry['doi'] = doi_str
                updated_any = True
            if updated_any:
                stats['updated'] += 1

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
                name = as_text(s.get('name'))
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
            if isinstance(entry, dict) and as_text(entry.get('label')).lower() == cat_label.lower():
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
        title = as_text(item.get('title'))
        if not title:
            stats['skipped'] += 1
            continue
        awarder = as_text(item.get('awarder'))
        year = as_text(item.get('year'))
        if year == '0':
            year = ''
        details = as_text(item.get('details'))

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
        name = as_text(item.get('name'))
        if not name:
            stats['skipped'] += 1
            continue
        issuer = as_text(item.get('issuer'))
        year = as_text(item.get('year'))
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
        name = as_text(item.get('name'))
        if not name:
            stats['skipped'] += 1
            continue
        result = as_text(item.get('result'))
        organizer = as_text(item.get('organizer'))
        project = as_text(item.get('project'))
        prize = as_text(item.get('prize'))

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
        name = as_text(item.get('name'))
        if not name:
            stats['skipped'] += 1
            continue
        jurisdiction = as_text(item.get('jurisdiction'))
        lic_num = as_text(item.get('license_number'))
        status = as_text(item.get('status'))

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
        level = as_text(item.get('level'))
        if not level:
            stats['skipped'] += 1
            continue
        agency = as_text(item.get('agency'))
        status = as_text(item.get('status'))
        poly = as_text(item.get('polygraph'))

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
        title = as_text(item.get('title'))
        if not title:
            stats['skipped'] += 1
            continue
        pat_num = as_text(item.get('patent_number') if item.get('patent_number') is not None else item.get('number'))
        filing_date = as_text(item.get('filing_date') if item.get('filing_date') is not None else item.get('date'))
        status = as_text(item.get('status'))

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
        title = as_text(item.get('title'))
        if not title:
            stats['skipped'] += 1
            continue
        funder = as_text(item.get('funder') if item.get('funder') is not None else item.get('agency'))
        amount = as_text(item.get('amount'))
        year = as_text(item.get('year'))
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


def extract_master_header(master_path: Path) -> str:
    """Extract top comment and blank lines before the first YAML key from master.yaml."""
    if not master_path.exists():
        return ""
    lines = []
    with open(master_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith('#') or not stripped:
                lines.append(line)
            else:
                break
    return "".join(lines)


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

    stats_exp = {'added_roles': 0, 'added_bullets': 0, 'updated_roles': 0, 'skipped': 0}
    stats_proj = {'added': 0, 'updated': 0, 'skipped': 0}
    stats_edu = {'added': 0, 'updated': 0, 'skipped': 0}
    stats_pubs = {'added': 0, 'updated': 0, 'skipped': 0}
    stats_skills = {'added': 0, 'updated': 0, 'skipped': 0}
    stats_ach = {'added': 0, 'updated': 0, 'skipped': 0}

    # Experience
    if section in ('all', 'exp', 'experience'):
        if exp_path.exists():
            exp_data = load_yaml(exp_path)
            stats_exp = sync_experience(exp_data, master_data, force=args.force)
            print(f"💼 Experience:   +{stats_exp['added_roles']} roles, +{stats_exp['added_bullets']} bullets "
                  f"({stats_exp['updated_roles']} updated, {stats_exp['skipped']} blank skipped)")
            if stats_exp.get('stale'):
                print("⚠️  Stale in master.yaml (identity/experience.yaml changed or removed them); "
                      "assemble.py refuses variants that select them:")
                for entry in stats_exp['stale']:
                    print(f"     - {entry}")
        else:
            print("💼 Experience:   identity/experience.yaml not found (skipped)")

    # Projects
    if section in ('all', 'proj', 'projects'):
        if proj_path.exists():
            proj_data = load_yaml(proj_path)
            stats_proj = sync_projects(proj_data, master_data, force=args.force)
            print(f"🚀 Projects:     +{stats_proj['added']} projects ({stats_proj['updated']} updated, {stats_proj['skipped']} blank skipped)")
        else:
            print("🚀 Projects:     identity/projects.yaml not found (skipped)")

    # Education
    if section in ('all', 'edu', 'education'):
        if creds_path.exists():
            creds_data = load_yaml(creds_path)
            stats_edu = sync_education(creds_data, master_data, force=args.force)
            print(f"🎓 Education:    +{stats_edu['added']} entries ({stats_edu['updated']} updated, {stats_edu['skipped']} blank skipped)")
        else:
            print("🎓 Education:    identity/credentials.yaml not found (skipped)")

    # Publications
    if section in ('all', 'pubs', 'publications'):
        if creds_path.exists():
            creds_data = load_yaml(creds_path)
            stats_pubs = sync_publications(creds_data, master_data, force=args.force)
            print(f"📚 Publications: +{stats_pubs['added']} entries ({stats_pubs['updated']} updated, {stats_pubs['skipped']} blank skipped)")
        else:
            print("📚 Publications: identity/credentials.yaml not found (skipped)")

    # Skills / Technologies
    if section in ('all', 'skills', 'technologies'):
        if skills_path.exists():
            skills_data = load_yaml(skills_path)
            stats_skills = sync_skills(skills_data, master_data, force=args.force)
            print(f"🛠️  Skills:       +{stats_skills['added']} categories ({stats_skills['updated']} updated, {stats_skills['skipped']} blank skipped)")
        else:
            print("🛠️  Skills:       identity/skills.yaml not found (skipped)")

    # Achievements (Awards, Certifications, Hackathons)
    if section in ('all', 'ach', 'achievements'):
        creds_data = load_yaml(creds_path) if creds_path.exists() else {}
        speaking_data = load_yaml(speaking_path) if speaking_path.exists() else {}
        if creds_path.exists() or speaking_path.exists():
            stats_ach = sync_achievements(creds_data, speaking_data, master_data, force=args.force)
            print(f"🏆 Achievements: +{stats_ach['added']} entries ({stats_ach['updated']} updated, {stats_ach['skipped']} blank skipped)")
        else:
            print("🏆 Achievements: credentials/speaking YAML not found (skipped)")

    print("-" * 60)

    total_added = (
        stats_exp.get('added_roles', 0) + stats_exp.get('added_bullets', 0) +
        stats_proj.get('added', 0) +
        stats_edu.get('added', 0) +
        stats_pubs.get('added', 0) +
        stats_skills.get('added', 0) +
        stats_ach.get('added', 0)
    )
    total_updated = (
        stats_exp.get('updated_roles', 0) +
        stats_proj.get('updated', 0) +
        stats_edu.get('updated', 0) +
        stats_pubs.get('updated', 0) +
        stats_skills.get('updated', 0) +
        stats_ach.get('updated', 0)
    )

    if args.dry_run:
        print("🔍 Dry run complete. Master file unchanged.")
    elif total_added == 0 and total_updated == 0:
        print("✨ tools/resume/master.yaml is already up to date with identity/ (no changes needed).")
    else:
        # Create a backup before writing
        bak_path = master_path.with_suffix('.yaml.bak')
        try:
            import shutil
            shutil.copy2(master_path, bak_path)
        except Exception:
            pass

        header_text = extract_master_header(master_path)
        dump_yaml(master_data, master_path, header=header_text)
        print(f"✅ tools/resume/master.yaml successfully updated (+{total_added} additions, {total_updated} updates; backup saved to master.yaml.bak).")


if __name__ == '__main__':
    main()
