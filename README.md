# PostgraduateExamPrep

A personal study-management repository for the 11408 postgraduate entrance exam track.

This workspace keeps the preparation process in one place: study progress, review notes, roadmap updates, textbook lookup scripts, OCR caches, and generated review artifacts. The repository is designed to make daily records searchable and reusable, so later reviews, stage summaries, and experience posts can be built from real study history instead of memory.

The 11408 preparation scope includes:

- Politics
- English I
- Mathematics I: advanced mathematics, linear algebra, probability and statistics
- 408 Computer Science: data structures, computer organization, operating systems, and computer networks

Textbook PDFs are kept locally because of file size and copyright constraints. They are ignored by Git by default. The repository stores scripts, OCR cache data, study logs, derived notes, and generated review artifacts.

## Repository layout

```text
PostgraduateExamPrep/
  AGENTS.md                      # Workspace rules for coding and study-record agents
  README.md                      # Project overview
  scripts/                       # Lookup, OCR, dashboard, and maintenance scripts
    query.py                     # Search page-level OCR caches under StudyMaterials/Cache/
    page_ocr.py                  # Build page-level OCR caches for local textbook PDFs
    docling_cache.py             # Legacy Docling cache script
    build_dashboard.py           # Compatibility entry point for the study dashboard
    build_dashboard_variants.py  # Capsule dashboard renderer and cleanup logic
  StudyProgress/                 # Progress records, planning, dashboards, and reviews
    README.md                    # Operational guide for study-progress logging
    ProgressIndex.md             # Route-level preparation index
    Roadmap.md                   # Stage planning, goals, and strategy adjustments
    dashboard.html               # Generated Capsule-style 16:9 study dashboard
    DailyLogs/                   # Daily logs with YAML frontmatter
    Reviews/                     # Weekly and stage reviews
  StudyMaterials/                # Local materials, OCR cache data, and derived notes
    README.md                    # Operational guide for textbook lookup and notes
    408/                         # Computer science textbooks
    Math/                        # Mathematics textbooks
    Cache/                       # Page-level OCR caches (*.docling.json)
    English/                     # English exam materials
      WritingTemplates/          # Writing-template artifacts
        index.html               # Browser deck version
        index.pdf                # PDF version
    BookNotes/                   # One Markdown note per textbook, updated by chapter
```

## Core areas

### Study progress

`StudyProgress/` is the source of truth for the preparation timeline. Daily logs live under `StudyProgress/DailyLogs/` with structured frontmatter for dates, subject-level minutes, chapter progress, and tags. `ProgressIndex.md` gives a compact route-level summary, while `Roadmap.md` records stage plans and strategy changes.

The generated dashboard at `StudyProgress/dashboard.html` is built from daily-log frontmatter. It is the only dashboard artifact kept in the repository.

### Study materials

`StudyMaterials/` stores local reference materials and textbook-derived notes. The page-level OCR cache under `StudyMaterials/Cache/` supports fast textbook lookup through the scripts in `scripts/`.

Book notes live in `StudyMaterials/BookNotes/`. Each textbook gets one Markdown file, updated chapter by chapter during review. Source PDFs and derived notes stay separate.

## Agent workflow

This repository is meant to be portable across agent sessions. A new agent should treat the Markdown files in the workspace as the project context and read these files first:

1. `AGENTS.md`
2. `README.md`
3. `StudyProgress/README.md` for progress logging tasks
4. `StudyMaterials/README.md` for textbook lookup, material organization, or book-note tasks

Daily study records belong under `StudyProgress/`. Textbook PDFs, textbook-derived chapter notes, and English source materials belong under `StudyMaterials/`. Existing notes, logs, templates, and PDFs should be preserved unless an explicit request says otherwise.

## Current status

The repository is set up for:

- Daily natural-language study logging with structured frontmatter
- A generated visual study dashboard
- Route-level planning and stage reviews
- OCR-backed textbook search
- Chapter-by-chapter textbook notes
- English writing-template artifacts in HTML and PDF formats
