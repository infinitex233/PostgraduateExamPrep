# AGENTS.md

## Repository-Level Agent Instructions

These instructions apply to the entire `D:\Documents\PostgraduateExamPrep` workspace and should be followed by any agent or new conversation working in this folder.

- Do not rely on prior conversation context. Treat the files in this workspace as the source of truth.
- Read this file before changing files or organizing study records.
- If present, read root `README.md` for a quick project overview.
- Treat `StudyProgress/README.md` as the operational guide for study-progress logging.
- Treat `StudyMaterials/README.md` as the operational guide for textbook lookup, book-note generation, and local study-material organization.
- For textbook lookup, use `scripts/query.py` and the OCR cache under `StudyMaterials/Cache/` first. Fall back to direct PDF inspection when cache evidence is missing, ambiguous, exact wording is needed, or printed page numbers must be confirmed.
- If the user reports daily study progress in natural language, handle it as a logging task unless they explicitly say they are only discussing or asking a question.
- Keep all study-progress records under `StudyProgress/`.
- Keep textbook PDFs, textbook-derived chapter notes, and English source materials under `StudyMaterials/`.
- Do not store daily progress logs in `StudyMaterials/`.
- Do not change this instruction file unless the user asks to update the workflow.

## Agent Startup Checklist

For a new conversation or another agent taking over this folder:

1. Read `AGENTS.md`.
2. Read `README.md`.
3. For study-progress tasks, read `StudyProgress/README.md` and inspect the target files before writing.
4. For textbook lookup, chapter-note tasks, or local study-material organization, read `StudyMaterials/README.md` and inspect the relevant PDF, note file, or material folder before answering or writing.
5. Preserve user-authored content. Do not overwrite existing notes, logs, or templates unless the user explicitly asks.
6. If source evidence is missing or unclear, say so instead of fabricating details.
7. After edits, report the exact files changed.

## Project Context

This workspace is for **11408 postgraduate entrance exam (考研)** preparation.

**11408 exam subjects:**
- **408 计算机学科专业基础综合**: 数据结构、计算机组成原理、操作系统、计算机网络
- **数学一**: 高等数学、线性代数、概率论与数理统计
- **英语一**
- **政治**

**Directory overview:**
- `StudyMaterials/`: local study materials, including 408/math PDFs, OCR cache, book notes, and English resources.
- `StudyProgress/`: study notes, progress records, plans, summaries, and review logs.

## Working Guidelines

- Keep source materials and derived notes separate.
- Do not rename, move, or delete study materials unless the user explicitly asks.
- Preserve existing folder structure when adding new files.
- Prefer clear, dated filenames for study plans, summaries, and progress records.
- Use Markdown for notes and planning documents unless another format is requested.
- Automatically delete unnecessary temporary files created during work, such as PDF page screenshots, rendered page images, OCR/debug intermediates, or other one-off inspection artifacts, unless the user explicitly asks to keep them.

## StudyProgress Workflow

When the user reports daily study progress in natural language:

- Create or update that day's log under `StudyProgress/DailyLogs/YYYY-MM/YYYY-MM-DD.md`.
- Start each daily log with a YAML frontmatter block per `DailyLogs/_template.md` (date, total_minutes, per-subject minutes, chapter progress, tags). This frontmatter is the data source for the dashboard — use the canonical subject names, minutes as integers, and `null` for anything the user didn't provide.
- Keep the original user report in the daily log.
- Extract the daily overview, subject-level progress, approximate time or quantity, current state, problems, and next actions when possible.
- Do not invent precise time, task counts, or completion status if the user did not provide them.
- Update `StudyProgress/ProgressIndex.md` with a short row for that day.
- After updating logs, regenerate the dashboard: `python scripts/build_dashboard.py` (rebuilds `StudyProgress/dashboard.html` from log frontmatter).
- Keep daily entries concise and easy to review.
- Treat `StudyProgress/ProgressIndex.md` as the route-level summary of the preparation process.
- Use `StudyProgress/Reviews/Weekly/` and `StudyProgress/Reviews/Stage/` for periodic summaries when the user asks for review.
- Experience-post material is optional and should be derived later from the records, not forced into every daily log.

## StudyMaterials Workflow

`StudyMaterials/` contains important postgraduate exam textbook PDFs and English resources for repeated lookup and review. These materials are reference sources, not a complete list of all materials used.

When the user asks what a textbook says about a knowledge point or asks for a page location:

- First search the local OCR cache with `python scripts/query.py "关键词" --book "书名关键词"` unless the user explicitly asks not to use cache.
- The current cache for the 408 four books and math three books is a page-level OCR cache under `StudyMaterials/Cache/`, using JSON files named `*.docling.json`.
- Treat cache hits as the primary route for locating candidate PDF pages. If the answer needs exact textbook wording, book-internal page numbers, diagrams, formulas, or ambiguous OCR text, inspect the relevant PDF page before answering.
- Cite the source with book name and page location. For any answer about knowledge-point page locations, provide both `书内印刷页码` and `PDF 页码` and label them clearly. If one cannot be confirmed, say so explicitly instead of omitting it.
- If the content cannot be confirmed in the available PDFs, say so clearly. Do not fabricate textbook wording, page numbers, examples, or conclusions.
- Do not rely only on memory for textbook-specific claims.

When the user asks to organize a chapter during review:

- Read the corresponding chapter from the relevant PDF.
- Create or update one Markdown note per book under `StudyMaterials/BookNotes/`.
- Keep chapter notes organized by chapter headings inside the book-level Markdown file.
- Treat book notes as incremental review notes updated chapter by chapter during the user's strengthening-stage review, not as one-time full-book summaries.
- Preserve user-authored edits, deletions, and additions in book notes. Do not overwrite or normalize the whole file unless the user explicitly asks.
- When updating an existing chapter, merge new verified material into that chapter and keep the user's personal notes intact.
- Separate verified textbook content from the agent's own understanding or supplements.
- Include page references for textbook-derived definitions, formulas, key conclusions, examples, and common pitfalls when possible.
- Do not modify, rename, move, or delete source PDFs unless the user explicitly asks.

## English Materials Workflow

`StudyMaterials/English/` stores English exam resources. Current generated writing-template artifacts live under:

```text
StudyMaterials/English/WritingTemplates/
  index.html  # 16:9 browser deck for writing templates
  index.pdf   # PDF export of the same deck
```

- Keep English source materials and generated review artifacts under `StudyMaterials/English/`.
- If updating `WritingTemplates/index.html`, keep `WritingTemplates/index.pdf` in sync when the user asks for the PDF version.
- When extracting text from local images, preserve the content order and omit obvious watermarks, platform marks, and screenshot-only noise.
- Delete temporary OCR screenshots, rendered page images, contact sheets, local HTTP-server PID files, and other one-off inspection artifacts after use unless the user explicitly asks to keep them.

## Language

- Default to Chinese for study notes, summaries, and user-facing documents.
- Keep technical or file-management instructions concise and unambiguous.

## Verification

- After creating or editing files, confirm the exact path changed.
- For generated plans or summaries, check that the output is readable and organized before reporting completion.
