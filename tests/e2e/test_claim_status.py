"""CRIT-08: talks, volunteering, certifications, awards, projects and degrees carry their verification status into
the resume build, so a claim marked ❌ in identity/ is always reported, as experience bullets already are."""
from _profile import BACKEND, load, make_repo, out, run, write_variant

SPEAKING = ('speaking:\n'
            '  - title: "Scaling payments to 1B events a day"\n'
            '    event: "Example Conf 2025"\n'
            '    date: "2025-05"\n'
            '    verification: "❌ UNVERIFIED — proposal submitted, not accepted"\n')
VOLUNTEERING = ('volunteering:\n'
                '  - organization: "Example Food Bank"\n'
                '    role: "Volunteer coordinator"\n'
                '    verification: "UNVERIFIED — no record yet"\n')

CREDENTIALS_EXTRA = ('certifications:\n'
                     '  - name: "Example Cloud Architect"\n'
                     '    issuer: "Example Cloud"\n'
                     '    verification: "❌ UNVERIFIED — exam booked, not passed"\n'
                     '  - name: "Example Kubernetes Admin"\n'
                     '    issuer: "Example Foundation"\n'
                     '    verification: "✅ VERIFIED — data-corpus/documents/offer-letter.pdf"\n'
                     'awards:\n'
                     '  - title: "Example Hero Award"\n'
                     '    awarder: "Example Payments Inc"\n'
                     '    verification: "⚠️ ESTIMATED — announced in a team meeting"\n')


def synced_pool(repo):
    run(repo, 'tools/resume/sync.py', check=True)
    return load(repo / 'tools/resume/master.yaml')


def build(repo, name, **fields):
    write_variant(repo, f'C_{name}.yaml', name, BACKEND, **fields)
    return run(repo, 'tools/resume/assemble.py', '--variant', 'C')


def test_unverified_talk_and_volunteering_are_reported(tmp_path):
    repo = make_repo(tmp_path)
    (repo / 'identity/speaking-and-community.yaml').write_text(SPEAKING, encoding='utf-8')
    (repo / 'identity/volunteering.yaml').write_text(VOLUNTEERING, encoding='utf-8')
    keys = sorted(synced_pool(repo).get('achievements') or {})
    assert len(keys) == 2, keys
    proc = build(repo, 'Talk', achievements=keys)
    for key in keys:
        assert key in out(proc), (key, out(proc))
    assert 'unverified' in out(proc).lower(), out(proc)


def test_unverified_project_is_reported(tmp_path):
    repo = make_repo(tmp_path)
    projects = repo / 'identity/projects.yaml'
    projects.write_text(projects.read_text(encoding='utf-8').replace(
        '✅ VERIFIED — data-corpus/documents/openretry-readme.txt', '❌ UNVERIFIED — repository is private'),
        encoding='utf-8')
    project = next(iter(synced_pool(repo).get('projects') or {}))
    proc = build(repo, 'Project', projects=[project])
    assert 'OpenRetry' in out(proc) and 'unverified' in out(proc).lower(), out(proc)


def test_unverified_degree_is_reported(tmp_path):
    repo = make_repo(tmp_path)
    credentials = repo / 'identity/credentials.yaml'
    credentials.write_text(credentials.read_text(encoding='utf-8').replace(
        '✅ VERIFIED — data-corpus/documents/diploma.pdf', '❌ UNVERIFIED — no certificate found'), encoding='utf-8')
    synced_pool(repo)
    proc = build(repo, 'Degree')
    assert 'B.S.' in out(proc) and 'unverified' in out(proc).lower(), out(proc)


def test_verified_profile_reports_nothing_and_keeps_status_out_of_the_resume(tmp_path):
    repo = make_repo(tmp_path)
    project = next(iter(synced_pool(repo).get('projects') or {}))
    proc = build(repo, 'Clean', projects=[project])
    assert proc.returncode == 0, out(proc)
    assert 'unverified' not in out(proc).lower() and 'estimated' not in out(proc).lower(), out(proc)
    generated = (repo / 'tools/resume/generated/Alex_Chen_Clean_CV.yaml').read_text(encoding='utf-8')
    assert '_verification' not in generated and 'VERIFIED' not in generated, generated
    second = run(repo, 'tools/resume/sync.py')
    assert second.returncode == 0 and 'already up to date' in out(second).lower(), out(second)


def test_certifications_and_awards_are_reported_by_their_own_status(tmp_path):
    repo = make_repo(tmp_path)
    credentials = repo / 'identity/credentials.yaml'
    credentials.write_text(credentials.read_text(encoding='utf-8') + CREDENTIALS_EXTRA, encoding='utf-8')
    keys = sorted(synced_pool(repo).get('achievements') or {})
    assert len(keys) == 3, keys
    lines = out(build(repo, 'Creds', achievements=keys)).splitlines()

    def said(key):
        return ' '.join(line.lower() for line in lines if key in line)

    unverified, verified, estimated = (next(k for k in keys if word in k)
                                       for word in ('architect', 'kubernetes', 'hero'))
    assert 'unverified' in said(unverified), lines
    assert 'estimated' in said(estimated) and 'unverified' not in said(estimated), lines
    assert said(verified) == '', lines

