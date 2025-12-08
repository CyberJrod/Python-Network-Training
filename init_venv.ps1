# init_venv.ps1
# Creates a `.venv` virtual environment in the repo root (Windows PowerShell)
# - Finds `python` or `py` on PATH
# - Creates `.venv` if missing
# - Upgrades pip inside the venv
# - Installs `requirements.txt` if present


$ErrorActionPreference = 'Stop'

# Determine the repository root as the directory where this script lives.
# This ensures the venv gets created next to the project files even if the
# script is invoked from a different working directory.
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Resolve-Path $scriptDir
$venvDir = Join-Path -Path $repoRoot -ChildPath '.venv'

# If a .venv exists in the current working directory (because the script was
# previously run from elsewhere), inform the user so they can optionally remove it.
$cwdVenv = Join-Path -Path (Get-Location) -ChildPath '.venv'
if ((Test-Path $cwdVenv) -and -not (Test-Path $venvDir)) {
    Write-Host "Note: I found a '.venv' at your current working directory: $cwdVenv"
    Write-Host "This script will create/use the venv at: $venvDir"
}

Write-Host "Repository root: $repoRoot"

# locate python
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = (Get-Command python).Source
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    # use the launcher for Windows
    $pythonCmd = 'py -3'
}

if (-not $pythonCmd) {
    Write-Error "Python not found. Install Python 3 and ensure 'python' or 'py' is on PATH."
    exit 1
}

if (-not (Test-Path $venvDir)) {
    Write-Host "Creating virtual environment at $venvDir..."
    & $pythonCmd -m venv $venvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment (exit code $LASTEXITCODE)."
        exit $LASTEXITCODE
    }
} else {
    Write-Host "Virtual environment already exists at $venvDir"
}

$venvPython = Join-Path $venvDir 'Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    Write-Error "Could not find venv python at $venvPython"
    exit 1
}

Write-Host "Upgrading pip in the venv..."
& $venvPython -m pip install --upgrade pip

if (Test-Path (Join-Path (Get-Location) 'requirements.txt')) {
    Write-Host "Installing requirements from requirements.txt..."
    & $venvPython -m pip install -r requirements.txt
} else {
    Write-Host "No requirements.txt found; skipping package installation."
}

Write-Host "\nDone. To activate the venv for this PowerShell session run:"
Write-Host "    .\\.venv\\Scripts\\Activate.ps1"
Write-Host "To run the Streamlit app once activated:"
Write-Host "    python -m streamlit run app.py"

Write-Host "If execution is blocked, you can run this script temporarily with:"
Write-Host "    powershell -ExecutionPolicy Bypass -File .\\init_venv.ps1"
