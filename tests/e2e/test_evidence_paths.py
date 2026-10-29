"""HIGH-05: every ✅ VERIFIED claim names an evidence file under data-corpus/ that exists."""
import json

from _profile import make_repo, run


def warnings(repo):
    proc = run(repo, '.pramedha/validate.py', '--json')
    return json.loads(proc.stdout)['warnings']


def test_verified_without_an_evidence_path_is_flagged(tmp_path):
    repo = make_repo(tmp_path, variants=False)
    exp = repo / 'identity/experience.yaml'
    exp.write_text(exp.read_text(encoding='utf-8').replace(
        '✅ VERIFIED — data-corpus/documents/offer-letter.pdf', '✅ VERIFIED — offer letter on file'), encoding='utf-8')
    found = warnings(repo)
    assert any('evidence' in w.lower() and 'experience.yaml' in w for w in found), found


def test_missing_evidence_file_is_flagged(tmp_path):
    repo = make_repo(tmp_path, variants=False)
    (repo / 'data-corpus/documents/offer-letter.pdf').unlink()
    found = warnings(repo)
    assert any('offer-letter.pdf' in w for w in found), found


def test_profile_with_evidence_files_is_clean(tmp_path):
    repo = make_repo(tmp_path, variants=False)
    found = warnings(repo)
    assert not any('evidence' in w.lower() for w in found), found


def test_a_folder_is_not_evidence(tmp_path):
    repo = make_repo(tmp_path, variants=False)
    exp = repo / 'identity/experience.yaml'
    exp.write_text(exp.read_text(encoding='utf-8').replace(
        'data-corpus/documents/offer-letter.pdf', 'data-corpus/documents/'), encoding='utf-8')
    found = warnings(repo)
    assert any('data-corpus/documents/' in w and 'file' in w.lower() for w in found), found


def test_public_url_counts_as_evidence(tmp_path):
    repo = make_repo(tmp_path, variants=False)
    proj = repo / 'identity/projects.yaml'
    proj.write_text(proj.read_text(encoding='utf-8').replace(
        'data-corpus/documents/openretry-readme.txt', 'https://github.com/example/openretry'), encoding='utf-8')
    found = warnings(repo)
    assert not any('evidence' in w.lower() for w in found), found


def test_shipped_examples_follow_the_evidence_rule():
    import re
    from pathlib import Path

    import yaml
    examples = Path(__file__).resolve().parents[2] / '.pramedha/examples'

    def values(node):
        if isinstance(node, dict):
            for key, item in node.items():
                if key == 'verification' and isinstance(item, str):
                    yield item
                else:
                    yield from values(item)
        elif isinstance(node, list):
            for item in node:
                yield from values(item)

    for path in sorted(examples.glob('*.yaml')):
        for text in values(yaml.safe_load(path.read_text(encoding='utf-8'))):
            if re.search(r'\u2705|\bVERIFIED\b', text):
                assert re.search(r'data-corpus/|https?://', text), (path.name, text)

