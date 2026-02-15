Windows Packaging Guide

This document explains the recommended steps to produce distributable artifacts for Transcriber on Windows: a single EXE (PyInstaller), a portable ZIP, and an installer (Inno Setup).

Prerequisites (on Windows):
- Python 3.9+ installed (or use the GitHub Actions runner)
- pip
- PyInstaller (we pin to 5.11.0 in CI)
- Inno Setup 6 (for building the installer)

Steps (manual, for local dev):

1. Create a virtualenv and install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller==5.11.0
```

2. Build with PyInstaller using the provided spec

```powershell
pyinstaller --clean --noconfirm transcriber.spec
# Or use the build script:
# .\scripts\build_windows.ps1 -PythonExe python -BuildDir dist -Name Transcriber
```

3. Create portable ZIP

```powershell
pwsh .\scripts\package_portable.ps1 -ExeName "Transcriber.exe" -DistDir "dist" -OutZip "Transcriber_portable.zip"
```

4. Build installer using Inno Setup

- Open `installer\transcriber.iss` in Inno Setup and replace the {#src} preprocessor path with your repo root if needed, or run the CI-provided command:

```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "installer\transcriber.iss"
```

CI notes

The repository contains a GitHub Actions workflow `.github/workflows/windows-build.yml` which runs these steps on `windows-latest` and uploads artifacts. Ensure you have a Release step (optional) to attach artifacts to a GitHub Release.

