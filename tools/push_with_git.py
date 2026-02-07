#!/usr/bin/env python3
"""Push helper using system git. Reads remote from GIT_REMOTE env var or prompts.
If GITHUB_TOKEN is set and remote is HTTPS, it will inject the token into the URL for non-interactive push.
"""
import os
import shutil
import subprocess
import sys


def check_git():
    if not shutil.which('git'):
        print('git not found. Install Git (https://git-scm.com/) and rerun.')
        sys.exit(1)


def run(cmd, cwd=None):
    print('>', ' '.join(cmd))
    r = subprocess.run(cmd, cwd=cwd)
    if r.returncode != 0:
        raise SystemExit(r.returncode)


def main():
    check_git()
    remote = os.environ.get('GIT_REMOTE')
    if not remote:
        remote = input('Enter remote repository URL (https://github.com/you/Repo.git): ').strip()
    if not remote:
        print('No remote provided. Aborting.')
        sys.exit(1)

    token = os.environ.get('GITHUB_TOKEN')
    if token and remote.startswith('https://'):
        # inject token in URL (be careful: exposes token in process list)
        remote_with_token = remote.replace('https://', f'https://{token}@')
    else:
        remote_with_token = remote

    # current branch
    branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode().strip()
    print('Current branch:', branch)

    # add or set origin
    try:
        out = subprocess.check_output(['git', 'remote']).decode()
        remotes = [r.strip() for r in out.splitlines() if r.strip()]
    except subprocess.CalledProcessError:
        remotes = []

    if 'origin' in remotes:
        print('Setting origin to', remote)
        run(['git', 'remote', 'set-url', 'origin', remote_with_token])
    else:
        print('Adding origin', remote)
        run(['git', 'remote', 'add', 'origin', remote_with_token])

    # push
    run(['git', 'push', '-u', 'origin', branch])


if __name__ == '__main__':
    main()
