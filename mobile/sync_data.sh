#!/usr/bin/env bash
# Copy the canonical data tables into the Flutter assets (single source of
# truth lives in ../data). Run before building or when data changes.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p assets/data
cp ../data/breakthrough.json ../data/pill_effect_sources.json ../data/respira_sources.json ../data/sources.json assets/data/
echo "synced data -> mobile/assets/data"
