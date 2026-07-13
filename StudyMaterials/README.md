# StudyMaterials

English | [简体中文](README.zh-CN.md)

This directory holds the high-value textbooks, local OCR caches, rolling textbook notes, and English study materials that need repeated retrieval during 11408 preparation. It is a curated working library, not a complete archive of every resource.

For repository-wide policy, read `../AGENTS.md` first. This guide owns the operational details for textbook lookup, cache generation, evidence verification, book notes, and English artifacts.

## Local-Only Policy

Textbook PDFs are large and may be copyrighted. Keep them in the appropriate local directories and do not commit them. OCR caches are derived, rebuildable local data and must also remain outside Git.

Git may track scripts, Markdown notes, documentation, and suitable review artifacts such as the HTML writing-template deck.

## Directory Layout

```text
StudyMaterials/
  README.md
  README.zh-CN.md
  408/                         # Local 408 textbook PDFs
  Math/
    Basic/                     # Foundation-stage Mathematics I PDFs
    Intensive/                 # Intensive-stage Mathematics I PDFs
  Cache/                       # Local categorized caches; git-ignored
    408/
    Math/
      Basic/
      Intensive/
  BookNotes/                   # One rolling Markdown note per textbook
  English/
    WritingTemplates/
      index.html               # Tracked browser version
      index.pdf                # Local generated PDF
```

The cache category mirrors the source category, including nested parent directories. For example, a PDF under `Math/Intensive/SetA/` writes its cache under `Cache/Math/Intensive/SetA/`. Both cache builders reuse `scripts/cache_layout.py` for this mapping.

## Cache Formats

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

`scripts/query.py` recursively reads `StudyMaterials/Cache/**/*.docling.json` and supports both this format and legacy Docling JSON containing structured `texts` entries.

## Query the Cache

When a user asks what a textbook says, where a concept appears, or how a definition is stated, search the local cache first:

```bash
python scripts/query.py "关键词"
python scripts/query.py "关键词" --book "数据结构"
python scripts/query.py "关键词" --book "线代" --page-only
python scripts/query.py "关键词" --book "高数" --context 2
python scripts/query.py --list-books
```

A cache miss does not prove that the book lacks the material. Try synonyms, shorter terms, and split queries before inspecting likely PDF pages or reporting that the current cache did not confirm it.

## Build the Cache

Use the page-level PyMuPDF + RapidOCR pipeline by default:

```bash
python scripts/page_ocr.py "StudyMaterials/408/某书.pdf"
python scripts/page_ocr.py "StudyMaterials/Math/Intensive/某书.pdf"
python scripts/page_ocr.py --all
```

It discovers PDFs recursively, uses embedded text when available, falls back to OCR for scanned pages, resumes incomplete JSON checkpoints, and skips complete caches.

`scripts/docling_cache.py` is a legacy-compatible alternative that writes both Docling JSON and Markdown. Keep it for existing cache compatibility, but do not present it as the default page-level workflow.

Full-cache generation can process gigabytes of local PDFs. Do not run it as a routine documentation or pre-commit check.

## Evidence and Page Numbers

OCR cache matches identify candidate **PDF pages** only. They are not final evidence.

Open the source PDF when the answer depends on:

- Exact wording or a direct quotation
- Formulas, symbols, tables, or diagrams
- Worked-example details
- Printed book page numbers
- A conclusion whose OCR text is ambiguous

A textbook-specific answer should identify the book and section when possible, and distinguish:

- `书内印刷页码`: the page number printed in the book
- `PDF 页码`: the page index in the PDF viewer/cache

If either value cannot be confirmed, state that explicitly. Never invent textbook wording, page locations, examples, formulas, or conclusions from memory.

## Chapter-by-Chapter Book Notes

`BookNotes/` contains one rolling Markdown note per textbook. Update it during review, chapter by chapter, instead of summarizing an entire book in one pass.

When a chapter is requested:

1. Locate the corresponding source PDF and relevant pages.
2. Open or create `BookNotes/<book name>.md`.
3. Update only the chapter currently under review.
4. Merge verified material into an existing chapter rather than replacing it wholesale.
5. Preserve the user's additions, deletions, ordering, annotations, and personal wording.
6. Separate verified textbook content from explanations or supplements.
7. Keep page references for definitions, formulas, theorems, examples, key conclusions, and common mistakes when possible.

Prioritize knowledge structure, key definitions, exam patterns, error traps, and useful problem-entry points. The note is a review aid, not a reproduction of the source book.

## English Materials

`English/` stores English I source material and derived review artifacts. The current writing-template outputs are:

```text
English/WritingTemplates/
  index.html
  index.pdf
```

When transcribing screenshots or PDFs, preserve source order and useful study content while omitting watermarks, platform chrome, correction-interface decoration, screenshot noise, and OCR diagnostics.

If `WritingTemplates/index.html` changes and the user requests a PDF version, regenerate `WritingTemplates/index.pdf` so both formats remain aligned. The PDF remains local because all PDFs below `StudyMaterials/` are ignored.

## Cleanup and Safety

- Never rename, move, or delete source PDFs unless the user explicitly requests it.
- Keep source materials separate from derived notes.
- Do not commit PDFs or anything under `Cache/`.
- Delete rendered PDF pages, screenshots, OCR diagnostics, temporary services, PID files, and other one-off artifacts after use.
- If source evidence is missing or unclear, report the limitation instead of filling the gap.
