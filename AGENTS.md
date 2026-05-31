# AGENTS.md

## Repository-Level Agent Instructions

These instructions apply to the entire `D:\Documents\PostgraduateExamPrep` workspace and should be followed by any agent or new conversation working in this folder.

- Do not rely on prior conversation context. Treat the files in this workspace as the source of truth.
- Read this file before changing files or organizing study records.
- If present, read root `README.md` for a quick project overview.
- Treat `StudyProgress/README.md` as the operational guide for study-progress logging.
- Treat `DigitalBooks/README.md` as the operational guide for textbook lookup and book-note generation.
- If the user reports daily study progress in natural language, handle it as a logging task unless they explicitly say they are only discussing or asking a question.
- Keep all study-progress records under `StudyProgress/`.
- Keep textbook PDFs and textbook-derived chapter notes under `DigitalBooks/`.
- Do not store daily progress logs in `DigitalBooks/`.
- Do not change this instruction file unless the user asks to update the workflow.

## Agent Startup Checklist

For a new conversation or another agent taking over this folder:

1. Read `AGENTS.md`.
2. Read `README.md`.
3. For study-progress tasks, read `StudyProgress/README.md` and inspect the target files before writing.
4. For textbook lookup or chapter-note tasks, read `DigitalBooks/README.md` and inspect the relevant PDF or note file before answering or writing.
5. Preserve user-authored content. Do not overwrite existing notes, logs, or templates unless the user explicitly asks.
6. If source evidence is missing or unclear, say so instead of fabricating details.
7. After edits, report the exact files changed.

## Project Context

This workspace is for postgraduate exam preparation materials.

- `DigitalBooks/`: digital textbooks, references, and source study materials.
- `StudyProgress/`: study notes, progress records, plans, summaries, and review logs.

## Working Guidelines

- Keep source materials and derived notes separate.
- Do not rename, move, or delete study materials unless the user explicitly asks.
- Preserve existing folder structure when adding new files.
- Prefer clear, dated filenames for study plans, summaries, and progress records.
- Use Markdown for notes and planning documents unless another format is requested.

## StudyProgress Workflow

When the user reports daily study progress in natural language:

- Create or update that day's log under `StudyProgress/DailyLogs/YYYY-MM/YYYY-MM-DD.md`.
- Keep the original user report in the daily log.
- Extract the daily overview, subject-level progress, approximate time or quantity, current state, problems, and next actions when possible.
- Do not invent precise time, task counts, or completion status if the user did not provide them.
- Update `StudyProgress/ProgressIndex.md` with a short row for that day.
- Keep daily entries concise and easy to review.
- Treat `StudyProgress/ProgressIndex.md` as the route-level summary of the preparation process.
- Use `StudyProgress/Reviews/Weekly/` and `StudyProgress/Reviews/Stage/` for periodic summaries when the user asks for review.
- Experience-post material is optional and should be derived later from the records, not forced into every daily log.

## DigitalBooks Workflow

`DigitalBooks/` contains important postgraduate exam textbook PDFs for repeated lookup. These PDFs are reference sources, not a complete list of all materials used.

When the user asks what a textbook says about a knowledge point or asks for a page location:

- Inspect the relevant PDF content before answering.
- Cite the source with book name and page location. If available, distinguish book page numbers from PDF page numbers.
- If the content cannot be confirmed in the available PDFs, say so clearly. Do not fabricate textbook wording, page numbers, examples, or conclusions.
- Do not rely only on memory for textbook-specific claims.

When the user asks to organize a chapter during review:

- Read the corresponding chapter from the relevant PDF.
- Create or update one Markdown note per book under `DigitalBooks/BookNotes/`.
- Keep chapter notes organized by chapter headings inside the book-level Markdown file.
- Treat book notes as incremental review notes updated chapter by chapter during the user's strengthening-stage review, not as one-time full-book summaries.
- Preserve user-authored edits, deletions, and additions in book notes. Do not overwrite or normalize the whole file unless the user explicitly asks.
- When updating an existing chapter, merge new verified material into that chapter and keep the user's personal notes intact.
- Separate verified textbook content from the agent's own understanding or supplements.
- Include page references for textbook-derived definitions, formulas, key conclusions, examples, and common pitfalls when possible.
- Do not modify, rename, move, or delete source PDFs unless the user explicitly asks.

## Language

- Default to Chinese for study notes, summaries, and user-facing documents.
- Keep technical or file-management instructions concise and unambiguous.

## Verification

- After creating or editing files, confirm the exact path changed.
- For generated plans or summaries, check that the output is readable and organized before reporting completion.
