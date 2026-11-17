"""HIGH-09: update docs tell pre-v0.1.0 copies to fetch the current update script and explain printed layout moves."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def text(rel):
    return (REPO / rel).read_text(encoding='utf-8')


def test_bootstrap_comment_covers_older_update_scripts():
    for rel in ('README.md', 'GETTING_STARTED.md'):
        assert 'no tools/update_template.py, or an older one' in text(rel), rel


def test_readme_and_changelog_document_printed_layout_moves():
    readme = text('README.md')
    assert '`git mv`' in readme and '`git rm`' in readme
    changelog = text('.github/CHANGELOG.md')
    assert 'tools/update_template.py' in changelog and '`moved`' in changelog and '`retired`' in changelog
