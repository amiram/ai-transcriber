; Inno Setup script for Transcriber
[Setup]
AppName=Transcriber
AppVersion=1.0
DefaultDirName={pf}\Transcriber
DefaultGroupName=Transcriber
OutputBaseFilename=TranscriberSetup
Compression=lzma
SolidCompression=yes

[Files]
; Use relative paths from the installer script location (repo root is parent folder)
Source: "..\dist\Transcriber.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\locales\*"; DestDir: "{app}\locales"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Transcriber"; Filename: "{app}\Transcriber.exe"

[Run]
Filename: "{app}\Transcriber.exe"; Description: "Launch Transcriber"; Flags: nowait postinstall skipifsilent

; Note: Run ISCC from the repository root or adjust paths accordingly.
