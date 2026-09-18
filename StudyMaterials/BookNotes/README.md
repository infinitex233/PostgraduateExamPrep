# Book Notes

English | [简体中文](README.zh-CN.md)

This directory contains rolling textbook notes grouped by subject family:

- `Math/`: Mathematics I textbook notes.
- `408/`: 408 Computer Science textbook notes.

Update one textbook note chapter by chapter. Preserve user annotations and ordering, and keep source materials separate from derived notes.

## Calculus Intensive Notes

- Note: [高数强化笔记.md](Math/高数强化笔记.md)
- Source textbook: `27武忠祥高数辅导讲义-强化`
- Source PDF: [27武忠祥高数辅导讲义-强化.pdf](../Library/Math/Intensive/27武忠祥高数辅导讲义-强化.pdf)
- Update order: follow the textbook chapter sequence and only organize chapters that have been studied and verified.
- Example policy: do not reproduce full example questions; extract reusable conclusions, methods, and common mistakes as knowledge points.
- Page references: use `printed book page / PDF page`. The PDF page is the actual page index shown by the reader.
- Content labels: `Textbook extract` identifies verified textbook knowledge; `Review note` identifies a problem-solving framework reorganized for revision.

## Content Layers

- Read the corresponding source pages before updating a chapter, and merge only verified material into the existing note.
- Keep primary textbook content in the normal document body. This includes definitions, theorems, standalone formulas, key conclusions, method trees, procedural steps, and checklists.
- Put supplemental derivations, proof ideas, detailed explanations, cautions, memory aids, and error analysis in Typora blockquotes. Prefix every explanatory paragraph with `>` and separate quoted paragraphs with a quoted blank line containing only `>`.
- Keep formulas inside supplemental blockquotes as `$...$` inline math. Split long derivations across quoted paragraphs; never use a `> $$` display-math delimiter.
- When editing a chapter, bring nearby supplemental explanations into this blockquote format without reformatting unrelated primary content.
- Prefer reusable frameworks, definitions, exam patterns, error traps, and useful entry points over reproducing the textbook.

## Emphasis Marks

- Use `**...**` bold for three things: named theorems, formulas, methods, and core concepts wherever they appear in prose (such as `**格林公式**`, `**洛必达法则**`); short lead-in labels at the start of a bullet or paragraph that end with a full-width colon, including numbered labels where the number is bolded together with the label (such as `**1. 换元积分法**：`); and recurring section labels such as 教材提炼, bolded consistently throughout the note.
- Use `==...==` highlight only for error-trap phrases inside caution blockquotes. Keep at most one highlight per leaf heading, and choose the phrase deliberately as a complete clause instead of applying it mechanically.
- Never place emphasis marks inside `$...$` inline math, `$$` display blocks, headings, or table rows. Keep each marker pair on a single line. Do not nest marks inside an existing bold span and avoid adjacent `****`.
- Emphasis marks are additive formatting only and never override the content-layer rules above: primary textbook content stays in the body, and supplemental explanation stays in blockquotes.

## Maintenance

- Keep the Typora `[TOC]` marker at the top of long notes instead of maintaining a duplicate manual outline.
- After the content of each leaf heading, keep three blank lines before the next heading, matching the reference note format. Do not append a blank paragraph after the final line of the file.
- Add page references for definitions, formulas, theorems, important conclusions, and common mistakes when possible.
- Update only the chapter currently under review. Preserve the user's additions, deletions, annotations, ordering, and personal wording, and merge around them instead of replacing the note wholesale.
- Apply the emphasis conventions above to new chapter content as it is written. Do not restyle existing unrelated chapters wholesale without an explicit request.
- Before finishing, check that math segments contain no `**` or `==`, that marker pairs are balanced, and that no `***` or `****` sequences were introduced.
