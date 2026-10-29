"""Shared helpers for the end-to-end tests.

make_repo() builds a throwaway career repository in a temporary folder from this repository's
template code (.pramedha/ and tools/resume/) plus a fixed, fully tagged example profile. It never
copies your own data (identity/, data-corpus/, master.yaml, variants) and never touches the real
repository or your home folder.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]

IDENTITY = """name: "Alex Chen"
email: "alex.chen@example.com"
location:
  city: "Springfield"
  country_code: "US"
work_authorization:
  status: "citizen"
  verification: "⚠️ ESTIMATED — self-declared; no ID document stored"
languages:
  - language: "English"
    level: "native"
total_years_experience: 6
professional_headline: "Senior Software Engineer"
"""

EXPERIENCE = """experience:
  - company: "Example Payments Inc"
    position: "Senior Software Engineer"
    start_date: "2022-03"
    end_date: "present"
    location: "Remote"
    verification: "✅ VERIFIED — data-corpus/documents/offer-letter.pdf"
    projects:
      - name: "Payment Retry"
        deliverables:
          - name: "Retry pipeline"
            verification: "✅ VERIFIED — data-corpus/documents/launch-note.txt"
            bullets:
              - "Designed retry pipeline that raised recovery rate by 12% [measured]"
              - "Processed 2M daily payment events in real time [measured]"
            skills: ["Python"]
  - company: "Example Messaging Co"
    position: "Software Engineer"
    start_date: "2020-06"
    end_date: "2022-02"
    location: "Remote"
    verification: "✅ VERIFIED — data-corpus/documents/experience-letter.pdf"
    projects:
      - name: "Messaging API"
        deliverables:
          - name: "Rate limiter"
            verification: "✅ VERIFIED — data-corpus/documents/experience-letter.pdf"
            bullets:
              - "Implemented rate limiting service for 100K concurrent clients [measured]"
            skills: ["Go"]
"""

SKILLS = """programming:
  - name: "Python"
    level: "expert"
    verification: "✅ VERIFIED — data-corpus/documents/offer-letter.pdf"
  - name: "Go"
    level: "advanced"
    verification: "✅ VERIFIED — data-corpus/documents/experience-letter.pdf"
"""

CREDENTIALS = """education:
  - degree: "B.S."
    field: "Computer Science"
    institution: "Example State University"
    start_date: "2012-08"
    end_date: "2016-05"
    score: "3.8/4.0"
    verification: "✅ VERIFIED — data-corpus/documents/diploma.pdf"
"""

PROJECTS = """public:
  - name: "OpenRetry"
    repo: "https://github.com/example/openretry"
    highlights:
      - "Open-source retry scheduler with pluggable backoff [measured]"
    verification: "✅ VERIFIED — data-corpus/documents/openretry-readme.txt"
internal: []
"""

EMPTY_POOL = """header:
  name: ""
experience: {}
projects: {}
publications: []
education: []
achievements: {}
technologies: []
"""

FILES = {
    'identity/identity.yaml': IDENTITY,
    'identity/experience.yaml': EXPERIENCE,
    'identity/skills.yaml': SKILLS,
    'identity/credentials.yaml': CREDENTIALS,
    'identity/projects.yaml': PROJECTS,
    'identity/claims-and-evidence.md': '# Claims\n',
    'identity/professional-summary.md': '# Professional summary\n',
    'tools/resume/master.yaml': EMPTY_POOL,
}
EVIDENCE = ['offer-letter.pdf', 'launch-note.txt', 'experience-letter.pdf', 'diploma.pdf',
            'openretry-readme.txt']
TEMPLATE_CODE = ['.pramedha', 'tools/resume']
SKIP_IN_RESUME = {'master.yaml', 'master.yaml.bak', 'generated', 'output', 'variants', 'jd', 'tests'}

PAYMENTS = 'example_payments_inc_senior_software_engineer'
MESSAGING = 'example_messaging_co_software_engineer'
BACKEND = {MESSAGING: [['implemented_rate_limiting', 'default']], PAYMENTS: [['processed_2m_daily']]}
PLATFORM = {PAYMENTS: [['designed_retry_pipeline', 'default'], 'processed_2m_daily']}


def run(repo, *args, check=False):
    """Run `python <args>` inside repo and return the CompletedProcess."""
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
    proc = subprocess.run([sys.executable, *map(str, args)], cwd=repo, capture_output=True,
                          text=True, encoding='utf-8', errors='replace', env=env, stdin=subprocess.DEVNULL)
    if check and proc.returncode != 0:
        raise AssertionError(f'{args} exited {proc.returncode}\n{proc.stdout}\n{proc.stderr}')
    return proc


def out(proc):
    return (proc.stdout or '') + (proc.stderr or '')


def load(path):
    return yaml.safe_load(Path(path).read_text(encoding='utf-8'))


def dump(data, path):
    Path(path).write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding='utf-8')


def write_variant(repo, filename, name, experience, keep_template_output_name=False, **fields):
    """Create tools/resume/variants/<filename> the documented way: starting from _template.yaml."""
    variant = load(repo / 'tools/resume/variants/_template.yaml') or {}
    variant['variant_name'] = name
    variant['summary'] = f'{name} engineer with six years of payments and messaging work.'
    variant['experience'] = experience
    if not keep_template_output_name:
        variant['output_filename'] = f'Alex_Chen_{name}_CV'
    variant.update(fields)
    dump(variant, repo / 'tools/resume/variants' / filename)


def make_repo(tmp_path, variants=True, keep_template_output_name=False):
    """Build tmp_path/repo; by default also run sync.py and create variants A_Backend and B_Platform."""
    repo = Path(tmp_path) / 'repo'
    for rel in TEMPLATE_CODE:
        skip = SKIP_IN_RESUME if rel == 'tools/resume' else set()
        shutil.copytree(REPO / rel, repo / rel,
                        ignore=lambda d, names, skip=skip: {n for n in names
                                                            if n in skip or n in ('__pycache__', '.pytest_cache')})
    for sub in ('variants', 'jd'):
        (repo / 'tools/resume' / sub).mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / 'tools/resume' / sub / '_template.yaml', repo / 'tools/resume' / sub / '_template.yaml')
    for sub in ('generated', 'output'):
        (repo / 'tools/resume' / sub).mkdir(parents=True, exist_ok=True)
    (repo / 'identity').mkdir()
    (repo / 'data-corpus/documents').mkdir(parents=True)
    schema = (load(repo / '.pramedha/manifest.yaml').get('template') or {}).get('schema_version', '0.1.0')
    dump({'schema_version': schema,
          'user': {'name': 'Alex Chen', 'email': 'alex.chen@example.com', 'headline': 'Senior Software Engineer'},
          'profession_type': 'engineering', 'career_type': 'employed', 'locale': 'en'}, repo / 'config.yaml')
    for rel, text in FILES.items():
        (repo / rel).write_text(text, encoding='utf-8')
    for name in EVIDENCE:
        (repo / 'data-corpus/documents' / name).write_text('placeholder evidence for tests\n', encoding='utf-8')
    if variants:
        run(repo, 'tools/resume/sync.py', check=True)
        write_variant(repo, 'A_Backend.yaml', 'Backend', BACKEND, keep_template_output_name)
        write_variant(repo, 'B_Platform.yaml', 'Platform', PLATFORM, keep_template_output_name)
    return repo

