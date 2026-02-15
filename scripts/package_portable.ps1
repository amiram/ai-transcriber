# Package a portable ZIP containing the EXE and locales
param(
    [string]$ExeName = "Transcriber.exe",
    [string]$DistDir = "dist",
    [string]$OutZip = "Transcriber_portable.zip"
)

$ErrorActionPreference = 'Stop'

$exePath = Join-Path $DistDir $ExeName
if (-not (Test-Path $exePath)) {
    Write-Error "Executable not found: $exePath"
    exit 1
}

# Create a temporary folder and copy exe + locales
$tmp = Join-Path $env:TEMP ([System.Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $tmp | Out-Null
Copy-Item $exePath -Destination $tmp
Copy-Item -Path "locales" -Destination $tmp -Recurse

# Zip
if (Test-Path $OutZip) { Remove-Item $OutZip }
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($tmp, $OutZip)
Write-Host "Created $OutZip"

# cleanup
Remove-Item -Recurse -Force $tmp

