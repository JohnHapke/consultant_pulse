#!/bin/bash
# Build the React dashboard to a configurable output directory.
#
# Usage:
#   ./scripts/publish.sh --output-dir ./dashboard_output
#
# After this, inject data with the aggregator:
#   python backend/src/aggregator.py --output <output-dir>/data --excel ... --week ...
#
# Then serve:
#   npx serve <output-dir>

set -e

OUTPUT_DIR=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

if [ -z "$OUTPUT_DIR" ]; then
  echo "Usage: $0 --output-dir <dir>"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT_ABS="$(realpath -m "$OUTPUT_DIR")"

cd "$PROJECT_ROOT/frontend"
npx vite build --outDir "$OUTPUT_ABS" --emptyOutDir

echo ""
echo "Dashboard built to: $OUTPUT_ABS"
echo ""
echo "Next steps:"
echo "  1. python backend/src/aggregator.py \\"
echo "       --excel <path/to/data.xlsx> \\"
echo "       --consultant-map <path/to/consultant_map.yaml> \\"
echo "       --week <YYYY-WNN> \\"
echo "       --output $OUTPUT_ABS/data"
echo ""
echo "  2. npx serve $OUTPUT_ABS"
