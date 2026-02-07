Param()

# Simple PowerShell push helper.
# Prompts for remote URL (or reads from GIT_REMOTE env var) and pushes current branch.

function Check-Git {
    $g = Get-Command git -ErrorAction SilentlyContinue
    if (-not $g) {
        Write-Error "Git not found. Install Git (https://git-scm.com/) and rerun this script."
        exit 1
    }
}

Check-Git

$remote = $env:GIT_REMOTE
if (-not $remote) {
    $remote = Read-Host "Enter remote repository URL (e.g. https://github.com/you/CertIVCoach.git)"
}

if (-not $remote) {
    Write-Error "No remote provided. Aborting."
    exit 1
}

# Determine current branch
$branch = (& git rev-parse --abbrev-ref HEAD).Trim()
if (-not $branch) { Write-Error "Cannot determine current branch"; exit 1 }

Write-Host "Using branch: $branch"

# Check if remote exists
$existing = (& git remote).Split("`n") | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }
if ($existing -contains 'origin') {
    Write-Host "Updating origin to $remote"
    git remote set-url origin $remote
} else {
    Write-Host "Adding origin: $remote"
    git remote add origin $remote
}

Write-Host "Pushing to origin/$branch..."
try {
    & git push -u origin $branch
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Host "Push completed."
} catch {
    Write-Error "Push failed. If HTTP authentication is required, consider running: `\n git push https://<TOKEN>@github.com/youruser/yourrepo.git` or configure your Git credentials manager." 
    exit 1
}
