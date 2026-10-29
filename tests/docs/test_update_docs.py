"""CRIT-06: the documented update path is the update script, and the manifest says who owns what."""
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]


def text(rel):
    return (REPO / rel).read_text(encoding='utf-8')


def test_docs_use_the_update_script_instead_of_merges():
    for rel in ('README.md', 'GETTING_STARTED.md'):
        body = text(rel)
        assert '--allow-unrelated-histories' not in body, rel
        assert '-X theirs' not in body and '-X ours' not in body, rel
        assert 'tools/update_template.py' in body, rel
        # copies made before v0.2.0 fetch the script and the requirements file it points to
        assert 'git checkout upstream/main -- tools/update_template.py tools/resume/requirements.txt' in body, rel


def test_manifest_lists_only_template_owned_paths():
    owned = yaml.safe_load(text('.pramedha/manifest.yaml'))['template_owned']
    for path in ('tools/resume/assemble.py', '.pramedha/validate.py', 'tools/update_template.py'):
        assert path in owned, path
    for path in owned:
        top = path.split('/')[0]
        if top in ('identity', 'personal', 'strategy', 'journal', 'stories', 'data-corpus'):
            assert path.endswith('README.md'), path
        assert path not in ('config.yaml', 'AGENTS.md', 'VISION.md', 'tools', 'tools/resume',
                            'tools/resume/master.yaml', 'tools/resume/design.yaml',
                            'tools/resume/variants', 'tools/resume/jd'), path

