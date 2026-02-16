#!/usr/bin/env bash
# Usage: GH_PAT=... ./scripts/upload_release_asset.sh v0.1.1 TranscriberSetup.exe
set -euo pipefail
if [ $# -ne 2 ]; then
  echo "Usage: $0 <tag> <asset-path>"
  exit 2
fi
TAG=$1
ASSET=$2
if [ ! -f "$ASSET" ]; then
  echo "Asset not found: $ASSET"
  exit 3
fi
if [ -z "${GH_PAT:-}" ]; then
  echo "Please set GH_PAT environment variable (classic PAT with repo scope)."
  exit 4
fi
REPO=amiram/ai-transcriber
# create release if not exists (idempotent - returns existing release if present)
create_resp=$(curl -s -H "Authorization: token $GH_PAT" -H "Content-Type: application/json" \
  -d "{\"tag_name\": \"$TAG\", \"name\": \"$TAG\", \"body\": \"Release $TAG\", \"draft\": false, \"prerelease\": false}" \
  "https://api.github.com/repos/$REPO/releases")

upload_url=$(echo "$create_resp" | grep -o "\"upload_url\": \"[^"]*\"" | sed -E 's/"upload_url": "([^"]+)"/\1/' | sed -e 's/{?name,label}//')
if [ -z "$upload_url" ]; then
  echo "Failed to determine upload_url from create response:" >&2
  echo "$create_resp" >&2
  exit 5
fi

name=$(basename "$ASSET")

curl -s -H "Authorization: token $GH_PAT" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @"$ASSET" \
  "$upload_url?name=$name"

echo "Uploaded $ASSET to release $TAG"

