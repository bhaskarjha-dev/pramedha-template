"""CRIT-06: a template update applies the template's fixes and never touches the user's data.

The throwaway "upstream" holds only the files listed under `template_owned` in this repository's
.pramedha/manifest.yaml plus five synthetic user files, so the test never copies your own data.
"""
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from _profile import EXPERIENCE, REPO, out

USER_FILES = {
    'config.yaml': 'user:\n  name: ""\n',
    'identity/experience.yaml': 'experience: []\n',
    'AGENTS.md': '# Agent instructions (template)\n',
    'VISION.md': '# Vision (template)\n',
    '.gitignore': '# ignore rules (template)\n',
}
SCRIPT = 'tools/update_template.py'
BOOTSTRAP = [SCRIPT, 'tools/resume/requirements.txt']  # what copies made before v0.2.0 lack


def env_for(tmp_path):
    config = tmp_path / 'gitconfig'
    config.write_text('', encoding='utf-8')
    return dict(os.environ, GIT_AUTHOR_NAME='Test User', GIT_AUTHOR_EMAIL='test@example.com',
                GIT_COMMITTER_NAME='Test User', GIT_COMMITTER_EMAIL='test@example.com',
                GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=str(config), PYTHONDONTWRITEBYTECODE='1')


def git(cwd, env, *args):
    proc = subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL)
    assert proc.returncode == 0, (args, proc.stdout, proc.stderr)
    return proc.stdout


def template_files():
    """Files (tracked, or new and not ignored) under the manifest's template_owned paths; never user data."""
    manifest = yaml.safe_load((REPO / '.pramedha/manifest.yaml').read_text(encoding='utf-8')) or {}
    owned = [str(p).strip('/') for p in (manifest.get('template_owned') or [])]
    proc = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=REPO,
                          capture_output=True, check=True, stdin=subprocess.DEVNULL)
    files = sorted({p for p in proc.stdout.decode('utf-8').split('\0') if p and (REPO / p).is_file()})
    return [f for f in files if any(f == o or f.startswith(o + '/') for o in owned)]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_copies(tmp_path, user_has_script):
    """Return (env, upstream, user, before): an upstream template and a filled "Use this template" copy."""
    env = env_for(tmp_path)
    upstream, user = tmp_path / 'upstream', tmp_path / 'user'
    for rel in template_files():
        (upstream / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, upstream / rel)
    for rel, text in USER_FILES.items():
        (upstream / rel).parent.mkdir(parents=True, exist_ok=True)
        (upstream / rel).write_text(text, encoding='utf-8')
    git(upstream, env, 'init', '-q', '-b', 'main')
    git(upstream, env, 'add', '-A')
    git(upstream, env, 'commit', '-qm', 'template')
    shutil.copytree(upstream, user, ignore=shutil.ignore_patterns('.git'))  # same files, unrelated history
    if not user_has_script:
        for rel in BOOTSTRAP:  # a copy made before the update script existed
            (user / rel).unlink()
    git(user, env, 'init', '-q', '-b', 'main')
    git(user, env, 'add', '-A')
    git(user, env, 'commit', '-qm', 'Initial commit')
    (user / 'identity/experience.yaml').write_text(EXPERIENCE, encoding='utf-8')
    with open(user / 'AGENTS.md', 'a', encoding='utf-8') as handle:
        handle.write('\n| Portfolio uses the "SDE" title | user decision | 2026-10-29 |\n')
    with open(user / 'config.yaml', 'a', encoding='utf-8') as handle:
        handle.write('\n# user edit\n')
    git(user, env, 'add', '-A')
    git(user, env, 'commit', '-qm', 'fill')
    before = {rel: sha(user / rel) for rel in USER_FILES}

    fixed = upstream / 'tools/resume/assemble.py'
    fixed.write_text(fixed.read_text(encoding='utf-8') + '\n# upstream fix marker\n', encoding='utf-8')
    template_exp = upstream / 'identity/experience.yaml'
    template_exp.write_text(template_exp.read_text(encoding='utf-8') + '# upstream comment\n', encoding='utf-8')
    with open(upstream / '.gitignore', 'a', encoding='utf-8') as handle:
        handle.write('# upstream ignore rule\n')
    git(upstream, env, 'commit', '-qam', 'fix')
    git(user, env, 'remote', 'add', 'upstream', str(upstream))
    git(user, env, 'fetch', '-q', 'upstream')
    return env, upstream, user, before


def run_update_and_check(env, upstream, user, before):
    proc = subprocess.run([sys.executable, SCRIPT], cwd=user, capture_output=True, text=True,
                          encoding='utf-8', env=env, stdin=subprocess.DEVNULL)
    assert proc.returncode == 0, out(proc)
    fixed = upstream / 'tools/resume/assemble.py'
    assert (user / 'tools/resume/assemble.py').read_text(encoding='utf-8') == fixed.read_text(encoding='utf-8')
    for rel, digest in before.items():
        assert sha(user / rel) == digest, rel
    assert 'tools/resume/assemble.py' in git(user, env, 'diff', '--staged', '--name-only')
    assert '.gitignore differs from the template' in proc.stdout, out(proc)  # merge-by-hand hint


def test_update_applies_template_fixes_and_keeps_user_data(tmp_path):
    run_update_and_check(*make_copies(tmp_path, user_has_script=True))


def test_copy_made_before_the_script_existed_can_bootstrap_it(tmp_path):
    env, upstream, user, before = make_copies(tmp_path, user_has_script=False)
    git(user, env, 'checkout', 'upstream/main', '--', *BOOTSTRAP)  # the documented one-time bootstrap
    git(user, env, 'commit', '-qm', 'Add template update script')
    run_update_and_check(env, upstream, user, before)

