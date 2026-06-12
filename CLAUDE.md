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

User reports progress in natural language → create `StudyProgress/DailyLogs/YYYY-MM/YYYY-MM-DD.md` (create month dir if needed) → append a row to `StudyProgress/ProgressIndex.md`. Preserve the original user report. Do not invent time/counts/status the user didn't provide — write `未说明` in prose, and `null` / empty in frontmatter.

**Each daily log MUST start with a YAML frontmatter block** — this is the machine-readable source that feeds the dashboard. Follow `StudyProgress/DailyLogs/_template.md`. Fields:

```yaml
---
date: 2026-06-11          # YYYY-MM-DD
total_minutes: 370        # 当日总学习时长（分钟）；用户给了总时长或可由各科相加得出时填，否则 null
mood: 受干扰              # 状态简述；无则 null
subjects:                 # 每个学到的科目一项
  - name: 数学-线代       # 必须用统一科目名（见下表）
    time_min: 72          # 该科时长（分钟）；未说明则 null
    detail: 开始学第三章   # 一句话完成内容
progress:                 # 章节推进，可选
  - subject: 数学-线代
    chapter: 第三章 向量组
    status: 起步          # 起步 / 进行中 / 完结
tags: ["受伤", "章节完结"] # 关键事件标签；无则 []
---
```

**统一科目命名**（frontmatter 的 `name` 字段必须从这里取，否则看板无法归并）：
`数学-高数`、`数学-线代`、`数学-概率`、`专业课-数据结构`、`专业课-组成原理`、`专业课-操作系统`、`专业课-计算机网络`、`英语`、`政治`。

**时长一律用分钟**（整数）填 frontmatter；正文散文里保留用户原话（如「2小时26分」）即可。各科 `time_min` 之和应与 `total_minutes` 一致——若用户只给了分项就求和填总数，只给了总数就把分项留 `null`。

正文部分（今日概览 / 原始汇报 / 分科记录 / 问题与调整）照旧保留，frontmatter 不替代正文，二者并存。

**更新看板**：每次新增或修改日志后，重新生成可视化看板：

```bash
python scripts/build_dashboard.py    # 扫描所有日志 frontmatter → StudyProgress/dashboard.html
```

`dashboard.html` 是零依赖单文件（数据/CSS/JS 全内联，遵循 frontend-slides 的 16:9 stage 规范），双击即可在浏览器打开，含四屏：封面汇总、每日时长趋势（堆叠柱状图）、各科进度追踪、关键节点时间线。`←/→/空格` 翻页。生成器只读 frontmatter，不读正文，所以 frontmatter 字段必须准确。

### 2. Textbook lookup

**Trigger**: The user is asking a **content question** about a textbook — they want to know what the book says, where something is, or whether a specific concept exists in the book. Any natural phrasing counts: "XX在哪一页", "书上有没有XX", "XX属于哪个知识点", "帮我查一下XX", "数据结构里怎么讲XX的", "XX在第几章", etc.

**Do NOT trigger** for mere mentions of subject names during progress reporting. If the user says "今天复习了组成原理第2章" or "做完了高数第三章习题", that's a study log, not a content question. The user would be asking you to *record* progress, not to *look up* content. Judge by intent: "我学了X" → study log. "X是什么/Y在哪" → textbook lookup.

**Cache system**: `DigitalBooks/Cache/` contains `*.docling.json` files — one per book. Despite the `.docling.json` name, **all 7 books use the same page-OCR format** — `{"book": "...", "total_pages": N, "pages": [{"page_no": N, "text": "..."}]}`, one OCR'd entry per PDF page. This applies to both:
- **408 textbooks** (数据结构/组成原理/操作系统/计算机网络)
- **Math textbooks** (张宇30讲 概率/线代/高数)

The `texts`/section-header docling structure is **not** present in any live cache — don't look for a `texts` key. (The `.docling.json` suffix is historical; the caches are all built by `page_ocr.py`.)

**Search workflow**:
```bash
python scripts/query.py "<keyword>" --book <partial-book-name>
```
- `--book` supports partial Chinese book names: `--book 数据结构`, `--book 组成原理`, `--book 概率`
- `--page-only` for page numbers only; `--context N` for more surrounding text
- `--list-books` to see all cached books

**CRITICAL — Page numbers**: The query tool reports **PDF page numbers** (the physical page in the PDF file). The **printed page number** (what the reader sees on the page) is often different, and **its position depends on the book**:
- **408 textbooks**: printed page number is on the **first line** of the page text.
- **Math textbooks** (张宇30讲): printed page number is on the **last line** of the page text.

Don't assume — check both ends of the OCR text and find the line that is a bare number. After running the query, ALWAYS confirm the printed page number by reading the page text:
```python
import json
with open(r'DigitalBooks/Cache/<book>.docling.json', encoding='utf-8') as f:
    data = json.load(f)
for p in data['pages']:
    if p['page_no'] == <PDF_PAGE>:
        lines = [l.strip() for l in p['text'].split('\n') if l.strip()]
        # 408: lines[0] is usually the printed number; 张宇: lines[-1] is.
        print(f'PDF p.{p["page_no"]}: head={lines[0]!r} tail={lines[-1]!r}')
```
**Always cite BOTH page numbers in your answer** — the user navigates by printed page numbers, not PDF page numbers. Be explicit: "印刷页码 p.286（PDF p.298）".

**When the query returns incomplete results**: OCR is not perfect. If a result seems to have missing content (e.g., only 4 of 5 numbered items), read the full page text directly from the JSON — the query tool may truncate long snippets.

**Rebuilding cache** (when PDFs are added or re-scanned):
```bash
# Builds the page-OCR cache for ALL books (both DigitalBooks/math/ and DigitalBooks/408/):
python scripts/page_ocr.py --all                # process all uncached PDFs
python scripts/page_ocr.py "path/to/file.pdf"   # single book
```
`page_ocr.py` is the script that produces the live `{book, total_pages, pages}` caches for every book, math and 408 alike. (`scripts/docling_cache.py` exists but emits a different, richer docling structure with a `texts` key — it is **not** what the current caches use. Don't use it to rebuild unless you intend to switch formats and update the query tooling to match.)

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
