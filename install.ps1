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

$ErrorActionPreference = "Stop"

function Info($msg)    { Write-Host "i  $msg" -ForegroundColor Blue }
function Success($msg) { Write-Host "OK $msg" -ForegroundColor Green }
function Warn($msg)    { Write-Host "!  $msg" -ForegroundColor Yellow }
function Fail($msg)    { Write-Host "X  $msg" -ForegroundColor Red; exit 1 }

Write-Host ""
Write-Host "+======================================+" -ForegroundColor Blue
Write-Host "|       NeoPilot Installer             |" -ForegroundColor Blue
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
    $env:GIT_REDIRECT_STDERR = '2>&1'
    $pullResult = cmd /c "git pull --ff-only origin main 2>&1"
    $pullExitCode = $LASTEXITCODE
    Remove-Item Env:\GIT_REDIRECT_STDERR -ErrorAction SilentlyContinue
    if ($pullExitCode -eq 0) {
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
$ClaudeConfigDir = Join-Path $env:APPDATA "Claude"
$ClaudeConfig = Join-Path $ClaudeConfigDir "claude_desktop_config.json"

if (-not (Test-Path $ClaudeConfigDir)) {
    Info "Creating Claude Desktop config directory..."
    New-Item -ItemType Directory -Path $ClaudeConfigDir -Force | Out-Null
}

if (Test-Path $ClaudeConfigDir) {
    Info "Configuring Claude Desktop..."

    # Build the neopilot config entry — use forward slashes in JSON for safety
    $PythonPathJson = $VenvPython -replace '\\', '\\\\'

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
        Success "Claude Desktop configured with NeoPilot"
    } else {
        Warn "Could not write Claude Desktop config"
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
