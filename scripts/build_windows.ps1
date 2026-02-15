# PowerShell build script for Windows (intended to run on a Windows runner or dev machine)
# Installs dependencies into a virtualenv and runs PyInstaller to create a single EXE.

param(
    [string]$PythonExe = "python",
    [string]$BuildDir = "dist",
    [string]$Name = "Transcriber"
)

$ErrorActionPreference = 'Stop'

Write-Host "Creating virtual environment and installing build deps..."
& $PythonExe -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller==5.11.0

# Build with PyInstaller
# Include locales directory; on Windows the separator in --add-data is ";" with dest folder name.
$adddata = "locales;locales"
pyinstaller --noconfirm --onefile --windowed --name $Name --add-data $adddata transcriber_gui.py

Write-Host "Build complete. Artifacts in .\dist\"$Name""}),({
