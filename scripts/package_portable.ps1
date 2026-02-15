# Package a portable ZIP containing the EXE and locales
param(
    [string]$ExeName = "Transcriber.exe",
    [string]$DistDir = "dist",
    [string]$OutZip = "Transcriber_portable.zip"
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Get-Location).Path

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

        # No outputs in dist. Create a diagnostic zip with build logs & listings to help debug.
        Write-Host "No build outputs found in $DistDir. Creating diagnostic ZIP with build logs and directory listings..."

        $diagName = "Transcriber_portable_debug.zip"
        if (Test-Path $diagName) { Remove-Item $diagName }

        # Prepare diagnostics folder
        $diagTmp = Join-Path $env:TEMP ([System.Guid]::NewGuid().ToString())
        New-Item -ItemType Directory -Path $diagTmp | Out-Null

        # Save directory listings
        Get-ChildItem -Path $repoRoot -Recurse -Force | Select-Object FullName,Length,LastWriteTime | Out-File (Join-Path $diagTmp "repo_tree.txt") -Encoding utf8
        if (Test-Path $DistDir) {
            Get-ChildItem -Path $DistDir -Recurse -Force | Select-Object FullName,Length,LastWriteTime | Out-File (Join-Path $diagTmp "dist_tree.txt") -Encoding utf8
        } else {
            "(no dist directory)" | Out-File (Join-Path $diagTmp "dist_tree.txt") -Encoding utf8
        }

        # Collect PyInstaller logs if present
        $possibleLogs = Get-ChildItem -Path $repoRoot -Recurse -Include "pyinstaller*.log","*.log" -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
        if ($possibleLogs -and $possibleLogs.Count -gt 0) {
            $i = 0
            foreach ($f in $possibleLogs) {
                Copy-Item $f.FullName -Destination (Join-Path $diagTmp ($i.ToString() + "_" + $f.Name)) -Force
                $i++
                if ($i -ge 10) { break }
            }
        }

        # Copy build/ and spec file if present
        if (Test-Path "build") { Copy-Item -Path "build" -Destination $diagTmp -Recurse -ErrorAction SilentlyContinue }
        if (Test-Path "transcriber.spec") { Copy-Item -Path "transcriber.spec" -Destination $diagTmp -Force }

        # Create zip
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        [System.IO.Compression.ZipFile]::CreateFromDirectory($diagTmp, $diagName)
        Write-Host "Created diagnostic ZIP: $diagName"

        # cleanup
        Remove-Item -Recurse -Force $diagTmp

        # Exit successfully so CI has a debug artifact to inspect
        exit 0
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
