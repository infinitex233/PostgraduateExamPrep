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

The builder discovers PDFs recursively, uses embedded text when available, falls back to OCR for scanned pages, resumes incomplete JSON checkpoints, and skips complete caches. Embedded text layers are screened for garbled font mappings first (private-use glyphs, replacement chars, unreadable ratios); a corrupt layer such as `f(x)` extracting as `f  x ` is discarded in favor of OCR so it cannot pollute the cache.

For scanned math books whose dense formulas RapidOCR cannot preserve (lost integral signs, broken fractions), use the vision-model builder for high-fidelity transcription:

```bash
python scripts/vision_cache.py "StudyMaterials/Library/Math/Intensive/某书.pdf"
python scripts/vision_cache.py "某书.pdf" --first 6 --last 219 --batch 2   # batch 2 for lecture/answer books
python scripts/vision_cache.py "某书.pdf" --chain-offset 3                  # offset keys when running streams in parallel
python scripts/vision_cache.py --all
```

It transcribes each page into LaTeX-formula Markdown via a vision model (gpt-5.6-terra → gpt-5.6-luna with automatic key failover), checkpoints every batch to `<cache-dir>/<stem>.vision-ckpt.json`, merges the range into the `.docling.json` cache once complete, and removes the checkpoint. Pages the model returns nothing for keep their old text, and re-running the same command resumes after interruption. It depends on the `multimodal-vision` toolkit (default path `/home/infinitex/code/multimodal-vision`, overridable with `MULTIMODAL_VISION_DIR`).

`scripts/docling_cache.py` is a legacy-compatible alternative that writes Docling JSON and Markdown. Keep it for compatibility, but do not present it as the default workflow. Full-cache generation can process gigabytes of local PDFs and should not be used as a routine documentation or pre-commit check.

## Verified Intensive Mathematics Cache

The following intensive-stage Mathematics I caches were rebuilt with the
vision-model builder (`scripts/vision_cache.py`) and verified on 2026-08-14:

| Source PDF | Cache JSON | Page coverage |
| --- | --- | ---: |
| `27武忠祥《高等数学辅导讲义.严选题》.pdf` | `27武忠祥《高等数学辅导讲义.严选题》.docling.json` | 219 / 219 |
| `27武忠祥高数辅导讲义-强化.pdf` | `27武忠祥高数辅导讲义-强化.docling.json` | 315 / 315 |
| `27版李林880题《数一解析册》.pdf` | `27版李林880题《数一解析册》.docling.json` | 416 / 416 |
| `27线代杨《满分线性代数》强化讲义.pdf` | `27线代杨《满分线性代数》强化讲义.docling.json` | 318 / 318 |
| `【A4紧凑版】李林880数一线概篇做题本.pdf` | `【A4紧凑版】李林880数一线概篇做题本.docling.json` | 82 / 82 |
| `【A4紧凑版】李林880数一高数篇做题本.pdf` | `【A4紧凑版】李林880数一高数篇做题本.docling.json` | 98 / 98 |
| `张宇1000题_数一_试题册.pdf` | `张宇1000题_数一_试题册.docling.json` | 195 / 195 |
| `张宇100题_数一_解析册.pdf` | `张宇100题_数一_解析册.docling.json` | 568 / 568 |

The source files live under `Math/Intensive/`, and their caches live under
`Cache/Math/Intensive/`. Nine pages across these books contain no transcribed
text; visual inspection confirmed that each is a blank page, back cover, or
text-free transition page, so the caches still cover every PDF page. Formulas
are transcribed as LaTeX with balanced `$` / `$$` delimiters and no unresolved
`[?]` markers.

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
