# AGENTS.md

## Scope and authority

These rules apply to the whole repository. Workspace files are the source of
truth; do not rely on conversation memory when the repository can answer the
question. `AGENTS.md` is the repository-wide policy. Do not edit it unless the
user asks to change the workflow.

The workspace supports the 11408 postgraduate entrance examination:

- Politics
- English I
- Mathematics I: calculus, linear algebra, probability, and statistics
- 408 Computer Science: data structures, computer organization, operating
  systems, and computer networks

## Read before editing

1. Read this file and the root `README.md`.
2. For progress work, read `StudyProgress/README.md` and inspect the target
   records.
3. For materials work, read `StudyMaterials/README.md`, then the guide that
   owns the target:
   - `StudyMaterials/Library/README.md` for textbooks, OCR caches, or English
     materials;
   - `StudyMaterials/BookNotes/README.md` for textbook notes;
   - `StudyMaterials/MistakeBook/README.md` for mistake books.
   Inspect the relevant source files before editing.
4. Run `git status --short` before editing. Preserve unrelated worktree
   changes, do not revert or rewrite them, and work with overlapping changes.
5. Preserve user-authored notes, logs, templates, plans, and source materials.
   If evidence is incomplete, report the gap instead of inventing details.

The relevant guide is mandatory: this file supplies global constraints, while
the guide supplies the directory-specific procedure and format.

## Repository boundaries

- `StudyProgress/` contains logs, indexes, plans, reviews, imports, summaries,
  and the generated dashboard.
- `StudyMaterials/Library/` contains local textbooks, categorized OCR caches,
  and English materials.
- `StudyMaterials/BookNotes/` contains one rolling note per textbook.
- `StudyMaterials/MistakeBook/` contains one rolling mistake book per concrete
  subject.
- `scripts/` contains lookup, cache, dashboard, test, and maintenance tools.

Keep daily logs under `StudyProgress/`. Keep PDFs, textbook-derived notes,
OCR caches, and English materials under `StudyMaterials/`. Keep source
materials separate from derived notes.

## Global documentation rules

Every repository README has an English `README.md` and a Simplified Chinese
`README.zh-CN.md`. Each pair must link to its counterpart at the top, use
relative links, and be updated together. Agent instruction files remain in
English. Chinese may be used for canonical subject names and literal schema
values required by code.

## Typora and mathematical notation

These rules apply to CLI-facing Markdown and repository Markdown:

- Use `$...$` for inline math and `$$` display blocks. Display delimiters must
  be on separate lines with blank lines around the block.
- A display delimiter line must contain exactly `$$`. Never put a heading, list
  marker, blockquote marker, equation, or other content on that line. Never put
  display math in a fenced code block.
- Use Markdown headings for descriptive sections, with a space after `#`.
  Inline math is allowed in a descriptive heading, but a standalone formula
  must never be a heading.
- Keep one logical equation or short derivation per display block. Use an
  `aligned` environment with explicit `&=` for multi-line derivations, and
  keep each relation operator on the same source line as its expression.
- Use `\ ` for explicit spacing. Never emit a backslash followed by a comma.
  Do not leave `=`, `<`, `>`, `\leq`, or `\geq` alone on a line inside a math
  block.
- Use `\frac` in inline math; avoid inline `\dfrac`. Put large fractions in a
  display block.
- Before finishing math-heavy output, check for heading lines containing `$$`,
  display delimiters sharing a line with other content, backslash-comma
  spacing, and relation operators on lines by themselves. Rewrite any match.

## Python environment

Use the interpreter for the current operating system explicitly on every
agent-run command. On POSIX, prefer `./.venv/bin/python` when it exists,
otherwise `python3`, then `python`. On native Windows, prefer
`.\\.venv\\Scripts\\python.exe`, then `py -3`, then `python`. Verify that the
selected interpreter is Python 3 before use. Do not create, delete, recreate,
copy, upgrade, or install a virtual environment merely because it is absent;
perform environment maintenance only when the task requires missing
dependencies or the user explicitly requests it.

Before OCR or document processing, verify that the selected interpreter has
the required third-party packages. Standard-library-only checks may use any
compatible Python 3 interpreter.

## File and Git safety

- Do not rename, move, edit, or delete source materials, including PDFs,
  unless the user explicitly requests it. Do not place daily logs in
  `StudyMaterials/`.
- Preserve existing notes, logs, plans, templates, and manual edits. Merge
  around user content instead of replacing it wholesale.
- PDFs below `StudyMaterials/` are local-only and must never be committed.
  Verified OCR cache JSON under `StudyMaterials/Library/Cache/` may be staged
  after checking completeness, readability, and absence of diagnostics.
- Never commit credentials, tokens, cookies, browser profiles, personal
  exports, or machine-specific diagnostics.
- Do not commit or push unless the user asks. In a mixed worktree, stage only
  explicit paths after inspecting the staged diff.
- Do not use destructive Git commands such as `git reset --hard` or
  `git checkout --` unless explicitly requested.
- At the end of a task, remove `tmp/`, `__pycache__/`, `.pytest_cache/`,
  rendered PDF pages, OCR diagnostics, PID files, screenshots, and other
  one-off artifacts, including empty temporary directories.

## Workflow routing

### Study progress

Treat a natural-language daily study report as a logging request unless the
user clearly asks only to discuss it. Follow `StudyProgress/README.md` and its
template. Preserve the original report, record only supported facts, use
integer minutes and canonical subject names, use `null` for unknown structured
values, update `ProgressIndex.md`, and regenerate `dashboard.html` with
`python scripts/build_dashboard.py`. Never infer duration, task counts,
chapter status, completion, mood, or plans from prose.

`dashboard.html` is generated output, not the source of truth. Do not hand-edit
it as the only source, create parallel dashboard variants, or change dashboard
schema keys, colors, layout, or interaction behavior without an explicit
request. Run the regression tests and rebuild after dashboard-code changes.

### Textbook lookup and library materials

Follow `StudyMaterials/Library/README.md`. Search the local cache with
`scripts/query.py` before opening a large PDF. Cache matches are candidate
pages only: inspect the source PDF for exact wording, formulas, diagrams,
examples, or ambiguous OCR. When reporting a location, distinguish both
`书内印刷页码` and `PDF 页码`; state when either cannot be confirmed. Never
fabricate textbook content, locations, examples, formulas, or conclusions.

Use `scripts/page_ocr.py` as the primary cache builder and
`scripts/docling_cache.py` only as the legacy-compatible alternative. Both
must use the source-relative layout defined by `scripts/cache_layout.py`.

### Book notes

Follow `StudyMaterials/BookNotes/README.md`. Maintain one rolling Markdown
note per textbook, update only the chapter under review, read the source pages,
and preserve the user's additions, deletions, ordering, annotations, and
wording. Keep verified textbook content separate from supplemental explanation
and retain page references where possible.

### Mistake books

Follow `StudyMaterials/MistakeBook/README.md`. Maintain one Markdown file per
concrete subject, with the full subject name, a Typora `[TOC]`, and headings
only for chapters, sections, and knowledge points. Each question stays in
normal body content and contains only the question, answer, analysis, and a
final source blockquote beginning with `> 来源：`. Preserve existing entries;
do not add review schedules, mastery states, YAML metadata, or daily-log links.

### English materials

Keep English sources and derived review artifacts under
`StudyMaterials/Library/English/` and follow the Library guide. Preserve source
order when transcribing material and omit watermarks, platform chrome,
screenshot noise, and OCR diagnostics. If `English/WritingTemplates/index.html`
changes and the user requests a PDF, regenerate the matching `index.pdf`.

## Verification and handoff

Run checks proportional to the changed surface. Confirm generated files are
readable and organized, verify README language links and referenced paths,
and remove Python caches after Python checks. Report checks that could not be
run and list the exact changed paths in the handoff.
