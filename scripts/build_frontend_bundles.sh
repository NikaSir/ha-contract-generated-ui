#!/usr/bin/env sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
frontend="$repo_root/custom_components/contract_generated_ui/frontend"
dist="$frontend/dist"

mkdir -p "$dist"

build_panel() {
  dependency=$1
  entry=$2
  output=$3
  temporary="$output.tmp"
  cp "$dependency" "$temporary"
  sed '1{/^import /d;}' "$entry" >> "$temporary"
  mv "$temporary" "$output"
}

build_panel \
  "$frontend/nikas-house-hero.js" \
  "$frontend/nikas-house-overview.js" \
  "$dist/nikas-house-overview.js"

build_panel \
  "$frontend/nikas-infrastructure-summary.js" \
  "$frontend/nikas-infrastructure-overview.js" \
  "$dist/nikas-infrastructure-overview.js"

temporary="$dist/nikas-generated-subpanel.js.tmp"
cp "$frontend/nikas-panel-zoom.js" "$temporary"
sed '1{/^import /d;}' "$frontend/nikas-specialized-panel-shell.js" >> "$temporary"
sed '1{/^import /d;}' "$frontend/nikas-generated-subpanel.js" >> "$temporary"
mv "$temporary" "$dist/nikas-generated-subpanel.js"

for bundle in "$dist"/*.js; do
  if grep -Eq '^[[:space:]]*import[[:space:]]' "$bundle"; then
    echo "runtime import remains in $bundle" >&2
    exit 1
  fi
done
