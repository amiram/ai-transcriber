# Package a portable ZIP containing the EXE and locales
param(
    [string]$ExeName = "Transcriber.exe",
    [string]$DistDir = "dist",
    [string]$OutZip = "Transcriber_portable.zip"
)

$ErrorActionPreference = 'Stop'

# Expect exe at DistDir\ExeName, but be tolerant and search recursively if not found
$exePath = Join-Path $DistDir $ExeName
if (-not (Test-Path $exePath)) {
    Write-Host "Expected executable not found at $exePath. Searching recursively in $DistDir for matching .exe files..."
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($ExeName)
    $found = Get-ChildItem -Path $DistDir -Recurse -File -ErrorAction SilentlyContinue |
             Where-Object { $_.Extension -ieq ".exe" -and $_.BaseName -like "$baseName*" }
    if ($found -and $found.Count -gt 0) {
        $exePath = $found[0].FullName
        Write-Host "Found executable: $exePath"
    } else {
        Write-Host "No matching executable found in $DistDir. Checking for other build outputs..."
        if (Test-Path $DistDir) {
            $entries = Get-ChildItem -Path $DistDir -Recurse -File -ErrorAction SilentlyContinue
            if ($entries -and $entries.Count -gt 0) {
                Write-Host "No executable found, but $DistDir contains other build outputs. Zipping entire $DistDir as a fallback artifact: $OutZip"
                if (Test-Path $OutZip) { Remove-Item $OutZip }
                Add-Type -AssemblyName System.IO.Compression.FileSystem
                [System.IO.Compression.ZipFile]::CreateFromDirectory((Resolve-Path $DistDir).Path, $OutZip)
                Write-Host "Created fallback ZIP: $OutZip"
                exit 0
            }
        }
        Write-Error "Executable not found: $exePath and no other build outputs found in $DistDir"
        exit 1
    }
} else {
    Write-Host "Using executable: $exePath"
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
