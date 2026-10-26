#!/usr/bin/env bash
# The Cloudflare Pages build command: `bash scripts/cf-pages-build.sh`, output directory `public`.
# It installs the same pinned tools as mise.toml, so the edge builds exactly what CI checked.
set -euo pipefail
curl -fsSL https://mise.run | sh
export PATH="$HOME/.local/bin:$PATH"
mise trust --yes && mise install
mise run build
# Cloudflare Pages limits: 25 MiB per file, 20,000 files per deploy. Fail here rather than at upload.
big=$(find public -type f -size +25M | head -1); [ -z "$big" ] || { echo "too large for Pages: $big"; exit 1; }
n=$(find public -type f | wc -l); [ "$n" -lt 20000 ] || { echo "too many files for Pages: $n"; exit 1; }
