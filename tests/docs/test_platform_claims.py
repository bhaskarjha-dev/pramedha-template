"""CRIT-07: no link to, or install command for, the unreleased Pramedha platform."""
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLATFORM_URL = re.compile(r'github\.com/bhaskarjha-dev/pramedha(?![-\w])')
INSTALL = 'pip install ' + 'pramedha'
CLI = 'pramedha ' + 'import --from'


def scanned_files():
    """The repository's own text files (tracked, or new and not ignored), so .venv/ and other ignored folders are skipped."""
    listed = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=REPO,
                            capture_output=True, check=True, stdin=subprocess.DEVNULL).stdout.decode('utf-8').split('\0')
    for rel in sorted(p for p in listed if p):
        path = REPO / rel
        if path.is_file() and path.suffix in {'.md', '.yaml', '.yml', '.py', '.sh', '.ps1'} \
                and not rel.startswith(('.agents/', 'tests/')):
            yield rel, path.read_text(encoding='utf-8', errors='replace')


def test_no_install_command_cli_or_link_for_the_platform():
    for rel, body in scanned_files():
        assert INSTALL not in body, rel
        assert CLI not in body, rel
        assert not PLATFORM_URL.search(body), rel


def test_readme_says_the_platform_is_not_available():
    assert 'not yet available' in (REPO / 'README.md').read_text(encoding='utf-8')

