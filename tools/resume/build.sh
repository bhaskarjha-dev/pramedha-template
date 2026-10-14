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
if command -v python3 >/dev/null 2>&1; then
    python3 "$SCRIPT_DIR/assemble.py"
elif command -v python >/dev/null 2>&1; then
    python "$SCRIPT_DIR/assemble.py"
elif command -v uv >/dev/null 2>&1; then
    uv run --with pyyaml python "$SCRIPT_DIR/assemble.py"
else
    echo "Python not found. Please install Python 3.10+." >&2
    exit 1
fi

# Step 2: Render
echo ""
echo "[2/2] Rendering PDFs..."
OUTPUT_DIR="$SCRIPT_DIR/output"
mkdir -p "$OUTPUT_DIR"

yaml_files=("$SCRIPT_DIR/generated/"*.yaml)
if [ ! -e "${yaml_files[0]}" ]; then
    echo "  No generated YAML files found in $SCRIPT_DIR/generated/"
    echo "  Create a variant file in tools/resume/variants/ first (e.g. copy _template.yaml to A_Role.yaml)."
    echo ""
    echo "=== Build Complete ==="
    exit 0
fi

if ! command -v rendercv >/dev/null 2>&1; then
    echo "  RenderCV CLI not found in PATH."
    echo "  Install with: pip install rendercv"
    echo "  Generated YAMLs are ready in: $SCRIPT_DIR/generated/"
    echo ""
    echo "=== Build Complete ==="
    exit 0
fi

cd "$SCRIPT_DIR"
for yaml_file in "${yaml_files[@]}"; do
    [ -f "$yaml_file" ] || continue
    name=$(basename "$yaml_file" .yaml)
    echo "  Rendering $name..."
    variant_out="$OUTPUT_DIR/$name"
    mkdir -p "$variant_out"
    if rendercv render "$yaml_file" -o "$variant_out" 2>&1; then
        pdf_file=$(find "$variant_out" -maxdepth 1 -name "*.pdf" | head -n 1)
        if [ -n "$pdf_file" ]; then
            cp "$pdf_file" "$OUTPUT_DIR/$name.pdf"
            echo "  ✅ $name -> output/$name.pdf"
        else
            echo "  ✅ $name"
        fi
    else
        echo "  ❌ Failed: $name"
    fi
done

echo ""
echo "=== Build Complete ==="
echo "PDFs are in: $OUTPUT_DIR"
