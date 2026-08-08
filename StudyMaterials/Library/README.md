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

Textbook and generated PDF files may be large or copyrighted. Keep every PDF below `StudyMaterials/` local and do not commit it. Verified OCR cache JSON under `Cache/` is derived data and may be tracked. Suitable English review artifacts such as `English/WritingTemplates/index.html` may also be tracked.

Before staging cache files, confirm that they are complete, readable, and free of temporary or diagnostic content. Never commit credentials, cookies, browser profiles, personal exports, or machine-specific diagnostics.

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

The builder discovers PDFs recursively, uses embedded text when available, falls back to OCR for scanned pages, resumes incomplete JSON checkpoints, and skips complete caches.

`scripts/docling_cache.py` is a legacy-compatible alternative that writes Docling JSON and Markdown. Keep it for compatibility, but do not present it as the default workflow. Full-cache generation can process gigabytes of local PDFs and should not be used as a routine documentation or pre-commit check.

## Verified Intensive Mathematics Cache

The following intensive-stage Mathematics I caches were complete and verified on 2026-07-13:

| Source PDF | Cache JSON | Page coverage |
| --- | --- | ---: |
| `27版李林880题《数一解析册》.pdf` | `27版李林880题《数一解析册》.docling.json` | 416 / 416 |
| `张宇100题_数一_解析册.pdf` | `张宇100题_数一_解析册.docling.json` | 568 / 568 |
| `张宇1000题_数一_试题册.pdf` | `张宇1000题_数一_试题册.docling.json` | 195 / 195 |

The source files live under `Math/Intensive/`, and their caches live under `Cache/Math/Intensive/`. Six pages across the first two books contain no OCR text; visual inspection confirmed that they are blank or text-free transition pages, so the caches still cover every PDF page.

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

- Do not rename, move, edit, or delete source PDFs unless explicitly requested.
- Keep source materials separate from notes and mistake books.
- Delete rendered PDF pages, screenshots, OCR diagnostics, PID files, temporary services, and other one-off artifacts after use.
- Report missing or unclear source evidence instead of filling the gap.
