"""HIGH-06: the README's first screen says who it is for, what it needs, its limits, and shows a sample."""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def head():
    return '\n'.join((REPO / 'README.md').read_text(encoding='utf-8').splitlines()[:80])


def test_audience_requirements_limits_and_sample():
    top = head()
    for heading in ("## Who it's for", '## What you need', '## Limits'):
        assert heading in top, heading
    match = re.search(r'\((docs/sample/[^)\s]+\.pdf)\)', top)
    assert match, 'no link to docs/sample/<file>.pdf in the first 80 lines'
    assert (REPO / match.group(1)).exists(), match.group(1)


def test_no_releases_page_option():
    assert 'releases page' not in (REPO / 'README.md').read_text(encoding='utf-8')

