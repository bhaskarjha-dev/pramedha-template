"""CRIT-01: the documented build renders one PDF per variant.

Needs `tools/resume/requirements.txt` installed (Python 3.12+); CI's render job installs it.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'e2e'))
from _profile import make_repo  # noqa: E402


def test_documented_build_renders_two_pdfs(tmp_path):
    repo = make_repo(tmp_path)
    if sys.platform == 'win32':
        command = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', r'tools\resume\build.ps1']
    else:
        command = ['bash', 'tools/resume/build.sh']
    proc = subprocess.run(command, cwd=repo, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    for name in ('Alex_Chen_Backend_CV', 'Alex_Chen_Platform_CV'):
        pdf = repo / 'tools/resume/output' / f'{name}.pdf'
        assert pdf.exists() and pdf.stat().st_size > 1000, (name, proc.stdout + proc.stderr)

