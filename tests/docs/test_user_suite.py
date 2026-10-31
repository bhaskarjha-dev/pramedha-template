"""HIGH-07: users' default test run leaves out the template's own document checks, which only the template's CI
runs. Those checks read files a template update never replaces (AGENTS.md, .gitignore, design.yaml, VISION.md),
so in users' copies they fail after a correct update."""
import configparser
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def test_default_test_run_leaves_out_template_document_checks():
    ini = configparser.ConfigParser()
    ini.read(REPO / 'pytest.ini', encoding='utf-8')
    testpaths = ini['pytest']['testpaths'].split()
    assert 'tests/e2e' in testpaths, testpaths
    assert 'tests/docs' not in testpaths and 'tests/render' not in testpaths, testpaths


def test_template_ci_still_runs_the_document_checks():
    workflow = (REPO / '.github/workflows/validate.yml').read_text(encoding='utf-8')
    template_job = workflow.split('template-checks:', 1)[1]
    assert 'pytest tests/docs' in template_job

