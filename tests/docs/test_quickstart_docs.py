"""CRIT-01: the documented commands are the ones that work on Windows, macOS and Linux."""
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOCS = ['README.md', 'GETTING_STARTED.md', 'AGENTS.md', 'VISION.md', '.pramedha/agent-instructions.md',
        'tools/resume/README.md', 'ops/guide.md', 'ops/prompts.md', 'ops/authority-map.md', '.github/CONTRIBUTING.md']
CODE = ['tools/resume/sync.py', 'tools/resume/assemble.py', '.pramedha/validate.py', 'tools/resume/master.yaml',
        'tools/resume/build.sh', 'tools/resume/build.ps1']
SETUP = ['python3 -m venv .venv', 'py -m venv .venv', 'source .venv/bin/activate', '.venv\\Scripts\\activate.bat',
         # Windows PowerShell's default policy blocks Activate.ps1 unless the window's policy is relaxed first
         'Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass', '.venv\\Scripts\\Activate.ps1',
         'python -m pip install -r tools/resume/requirements.txt']
WINDOWS_BUILD = r'powershell -ExecutionPolicy Bypass -File tools\resume\build.ps1'
FENCE = '`' * 3  # a Markdown code fence
# Inside the activated virtual environment `python` works on every OS; `py` and `python3` don't.
WRONG_COMMAND = re.compile(r'(?<![\w./\\-])(?:py|python3) (?:\.pramedha|tools)[/\\]')


def text(rel):
    return (REPO / rel).read_text(encoding='utf-8')


def test_requirements_pin_the_full_rendercv():
    lines = [l.split('#')[0].strip() for l in text('tools/resume/requirements.txt').splitlines()]
    lines = [l for l in lines if l]
    assert 'pyyaml==6.0.3' in lines, lines  # no marker: the scripts run on Python 3.10+
    marker = r'rendercv\[full\]==2\.8\s*;\s*python_version\s*>=\s*["\']3\.12["\']'
    assert any(re.fullmatch(marker, l) for l in lines), lines  # skipped, not failed, on 3.10/3.11


def test_no_install_command_without_the_full_extra():
    for rel in DOCS + CODE + ['.github/workflows/validate.yml']:
        body = text(rel)
        assert 'pip install rendercv' not in body, rel
        assert 'pip install pyyaml rendercv' not in body, rel


def test_docs_show_the_virtual_environment_setup():
    for rel in ['README.md', 'GETTING_STARTED.md', 'tools/resume/README.md']:
        body = text(rel)
        for step in SETUP:
            assert step in body, (rel, step)
    assert 'python3-venv' in text('GETTING_STARTED.md')


def test_pdf_build_requires_python_3_12():
    for rel in ['GETTING_STARTED.md', 'tools/resume/build.sh']:
        assert 'Python 3.10+' not in text(rel), rel
    for rel in ['GETTING_STARTED.md', 'ops/guide.md', 'tools/resume/build.sh']:
        assert 'Python 3.12' in text(rel), rel


def test_script_commands_use_python_inside_the_venv():
    for rel in DOCS + CODE:
        for number, line in enumerate(text(rel).splitlines(), 1):
            if WRONG_COMMAND.search(line):
                raise AssertionError(f'{rel}:{number}: {line.strip()}')


def test_windows_build_command_works_under_the_default_policy():
    for rel in ['README.md', 'GETTING_STARTED.md', 'tools/resume/README.md']:
        body = text(rel)
        assert WINDOWS_BUILD in body, rel
        assert not re.search(r'^\s*\.\\tools\\resume\\build\.ps1', body, re.M), rel
        assert 'pwsh tools/resume/build.ps1' not in body, rel


def test_build_scripts_prefer_the_repository_venv():
    assert '.venv/bin/python' in text('tools/resume/build.sh')
    assert '.venv\\Scripts\\python.exe' in text('tools/resume/build.ps1')


def test_theme_lists_name_only_rendercv_2_8_themes():
    body = text('tools/resume/README.md')
    design = text('tools/resume/design.yaml')
    for theme in ('developer', 'compact', 'academic'):
        assert f'`{theme}`' not in body, theme
        assert not re.search(rf'\b{theme}\b', design), theme


def test_quick_starts_create_a_variant_before_building():
    for rel in ['README.md', 'GETTING_STARTED.md', 'tools/resume/README.md']:
        blocks = [b for b in re.findall(FENCE + r'[a-z]*\n(.*?)' + FENCE, text(rel), re.S)
                  if 'bash tools/resume/build.sh' in b]
        assert blocks, rel
        for block in blocks:
            assert 'variants/_template.yaml' in block, (rel, block)
            assert block.index('variants/_template.yaml') < block.index('bash tools/resume/build.sh'), (rel, block)


def test_build_sh_is_executable_and_docs_run_it_with_bash():
    entry = subprocess.run(['git', 'ls-files', '-s', 'tools/resume/build.sh'], cwd=REPO,
                           capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout
    assert entry.startswith('100755'), entry
    for rel in ['README.md', 'GETTING_STARTED.md', 'tools/resume/README.md']:
        assert 'bash tools/resume/build.sh' in text(rel), rel

