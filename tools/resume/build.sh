#!/usr/bin/env bash
# Resume Cascade Build Script (Linux/Mac)
# Assembles all variants from master.yaml and renders to PDF.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo ""
echo "=== Resume Cascade Build ==="

# Use the repository's virtual environment (README Quick Start), else the active one, else python3
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
    PY="$REPO_ROOT/.venv/bin/python"
elif [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
    PY="$VIRTUAL_ENV/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PY="python3"
else
    echo "Python not found. Install Python 3.12+ and create .venv as README Quick Start shows." >&2
    exit 1
fi

# Step 1: Assemble. generated/ holds only build output: clear it so removed or renamed variants aren't rendered again
echo ""
echo "[1/2] Assembling variants..."
rm -f "$SCRIPT_DIR/generated/"*.yaml
"$PY" "$SCRIPT_DIR/assemble.py"

# Step 2: Render
echo ""
echo "[2/2] Rendering PDFs..."
OUTPUT_DIR="$SCRIPT_DIR/output"
mkdir -p "$OUTPUT_DIR"

yaml_files=("$SCRIPT_DIR/generated/"*.yaml)
if [ ! -e "${yaml_files[0]}" ]; then
    echo "  Nothing to render: no files in $SCRIPT_DIR/generated/."
    echo "  Run python tools/resume/sync.py, copy tools/resume/variants/_template.yaml to"
    echo "  tools/resume/variants/A_Role.yaml, select bullets, then run this script again."
    echo ""
    echo "=== Build FAILED: no PDF was rendered ==="
    exit 1
fi

if "$PY" -m rendercv --version >/dev/null 2>&1; then
    RENDERCV=("$PY" -m rendercv)
elif command -v rendercv >/dev/null 2>&1; then
    RENDERCV=(rendercv)
else
    echo "  RenderCV not found. It needs Python 3.12+ (this is $("$PY" --version 2>&1))."
    echo "  Install it in the virtual environment: python -m pip install -r tools/resume/requirements.txt"
    echo "  Generated YAMLs are ready in: $SCRIPT_DIR/generated/"
    echo ""
    echo "=== Build FAILED: no PDF was rendered ==="
    exit 1
fi

cd "$SCRIPT_DIR"
failed=0
for yaml_file in "${yaml_files[@]}"; do
    [ -f "$yaml_file" ] || continue
    name=$(basename "$yaml_file" .yaml)
    echo "  Rendering $name..."
    variant_out="$OUTPUT_DIR/$name"
    mkdir -p "$variant_out"
    pdf_file=""
    if "${RENDERCV[@]}" render "$yaml_file" -o "$variant_out" 2>&1; then
        pdf_file=$(find "$variant_out" -maxdepth 1 -name "*.pdf" | head -n 1)
    fi
    if [ -n "$pdf_file" ]; then
        cp "$pdf_file" "$OUTPUT_DIR/$name.pdf"
        echo "  ✅ $name -> output/$name.pdf"
    else
        echo "  ❌ Failed: $name"
        failed=$((failed + 1))
    fi
done

echo ""
if [ "$failed" -gt 0 ]; then
    echo "=== Build FAILED: $failed file(s) did not render ==="
    exit 1
fi
echo "=== Build Complete ==="
echo "PDFs are in: $OUTPUT_DIR"
