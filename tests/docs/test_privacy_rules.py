"""CRIT-04: every privacy statement matches what git tracks, and public copies fail CI."""
import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]


def text(rel):
    return (REPO / rel).read_text(encoding='utf-8')


def test_public_repository_recipe_is_gone():
    assert 'If you MUST use a public repo' not in text('README.md')
    assert 'PUBLIC REPOSITORY SAFETY OVERRIDE' not in text('.gitignore')
    assert not re.search(r'^#\s*(personal/|data-corpus/|strategy/financial\.md)', text('.gitignore'), re.M)
    assert 'uncomment the private file exclusions' not in text('GETTING_STARTED.md')


def test_no_false_privacy_statements():
    protocol = text('.pramedha/agent-instructions.md')
    assert 'excluded in .gitignore' not in protocol
    assert 'identity/ → public' not in protocol
    assert 'excluded in `.gitignore`' not in text('data-corpus/documents/README.md')


def test_sensitivity_map_marks_private_files():
    rows = text('README.md').splitlines()
    for rel in ('identity/identity.yaml', 'strategy/job-tracker.md', 'strategy/offer-comparison.md',
                'ops/session-handoff.md'):
        assert any(r.startswith(f'| `{rel}`') and 'Never' in r for r in rows), rel


def test_ci_fails_in_a_public_copy():
    jobs = yaml.safe_load(text('.github/workflows/validate.yml'))['jobs']
    guard = jobs['privacy-guard']
    condition = guard['if']
    assert 'github.event.repository.private == false' in condition
    assert "github.repository != 'bhaskarjha-dev/pramedha-template'" in condition
    assert any('exit 1' in str(step.get('run', '')) for step in guard['steps'])

