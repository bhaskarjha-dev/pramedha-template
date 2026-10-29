"""CRIT-03: a resume never shows a claim or role whose identity/ source changed or vanished.
Un-sourced claims typed directly into master emit warnings (Soft Gate D2=B)."""
from _profile import MESSAGING, PAYMENTS, dump, load, make_repo, out, run, write_variant


def edit_experience(repo, old, new):
    path = repo / 'identity/experience.yaml'
    body = path.read_text(encoding='utf-8')
    assert old in body
    path.write_text(body.replace(old, new), encoding='utf-8')
    run(repo, 'tools/resume/sync.py', check=True)


def test_corrected_bullet_is_refused_as_stale(tmp_path):
    repo = make_repo(tmp_path)
    edit_experience(repo, 'by 12% [measured]', 'by 9% [measured]')
    proc = run(repo, 'tools/resume/assemble.py', '--validate')
    assert proc.returncode == 1, out(proc)
    assert 'stale' in out(proc).lower() and 'designed_retry_pipeline' in out(proc), out(proc)


def test_changed_start_date_is_refused_as_stale(tmp_path):
    repo = make_repo(tmp_path)
    edit_experience(repo, 'start_date: "2020-06"', 'start_date: "2020-07"')
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'A')
    assert proc.returncode == 1, out(proc)
    assert 'stale' in out(proc).lower() and MESSAGING in out(proc), out(proc)


def test_changed_end_date_flows_through_without_reselecting(tmp_path):
    repo = make_repo(tmp_path)
    edit_experience(repo, 'end_date: "present"', 'end_date: "2026-09"')
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'B')
    assert proc.returncode == 0, out(proc)
    assert "2026-09" in (repo / 'tools/resume/generated/Alex_Chen_Platform_CV.yaml').read_text(encoding='utf-8')


def test_bullet_typed_into_master_warns_as_unsourced_and_builds(tmp_path):
    repo = make_repo(tmp_path)
    pool = load(repo / 'tools/resume/master.yaml')
    pool['experience'][PAYMENTS]['bullets']['typed_in_master'] = {'default': 'Typed straight into master.yaml'}
    dump(pool, repo / 'tools/resume/master.yaml')
    write_variant(repo, 'C_Typed.yaml', 'Typed', {PAYMENTS: [['typed_in_master']]})
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'C')
    assert proc.returncode == 0, out(proc)
    assert 'unsourced' in out(proc).lower() and 'typed_in_master' in out(proc)


def test_pool_synced_by_the_old_sync_is_backfilled(tmp_path):
    repo = make_repo(tmp_path)
    pool = load(repo / 'tools/resume/master.yaml')
    for role in pool['experience'].values():
        role.pop('_source', None)
        for bullet in role['bullets'].values():
            if isinstance(bullet, dict):
                bullet.pop('_source', None)
    dump(pool, repo / 'tools/resume/master.yaml')
    run(repo, 'tools/resume/sync.py', check=True)
    proc = run(repo, 'tools/resume/assemble.py', '--validate')
    assert proc.returncode == 0, out(proc)


def test_second_sync_changes_nothing(tmp_path):
    repo = make_repo(tmp_path)
    proc = run(repo, 'tools/resume/sync.py', check=True)
    assert 'already up to date' in out(proc), out(proc)


def test_shipped_example_pool_builds_with_unsourced_warning(tmp_path):
    repo = make_repo(tmp_path, variants=False)
    examples = repo / '.pramedha/examples'
    (repo / 'tools/resume/master.yaml').write_text((examples / 'master-filled.yaml').read_text(encoding='utf-8'),
                                                   encoding='utf-8')
    (repo / 'tools/resume/variants/backend.yaml').write_text(
        (examples / 'variant-example.yaml').read_text(encoding='utf-8'), encoding='utf-8')
    proc = run(repo, 'tools/resume/assemble.py', '--validate')
    assert proc.returncode == 0, out(proc)
    assert 'unsourced' in out(proc).lower()

