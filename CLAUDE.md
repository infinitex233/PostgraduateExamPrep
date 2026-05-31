# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a personal postgraduate exam preparation (考研) workspace — not a software project. There is no build, lint, or test system. The repo tracks study progress, textbook notes, and review cycles through structured Markdown files.

## Startup

Always read these files first when entering the repo:

1. `AGENTS.md` — authoritative agent rules for all operations
2. `README.md` — project overview and directory structure
3. `StudyProgress/README.md` — before any study-progress task
4. `DigitalBooks/README.md` — before any textbook lookup or book-note task

## Key boundaries

- **StudyProgress/** — daily logs, ProgressIndex, Roadmap, weekly/stage reviews. Never write study progress here to DigitalBooks.
- **DigitalBooks/** — textbook PDFs (gitignored) and BookNotes/ (one `.md` per book, incrementally updated chapter by chapter). Never move/rename/delete PDFs unless asked.
- **Two separate domains** — do not cross-store: study logs stay in StudyProgress, textbook-derived content stays in DigitalBooks.

## Primary workflows

### 1. Daily study logging

User reports progress in natural language → create `StudyProgress/DailyLogs/YYYY-MM/YYYY-MM-DD.md` (create month dir if needed) → append a row to `StudyProgress/ProgressIndex.md`. Preserve the original user report. Do not invent time/counts/status the user didn't provide — write `未说明`.

### 2. Textbook lookup

**Trigger**: The user is asking a **content question** about a textbook — they want to know what the book says, where something is, or whether a specific concept exists in the book. Any natural phrasing counts: "XX在哪一页", "书上有没有XX", "XX属于哪个知识点", "帮我查一下XX", "数据结构里怎么讲XX的", "XX在第几章", etc.

**Do NOT trigger** for mere mentions of subject names during progress reporting. If the user says "今天复习了组成原理第2章" or "做完了高数第三章习题", that's a study log, not a content question. The user would be asking you to *record* progress, not to *look up* content. Judge by intent: "我学了X" → study log. "X是什么/Y在哪" → textbook lookup.

**Cache system**: `DigitalBooks/Cache/` contains `.docling.json` files — one per book.
- **408 textbooks** (数据结构/组成原理/操作系统/计算机网络): page-OCR format — `{"pages": [{"page_no": N, "text": "..."}]}` — each page has been OCR'd from the PDF. Supports keyword search.
- **Math textbooks** (张宇30讲 概率/线代/高数): docling format — `{"texts": [...], ...}` — richer structure with section headers.

**Search workflow**:
```bash
python scripts/query.py "<keyword>" --book <partial-book-name>
```
- `--book` supports partial Chinese book names: `--book 数据结构`, `--book 组成原理`, `--book 概率`
- `--page-only` for page numbers only; `--context N` for more surrounding text
- `--list-books` to see all cached books

**CRITICAL — Page numbers**: The query tool reports **PDF page numbers** (the physical page in the PDF file). The **printed page number** (what the reader sees on the page) is often different — it's typically the first line of each page's OCR text. After running the query, ALWAYS check the printed page number by reading a few lines of the page text:
```python
import json
with open(r'DigitalBooks/Cache/<book>.docling.json', encoding='utf-8') as f:
    data = json.load(f)
for p in data['pages']:
    if p['page_no'] == <PDF_PAGE>:
        printed = p['text'].split('\n')[0].strip()
        print(f'PDF p.{p["page_no"]} = printed p.{printed}')
```
**Always cite BOTH page numbers in your answer** — the user navigates by printed page numbers, not PDF page numbers. Be explicit: "印刷页码 p.286（PDF p.298）".

**When the query returns incomplete results**: OCR is not perfect. If a result seems to have missing content (e.g., only 4 of 5 numbered items), read the full page text directly from the JSON — the query tool may truncate long snippets.

**Rebuilding cache** (when PDFs are added or re-scanned):
```bash
# For 408 textbooks (image-based PDFs):
python scripts/page_ocr.py --all        # process all uncached PDFs
python scripts/page_ocr.py "path/to/file.pdf"  # single book

# For math textbooks (scanned PDFs with better layout):
python scripts/docling_cache.py --all
```

Both scripts support resume: if interrupted, re-running will auto-detect partial progress and continue from checkpoint.

### 3. Chapter note organization

User asks to organize a chapter (e.g., "整理《数据结构》第2章") → read the chapter from the PDF → create/update `DigitalBooks/BookNotes/<book-name>.md`. One file per book, updated incrementally. Preserve user-authored edits, deletions, and annotations — only merge in new material for the chapter being reviewed.

### 4. Periodic reviews

Weekly reviews → `StudyProgress/Reviews/Weekly/YYYY-Www.md`. Stage reviews → `StudyProgress/Reviews/Stage/`. Use the `_template.md` files as structure guides.

## Templates

All `_template.md` files define the expected structure for new records:

- `StudyProgress/DailyLogs/_template.md`
- `StudyProgress/Reviews/Weekly/_template.md`
- `StudyProgress/Reviews/Stage/_template.md`
- `DigitalBooks/BookNotes/_template.md`

## Language

Default to Chinese for all study notes, summaries, and user-facing content.

## Verification

After any file edit, report the exact paths changed.
