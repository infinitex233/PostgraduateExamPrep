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

For Codex desktop chat replies, use `\(...\)` for inline math and `$$`
display blocks. Put each `$$` delimiter on its own line with blank lines
around the block; do not use `$...$` for inline math in desktop chat.

The following rules apply to CLI-facing Markdown and repository Markdown:

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
otherwise `python3`, then `python`. On native Windows, use system Python:
prefer `python`, then `py -3`. Do not use or create a repository virtual
environment on Windows. Verify that the selected interpreter is Python 3
before use. On POSIX, do not create, delete, recreate, copy, upgrade, or
install a virtual environment merely because it is absent; perform environment
maintenance only when the task requires missing dependencies or the user
explicitly requests it.

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
  explicit paths after inspecting the staged diff. The sole exception is
  study-report logging, which must be committed and pushed automatically per
  the Study progress workflow.
- Do not use destructive Git commands such as `git reset --hard` or
  `git checkout --` unless explicitly requested.
- At the end of a task, remove only temporary files and directories created
  by that task, including rendered PDF pages, OCR diagnostics, PID files,
  screenshots, and Python caches; stop temporary services started for the
  task. Preserve pre-existing contents of `tmp/` and other temporary
  directories.

## Workflow routing

### Study progress

Treat a natural-language daily study report as a logging request unless the
user clearly asks only to discuss it. Follow `StudyProgress/README.md` and its
template for the data rules, dashboard build, and checks. Every study-report
logging run must pass the regression suite, then commit its changes and push
them to the remote as specified in that guide. Never push with failing tests;
report a push failure.

### Textbook lookup and library materials

Follow `StudyMaterials/Library/README.md` for cache-first lookup, source-PDF
verification, page citations, and OCR maintenance. Cache matches are candidate
pages; never fabricate textbook content or locations.

### Book notes

Follow `StudyMaterials/BookNotes/README.md` for chapter-scoped, source-verified
updates to each textbook's rolling note.

### Mistake books

Follow `StudyMaterials/MistakeBook/README.md` for the subject files, question
format, and source citations.

### English materials

Follow the English-materials section of `StudyMaterials/Library/README.md`.

## Verification and handoff

Run checks proportional to the changed surface. Confirm generated files are
readable and organized, verify README language links and referenced paths,
and remove Python caches created by this task after Python checks. Report
checks that could not be run and list the exact changed paths in the handoff.
