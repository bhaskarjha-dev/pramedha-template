"""CRIT-01: the build script fails (non-zero exit) whenever it produces no PDF, and never renders
files that removed or renamed variants left in generated/."""
import os
import re
import subprocess
import sys

from _profile import make_repo


def build(repo):
    if sys.platform == 'win32':
        command = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', r'tools\resume\build.ps1']
    else:
        command = ['bash', 'tools/resume/build.sh']
    env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
    return subprocess.run(command, cwd=repo, capture_output=True, text=True,
                          encoding='utf-8', errors='replace', stdin=subprocess.DEVNULL, env=env)


def test_build_fails_when_a_render_fails_or_rendercv_is_missing(tmp_path):
    repo = make_repo(tmp_path)
    design = repo / 'tools/resume/design.yaml'  # the user's own theme file in their copies: any theme may be set
    body, count = re.subn(r'(?m)^(\s*theme:\s*)\S+', r'\1no_such_theme', design.read_text(encoding='utf-8'), count=1)
    assert count == 1, body
    design.write_text(body, encoding='utf-8')
    proc = build(repo)  # RenderCV rejects the theme; without RenderCV the build stops earlier
    out = (proc.stdout or '') + (proc.stderr or '')
    assert proc.returncode != 0, out


def test_build_fails_when_there_is_nothing_to_render(tmp_path):
    repo = make_repo(tmp_path, variants=False)
    proc = build(repo)
    out = (proc.stdout or '') + (proc.stderr or '')
    assert proc.returncode != 0, out
    assert 'sync.py' in out


def test_build_never_renders_files_left_by_removed_variants(tmp_path):
    repo = make_repo(tmp_path)
    stale = repo / 'tools/resume/generated/Old_Role_CV.yaml'
    stale.write_text('cv:\n  name: Alex Chen\n', encoding='utf-8')
    proc = build(repo)
    out = (proc.stdout or '') + (proc.stderr or '')
    assert not stale.exists(), out
    assert (repo / 'tools/resume/generated/Alex_Chen_Backend_CV.yaml').exists(), out

