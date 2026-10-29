"""CRIT-02: claims marked ❌, [unverified] or [to-verify] warn on resume build (Soft Gate D1=B)."""
from _profile import PAYMENTS, dump, load, make_repo, out, run, write_variant

ANCHOR = '"Processed 2M daily payment events in real time [measured]"'


def add_bullets(repo, *bullets):
    path = repo / 'identity/experience.yaml'
    extra = ''.join(f'\n              - "{b}"' for b in bullets)
    path.write_text(path.read_text(encoding='utf-8').replace(ANCHOR, ANCHOR + extra), encoding='utf-8')
    run(repo, 'tools/resume/sync.py', check=True)


def test_unverified_and_to_verify_claims_warn_and_build(tmp_path):
    repo = make_repo(tmp_path)
    add_bullets(repo, 'Led a 20-person team across 12 countries [unverified]', 'Saved $5M a year in fees [to-verify]')
    write_variant(repo, 'C_Lead.yaml', 'Lead', {PAYMENTS: [['led_20_person'], ['saved_5m_year']]})
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'C')
    assert proc.returncode == 0, out(proc)
    assert 'led_20_person' in out(proc) and 'saved_5m_year' in out(proc), out(proc)
    assert 'unverified' in out(proc).lower()
    assert (repo / 'tools/resume/generated/Alex_Chen_Lead_CV.yaml').exists()


def test_cross_mark_claim_warns_and_builds(tmp_path):
    repo = make_repo(tmp_path)
    add_bullets(repo, '❌ Mentored 12 engineers into senior roles')
    write_variant(repo, 'C_Lead.yaml', 'Lead', {PAYMENTS: ['mentored_12_engineers']})
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'C')
    assert proc.returncode == 0, out(proc)
    assert 'mentored_12_engineers' in out(proc)
    assert 'unverified' in out(proc).lower()
    assert (repo / 'tools/resume/generated/Alex_Chen_Lead_CV.yaml').exists()


def test_allow_unverified_flag_accepted(tmp_path):
    repo = make_repo(tmp_path)
    add_bullets(repo, 'Led a 20-person team across 12 countries [unverified]')
    write_variant(repo, 'C_Lead.yaml', 'Lead', {PAYMENTS: [['led_20_person']]})
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'C', '--allow-unverified')
    assert proc.returncode == 0, out(proc)
    assert 'unverified' in out(proc).lower()


def test_estimated_claim_builds_with_a_warning(tmp_path):
    repo = make_repo(tmp_path)
    add_bullets(repo, 'Cut cloud spend by about 30% [estimated]')
    write_variant(repo, 'C_Cost.yaml', 'Cost', {PAYMENTS: [['cut_cloud_spend']]})
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'C')
    assert proc.returncode == 0, out(proc)
    assert 'estimated' in out(proc).lower() and 'cut_cloud_spend' in out(proc)


def test_verified_profile_still_builds_without_tags_in_output(tmp_path):
    repo = make_repo(tmp_path)
    proc = run(repo, 'tools/resume/assemble.py')
    assert proc.returncode == 0, out(proc)
    generated = (repo / 'tools/resume/generated/Alex_Chen_Platform_CV.yaml').read_text(encoding='utf-8')
    assert 'recovery rate by 12%' in generated and '[measured]' not in generated


def add_deliverable(repo, verification, bullet):
    """Add a deliverable whose status lives in its `verification:` field, with an untagged bullet."""
    path = repo / 'identity/experience.yaml'
    anchor = '            skills: ["Python"]\n'
    extra = (anchor + '          - name: "Side deliverable"\n'
             f'            verification: "{verification}"\n'
             '            bullets:\n'
             f'              - "{bullet}"\n')
    path.write_text(path.read_text(encoding='utf-8').replace(anchor, extra, 1), encoding='utf-8')
    run(repo, 'tools/resume/sync.py', check=True)


def test_cross_mark_in_the_verification_field_warns_and_builds(tmp_path):
    repo = make_repo(tmp_path)
    add_deliverable(repo, '❌ UNVERIFIED — from a brain dump', 'Cut chargebacks by 40% with a fraud model')
    write_variant(repo, 'C_Fraud.yaml', 'Fraud', {PAYMENTS: [['cut_chargebacks_40']]})
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'C')
    assert proc.returncode == 0, out(proc)
    assert 'cut_chargebacks_40' in out(proc)
    assert 'unverified' in out(proc).lower()


def test_unverified_word_in_the_verification_field_warns_and_builds(tmp_path):
    repo = make_repo(tmp_path)
    add_deliverable(repo, 'UNVERIFIED — no evidence yet', 'Cut chargebacks by 40% with a fraud model')
    write_variant(repo, 'C_Fraud.yaml', 'Fraud', {PAYMENTS: [['cut_chargebacks_40']]})
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'C', '--validate')
    assert proc.returncode == 0, out(proc)
    assert 'unverified' in out(proc).lower()


def test_estimated_verification_field_warns(tmp_path):
    repo = make_repo(tmp_path)
    add_deliverable(repo, '⚠️ ESTIMATED — numbers from memory', 'Cut chargebacks by 40% with a fraud model')
    write_variant(repo, 'C_Fraud.yaml', 'Fraud', {PAYMENTS: [['cut_chargebacks_40']]})
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'C')
    assert proc.returncode == 0, out(proc)
    assert 'estimated' in out(proc).lower() and 'cut_chargebacks_40' in out(proc)


def test_clean_phrasing_with_unverified_source_warns_and_strips_tags(tmp_path):
    repo = make_repo(tmp_path)
    add_bullets(repo, 'Led a 20-person team across 12 countries [unverified]')
    pool = load(repo / 'tools/resume/master.yaml')
    pool['experience'][PAYMENTS]['bullets']['led_20_person']['short'] = 'Led a 20-person team'
    dump(pool, repo / 'tools/resume/master.yaml')
    write_variant(repo, 'C_Lead.yaml', 'Lead', {PAYMENTS: [['led_20_person', 'short']]})
    proc = run(repo, 'tools/resume/assemble.py', '--variant', 'C')
    assert proc.returncode == 0, out(proc)
    assert 'unverified' in out(proc).lower()

