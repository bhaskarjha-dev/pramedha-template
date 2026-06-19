#!/usr/bin/env bash
# Resume Cascade Build Script (Linux/Mac)
# Assembles all variants from master.yaml and renders to PDF.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "=== Resume Cascade Build ==="

# Step 1: Assemble
echo ""
echo "[1/2] Assembling variants..."
python3 "$SCRIPT_DIR/assemble.py"

# Step 2: Render
echo ""
echo "[2/2] Rendering PDFs..."
OUTPUT_DIR="$SCRIPT_DIR/output"
mkdir -p "$OUTPUT_DIR"

for yaml_file in "$SCRIPT_DIR/generated/"*.yaml; do
    name=$(basename "$yaml_file" .yaml)
    echo "  Rendering $name..."
    if rendercv render "$yaml_file" --output-folder-name "$OUTPUT_DIR" 2>&1; then
        echo "  ✅ $name"
    else
        echo "  ❌ Failed: $name"
    fi
done

echo ""
echo "=== Build Complete ==="
echo "PDFs are in: $OUTPUT_DIR"
