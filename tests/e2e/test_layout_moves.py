"""HIGH-09: a copy made before the template moved its folders learns, when it updates, exactly how to move
its own files to the template's layout. The script prints the commands; the files' contents never change."""
import subprocess
import sys

import yaml

from _profile import out
from test_template_update import SCRIPT, git, make_copies

OLD_LAYOUT = {
    'stories/star-stories.md': '# STAR stories\n\n## Story 1: cut checkout latency (mine)\n',
    'journal/wins.md': '# Wins\n\n- Shipped the retry service (mine)\n',
    'ops/session-handoff.md': '# Session handoff\n\n- Next: tailor the resume for Example Corp (mine)\n',
    'ops/guide.md': '# Maintenance guide (old template copy)\n',
    'ops/prompts.md': '# AI prompts (old template copy)\n',
    'ops/authority-map.md': '# Authority map (old template copy)\n',
    'identity/professional-summary.md': '# Professional Summary\n\n'
                                        'Dana is a backend engineer with six years of payments work.\n',
    'personal/career-narrative.md': '# Career Narrative\n\nMy walk-me-through script.\n',
    'identity/references.yaml': 'references:\n  - name: "Riley Example"\n    email: "riley@example.com"\n',
}
RETIRED = ('ops/guide.md', 'ops/prompts.md', 'ops/authority-map.md')
NEW_PATHS = {
    'stories/star-stories.md': 'positioning/star-stories.md',
    'journal/wins.md': 'records/wins.md',
    'ops/session-handoff.md': '.pramedha/ops/session-handoff.md',
    'identity/professional-summary.md': 'positioning/professional-summary.md',
    'personal/career-narrative.md': 'positioning/career-narrative.md',
    'identity/references.yaml': 'personal/references.yaml',
}


def strip_layout_lists(repo):
    manifest_file = repo / '.pramedha/manifest.yaml'
    data = yaml.safe_load(manifest_file.read_text(encoding='utf-8')) or {}
    data.pop('moved', None)
    data.pop('retired', None)
    manifest_file.write_text(yaml.safe_dump(data, sort_keys=False), encoding='utf-8')


def old_layout_copy(tmp_path):
    env, upstream, user, _ = make_copies(tmp_path, user_has_script=True)
    strip_layout_lists(user)  # pre-restructure copies had no moved/retired lists locally
    for rel, body in OLD_LAYOUT.items():
        (user / rel).parent.mkdir(parents=True, exist_ok=True)
        (user / rel).write_text(body, encoding='utf-8')
    git(user, env, 'add', '-A')
    git(user, env, 'commit', '-qm', 'my files, in the layout my copy started with')
    return env, upstream, user


def run(user, env, *args):
    return subprocess.run([sys.executable, *args], cwd=user, capture_output=True, text=True,
                          encoding='utf-8', errors='replace', env=env, stdin=subprocess.DEVNULL)


def printed_commands(proc):
    return [line.strip() for line in proc.stdout.splitlines()
            if line.strip().startswith(('git mv ', 'git rm ', 'mkdir '))]


def exec_printed(user, env, commands):
    for command in commands:
        words = command.split()
        if words[0] == 'mkdir':
            (user / words[1]).mkdir()
        else:
            git(user, env, *words[1:])


def test_update_prints_the_moves_and_running_them_keeps_every_file(tmp_path):
    env, _, user = old_layout_copy(tmp_path)
    proc = run(user, env, SCRIPT)
    assert proc.returncode == 0, out(proc)
    commands = printed_commands(proc)
    for old, new in NEW_PATHS.items():
        source = old.split('/')[0] if old.split('/')[0] in ('stories', 'journal') else old
        target = new.split('/')[0] if old.split('/')[0] in ('stories', 'journal') else new
        assert f'git mv {source} {target}' in commands, (old, proc.stdout)
    for retired in RETIRED:
        assert f'git rm -q {retired}' in commands, (retired, proc.stdout)
    exec_printed(user, env, commands)
    for old, new in NEW_PATHS.items():
        assert not (user / old).exists(), old
        assert (user / new).read_text(encoding='utf-8') == OLD_LAYOUT[old], new
    assert not (user / 'ops').exists()
    status = run(user, env, '.pramedha/validate.py', '--status')
    assert '✅ professional-summary.md' in out(status), out(status)
    git(user, env, 'commit', '-qm', 'Update template files and move to the new layout')
    assert printed_commands(run(user, env, SCRIPT)) == []  # nothing left to move


def test_dry_run_lists_the_moves_and_changes_nothing(tmp_path):
    env, _, user = old_layout_copy(tmp_path)
    proc = run(user, env, SCRIPT, '--dry-run')
    assert proc.returncode == 0 and 'git mv stories positioning' in printed_commands(proc), out(proc)
    assert 'After updating, run' in proc.stdout, proc.stdout
    assert (user / 'stories/star-stories.md').exists()
    assert git(user, env, 'status', '--porcelain') == ''


def test_a_copy_that_has_both_layouts_is_told_to_merge_by_hand(tmp_path):
    env, _, user = old_layout_copy(tmp_path)
    (user / 'positioning').mkdir()
    (user / 'positioning/star-stories.md').write_text('# STAR stories (started by an agent)\n', encoding='utf-8')
    git(user, env, 'add', '-A')
    git(user, env, 'commit', '-qm', 'an agent started the new folder')
    proc = run(user, env, SCRIPT)
    assert proc.returncode == 0, out(proc)
    assert 'stories and positioning both exist' in proc.stdout, proc.stdout
    assert 'git mv stories positioning' not in printed_commands(proc), proc.stdout


def test_moves_come_from_upstream_manifest_and_create_missing_parents(tmp_path):
    env, upstream, user, _ = make_copies(tmp_path, user_has_script=True)
    strip_layout_lists(user)
    (user / 'identity/professional-summary.md').write_text(OLD_LAYOUT['identity/professional-summary.md'], encoding='utf-8')
    (user / 'legacy').mkdir()
    (user / 'legacy/note.md').write_text('# Custom legacy note\n', encoding='utf-8')
    git(user, env, 'add', '-A')
    git(user, env, 'commit', '-qm', 'no stories folder, plus a future custom move')

    mfile = upstream / '.pramedha/manifest.yaml'
    mdata = yaml.safe_load(mfile.read_text(encoding='utf-8')) or {}
    mdata.setdefault('moved', {})['legacy/note.md'] = 'archive/note.md'
    mfile.write_text(yaml.safe_dump(mdata, sort_keys=False), encoding='utf-8')
    git(upstream, env, 'add', '.pramedha/manifest.yaml')
    git(upstream, env, 'commit', '-qm', 'upstream adds a future move')
    git(user, env, 'fetch', '-q', 'upstream')

    proc = run(user, env, SCRIPT)
    assert proc.returncode == 0, out(proc)
    commands = printed_commands(proc)
    assert commands.index('mkdir positioning') < commands.index(
        'git mv identity/professional-summary.md positioning/professional-summary.md'), commands
    assert commands.index('mkdir archive') < commands.index('git mv legacy/note.md archive/note.md'), commands
    exec_printed(user, env, commands)
    assert (user / 'positioning/professional-summary.md').read_text(encoding='utf-8') == OLD_LAYOUT['identity/professional-summary.md']
    assert (user / 'archive/note.md').read_text(encoding='utf-8') == '# Custom legacy note\n'
