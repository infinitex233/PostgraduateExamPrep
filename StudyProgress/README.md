# StudyProgress

English | [简体中文](README.zh-CN.md)

This directory is the long-term progress record for the 11408 postgraduate entrance examination. Short natural-language reports become consistent Markdown logs that can support daily review, stage analysis, and a complete retrospective of the preparation process.

## Scope

Records cover Politics, English I, Mathematics I (calculus, linear algebra, probability), and 408 Computer Science (data structures, computer organization, operating systems, computer networks).

For repository-wide policy, read `../AGENTS.md` first. This guide owns the operational details for progress records and the dashboard.

## Directory Layout

```text
StudyProgress/
  README.md
  README.zh-CN.md
  ProgressIndex.md             # Long-term route and archive summaries
  Roadmap.md                   # Goals and stage planning
  dashboard.html               # Generated Capsule dashboard
  DailyLogs/
    _template.md               # Canonical frontmatter and log structure
    YYYY-MM/
      YYYY-MM-DD.md
    Monthly/                   # Optional monthly subject summaries
  Reviews/
    Weekly/
      _template.md
      YYYY-Www.md
    Stage/
      _template.md
```

## Daily Logging Workflow

A natural-language daily report is treated as a logging request unless the user explicitly asks only to discuss it.

For each report:

1. Create or update `DailyLogs/YYYY-MM/YYYY-MM-DD.md`.
2. Follow `DailyLogs/_template.md` and preserve the YAML frontmatter at the top.
3. Preserve the user's original report verbatim in the designated section.
4. Record only supported facts: completed work, stated time or quantity, current state, problems, and next actions.
5. Use integer minutes and the canonical subject names below. Use `null` for unknown structured values and `未说明` for unknown narrative fields.
6. Never invent durations, task counts, chapter status, completion, mood, or plans.
7. Add a concise row or update to `ProgressIndex.md`.
8. Run `python scripts/build_dashboard.py` to regenerate `dashboard.html`.

Example report:

```text
今天数学做了高数第三章 40 道题，错了 9 道；英语背了 100 个单词，阅读 1 篇；专业课看了栈和队列，整理了半小时笔记。政治没学。状态一般，数学错题还没复盘。
```

The resulting record should remain concise: overview, original report, subject details, review, and next priorities.

## Frontmatter Contract

Structured daily metrics are read only from the YAML frontmatter in `DailyLogs/`; prose is never mined for exact minutes or progress state.

Canonical subject keys must remain unchanged because aggregation and dashboard color maps depend on them:

- `数学-高数`
- `数学-线代`
- `数学-概率`
- `专业课-数据结构`
- `专业课-组成原理`
- `专业课-操作系统`
- `专业课-计算机网络`
- `英语`
- `政治`

Do not replace an unknown value with zero. Zero means the user explicitly reported no study for that subject; `null` means the value was not provided.

## Indexes and Reviews

- `ProgressIndex.md` is the long-term route and historical overview. Keep its monthly overview and stage-observation structure stable because the dashboard reads those sections for archive presentation.
- `Roadmap.md` stores goals and stage planning rather than daily facts.
- `Reviews/Weekly/` and `Reviews/Stage/` are maintained when a weekly or stage review is requested; they do not need daily updates.
- `DailyLogs/Monthly/` may provide monthly per-subject summaries used by archive cards.

The system's primary goal is reliable recording and review. Experience-post material can be derived later from accumulated records.

## Dashboard Data Flow

The generated dashboard uses two layers of data:

1. Daily and current structured metrics come from `DailyLogs/**/YYYY-MM-DD.md` frontmatter only.
2. Archive and monthly presentation also reads stable summaries in `ProgressIndex.md` and optional files under `DailyLogs/Monthly/`.

The build path is:

```text
DailyLogs frontmatter + archive summaries
  -> scripts/build_dashboard.py
  -> scripts/build_dashboard_variants.py
  -> StudyProgress/dashboard.html
```

`scripts/build_dashboard.py` is the compatibility entry point and aggregation layer. `scripts/build_dashboard_variants.py` handles archive enrichment, the fixed 1920 x 1080 Capsule layout, typography, color maps, interaction, and stale-output cleanup.

## Build and Test

Regenerate the dashboard after any daily-log, progress-index, monthly-summary, or dashboard-code change:

```bash
python scripts/build_dashboard.py
```

After changing dashboard code, run the regression suite first:

```bash
python -m unittest scripts.test_build_dashboard scripts.test_build_dashboard_variants
python scripts/build_dashboard.py
```

Inspect the generated HTML after visual or interaction changes.

## Generated-File Policy

- `dashboard.html` is the only retained dashboard artifact.
- Do not hand-edit generated HTML as the source of truth.
- Do not create or retain parallel variants such as `dashboard_capsule*.html`, `dashboard_signal.html`, or `DashboardTemplatePreviews.html`.
- Use `subject_colors` for concrete subjects and `group_colors` for aggregate groups. A subject must keep the same color across charts, legends, totals, and progress indicators.
- Keep the fixed page sequence and interaction behavior unless the user explicitly requests a structural redesign.

## Record Integrity

- Prefer a sustainable concise record over an embellished one.
- Preserve the user's wording and manual edits.
- Separate unknown information from explicit zero values.
- Keep daily records under `StudyProgress/`; do not modify `StudyMaterials/` during a progress-only task.
- Report any missing evidence instead of inferring it.
