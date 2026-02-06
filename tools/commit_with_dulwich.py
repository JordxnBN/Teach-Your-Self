import os
from dulwich import porcelain
from dulwich.repo import Repo

repo_path = '.'
branch = b'feature/quiz-hints-glossary'

print('Running dulwich commit in', os.path.abspath(repo_path))

# Init repo if missing
if not os.path.exists(os.path.join(repo_path, '.git')):
    print('Initializing new git repo')
    porcelain.init(repo_path)
else:
    print('.git exists; using existing repo')

# Collect files to add (exclude .git)
paths = []
for dirpath, dirnames, filenames in os.walk(repo_path):
    # skip .git directory
    if '.git' in dirpath.split(os.sep):
        continue
    for fn in filenames:
        # skip compiled/venv directories
        if fn.endswith('.pyc'):
            continue
        full = os.path.join(dirpath, fn)
        rel = os.path.relpath(full, repo_path)
        paths.append(rel)

# Stage files
print('Staging', len(paths), 'files')
porcelain.add(repo_path, paths)

# Commit
msg = b'Add quiz hint UI, glossary modal, seed contexts, DB migration, CI, and docs'
author = b'CertIVCoach Bot <noreply@example.com>'
print('Committing...')
porcelain.commit(repo_path, msg, author=author)

# Create branch if not exists and point HEAD to it
repo = Repo(repo_path)
try:
    repo.refs[b'refs/heads/' + branch]
    print('Branch already exists')
except KeyError:
    print('Creating branch', branch.decode())
    porcelain.branch_create(repo_path, branch)

print('Setting HEAD to branch', branch.decode())
repo.refs.set_symbolic_ref(b'HEAD', b'refs/heads/' + branch)
print('Done')
