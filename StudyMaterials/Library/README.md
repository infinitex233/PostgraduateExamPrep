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

Interpreter follows the root README "Runtime Environment" section: on Windows run `python` (or `py -3`) directly; on WSL/Linux prefer `./.venv/bin/python` when present, otherwise `python3`.

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

For scanned math books whose dense formulas RapidOCR cannot preserve (lost integral signs, broken fractions), re-transcribe the affected pages at high fidelity by rendering them and reading them directly. Create the output directory first (for example `mkdir -p tmp/vision-pages`); rendered pages are one-off artifacts and must be deleted afterwards:

```bash
pdftoppm -f 161 -l 188 -r 180 -png "StudyMaterials/Library/408/某书.pdf" tmp/vision-pages/p
```

Read the rendered page images in batches, transcribe each page into LaTeX-formula Markdown, then merge only that page range into the `.docling.json` cache while preserving `total_pages` and the page-level structure. Repair just the pages that need it and leave the rest of the cache untouched.

`scripts/docling_cache.py` is a legacy-compatible alternative that writes Docling JSON and Markdown. Keep it for compatibility, but do not present it as the default workflow. Full-cache generation can process gigabytes of local PDFs and should not be used as a routine documentation or pre-commit check.

## Verified Intensive Mathematics Cache

The following intensive-stage Mathematics I caches were rebuilt with a
vision-model transcription pipeline and verified on 2026-08-14:

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

## Partially Verified Basic Mathematics Cache

`27张宇基础30讲高数.docling.json` was partially rebuilt with the
vision-transcription pipeline on 2026-09-19: PDF pages 1-284 are high-fidelity
LaTeX transcriptions (handwritten margin notes included; formulas and `$` /
`$$` delimiters verified), while pages 285-586 still hold the original
RapidOCR text and may contain broken formulas. When a query hits page 285 or
later, verify formulas against the source PDF.

The caches for `27张宇基础30讲线代`, `27张宇基础30讲概率`, and the four 王道
408 books remain unfixed: body prose is mostly usable, but figure regions and
formulas may still contain OCR errors.

## Verified 408 Recitation Handbook Cache

`27计算机网络背诵手册(公众号：里昂408考研）.docling.json` was rebuilt from its
scanned source PDF (`408/27计算机网络背诵手册(公众号：里昂408考研）.pdf`, 125
pages of 192 ppi page bitmaps with no text layer) with the vision pipeline and
verified on 2026-09-22; it covers 125 / 125 pages.

Printed headings, tables, formulas, footnotes, exam-question boxes, and figure
captions are transcribed as printed. Figure interiors are recorded as a list of
the labels visible in the figure followed by a short description of what the
figure shows. Watermarks, QR codes, and footer page numbers are omitted, and a
table continued from the previous page is marked as such. Page numbering:
`书内印刷页码 + 5 = PDF 页码` (印刷 20 = PDF 25); PDF pages 2-5 hold the table
of contents and PDF page 125 is the 艾宾浩斯遗忘曲线 appendix, and neither
carries a printed number.

Per-position bit sequences inside the waveform and framing figures 图 2.3, 图
2.4, 图 3.3, and 图 3.12 fall below the source bitmap's resolution; those figure
blocks list only the labels that are legible instead of digit-by-digit values.

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
