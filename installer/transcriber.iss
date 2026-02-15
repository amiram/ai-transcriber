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
Source: "{#src}\dist\Transcriber.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#src}\locales\*"; DestDir: "{app}\locales"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Transcriber"; Filename: "{app}\Transcriber.exe"

[Run]
Filename: "{app}\Transcriber.exe"; Description: "Launch Transcriber"; Flags: nowait postinstall skipifsilent

; Note: Replace {#src} with the installer build path when compiling.

