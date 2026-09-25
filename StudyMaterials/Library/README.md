# Study Library

English | [简体中文](README.zh-CN.md)

This directory contains the local textbook library, categorized OCR caches, and English I materials used during 11408 preparation. For the top-level materials map, see the [StudyMaterials guide](../README.md). Repository-wide policy remains in [AGENTS.md](../../AGENTS.md).

## Directory Layout

```text
Library/
  README.md
  README.zh-CN.md
  408/                         # Local 408 textbook PDFs
  Math/
    Basic/                     # Foundation-stage Mathematics I PDFs
    Intensive/                 # Intensive-stage Mathematics I PDFs
  Cache/                       # Categorized OCR caches; may be tracked
    STATUS.md                  # Dated verification records
    408/
    Math/
      Basic/
      Intensive/
  English/
    WritingTemplates/
      index.html               # Tracked browser version
      index.pdf                # Local generated PDF
```

## Version Control Policy

Follow [AGENTS.md](../../AGENTS.md) for source-PDF and Git safety. Verified OCR cache JSON under `Cache/` is derived data that may be tracked after checking completeness, readability, and diagnostic content. Suitable English review artifacts such as `English/WritingTemplates/index.html` may also be tracked.

## Cache Layout And Format

The cache tree mirrors each textbook's subject, stage, and nested source directory. For example, a PDF under `Math/Intensive/SetA/` writes its cache under `Cache/Math/Intensive/SetA/`. Both cache builders use `scripts/cache_layout.py` for this mapping.

The primary page-level format is:

```json
{
  "book": "book name",
  "total_pages": 100,
  "pages": [
    {"page_no": 1, "text": "..."}
  ]
}
```

`scripts/query.py` recursively reads `StudyMaterials/Library/Cache/**/*.docling.json`. It supports both the page-level format and legacy Docling JSON containing structured `texts` entries, while preferring categorized copies over legacy flat duplicates.

## Query The Cache

Use the interpreter selected under the root README's [Runtime Environment](../../README.md#runtime-environment) rules for the commands below.

Search the local cache before opening a large PDF:

```bash
python scripts/query.py "关键词"
python scripts/query.py "关键词" --book "数据结构"
python scripts/query.py "关键词" --book "线代" --page-only
python scripts/query.py "关键词" --book "高数" --context 2
python scripts/query.py --list-books
```

A cache miss does not prove that a book lacks the material. Try synonyms, shorter terms, and split queries before inspecting likely PDF pages or reporting that the cache did not confirm the content.

## Build The Cache

Use the page-level PyMuPDF + RapidOCR pipeline by default:

```bash
python scripts/page_ocr.py "StudyMaterials/Library/408/某书.pdf"
python scripts/page_ocr.py "StudyMaterials/Library/Math/Intensive/某书.pdf"
python scripts/page_ocr.py --all
```

The builder discovers PDFs recursively, uses embedded text when available, falls back to OCR for scanned pages, resumes incomplete JSON checkpoints, and skips complete caches. Embedded text layers are screened for garbled font mappings first (private-use glyphs, replacement chars, unreadable ratios); a corrupt layer such as `f(x)` extracting as `f  x ` is discarded in favor of OCR so it cannot pollute the cache.

For scanned math books whose dense formulas RapidOCR cannot preserve (lost integral signs, broken fractions), re-transcribe the affected pages at high fidelity by rendering them and reading them directly. Create the output directory first (for example `mkdir -p tmp/vision-pages`); remove only the rendered pages created by this task afterwards:

```bash
pdftoppm -f 161 -l 188 -r 180 -png "StudyMaterials/Library/408/某书.pdf" tmp/vision-pages/p
```

Read the rendered page images in batches, transcribe each page into LaTeX-formula Markdown, then merge only that page range into the `.docling.json` cache while preserving `total_pages` and the page-level structure. Repair just the pages that need it and leave the rest of the cache untouched.

`scripts/docling_cache.py` is a legacy-compatible alternative that writes Docling JSON and Markdown. Keep it for compatibility, but do not present it as the default workflow. Full-cache generation can process gigabytes of local PDFs and should not be used as a routine documentation or pre-commit check.

## Cache Verification Records

Dated per-book coverage and known OCR limitations are kept in the bilingual
[cache status record](Cache/STATUS.md). Recheck a cache after it changes; these
records do not replace the source-PDF evidence rules below.

## Evidence And Page Numbers

OCR cache matches identify candidate PDF pages only. Open the source PDF when an answer depends on:

- Exact wording or a direct quotation
- Formulas, symbols, tables, or diagrams
- Worked-example details
- Printed book page numbers
- A conclusion whose OCR text is ambiguous

A textbook-specific answer should identify the book and section when possible and distinguish:

- `书内印刷页码`: the page number printed in the book
- `PDF 页码`: the actual page index shown by the PDF reader and cache

If either value cannot be confirmed, state that explicitly. Never invent textbook wording, locations, examples, formulas, or conclusions.

## English Materials

`English/` stores English I source materials and derived review artifacts. The current writing-template outputs are:

```text
English/WritingTemplates/
  index.html
  index.pdf
```

When transcribing screenshots or PDFs, preserve source order and useful study content while omitting watermarks, platform chrome, correction-interface decoration, screenshot noise, and OCR diagnostics.

If `index.html` changes and a PDF version is requested, regenerate `index.pdf` so both formats remain aligned. The PDF remains local under the repository-wide ignore rule.

## Cleanup And Safety

Remove rendered PDF pages, screenshots, OCR diagnostics, PID files, and other
temporary artifacts created by this task after use. Preserve any pre-existing
temporary files. Follow [AGENTS.md](../../AGENTS.md) for source-material and
evidence rules.
