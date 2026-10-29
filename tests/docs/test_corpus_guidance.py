"""CRIT-05: the evidence guidance keeps employer-confidential material and other people's data out,
and says what the AI assistant sends to its provider."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def text(rel):
    return (REPO / rel).read_text(encoding='utf-8')


def test_checklist_drops_employer_internal_material():
    body = text('data-corpus/README.md')
    for item in ('Internal documentation/wikis', 'README files for private/internal repos',
                 'Database schemas, data models', 'Technical reports, RFCs', 'API documentation you wrote',
                 'LinkedIn full data export', 'Technical presentations & slide decks',
                 'Screen-recorded demos of working projects', 'Screenshots of live products, dashboards, outputs',
                 'Thank-you emails about specific work', 'Peer review feedback from performance cycles',
                 'Project demo recordings (screen capture', 'Screenshots of deployed UIs, dashboards, metrics'):
        assert item not in body, item


def test_never_and_provider_sections_exist():
    body = text('data-corpus/README.md')
    assert '## Never put these here' in body
    assert '## What your AI assistant sends' in body
    assert 'data-corpus/README.md#never-put-these-here' in text('GETTING_STARTED.md')


def test_linkedin_guidance_excludes_other_peoples_data():
    body = text('data-corpus/linkedin/README.md')
    assert 'Connections.csv' not in body
    assert 'messages' in body.lower()


def test_agent_skips_confidential_files():
    assert 'Files skipped' in text('.pramedha/agent-instructions.md')

