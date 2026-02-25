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
# Use the transcriber.spec which contains a recursionlimit increase and ensures proper data collection
$pyinstallerCmd = "pyinstaller --clean --noconfirm --onefile --distpath $BuildDir transcriber.spec"
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

# Normalize output: ensure a predictable path dist\<Name>.exe exists.
# PyInstaller normally places the onefile exe at --distpath\<Name>.exe, but some builds or spec usage
# may produce a nested folder or different naming; search and copy the newest .exe as a fallback.
try {
    $buildDirPath = Join-Path (Get-Location) $BuildDir
    if (Test-Path $buildDirPath) {
        $found = Get-ChildItem -Path $buildDirPath -Recurse -Filter '*.exe' -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($null -ne $found) {
            $expected = Join-Path $buildDirPath ("$Name.exe")
            # If the found exe isn't the expected path, copy/overwrite the expected path for downstream steps
            if (-not (Test-Path $expected) -or (Resolve-Path $found.FullName).Path -ne (Resolve-Path $expected -ErrorAction SilentlyContinue).Path) {
                Copy-Item -Path $found.FullName -Destination $expected -Force
                Write-Host "Normalized EXE: $($found.FullName) -> $expected"
            } else {
                Write-Host "Expected EXE already present at $expected"
            }
        } else {
            Write-Host "Warning: No executable found under $buildDirPath"
        }
    } else {
        Write-Host "Warning: Build directory $buildDirPath does not exist"
    }
} catch {
    Write-Host "Warning: failed to normalize exe path: $_"
}

# Success message
Write-Host "Build complete. Artifacts are expected under .\$BuildDir"
Write-Host "Example artifact (onefile): .\$BuildDir\$Name.exe or in a subfolder depending on PyInstaller output"

exit 0
