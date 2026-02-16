param(
  [Parameter(Mandatory=$true)][string]$Tag,
  [Parameter(Mandatory=$true)][string]$AssetPath
)

if (-not (Test-Path $AssetPath)) {
  Write-Error "Asset not found: $AssetPath"
  exit 1
}
if (-not $env:GH_PAT) {
  Write-Error "Please set environment variable GH_PAT (classic PAT with repo scope)"
  exit 2
}
$repo = "amiram/ai-transcriber"
$body = @{ tag_name = $Tag; name = $Tag; body = "Release $Tag"; draft = $false; prerelease = $false } | ConvertTo-Json

$createResp = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/releases" -Method Post -Headers @{ Authorization = "token $env:GH_PAT"; Accept = 'application/vnd.github+json' } -Body $body -ContentType 'application/json'
$uploadUrlTemplate = $createResp.upload_url
$uploadUrl = $uploadUrlTemplate -replace '\{\?name,label\}', ''
$name = Split-Path $AssetPath -Leaf

Invoke-RestMethod -Uri "$uploadUrl?name=$name" -Method Post -Headers @{ Authorization = "token $env:GH_PAT"; 'Content-Type' = 'application/octet-stream' } -InFile $AssetPath -UseBasicParsing
Write-Host "Uploaded $AssetPath to release $Tag"

