# CLAUDE.md

This file is the concise Claude Code entry point for this repository.

## No Subagents

- Never call or spawn subagents in this repository.
- Do not use the `Agent` or `Task` tools, agent teams, background agents, or worktree-isolated agents.
- Complete all exploration, planning, implementation, review, and verification directly in the main session, regardless of task complexity.
- Do not create `.claude/worktrees`. Planning may be done in the main session without delegation.

## Read First

`AGENTS.md` is the authoritative source for repository policy and overrides this file. Read it before changing files, followed by the relevant operational guide:

- `StudyProgress/README.md` for daily logs, reviews, progress indexes, and dashboard work
- `StudyMaterials/README.md` for the materials directory map and shared rules
- `StudyMaterials/Library/README.md` for textbook lookup, OCR caches, and English materials
- `StudyMaterials/BookNotes/README.md` for rolling textbook notes
- `StudyMaterials/MistakeBook/README.md` for subject-level mistake books

When the user asks what a textbook says, where a concept appears, or how a definition is stated, search `StudyMaterials/Library/Cache/**/*.docling.json` first with `scripts/query.py`. Open the source PDF when the cache is missing or ambiguous, or when exact wording, formulas, diagrams, examples, or printed page numbers matter.

## Repository Scope

This is a personal study-management workspace for China's 11408 postgraduate entrance examination: Politics, English I, Mathematics I, and 408 Computer Science. Most content is Markdown records, local study material, and generated review artifacts; executable code is limited to the utilities under `scripts/`. User-facing study content defaults to Chinese.

## Common Commands

```bash
# Regenerate the dashboard after progress-data changes
python scripts/build_dashboard.py

# Run dashboard regression tests after dashboard-code changes
python -m unittest scripts.test_build_dashboard scripts.test_build_dashboard_variants

# Search local textbook caches
python scripts/query.py "二叉树"
python scripts/query.py "二叉树" --book "数据结构"
python scripts/query.py "二叉树" --book "线代" --page-only
python scripts/query.py "二叉树" --book "高数" --context 2
python scripts/query.py --list-books

# Build or resume primary page-level OCR caches
python scripts/page_ocr.py "StudyMaterials/Library/Math/Intensive/某书.pdf"
python scripts/page_ocr.py --all
```

`scripts/docling_cache.py` is a legacy-compatible alternative cache builder, not the default workflow. Full OCR builds are expensive and should not be used as routine verification.

## Progress and Dashboard Architecture

Daily logs live at `StudyProgress/DailyLogs/YYYY-MM/YYYY-MM-DD.md` and follow `StudyProgress/DailyLogs/_template.md`.

- Structured daily metrics come only from YAML frontmatter. Never infer minutes or progress from prose; use `null` for values the user did not provide.
- Archive and monthly presentation also reads stable summaries in `StudyProgress/ProgressIndex.md` and optional files under `StudyProgress/Summaries/Monthly/`.
- `scripts/build_dashboard.py` is the compatibility entry point and daily-data aggregation layer.
- `scripts/build_dashboard_variants.py` performs archive enrichment, Capsule rendering, typography, color mapping, interaction, and stale-output cleanup.
- The only retained output is `StudyProgress/dashboard.html`. Do not hand-edit it as the source of truth or create parallel dashboard variants.

Canonical subject keys must remain unchanged:

`数学-高数`, `数学-线代`, `数学-概率`, `专业课-数据结构`, `专业课-组成原理`, `专业课-操作系统`, `专业课-计算机网络`, `英语`, `政治`.

Concrete subjects use `subject_colors`; aggregate groups use `group_colors` (`数学`, `专业课`, `英语`, `政治`, `其他`).

## Textbook Retrieval

`scripts/query.py` recursively reads categorized caches under `StudyMaterials/Library/Cache/` and supports both page-level JSON and legacy Docling JSON.

Cache matches identify candidate PDF pages only. For textbook-specific claims:

- Verify exact wording, formulas, diagrams, examples, and printed page numbers in the source PDF.
- Distinguish `书内印刷页码` from `PDF 页码`.
- State explicitly when either value cannot be confirmed.
- Never fabricate textbook content or page locations.

## Book Notes

Keep one rolling Markdown note per book under `StudyMaterials/BookNotes/`. Update only the chapter under review, merge incrementally, preserve the user's manual edits, separate verified textbook content from supplements, and retain page references where possible.

## Mistake Books

Keep one rolling Markdown mistake book per concrete subject under `StudyMaterials/MistakeBook/`. Use headings only for chapters, sections, and knowledge points. Each question remains body content with the question, answer, analysis, and a final source blockquote beginning with `> 来源：`. Follow `StudyMaterials/MistakeBook/README.md` for the full maintenance rules.

## Safety and Handoff

Follow `AGENTS.md` for full rules. In particular:

- Keep PDFs local and out of Git. Verified OCR caches may be committed.
- Preserve unrelated working-tree changes and stage explicit paths in mixed worktrees.
- Remove temporary inspection and Python cache artifacts after use.
- Run checks appropriate to the changed surface.
- Report exact changed paths and any verification that could not be completed.
