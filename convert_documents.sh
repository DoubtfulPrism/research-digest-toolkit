#!/bin/bash
# Document Converter - Uses native Linux tools for best quality
# Converts PDFs and DOCX to markdown for research digest

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_DIR="${1:-}"
OUTPUT_DIR="${2:-}"

if [ -z "$INPUT_DIR" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Usage: $0 <input_dir> <output_dir>"
    exit 1
fi

# Check for required tools
MISSING_TOOLS=()

command -v pdftotext >/dev/null 2>&1 || MISSING_TOOLS+=("pdftotext (poppler-utils)")
command -v pandoc >/dev/null 2>&1 || MISSING_TOOLS+=("pandoc")

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo "Error: Missing required tools:"
    printf '  - %s\n' "${MISSING_TOOLS[@]}"
    echo ""
    echo "Install with:"
    echo "  sudo dnf install pandoc poppler-utils"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "Converting documents using native tools..."
echo "Input:  $INPUT_DIR"
echo "Output: $OUTPUT_DIR"
echo ""

PDF_COUNT=0
DOCX_COUNT=0
FAILED_COUNT=0

# Convert PDFs (using pdftotext - better than PyPDF2)
echo "🔍 Looking for PDFs..."
while IFS= read -r -d '' pdf_file; do
    filename=$(basename "$pdf_file" .pdf)
    output_file="$OUTPUT_DIR/${filename}.md"

    echo "  Converting: $(basename "$pdf_file")"

    if pdftotext -layout "$pdf_file" - | pandoc -f plain -t markdown -o "$output_file" 2>/dev/null; then
        ((PDF_COUNT++))
        echo "    ✓ Saved to: $(basename "$output_file")"
    else
        echo "    ✗ Failed to convert $(basename "$pdf_file")" >&2
        ((FAILED_COUNT++))
    fi

done < <(find "$INPUT_DIR" -type f -iname "*.pdf" -print0 2>/dev/null)

# Convert DOCX (using pandoc - better than python-docx)
echo ""
echo "🔍 Looking for DOCX files..."
while IFS= read -r -d '' docx_file; do
    filename=$(basename "$docx_file" .docx)
    output_file="$OUTPUT_DIR/${filename}.md"

    echo "  Converting: $(basename "$docx_file")"

    if pandoc "$docx_file" -o "$output_file" 2>/dev/null; then
        ((DOCX_COUNT++))
        echo "    ✓ Saved to: $(basename "$output_file")"
    else
        echo "    ✗ Failed to convert $(basename "$docx_file")" >&2
        ((FAILED_COUNT++))
    fi

done < <(find "$INPUT_DIR" -type f -iname "*.docx" -print0 2>/dev/null)

# Summary
echo ""
echo "======================================================================"
echo "Conversion Summary:"
echo "  PDFs converted:  $PDF_COUNT"
echo "  DOCX converted:  $DOCX_COUNT"
if [ $FAILED_COUNT -gt 0 ]; then
    echo "  Failed:          $FAILED_COUNT"
fi
echo "  Total:           $((PDF_COUNT + DOCX_COUNT))"
echo "======================================================================"

exit 0
