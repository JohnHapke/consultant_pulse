#!/bin/bash
# Populate frontend/public/data/ with synthetic pulse JSON for local development.
# Run from the project root (consultant_pulse/).

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SRC="$PROJECT_ROOT/data/synthetic/output"
DST="$PROJECT_ROOT/frontend/public/data"

if [ ! -d "$SRC" ]; then
  echo "Error: $SRC not found. Run the synthetic generator first."
  exit 1
fi

cp "$SRC"/*.json "$DST"/
echo "Synthetic data copied to frontend/public/data/"
echo "Run 'npm run dev' inside frontend/ to start the dev server."
