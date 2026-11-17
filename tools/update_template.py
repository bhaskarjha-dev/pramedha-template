#!/usr/bin/env python3
"""Update this career repository's template-owned files from the upstream template.

Usage (from the repository root, inside the virtual environment, after `git fetch upstream`):
    python tools/update_template.py              # replace template-owned files
    python tools/update_template.py --dry-run    # list what would change
    python tools/update_template.py --ref upstream/main

It reads the `template_owned` list from the upstream copy of .pramedha/manifest.yaml and checks out
exactly those paths from the upstream ref into your working tree and index. It never merges and never
touches your data: identity/, personal/, strategy/, positioning/, records/, data-corpus/ files, config.yaml,
VISION.md, AGENTS.md, .gitignore, tools/resume/master.yaml, design.yaml or your variants. When the template
changed AGENTS.md or .gitignore, it prints the command to compare them. Review the result with
`git diff --staged`, then commit.
"""
import argparse
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("ERROR: PyYAML required. In the virtual environment run: python -m pip install pyyaml==6.0.3")

MIXED_FILES = ['AGENTS.md', '.gitignore']  # template text plus your own lines: merge these by hand


def git(*args, check=True):
    proc = subprocess.run(['git', *args], capture_output=True, text=True,
                          encoding='utf-8', errors='replace', stdin=subprocess.DEVNULL)
    if check and proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc


def layout_steps(manifest: dict):
    """Commands that bring a copy made before a template restructure to the template's layout.

    `moved` in the upstream manifest maps old git-tracked paths to new ones; `retired` lists
    git-tracked template files the template no longer ships. Single-level parent folders are
    created when missing; nested targets must live under a `template_owned` folder or a folder
    moved earlier in `moved`. Returns (commands, conflicts). Moves nothing itself.
    """
    commands, conflicts, made = [], [], set()
    for old, new in (manifest.get('moved') or {}).items():
        old, new = str(old), str(new)
        if not Path(old).exists():
            continue
        if Path(new).exists():
            conflicts.append(f"{old} and {new} both exist: move your content from {old} into {new} by hand")
            continue
        parent = new.rsplit('/', 1)[0] if '/' in new else ''
        if parent and '/' not in parent and not Path(parent).exists() and parent not in made:
            commands.append(f"mkdir {parent}")
            made.add(parent)
        commands.append(f"git mv {old} {new}")
        made.add(new)
    for old in (manifest.get('retired') or []):
        if Path(str(old)).exists():
            commands.append(f"git rm -q {old}")
    return commands, conflicts


def print_layout_steps(manifest: dict, dry_run: bool = False):
    commands, conflicts = layout_steps(manifest)
    for conflict in conflicts:
        print(conflict)
    if commands:
        lead = "After updating, run" if dry_run else "Run"
        print("The template moved or retired files since your copy was made. "
              f"{lead} these to match its layout (file contents don't change), then commit and merge AGENTS.md:")
        for command in commands:
            print(f"  {command}")


def main():
    parser = argparse.ArgumentParser(description='Update template-owned files from the upstream template.')
    parser.add_argument('--ref', default='upstream/main', help='upstream ref to update from (default: upstream/main)')
    parser.add_argument('--dry-run', action='store_true', help='show what would change, change nothing')
    args = parser.parse_args()

    try:
        manifest = yaml.safe_load(git('show', f'{args.ref}:.pramedha/manifest.yaml').stdout) or {}
    except RuntimeError:
        sys.exit(f"Cannot read {args.ref}. Run once:\n"
                 f"  git remote add upstream https://github.com/bhaskarjha-dev/pramedha-template.git\n"
                 f"then: git fetch upstream")
    owned = [str(p).strip('/') for p in (manifest.get('template_owned') or [])]
    if not owned:
        sys.exit(f"{args.ref} has no template_owned list in .pramedha/manifest.yaml; nothing updated.")

    upstream_files = set(git('ls-tree', '-r', '--name-only', '-z', args.ref).stdout.split('\0'))
    paths = [p for p in owned if p in upstream_files or any(f.startswith(p + '/') for f in upstream_files)]
    if not paths:
        sys.exit(f"No matching template-owned files found in {args.ref}; nothing to update.")
    dirty = git('status', '--porcelain', '--', *paths).stdout.strip()
    if dirty:
        sys.exit("Commit or stash your changes to these template files first:\n" + dirty)

    local = Path('.pramedha/manifest.yaml')
    old = ((yaml.safe_load(local.read_text(encoding='utf-8')) or {}).get('template') or {}).get('version', '?') \
        if local.exists() else '?'
    new = (manifest.get('template') or {}).get('version', '?')
    print(f"Template files: {old} -> {new} (from {args.ref})")

    if args.dry_run:
        print(git('diff', '--stat', '--no-renames', '--diff-filter=AM', 'HEAD', args.ref, '--', *paths).stdout
              or 'No changes.')
        print_layout_steps(manifest, dry_run=True)
        return
    git('checkout', args.ref, '--', *paths)
    print(git('status', '--short', '--', *paths).stdout or 'Already up to date.')
    for mixed in MIXED_FILES:
        if git('diff', '--quiet', 'HEAD', args.ref, '--', mixed, check=False).returncode == 1:
            print(f"{mixed} differs from the template; merge template changes by hand: git diff HEAD {args.ref} -- {mixed}")
    print_layout_steps(manifest)
    print("Review with: git diff --staged    then commit.")


if __name__ == '__main__':
    main()

