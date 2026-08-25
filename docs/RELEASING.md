# Releasing a New Version of NeoPilot

This guide explains how to deploy a new version of NeoPilot so that all users
get the update.

## Repository Setup

NeoPilot lives in two remotes:

| Remote | URL | Purpose |
|--------|-----|---------|
| `origin` | `https://bitbucket.org/odash/neopilot.git` | Private development repo (Bitbucket) |
| `github` | `https://github.com/tetris-solutions/neopilot.git` | Public distribution repo (GitHub) |

Development happens on Bitbucket. GitHub is the public mirror that users
install from.

## How Users Install

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/tetris-solutions/neopilot/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/tetris-solutions/neopilot/main/install.ps1 | iex
```

This clones the GitHub repo to `~/.neopilot/app/` and configures Claude Desktop.

## Release Process

### 1. Bump the version

Update the version in **two** places (they must match):

```bash
# src/neopilot/__init__.py
__version__ = "0.2.0"

# pyproject.toml
version = "0.2.0"
```

### 2. Update `version.json`

This file controls what users see when they connect:

```json
{
  "latest": "0.2.0",
  "minimum": "0.1.0",
  "update_url": "https://github.com/tetris-solutions/neopilot#updating-neopilot",
  "message": null
}
```

- `latest` — the newest version available. Users on older versions see a
  *"update available"* notice.
- `minimum` — the oldest version allowed. Users below this **cannot use**
  NeoPilot until they update. Use this for breaking changes or critical fixes.
- `update_url` — shown to users in the update notice.
- `message` — optional custom message (e.g., *"Important security fix"*).

### 3. Commit and push to Bitbucket

```bash
git add -A
git commit -m "Release v0.2.0"
git push origin develop
```

### 4. Push to GitHub (public)

```bash
git push github develop:main
```

This single command pushes your `develop` branch to GitHub's `main` branch,
which is what users install from.

### 5. Users update

**macOS / Linux:**
```bash
cd ~/.neopilot/app && git pull && .venv/bin/pip install -e .
```

**Windows (PowerShell):**
```powershell
cd $env:USERPROFILE\.neopilot\app; git pull; .venv\Scripts\pip.exe install -e .
```

Then restart Claude Desktop. Or they can re-run the install script which also
handles updates.

## Update Types

### Optional Update (soft nudge)

Set `latest` higher than `minimum`:

```json
{
  "latest": "0.3.0",
  "minimum": "0.1.0"
}
```

Users see when connecting:
> **NeoPilot update available:** v0.1.0 -> v0.3.0

They can keep using the old version.

### Forced Update (hard block)

Raise `minimum` to match `latest`:

```json
{
  "latest": "0.3.0",
  "minimum": "0.3.0",
  "message": "Breaking API change. Please update."
}
```

Users see when trying to query data:
> **NeoPilot v0.1.0 is no longer supported.**
> Minimum required version: v0.3.0
> Please update NeoPilot to continue.

### Emergency: Force update without a new release

If you need to block old versions **right now** without releasing new code,
just edit `version.json` on GitHub and raise `minimum`. You can do this
directly on github.com without touching the rest of the code. Users will be
blocked on their next `query_data` call.

## Adding the GitHub Remote (first time only)

If your local repo doesn't have the `github` remote yet:

```bash
git remote add github https://github.com/tetris-solutions/neopilot.git
```

Verify:
```bash
git remote -v
# origin   https://...bitbucket.org/odash/neopilot.git (fetch)
# origin   https://...bitbucket.org/odash/neopilot.git (push)
# github   https://github.com/tetris-solutions/neopilot.git (fetch)
# github   https://github.com/tetris-solutions/neopilot.git (push)
```

## Checklist

- [ ] Version bumped in `__init__.py` and `pyproject.toml`
- [ ] `version.json` updated with new `latest` (and `minimum` if forced)
- [ ] Tests pass: `python3 -m pytest tests/ -v --ignore=tests/test_integration.py`
- [ ] Lint passes: `ruff check src/ tests/`
- [ ] Committed and pushed to Bitbucket (`git push origin develop`)
- [ ] Pushed to GitHub (`git push github develop:main`)
