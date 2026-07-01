# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Read first

**When the user asks about exam-prep (考研) content — a knowledge point, definition, page location, or "what does the book say about X" — read the matching OCR cache under `StudyMaterials/Cache/*.docling.json` first** (via `python scripts/query.py "关键词" --book 书名`) to extract the relevant chapter content. Treat the cache as the primary retrieval route; fall back to direct PDF inspection only when the cache is missing, ambiguous, or when exact wording/formulas/printed page numbers are required.

`AGENTS.md` is the **source of truth** for workspace rules and overrides everything else. Read it before changing files. Two operational guides sit alongside it:

- `StudyProgress/README.md` — daily-log and dashboard workflow
- `StudyMaterials/README.md` — textbook lookup, OCR cache, and book-note workflow

This file summarizes commands and architecture; defer to those three for policy.

## What this repo is

A personal study-management workspace for China's **11408 postgraduate entrance exam** (考研): Politics, English I, Math I (calc / linear algebra / probability), 408 CS (data structures / computer organization / OS / networks). It is **not a software project** — the only executable code is a handful of Python/shell scripts under `scripts/`. The bulk of the repo is Markdown records, generated HTML dashboards, and an OCR cache. User-facing content defaults to **Chinese**.

## Common commands

```bash
# Daily study logging — after writing/updating any daily log, regenerate the dashboard:
python scripts/build_dashboard.py

# Dashboard regression tests (run after touching dashboard code):
python -m unittest scripts.test_build_dashboard scripts.test_build_dashboard_variants

# Search the textbook OCR cache (primary route for "what does the book say about X"):
python scripts/query.py "二叉树"
python scripts/query.py "二叉树" --book 数据结构
python scripts/query.py "二叉树" --book 线代 --page-only
python scripts/query.py "二叉树" --book 高数 --context 2

# (Re)build page-level OCR cache for a local textbook PDF — heavy, runs PyMuPDF + RapidOCR:
python scripts/page_ocr.py "StudyMaterials/408/某书.pdf"
python scripts/page_ocr.py --all          # all uncached PDFs

# Weekly summary commit + push (regenerates dashboard first, then commits in Chinese):
bash scripts/auto-commit.sh
```

## Architecture: the data pipeline

The core of the repo is a **frontmatter → dashboard** pipeline. Understand this before touching progress code:

1. **Daily logs** (`StudyProgress/DailyLogs/YYYY-MM/YYYY-MM-DD.md`) each start with a YAML frontmatter block (template: `DailyLogs/_template.md`). Fields: `date`, `total_minutes`, per-subject integer minutes, chapter progress, tags. **This frontmatter is the only dashboard data source** — never infer minutes/status from prose. Use `null` for values the user didn't give; never fabricate.
2. `scripts/build_dashboard.py` is the **compatibility entry point** — it aggregates frontmatter and delegates rendering to `scripts/build_dashboard_variants.py`.
   - Aggregation/helpers → `build_dashboard.py`
   - Visual layout, Capsule color mapping, typography, cleanup → `build_dashboard_variants.py`
   - Output is a single artifact: `StudyProgress/dashboard.html` (Capsule-style 16:9 deck).
3. After any progress or dashboard-code change, run `python scripts/build_dashboard.py` to regenerate the HTML. `auto-commit.sh` also refreshes the dashboard before committing.

### Canonical subject names (do not rename)

These strings feed both aggregation and the `subject_colors` map, so they must stay stable across stacked bars, legend swatches, totals, and current-progress bars:
`数学-高数`, `数学-线代`, `数学-概率`, `专业课-数据结构`, `专业课-组成原理`, `专业课-操作系统`, `专业课-计算机网络`, `英语`, `政治`.
Aggregate group colors use a separate `group_colors` map (`数学`, `专业课`, `英语`, `政治`, `其他`).

### Dashboard constraints

- `dashboard.html` is generated — **don't hand-edit it as the source of truth**, and don't create parallel variants (`dashboard_capsule*.html`, `dashboard_signal.html`, etc.).
- Keep layout, frontmatter schema, and interaction logic unchanged unless the user explicitly asks for structural changes.

## Textbook lookup discipline

`StudyMaterials/Cache/*.docling.json` is a page-level OCR cache (`{"book","total_pages","pages":[{"page_no","text"}]}`), git-ignored and rebuilt locally from PDFs. `query.py` reads it (and tolerates legacy Docling-format JSON for math books).

- Cache hits only **locate candidate pages**. For exact wording, formulas, diagrams, examples, or printed page numbers, open the PDF page to confirm.
- `page_no` is the **PDF page**, not the **printed book page**. Cite both `书内印刷页码` and `PDF 页码`; label any unconfirmed one explicitly rather than omitting it.
- Never answer textbook-specific claims from memory or fabricate wording/page numbers. If it can't be confirmed in the PDF, say so.

## Book notes

One Markdown file per book under `StudyMaterials/BookNotes/`, updated **chapter-by-chapter during review** (not full-book summaries). Merge new material incrementally into the existing chapter — **preserve the user's manual edits** and never overwrite/normalize the whole file. Separate verified textbook content from your own supplements, and keep page references for definitions/formulas/key conclusions.

## Hard rules (from AGENTS.md)

- Don't rename, move, or delete source PDFs or existing notes/logs/templates unless explicitly asked. Don't store daily logs in `StudyMaterials/`.
- Source PDFs and derived notes stay separate.
- After edits, report the **exact paths changed**. If source evidence is missing or unclear, say so rather than inventing details.
- Delete one-off inspection artifacts (PDF page screenshots, rendered images, OCR/debug intermediates) after use unless asked to keep them. `__pycache__/` is git-ignored — don't commit Python temp files.

## Known path drift

`scripts/auto-commit.sh` still matches the legacy `DigitalBooks/BookNotes/` path when counting book-note changes; the real directory is now `StudyMaterials/BookNotes/`. Book-note commits currently fall into "其他" — fix the script if touching it.

## Note on AGENTS.md vs. README.md

The directory is named `StudyMaterials/` in the actual filesystem and in `AGENTS.md`. Older commit messages and `auto-commit.sh` may reference `DigitalBooks/` — treat `StudyMaterials/` as canonical.
