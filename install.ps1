# ============================================================================
# NeoPilot Installer for Windows
# One-command setup for Windows users with Claude Desktop
#
# Usage (PowerShell):
#   irm https://raw.githubusercontent.com/tetris-solutions/neopilot/main/install.ps1 | iex
#
# Or clone + run locally:
#   git clone https://github.com/tetris-solutions/neopilot.git
#   cd neopilot; .\install.ps1
# ============================================================================

$ErrorActionPreference = "Continue"

function Info($msg)    { Write-Host "i  $msg" -ForegroundColor Blue }
function Success($msg) { Write-Host "OK $msg" -ForegroundColor Green }
function Warn($msg)    { Write-Host "!  $msg" -ForegroundColor Yellow }
function Fail($msg)    { Write-Host "X  $msg" -ForegroundColor Red; exit 1 }

Write-Host ""
Write-Host "+======================================+" -ForegroundColor Blue
Write-Host "|       NeoPilot Installer v2          |" -ForegroundColor Blue
Write-Host "|  NeoDash AI Connector for Claude     |" -ForegroundColor Blue
Write-Host "+======================================+" -ForegroundColor Blue
Write-Host ""

# -------------------------------------------------------------------
# 1. Check prerequisites
# -------------------------------------------------------------------
Info "Checking prerequisites..."

# Python 3.11+
$PY = Get-Command python -ErrorAction SilentlyContinue
if (-not $PY) {
    $PY = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $PY) {
    Fail "Python 3 not found. Install it from https://www.python.org/downloads/"
}

$PY = $PY.Source
$PyVersionOutput = & $PY --version 2>&1
$PyVersion = ($PyVersionOutput -replace "Python ", "").Trim()
$parts = $PyVersion.Split(".")
$major = [int]$parts[0]
$minor = [int]$parts[1]

if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
    Fail "Python 3.11+ is required (found $PyVersion). Please upgrade Python."
}
Success "Python $PyVersion found at $PY"

# Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Fail "Git not found. Install it from https://git-scm.com/"
}
Success "Git found"

# -------------------------------------------------------------------
# 2. Clone or update the repo
# -------------------------------------------------------------------
$InstallDir = Join-Path $env:USERPROFILE ".neopilot\app"

if (Test-Path (Join-Path $InstallDir ".git")) {
    Info "NeoPilot already installed. Updating..."
    Push-Location $InstallDir
    git pull --ff-only origin main 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Success "Updated to latest version"
    } else {
        Warn "Could not auto-update. Try: cd $InstallDir; git pull"
    }
    Pop-Location
} else {
    Info "Installing NeoPilot to $InstallDir ..."
    $parentDir = Split-Path $InstallDir -Parent
    if (-not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    # If running from inside the repo, clone from local; otherwise from GitHub
    $ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { $PWD.Path }
    $localPyproject = Join-Path $ScriptDir "pyproject.toml"

    if ((Test-Path $localPyproject) -and ($ScriptDir -ne $InstallDir)) {
        git clone $ScriptDir $InstallDir
    } else {
        git clone https://github.com/tetris-solutions/neopilot.git $InstallDir
    }
    Success "Cloned NeoPilot"
}

Push-Location $InstallDir

# -------------------------------------------------------------------
# 3. Set up virtual environment
# -------------------------------------------------------------------
$VenvDir = Join-Path $InstallDir ".venv"
$VenvPip = Join-Path $VenvDir "Scripts\pip.exe"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Test-Path $VenvDir)) {
    Info "Creating virtual environment..."
    & $PY -m venv $VenvDir
    Success "Virtual environment created"
} else {
    Info "Virtual environment already exists"
}

Info "Installing dependencies..."
& $VenvPip install --quiet --upgrade pip
& $VenvPip install --quiet -e .
Success "Dependencies installed"

# Get the installed version
try {
    $NeopilotVersion = & $VenvPython -c "from neopilot import __version__; print(__version__)" 2>$null
} catch {
    $NeopilotVersion = "unknown"
}
Success "NeoPilot v$NeopilotVersion ready"

# -------------------------------------------------------------------
# 4. Configure Claude Desktop
# -------------------------------------------------------------------
# Detect config path: Microsoft Store version uses a sandboxed path
$ClaudeConfigDirs = @()

# Microsoft Store path (check first — takes priority if both exist)
$msStorePattern = Join-Path $env:LOCALAPPDATA "Packages\Claude_*\LocalCache\Roaming\Claude"
$msStoreDirs = @(Get-ChildItem -Path (Join-Path $env:LOCALAPPDATA "Packages") -Filter "Claude_*" -Directory -ErrorAction SilentlyContinue)
foreach ($d in $msStoreDirs) {
    $candidate = Join-Path $d.FullName "LocalCache\Roaming\Claude"
    if (Test-Path $candidate) {
        $ClaudeConfigDirs += $candidate
    }
}

# Standard (standalone installer) path
$standardDir = Join-Path $env:APPDATA "Claude"
if (Test-Path $standardDir) {
    $ClaudeConfigDirs += $standardDir
}

# If neither found, create the standard path as fallback
if ($ClaudeConfigDirs.Count -eq 0) {
    Info "Creating Claude Desktop config directory..."
    New-Item -ItemType Directory -Path $standardDir -Force | Out-Null
    $ClaudeConfigDirs = @($standardDir)
}

foreach ($ClaudeConfigDir in $ClaudeConfigDirs) {
    $ClaudeConfig = Join-Path $ClaudeConfigDir "claude_desktop_config.json"
    Info "Configuring Claude Desktop at $ClaudeConfigDir ..."

    $pyScript = @"
import json, os
config_path = r'$ClaudeConfig'
python_path = r'$VenvPython'
if os.path.exists(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
else:
    config = {}
config.setdefault('mcpServers', {})
config['mcpServers']['neopilot'] = {
    'command': python_path,
    'args': ['-m', 'neopilot.server']
}
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2)
"@

    & $VenvPython -c $pyScript

    if (Test-Path $ClaudeConfig) {
        Success "Claude Desktop configured ($ClaudeConfigDir)"
    } else {
        Warn "Could not write config to $ClaudeConfigDir"
    }
}

Pop-Location

# -------------------------------------------------------------------
# 5. Done!
# -------------------------------------------------------------------
Write-Host ""
Write-Host "+======================================+" -ForegroundColor Green
Write-Host "|    NeoPilot installed successfully!  |" -ForegroundColor Green
Write-Host "+======================================+" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Restart Claude Desktop (quit and reopen)"
Write-Host "  2. In Claude, say: `"Connect to my NeoDash instance 'yourslug' with token 'yourtoken'`""
Write-Host ""
Write-Host "To update later, run:"
Write-Host "  cd $InstallDir; git pull; .venv\Scripts\pip.exe install -e ."
Write-Host ""
Write-Host "Installed at: $InstallDir"
Write-Host "Python:       $VenvPython"
Write-Host ""
