"""CRIT-01: the build script fails (non-zero exit) whenever it produces no PDF, and never renders
files that removed or renamed variants left in generated/."""
import subprocess
import sys

from _profile import make_repo


def build(repo):
    if sys.platform == 'win32':
        command = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', r'tools\resume\build.ps1']
    else:
        command = ['bash', 'tools/resume/build.sh']
    return subprocess.run(command, cwd=repo, capture_output=True, text=True, stdin=subprocess.DEVNULL)


def test_build_fails_when_a_render_fails_or_rendercv_is_missing(tmp_path):
    repo = make_repo(tmp_path)
    design = repo / 'tools/resume/design.yaml'
    body = design.read_text(encoding='utf-8')
    assert 'theme: engineeringresumes' in body
    design.write_text(body.replace('theme: engineeringresumes', 'theme: no_such_theme'), encoding='utf-8')
    proc = build(repo)  # RenderCV rejects the theme; without RenderCV the build stops earlier
    assert proc.returncode != 0, proc.stdout + proc.stderr


def test_build_fails_when_there_is_nothing_to_render(tmp_path):
    repo = make_repo(tmp_path, variants=False)
    proc = build(repo)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert 'sync.py' in proc.stdout + proc.stderr


def test_build_never_renders_files_left_by_removed_variants(tmp_path):
    repo = make_repo(tmp_path)
    stale = repo / 'tools/resume/generated/Old_Role_CV.yaml'
    stale.write_text('cv:\n  name: Alex Chen\n', encoding='utf-8')
    proc = build(repo)
    assert not stale.exists(), proc.stdout + proc.stderr
    assert (repo / 'tools/resume/generated/Alex_Chen_Backend_CV.yaml').exists(), proc.stdout + proc.stderr

