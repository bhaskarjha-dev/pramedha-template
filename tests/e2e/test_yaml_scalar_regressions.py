"""HIGH-01: numbers, booleans and empty values in identity files never crash sync.py or validate.py."""
from _profile import make_repo, out, run

CREDENTIALS = """education:
  - degree: "B.S."
    field:
    institution: "Example State University"
    score: 3.8
    year: 2016
    verification: "✅ VERIFIED — data-corpus/documents/diploma.pdf"
certifications:
  - name: "Example Cloud Practitioner"
    issuer:
    year: 2024
awards:
  - title: "Example Award"
    awarder:
    year: 2020
    details:
licenses:
  - name: "Example License"
    license_number: 12345
    jurisdiction:
"""


def test_sync_accepts_numbers_and_empty_values(tmp_path):
    repo = make_repo(tmp_path, variants=False)
    (repo / 'identity/credentials.yaml').write_text(CREDENTIALS, encoding='utf-8')
    (repo / 'identity/projects.yaml').write_text('public:\n  - name: "Proj"\n    tagline:\ninternal: []\n',
                                                 encoding='utf-8')
    proc = run(repo, 'tools/resume/sync.py')
    assert proc.returncode == 0, out(proc)
    pool = (repo / 'tools/resume/master.yaml').read_text(encoding='utf-8')
    assert 'Score: 3.8' in pool and 'License #12345' in pool


def test_validate_accepts_numbers_booleans_and_empty_values(tmp_path):
    repo = make_repo(tmp_path, variants=False)
    skills = repo / 'identity/skills.yaml'
    skills.write_text(skills.read_text(encoding='utf-8').replace('level: "advanced"', 'level: 4'), encoding='utf-8')
    exp = repo / 'identity/experience.yaml'
    exp.write_text(exp.read_text(encoding='utf-8').replace(
        'verification: "✅ VERIFIED — data-corpus/documents/offer-letter.pdf"', 'verification: true', 1), encoding='utf-8')
    ident = repo / 'identity/identity.yaml'
    ident.write_text(ident.read_text(encoding='utf-8').replace('name: "Alex Chen"', 'name:'), encoding='utf-8')
    proc = run(repo, '.pramedha/validate.py')
    assert 'Traceback' not in out(proc) and proc.returncode == 0, out(proc)
    proc = run(repo, '.pramedha/validate.py', '--status')
    assert 'parse error' not in out(proc), out(proc)

