"""HIGH-03: validate.py accepts the documented variant syntax and flags missing verification tags."""
import json
import shutil

from _profile import PAYMENTS, make_repo, out, run, write_variant


def validate_json(repo, *args):
    proc = run(repo, '.pramedha/validate.py', '--json', *args)
    return proc, json.loads(proc.stdout)


def test_with_resume_accepts_the_documented_list_syntax(tmp_path):
    repo = make_repo(tmp_path)
    proc, data = validate_json(repo, '--with-resume')
    assert data['error_count'] == 0, data['errors']


def test_with_resume_accepts_the_shipped_example_pair(tmp_path):
    repo = make_repo(tmp_path, variants=False)
    shutil.copy(repo / '.pramedha/examples/master-filled.yaml', repo / 'tools/resume/master.yaml')
    shutil.copy(repo / '.pramedha/examples/variant-example.yaml', repo / 'tools/resume/variants/backend.yaml')
    proc, data = validate_json(repo, '--with-resume')
    assert data['error_count'] == 0, data['errors']


def test_with_resume_reports_a_missing_bullet(tmp_path):
    repo = make_repo(tmp_path)
    write_variant(repo, 'C_Bad.yaml', 'Bad', {PAYMENTS: [['no_such_bullet']]})
    proc, data = validate_json(repo, '--with-resume')
    assert proc.returncode == 1, out(proc)
    assert any('no_such_bullet' in e for e in data['errors']), data['errors']


def test_untagged_entry_is_flagged_even_when_comments_carry_tags(tmp_path):
    repo = make_repo(tmp_path, variants=False)
    (repo / 'identity/experience.yaml').write_text(
        '# Verification Legend:\n'
        '#   ✅ VERIFIED   — Evidence exists\n'
        '#   ⚠️ ESTIMATED  — Reasonable but unverified\n'
        'experience:\n'
        '  - company: "Example Corp"\n'
        '    position: "Engineer"\n'
        '    start_date: "2021-01"\n'
        '    verification: "yes"\n', encoding='utf-8')
    proc, data = validate_json(repo)
    assert any('verification' in w.lower() and 'tag' in w.lower() for w in data['warnings']), data['warnings']


def test_fully_tagged_profile_gets_no_tag_warnings(tmp_path):
    repo = make_repo(tmp_path, variants=False)
    proc, data = validate_json(repo)
    assert not any('tag' in w.lower() for w in data['warnings']), data['warnings']


def test_untagged_credentials_file_is_flagged_even_when_comments_carry_tags(tmp_path):
    repo = make_repo(tmp_path, variants=False)
    (repo / 'identity/credentials.yaml').write_text(
        '# Verification Legend:\n'
        '#   ✅ VERIFIED   — Certificate/document exists\n'
        'education:\n'
        '  - degree: "B.S."\n'
        '    institution: "Example State University"\n', encoding='utf-8')
    proc, data = validate_json(repo)
    assert any('credentials.yaml' in w and 'tag' in w.lower() for w in data['warnings']), data['warnings']

