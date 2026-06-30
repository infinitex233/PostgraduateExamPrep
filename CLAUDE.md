# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a personal postgraduate exam preparation (考研) workspace — not a software project. There is no build or lint system. The dashboard checks are `scripts/test_build_dashboard.py` and `scripts/test_build_dashboard_variants.py` (run with `python -m unittest scripts.test_build_dashboard scripts.test_build_dashboard_variants`). The repo tracks study progress, textbook notes, and review cycles through structured Markdown files.

## Startup

Always read these files first when entering the repo:

1. `AGENTS.md` — authoritative agent rules for all operations
2. `README.md` — project overview and directory structure
3. `StudyProgress/README.md` — before any study-progress task
4. `StudyMaterials/README.md` — before any textbook lookup or book-note task

## Scripts (`scripts/`)

| Script | Purpose |
|---|---|
| `query.py` | Search the textbook OCR cache by keyword (`--book`, `--page-only`, `--context`, `--list-books`). Primary entry for textbook lookup. |
| `page_ocr.py` | Build the page-OCR cache for ALL books (math + 408). Run after adding/re-scanning PDFs. Produces the live `{book, total_pages, pages}` caches. |
| `docling_cache.py` | Legacy alt cache builder — emits a different docling `texts` structure that the current tooling does NOT use. Don't run unless intentionally switching formats. |
| `build_dashboard.py` | Compatibility entry point for regenerating the single `StudyProgress/dashboard.html`; aggregation helpers live here, and the CLI delegates to `build_dashboard_variants.py`. Run after every log change. |
| `build_dashboard_variants.py` | Capsule 16:9 landscape dashboard renderer, visual theme, Capsule subject colors, typography, and stale-dashboard cleanup. It writes only `StudyProgress/dashboard.html`. |
| `test_build_dashboard.py` | Unit tests for `build_dashboard.py`'s aggregation (`python -m unittest scripts.test_build_dashboard`). Run after editing aggregation logic. |
| `test_build_dashboard_variants.py` | Unit tests for the Capsule dashboard renderer and single-dashboard output (`python -m unittest scripts.test_build_dashboard_variants`). Run after editing dashboard visuals or output paths. |
| `auto-commit.sh` | Weekly auto-commit: stages everything, writes a Chinese summary message, pushes to `main`. It does NOT rebuild the dashboard — regenerate it when you write the log, not at commit time. |

## Repo state & git

- This is a tracked git repo pushed to GitHub. PDFs (`StudyMaterials/**/*.pdf`), the OCR cache (`StudyMaterials/Cache/`), and `.claude/` are gitignored — never try to commit them.
- `dashboard.html` is the only dashboard artifact and IS committed (small, single-file, viewable on GitHub). Always regenerate it after changing logs so the committed copy stays current. Do not keep `dashboard_capsule*.html`, `dashboard_signal.html`, or `DashboardTemplatePreviews.html`.
- Do not commit anything that identifies the user's real target school. Roadmap uses a generic placeholder ("目标院校") on purpose — keep it that way.

## Key boundaries

- **StudyProgress/** — daily logs, ProgressIndex, Roadmap, weekly/stage reviews. Never write study progress to StudyMaterials.
- **StudyMaterials/** — textbook PDFs (gitignored), BookNotes/ (one `.md` per book, incrementally updated chapter by chapter), and English resources. Never move/rename/delete PDFs unless asked.
- **StudyMaterials/English/** — English exam resources and generated review artifacts. Current writing-template deliverables live in `StudyMaterials/English/WritingTemplates/index.html` and `index.pdf`.
- **Two separate domains** — do not cross-store: study logs stay in StudyProgress, textbook-derived content stays in StudyMaterials.

## Primary workflows

### 1. Daily study logging

User reports progress in natural language → create `StudyProgress/DailyLogs/YYYY-MM/YYYY-MM-DD.md` (create month dir if needed) → append a row to `StudyProgress/ProgressIndex.md`. Preserve the original user report. Do not invent time/counts/status the user didn't provide — write `未说明` in prose, and `null` / empty in frontmatter.

**Each daily log MUST start with a YAML frontmatter block** — this is the machine-readable source that feeds the dashboard. Follow `StudyProgress/DailyLogs/_template.md`. Fields:

```yaml
---
date: 2026-06-11          # YYYY-MM-DD
phase: null               # 阶段，如 "基础阶段（一轮）" / "强化阶段"；未说明 null
total_minutes: 370        # 当日总学习时长（分钟）；用户给了总时长或可由各科相加得出时填，否则 null
mood: 受干扰              # 状态简述；无则 null
focus: null               # 今日主线，一句话概括；未说明 null
subjects:                 # 每个学到的科目一项
  - name: 数学-线代       # 必须用统一科目名（见下表）
    time_min: 72          # 该科时长（分钟）；未说明则 null
    detail: 开始学第三章   # 一句话完成内容
    result: ""            # 可选：完成度/产出，如 "完结"、"差 3 题"
    next: ""              # 可选：该科后续动作
progress:                 # 章节推进，可选
  - subject: 数学-线代
    chapter: 第三章 向量组
    status: 起步          # 起步 / 进行中 / 完结
review:                   # 可选：今日复盘，dashboard 会优先展示 next_actions
  wins: []                # 今日有效做法或完成点
  issues: []              # 卡点、干扰、身体状态等
  next_actions: []        # 次日优先动作
tags: ["受伤", "章节完结"] # 关键事件标签；无则 []
---
```

完整字段清单以 `StudyProgress/DailyLogs/_template.md` 为准；模板新增字段时以模板为准。

**统一科目命名**（frontmatter 的 `name` 字段必须从这里取，否则看板无法归并）：
`数学-高数`、`数学-线代`、`数学-概率`、`专业课-数据结构`、`专业课-组成原理`、`专业课-操作系统`、`专业课-计算机网络`、`英语`、`政治`。

**时长一律用分钟**（整数）填 frontmatter；正文散文里保留用户原话（如「2小时26分」）即可。各科 `time_min` 之和应与 `total_minutes` 一致——若用户只给了分项就求和填总数，只给了总数就把分项留 `null`。

正文部分（今日概览 / 原始汇报 / 分科记录 / 问题与调整）照旧保留，frontmatter 不替代正文，二者并存。

**更新看板**：每次新增或修改日志后，重新生成可视化看板：

```bash
python scripts/build_dashboard.py    # 扫描所有日志 frontmatter → StudyProgress/dashboard.html
```

`dashboard.html` 是唯一零依赖单文件（数据/CSS/JS 全内联，Capsule 风格 16:9 横屏 stage），双击即可在浏览器打开。`←/→/空格` 翻页。生成器只读 frontmatter，不读正文，所以 frontmatter 字段必须准确。

**看板是生成产物，聚合逻辑在 `scripts/build_dashboard.py`，Capsule 版式/配色/字体在 `scripts/build_dashboard_variants.py` 里维护**——不要只手改 `dashboard.html`。改主题、Capsule 科目色、强调文字或图表细节时，先改生成脚本再重新运行。同一科目在柱状图、图例、科目投入、当前推进中必须保持同色。当前视觉方向：纸感浅底、深色正文、Capsule 原生低饱和配色、胶囊控件、堆叠柱分隔清楚、克制的学术风。改样式时保持 frontmatter schema 和既有翻页交互不变，除非用户明确要求结构性改动。

**改动看板后的验证**（涉及聚合或样式时）：

```bash
python -m unittest scripts.test_build_dashboard scripts.test_build_dashboard_variants
python scripts/build_dashboard.py                  # 重新生成 dashboard.html
```

### 2. Textbook lookup

**Trigger**: The user is asking a **content question** about a textbook — they want to know what the book says, where something is, or whether a specific concept exists in the book. Any natural phrasing counts: "XX在哪一页", "书上有没有XX", "XX属于哪个知识点", "帮我查一下XX", "数据结构里怎么讲XX的", "XX在第几章", etc.

**Do NOT trigger** for mere mentions of subject names during progress reporting. If the user says "今天复习了组成原理第2章" or "做完了高数第三章习题", that's a study log, not a content question. The user would be asking you to *record* progress, not to *look up* content. Judge by intent: "我学了X" → study log. "X是什么/Y在哪" → textbook lookup.

**Cache system**: `StudyMaterials/Cache/` contains `*.docling.json` files — one per book. Despite the `.docling.json` name, **all 7 books use the same page-OCR format** — `{"book": "...", "total_pages": N, "pages": [{"page_no": N, "text": "..."}]}`, one OCR'd entry per PDF page. This applies to both:
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
with open(r'StudyMaterials/Cache/<book>.docling.json', encoding='utf-8') as f:
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
# Builds the page-OCR cache for ALL books (both StudyMaterials/Math/ and StudyMaterials/408/):
python scripts/page_ocr.py --all                # process all uncached PDFs
python scripts/page_ocr.py "path/to/file.pdf"   # single book
```
`page_ocr.py` is the script that produces the live `{book, total_pages, pages}` caches for every book, Math and 408 alike. (`scripts/docling_cache.py` exists but emits a different, richer docling structure with a `texts` key — it is **not** what the current caches use. Don't use it to rebuild unless you intend to switch formats and update the query tooling to match.)

### 3. Chapter note organization

User asks to organize a chapter (e.g., "整理《数据结构》第2章") → read the chapter from the PDF → create/update `StudyMaterials/BookNotes/<book-name>.md`. One file per book, updated incrementally. Preserve user-authored edits, deletions, and annotations — only merge in new material for the chapter being reviewed.

### 4. English materials

English resources belong under `StudyMaterials/English/`. The current writing-template deck is:

```text
StudyMaterials/English/WritingTemplates/
  index.html  # 16:9 browser deck
  index.pdf   # PDF export of the same deck
```

When updating writing-template materials from images or PDFs, preserve source order and useful learning content, but omit watermarks, platform marks, UI decoration, and OCR/debug noise. If the HTML deck changes and the user needs a PDF version, regenerate the PDF next to it. Delete temporary contact sheets, rendered pages, OCR intermediates, and local server PID files after use unless the user asks to keep them.

### 5. Periodic reviews

Weekly reviews → `StudyProgress/Reviews/Weekly/YYYY-Www.md`. Stage reviews → `StudyProgress/Reviews/Stage/`. Use the `_template.md` files as structure guides.

## Templates

All `_template.md` files define the expected structure for new records:

- `StudyProgress/DailyLogs/_template.md`
- `StudyProgress/Reviews/Weekly/_template.md`
- `StudyProgress/Reviews/Stage/_template.md`
- `StudyMaterials/BookNotes/_template.md`

## Language

Default to Chinese for all study notes, summaries, and user-facing content.

## Verification

After any file edit, report the exact paths changed.
