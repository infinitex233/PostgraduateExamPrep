# PostgraduateExamPrep

English | [简体中文](README.zh-CN.md)

A file-based study management system for the 11408 postgraduate entrance examination. It keeps daily progress, stage plans, textbook retrieval, review notes, and a generated study dashboard in one repository.

## Exam Scope

The workspace covers all four parts of the 11408 track:

- Politics
- English I
- Mathematics I: calculus, linear algebra, probability, and statistics
- 408 Computer Science: data structures, computer organization, operating systems, and computer networks

## What This Repository Does

- Turns short natural-language study reports into dated Markdown records with structured YAML frontmatter.
- Maintains a long-term progress index, roadmap, weekly reviews, and stage reviews.
- Generates a single Capsule-style HTML dashboard from the study records.
- Searches local textbook OCR caches before opening multi-hundred-megabyte PDFs.
- Keeps one rolling, chapter-by-chapter Markdown note for each reviewed textbook.
- Stores English study sources and derived review artifacts separately from progress logs.

Source PDFs remain local. Git may track verified OCR caches together with the scripts, study records, notes, documentation, and suitable derived artifacts needed to maintain the system.

## Repository Layout

```text
PostgraduateExamPrep/
  AGENTS.md                      # Authoritative repository rules
  CLAUDE.md                      # Concise Claude Code entry point
  README.md                      # English GitHub landing page
  README.zh-CN.md                # Simplified Chinese landing page
  scripts/
    cache_layout.py              # Shared source-to-cache path rules
    query.py                     # Search categorized OCR caches
    page_ocr.py                  # Primary page-level cache builder
    docling_cache.py             # Legacy-compatible Docling builder
    build_dashboard.py           # Dashboard build entry point
    build_dashboard_variants.py  # Archive enrichment and rendering
    test_build_dashboard.py
    test_build_dashboard_variants.py
  StudyProgress/
    README.md                    # English progress workflow
    README.zh-CN.md              # Simplified Chinese progress workflow
    DailyLogs/                   # Daily records with YAML frontmatter
    Summaries/                   # Stable monthly subject summaries
    Reviews/                     # Weekly and stage reviews
    Imports/                     # Raw exports used for historical backfill
    ProgressIndex.md             # Long-term route and archive summary
    Roadmap.md                   # Goals and stage planning
    dashboard.html               # Generated Capsule dashboard
  StudyMaterials/
    README.md                    # English materials workflow
    README.zh-CN.md              # Simplified Chinese materials workflow
    408/                         # Local 408 textbook PDFs
    Math/Basic/                  # Local foundation-stage math PDFs
    Math/Intensive/              # Local intensive-stage math PDFs
    Cache/                       # Local categorized OCR caches
    BookNotes/                   # Rolling textbook notes
    English/                     # English sources and review artifacts
```

## Daily Progress

A natural-language report is normalized into:

```text
StudyProgress/DailyLogs/YYYY-MM/YYYY-MM-DD.md
```

Each record follows `StudyProgress/DailyLogs/_template.md`. Structured daily metrics come only from YAML frontmatter: unknown values stay `null`, and minutes or completion states are never inferred from prose. The same update also refreshes `StudyProgress/ProgressIndex.md` and the generated dashboard.

```bash
python scripts/build_dashboard.py
```

Archive and monthly dashboard sections additionally read stable summaries in `StudyProgress/ProgressIndex.md` and, when present, `StudyProgress/Summaries/Monthly/*.md`. Raw source exports used for historical backfill are kept separately under `StudyProgress/Imports/`.

See the [StudyProgress guide](StudyProgress/README.md) for the complete logging and dashboard workflow.

## Textbook Lookup

Search the local page cache before opening a large PDF:

```bash
python scripts/query.py "二叉树"
python scripts/query.py "矩阵" --book "线性代数"
python scripts/query.py "极限" --book "高数" --page-only
```

Build or resume page-level caches with the primary OCR pipeline:

```bash
python scripts/page_ocr.py "StudyMaterials/Math/Intensive/某书.pdf"
python scripts/page_ocr.py --all
```

Cache hits locate candidate PDF pages; they are not final evidence. Exact wording, formulas, diagrams, examples, and printed page numbers must be checked against the source PDF. Page citations distinguish the printed book page from the PDF page.

See the [StudyMaterials guide](StudyMaterials/README.md) for cache formats, evidence rules, and book-note workflow.

## Dashboard Checks

After changing dashboard code:

```bash
python -m unittest scripts.test_build_dashboard scripts.test_build_dashboard_variants
python scripts/build_dashboard.py
```

`StudyProgress/dashboard.html` is the only retained dashboard artifact. The renderer removes obsolete parallel variants during a production build.

## Local-Only Content

The following content must not be committed:

- Textbook and generated PDF files below `StudyMaterials/`
- Python bytecode, test caches, rendered PDF pages, screenshots, diagnostics, and temporary files
- Credentials, browser profiles, cookies, and machine-specific data

Verified OCR cache JSON under `StudyMaterials/Cache/` may be committed so textbook lookup works without rebuilding every cache. Keeping PDFs and transient artifacts out of Git avoids publishing copyrighted source material or machine-specific clutter.

## Working With Agents

Read the documentation in this order before changing files:

1. `AGENTS.md`
2. This README
3. `StudyProgress/README.md` for logs, reviews, or dashboard work
4. `StudyMaterials/README.md` for textbooks, caches, book notes, or English materials

`AGENTS.md` is authoritative. `CLAUDE.md` is a concise command and architecture reference.
