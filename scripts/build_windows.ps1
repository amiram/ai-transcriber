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
$venvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    Write-Host "Upgrading pip inside venv: $venvPython -m pip install --upgrade pip"
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r requirements.txt
    & $venvPython -m pip install pyinstaller==5.11.0
} else {
    Write-Host "No venv python found, falling back to system python"
    & $PythonExe -m pip install --upgrade pip
    & $PythonExe -m pip install -r requirements.txt
    & $PythonExe -m pip install pyinstaller==5.11.0
}

# Build with PyInstaller
# Include locales directory; on Windows the separator in --add-data is ";" with dest folder name.
$adddata = "locales;locales"
$pyinstallerCmd = "pyinstaller --noconfirm --onefile --windowed --name $Name --add-data $adddata transcriber_gui.py"
Write-Host "Running: $pyinstallerCmd"

# Capture output to a log file for CI debugging
$logFile = Join-Path (Get-Location) "pyinstaller_build.log"
try {
    & cmd /c "$pyinstallerCmd" 2>&1 | Tee-Object -FilePath $logFile
} catch {
    Write-Host "PyInstaller command failed. See $logFile for details."
    # Dump last lines of log for immediate visibility
    if (Test-Path $logFile) { Get-Content $logFile -Tail 100 }
    throw
}

Write-Host "PyInstaller finished. Log saved to: $logFile"

# Success message
Write-Host "Build complete. Artifacts are expected under .\dist\"
Write-Host "Example artifact (onefile): .\dist\$Name.exe or in a subfolder depending on PyInstaller output"

exit 0
