Windows Packaging Guide

This document explains the recommended steps to produce distributable artifacts for Transcriber on Windows: a single EXE (PyInstaller), a portable ZIP, and an installer (Inno Setup).

Prerequisites (on Windows):
- Python 3.9+ installed (or use the GitHub Actions runner)
- pip
- PyInstaller (we pin to 5.11.0 in CI)
- Inno Setup 6 (for building the installer)
- (Optional) Windows code signing certificate (for signing installer / exe)

Versioning and installer location
- The Inno Setup script uses the preprocessor variable `MyAppVersion` (default `1.0`) and the workflow passes the Git tag name to ISCC as `/DMyAppVersion=...` so the installer `AppVersion` aligns with your tag (e.g. tag `v0.1.2` → version `v0.1.2`).
- The installer default path is `{pf64}\Transcriber` which means the installer targets the 64-bit "Program Files" directory (`C:\Program Files\Transcriber`). Use `{pf}` if you specifically need Program Files (x86).

Signing the EXE and installer (Known Publisher)

Why sign?
- Code signing lets Windows and users verify the publisher. Signing reduces SmartScreen warnings and identifies the installer as coming from a trusted publisher.

Obtaining a code signing certificate
- Purchase a code signing certificate from an official CA (DigiCert, Sectigo, GlobalSign, etc.) or use an EV code signing certificate for better SmartScreen reputation.
- The provider gives you a .pfx or points you to an Azure Key Vault / HSM option. Keep the private key secure.

Signing locally with signtool
- Windows supplies `signtool.exe` as part of the Windows SDK. Example:

```powershell
# sign an EXE or installer using a PFX
$signtool = 'C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe'
& $signtool sign /fd SHA256 /a /f C:\path\to\yourcert.pfx /p "pfx-password" "C:\path\to\TranscriberSetup.exe"
```

- For timestamping (recommended so signatures remain valid after cert expiry):
```powershell
& $signtool sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 /a /f C:\path\to\yourcert.pfx /p "pfx-password" "C:\path\to\TranscriberSetup.exe"
```

Signing on CI (recommended approach)
- Upload the private key to a secure secret store (do NOT commit it). Use a signing action or Azure Key Vault agent on GitHub Actions, or a self-hosted runner with the certificate installed.
- Example: use `sigstore/cosign` or `Azure SignTool` actions or call `signtool.exe` on a Windows self-hosted runner where you installed the cert.

Register as a Known Publisher with Microsoft
- To remove SmartScreen blocks you may need reputation: buy an EV certificate and sign your binaries. Microsoft’s SmartScreen reputation is built over time as users download and run your signed app.

Troubleshooting
- If the installer attempts to install into `Program Files (x86)`:
  - The Inno Setup script now uses `{pf64}` for 64-bit Program Files; if an installer was built with `{pf}` or using 32-bit Inno Setup, Windows may choose Program Files (x86).
  - Ensure `DefaultDirName={pf64}\Transcriber` in `installer/transcriber.iss`.

Manual build steps
1. Create a virtualenv and install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller==5.11.0
```

2. Build with PyInstaller using the provided spec

```powershell
pyinstaller --clean --noconfirm transcriber.spec
```

3. Create portable ZIP

```powershell
pwsh .\scripts\package_portable.ps1 -ExeName "Transcriber.exe" -DistDir "dist" -OutZip "Transcriber_portable.zip"
```

4. Build installer with Inno Setup and pass version (example):

```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /DMyAppVersion=v0.1.2 installer\transcriber.iss
```

CI notes
- The GitHub Actions workflow passes the tag to ISCC, and copies the built installer to `TranscriberSetup.exe` so the release attaches it automatically.
