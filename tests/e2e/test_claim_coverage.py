"""CRIT-09: skills and publications carry their verification status into the resume build, like every other
claim, whichever way a variant puts them on the resume, and every resume section built from identity/
reports the unverified entries it holds."""
import re

from _profile import BACKEND, MESSAGING, PAYMENTS, load, make_repo, out, run, write_variant

SKILLS_EXTRA = ('cloud:\n'
                '  - name: "Kubernetes"\n'
                '    level: "advanced"\n'
                '    verification: "❌ UNVERIFIED — want to learn; never used"\n'
                '  - name: "AWS (EC2, S3)"\n'
                '    verification: "❌ UNVERIFIED — never used"\n'
                'systems:\n'
                '  - name: "Rust"\n'
                '    level: "intermediate"\n'
                '    verification: "⚠️ ESTIMATED — self-assessed"\n')
PUBLICATION = ('publications:\n'
               '  - title: "Exactly-once payments at scale"\n'
               '    authors: ["Alex Chen"]\n'
               '    date: "2025-03"\n'
               '    journal: "Example Systems Conference"\n'
               '    verification: "❌ UNVERIFIED — submitted, not accepted"\n')
TALK = ('speaking:\n'
        '  - title: "Retry budgets in practice"\n'
        '    event: "Example Meetup"\n'
        '    date: "2024-09"\n'
        '    verification: "✅ VERIFIED — data-corpus/documents/launch-note.txt"\n')
# Every resume section built from identity/, and how assemble.py labels its claims ("[variant] <label>...").
LABELS = {'experience': (PAYMENTS, MESSAGING), 'projects': ('project ',), 'education': ('education ',),
          'achievements': ('achievement ',), 'technologies': ('skills ',), 'publications': ('publication ',)}


def append(repo, rel, text):
    path = repo / rel
    path.write_text(path.read_text(encoding='utf-8') + text, encoding='utf-8')


def build(repo, name, **fields):
    write_variant(repo, f'C_{name}.yaml', name, BACKEND, **fields)
    return run(repo, 'tools/resume/assemble.py', '--variant', 'C')


def test_unverified_and_estimated_skills_are_reported(tmp_path):
    repo = make_repo(tmp_path)
    append(repo, 'identity/skills.yaml', SKILLS_EXTRA)
    run(repo, 'tools/resume/sync.py', check=True)
    proc = build(repo, 'Skills')
    lines = out(proc).splitlines()
    assert proc.returncode == 0, out(proc)
    assert any('Kubernetes' in line and 'unverified' in line.lower() for line in lines), lines
    assert any('AWS (EC2, S3)' in line and 'unverified' in line.lower() for line in lines), lines
    assert any('Rust' in line and 'estimated' in line.lower() for line in lines), lines
    assert not any('Programming' in line for line in lines), lines  # the verified skills stay quiet
    generated = (repo / 'tools/resume/generated/Alex_Chen_Skills_CV.yaml').read_text(encoding='utf-8')
    assert 'Kubernetes' in generated and '_verification' not in generated and 'ESTIMATED' not in generated, generated
    second = run(repo, 'tools/resume/sync.py')
    assert second.returncode == 0 and 'already up to date' in out(second).lower(), out(second)


def test_publications_are_reported_exactly_when_on_the_resume(tmp_path):
    repo = make_repo(tmp_path)
    append(repo, 'identity/credentials.yaml', PUBLICATION)
    run(repo, 'tools/resume/sync.py', check=True)
    pool = load(repo / 'tools/resume/master.yaml')
    own = [{k: v for k, v in pool['publications'][0].items() if not k.startswith('_')}]  # typed into the variant
    write_variant(repo, 'C_NoPubs.yaml', 'NoPubs', BACKEND)
    write_variant(repo, 'C_Pubs.yaml', 'Pubs', BACKEND, publications=True)
    write_variant(repo, 'C_Legacy.yaml', 'Legacy', BACKEND, include_publications=True)
    write_variant(repo, 'C_Own.yaml', 'Own', BACKEND, publications=own)
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'C')
    assert proc.returncode == 0, out(proc)
    flagged = [line for line in out(proc).splitlines() if 'Exactly-once' in line and 'unverified' in line.lower()]
    for name in ('Pubs', 'Legacy', 'Own'):
        assert any(f'[{name}]' in line for line in flagged), (name, flagged)
    assert not any('[NoPubs]' in line for line in flagged), flagged
    generated = (repo / 'tools/resume/generated/Alex_Chen_Pubs_CV.yaml').read_text(encoding='utf-8')
    assert 'Exactly-once' in generated and '_verification' not in generated and 'UNVERIFIED' not in generated, \
        generated


def test_every_identity_section_on_the_resume_reports_its_unverified_entries(tmp_path):
    repo = make_repo(tmp_path, variants=False)
    append(repo, 'identity/skills.yaml', SKILLS_EXTRA)
    append(repo, 'identity/credentials.yaml', PUBLICATION)
    (repo / 'identity/speaking-and-community.yaml').write_text(TALK, encoding='utf-8')
    for path in (repo / 'identity').glob('*.yaml'):
        text = path.read_text(encoding='utf-8')
        path.write_text(re.sub(r'✅ VERIFIED[^"\n]*', '❌ UNVERIFIED — not checked', text), encoding='utf-8')
    run(repo, 'tools/resume/sync.py', check=True)
    pool = load(repo / 'tools/resume/master.yaml')
    proc = build(repo, 'Everything', projects=sorted(pool.get('projects') or {}),
                 achievements=sorted(pool.get('achievements') or {}), publications=True)
    assert proc.returncode == 0, out(proc)
    flagged = [line for line in out(proc).splitlines() if 'unverified' in line.lower()]
    sections = load(repo / 'tools/resume/generated/Alex_Chen_Everything_CV.yaml')['cv']['sections']
    assert len(sections) >= 7, sections.keys()
    for section in sections:
        if section == 'summary':
            continue
        assert section in LABELS, f'resume section {section!r} has no unverified-claim check'
        assert any(f'] {label}' in line for line in flagged for label in LABELS[section]), (section, flagged)


def test_skills_in_a_variants_own_technologies_list_are_reported(tmp_path):
    repo = make_repo(tmp_path)
    append(repo, 'identity/skills.yaml', SKILLS_EXTRA)
    run(repo, 'tools/resume/sync.py', check=True)
    proc = build(repo, 'Own', technologies=[{'label': 'Cloud', 'details': 'kubernetes, Rust, Terraform'}])
    lines = out(proc).splitlines()
    assert proc.returncode == 0, out(proc)
    assert any('Kubernetes' in line and 'unverified' in line.lower() for line in lines), lines
    assert any('Rust' in line and 'estimated' in line.lower() for line in lines), lines
    assert not any('Terraform' in line for line in lines), lines  # not in identity/: no status, like typed bullets


def test_statuses_changed_after_the_first_sync_are_reported(tmp_path):
    repo = make_repo(tmp_path)  # its sync already copied Python and Go, both ✅
    append(repo, 'identity/credentials.yaml', PUBLICATION.replace('❌ UNVERIFIED — submitted, not accepted',
                                                                  '✅ VERIFIED — data-corpus/documents/diploma.pdf'))
    run(repo, 'tools/resume/sync.py', check=True)
    for rel in ('identity/skills.yaml', 'identity/credentials.yaml'):
        path = repo / rel
        text = path.read_text(encoding='utf-8')
        for evidence in ('experience-letter.pdf', 'diploma.pdf'):
            text = text.replace(f'✅ VERIFIED — data-corpus/documents/{evidence}', '❌ UNVERIFIED — not checked')
        path.write_text(text, encoding='utf-8')
    run(repo, 'tools/resume/sync.py', check=True)
    proc = build(repo, 'Later', publications=True)
    flagged = [line for line in out(proc).splitlines() if 'unverified' in line.lower()]
    assert any('] skills Go' in line for line in flagged), flagged
    assert any('Exactly-once' in line for line in flagged), flagged


def test_skills_not_on_the_resume_stay_quiet(tmp_path):
    repo = make_repo(tmp_path)
    append(repo, 'identity/skills.yaml', SKILLS_EXTRA)
    run(repo, 'tools/resume/sync.py', check=True)
    append(repo, 'identity/skills.yaml', '  - name: "Haskell"\n    verification: "❌ UNVERIFIED — never used"\n')
    run(repo, 'tools/resume/sync.py', check=True)  # without --force, the existing Systems category keeps "Rust"
    build(repo, 'Hidden', section_order=['summary', 'experience'])
    lines = out(build(repo, 'Shown')).splitlines()  # --variant C builds C_Hidden and C_Shown
    assert any('[Shown] skills Kubernetes' in line for line in lines), lines
    assert not any('[Hidden] skills' in line for line in lines), lines
    assert not any('Haskell' in line for line in lines), lines

