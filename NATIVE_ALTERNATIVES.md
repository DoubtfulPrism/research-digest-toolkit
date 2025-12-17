# Native Linux Alternatives for File Conversion

While `file_converter.py` provides a unified Python interface, **native Linux tools often produce better quality results**, especially for PDF extraction. Here's a comprehensive guide.

---

## Recommended: Pandoc (Universal Converter)

**Pandoc** is the Swiss Army knife of document conversion and is generally superior to Python-based converters.

### Installation (Fedora)

```bash
sudo dnf install pandoc
```

### Common Conversions

```bash
# DOCX to Markdown
pandoc input.docx -o output.md

# Markdown to DOCX
pandoc input.md -o output.docx

# Markdown to HTML
pandoc input.md -o output.html

# HTML to Markdown
pandoc input.html -o output.md

# Markdown to PDF (requires LaTeX)
pandoc input.md -o output.pdf

# DOCX to plain text
pandoc input.docx -o output.txt

# With custom options
pandoc input.md -o output.html --standalone --toc
```

### Batch Processing with Pandoc

```bash
# Convert all markdown files to HTML
for f in *.md; do pandoc "$f" -o "${f%.md}.html"; done

# Convert all DOCX to markdown
for f in *.docx; do pandoc "$f" -o "${f%.docx}.md"; done

# Using find for recursive conversion
find . -name "*.md" -exec sh -c 'pandoc "$1" -o "${1%.md}.html"' _ {} \;
```

---

## PDF Extraction (Better than PyPDF2)

PyPDF2 often produces garbled or poorly formatted text. Use these native tools instead:

### pdftotext (poppler-utils)

```bash
# Installation
sudo dnf install poppler-utils

# Basic usage
pdftotext input.pdf output.txt

# Extract with layout preserved
pdftotext -layout input.pdf output.txt

# Extract specific pages
pdftotext -f 1 -l 10 input.pdf output.txt

# Extract to stdout
pdftotext input.pdf -

# Batch convert all PDFs
for f in *.pdf; do pdftotext "$f" "${f%.pdf}.txt"; done
```

### pdftohtml

```bash
# Installation (included in poppler-utils)
sudo dnf install poppler-utils

# Convert PDF to HTML
pdftohtml input.pdf output.html

# Single page HTML
pdftohtml -s input.pdf
```

### OCR for Scanned PDFs

If the PDF is scanned images (no text layer):

```bash
# Installation
sudo dnf install tesseract tesseract-langpack-eng ocrmypdf

# OCR a scanned PDF
ocrmypdf input.pdf output.pdf

# Then extract text
pdftotext output.pdf text.txt
```

---

## Other Useful Conversions

### HTML to Text (lynx)

```bash
# Installation
sudo dnf install lynx

# Convert HTML to text
lynx -dump input.html > output.txt

# Convert HTML to text with links
lynx -dump -listonly input.html
```

### HTML to Text (w3m)

```bash
# Installation
sudo dnf install w3m

# Convert HTML to text
w3m -dump input.html > output.txt
```

### Office Documents (LibreOffice)

```bash
# Installation (usually pre-installed on Fedora)
sudo dnf install libreoffice

# Convert DOCX to PDF
libreoffice --headless --convert-to pdf input.docx

# Convert DOCX to ODT
libreoffice --headless --convert-to odt input.docx

# Convert to HTML
libreoffice --headless --convert-to html input.docx

# Batch convert all DOCX to PDF
libreoffice --headless --convert-to pdf *.docx
```

---

## Comparison: Python vs Native Tools

| Task | Python (file_converter.py) | Native Tool | Winner |
|------|---------------------------|-------------|--------|
| PDF → Text | PyPDF2 (often garbled) | pdftotext | **Native** |
| DOCX → MD | python-docx (basic) | pandoc (excellent) | **Native** |
| MD → DOCX | python-docx (basic) | pandoc (excellent) | **Native** |
| HTML → MD | markdownify (good) | pandoc (excellent) | **Native** |
| Batch processing | Built-in | Shell scripts needed | Python |
| Unified interface | Single command | Multiple tools | Python |
| Installation | pip packages | System packages | Tie |
| Quality | Moderate | High | **Native** |

---

## When to Use Each

### Use Native Tools When:
- ✓ Converting a few files manually
- ✓ Quality is critical (especially PDF extraction)
- ✓ You need advanced options (table of contents, styling, etc.)
- ✓ Converting complex documents with formatting

### Use file_converter.py When:
- ✓ Batch processing many files with consistent interface
- ✓ Integrating with other Python scripts
- ✓ You prefer a single unified command
- ✓ Converting simple documents where quality differences are minimal

---

## Example Workflows

### Workflow 1: PDF Research Paper to Markdown

```bash
# Best approach using native tools
pdftotext -layout paper.pdf paper.txt
pandoc paper.txt -o paper.md

# Or with file_converter.py
./file_converter.py paper.pdf --to md
```

### Workflow 2: Batch Convert Documentation

```bash
# Using pandoc (better quality)
for f in docs/*.docx; do
  pandoc "$f" -o "output/$(basename "${f%.docx}").md"
done

# Using file_converter.py (easier syntax)
./file_converter.py docs/*.docx --to md --batch -o output/
```

### Workflow 3: Complete Document Pipeline

```bash
#!/bin/bash
# Convert all sources to markdown for NotebookLM

# 1. Extract text from PDFs
for pdf in pdfs/*.pdf; do
  pdftotext -layout "$pdf" "txt/$(basename "${pdf%.pdf}").txt"
done

# 2. Convert DOCX to markdown
for docx in docx/*.docx; do
  pandoc "$docx" -o "md/$(basename "${docx%.docx}").md"
done

# 3. Convert all text to markdown
for txt in txt/*.txt; do
  pandoc "$txt" -o "md/$(basename "${txt%.txt}").md"
done

# 4. Split large files if needed
./file_splitter.py -i md/ -r -o final/
```

---

## Quick Reference Card

```bash
# PDF to text (best quality)
pdftotext -layout input.pdf output.txt

# DOCX to markdown (best quality)
pandoc input.docx -o output.md

# Any to any (universal)
pandoc input.FORMAT -o output.FORMAT

# Batch with Python script
./file_converter.py *.pdf --to txt --batch

# PDF with OCR (scanned documents)
ocrmypdf scanned.pdf output.pdf && pdftotext output.pdf text.txt
```

---

## Installation Summary

Install everything for maximum capability:

```bash
# Fedora installation
sudo dnf install \
  pandoc \
  poppler-utils \
  libreoffice \
  lynx \
  w3m \
  tesseract \
  tesseract-langpack-eng \
  ocrmypdf

# Python packages (optional, for file_converter.py)
pip install --user python-docx markdownify PyPDF2
```

---

## Recommendation

**For most use cases, prefer native tools like `pandoc` and `pdftotext`** for their superior quality and extensive options. Use `file_converter.py` when you need:
- Batch processing with a unified interface
- Integration with Python workflows
- Simple conversions where quality differences are negligible

The native tools are more mature, better maintained, and produce higher quality output, especially for PDF extraction and complex document conversions.
