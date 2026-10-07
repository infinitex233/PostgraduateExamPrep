# Book Notes

English | [简体中文](README.zh-CN.md)

This directory contains rolling textbook notes grouped by subject family:

- `Math/`: Mathematics I textbook notes.
- `408/`: 408 Computer Science textbook notes.

Update each textbook note in textbook chapter order, covering only chapters that have been studied and verified against the source. Preserve user annotations and ordering, and keep source materials separate from derived notes.

## Calculus Intensive Notes

- Note: [高数强化笔记.md](Math/高数强化笔记.md)
- Source textbook: `27武忠祥高数辅导讲义-强化`
- Source PDF: [27武忠祥高数辅导讲义-强化.pdf](../Library/Math/Intensive/27武忠祥高数辅导讲义-强化.pdf)
- Current coverage: Chapters 1-9, organized as concise knowledge and formula references without page annotations.

## Linear Algebra Intensive Notes

- Note: [线代强化笔记.md](Math/线代强化笔记.md)
- Source textbook: 27线代杨《满分线性代数》强化讲义
- Source PDF: [27线代杨《满分线性代数》强化讲义.pdf](../Library/Math/Intensive/27线代杨《满分线性代数》强化讲义.pdf)
- Current coverage: Chapters 1-6, organized as concise knowledge and formula references without page annotations.

## Probability and Statistics Intensive Notes

- Note: [概统强化笔记.md](Math/概统强化笔记.md)
- Source textbook: Fang Hao, Probability and Mathematical Statistics, Intensive Volume (2027 edition)
- Source PDF: [2027考研数学--概率统计就这点事-强化篇--方浩.pdf](../Library/Math/Intensive/2027考研数学--概率统计就这点事-强化篇--方浩.pdf)
- Current coverage: Chapters 1-8, organized as concise knowledge and formula references without page annotations.

## Content Layers

- Read the corresponding source pages before updating a chapter, and merge only verified material into the existing note.
- Read existing chapters in the target note before writing. Follow their knowledge-centered narrative, heading granularity, and layout. The user's latest requirements take precedence over existing style; do not reproduce older problems merely for consistency.
- Write notes that can be understood without the original exercise statements. Lead with concepts or methods, or state definitions and conclusions directly; a bold lead-in is optional, not required for every paragraph.
- Do not add editorial process labels such as `教材提炼` (textbook extract) or `复习提示` (review note), or explanations of such labels, to the body or chapter introduction. When a supplemental derivation or correction needs to be distinguished from the source, explain it in the relevant blockquote.
- Keep primary textbook content in the normal document body. This includes definitions, theorems, standalone formulas, key conclusions, method trees, procedural steps, and checklists.
- Put supplemental derivations, proof ideas, detailed explanations, cautions, memory aids, and error analysis in Typora blockquotes. Prefix every explanatory paragraph with `>` and separate quoted paragraphs with a quoted blank line containing only `>`.
- Keep formulas inside supplemental blockquotes as `$...$` inline math. Split long derivations across quoted paragraphs; never use a `> $$` display-math delimiter.
- When editing a chapter, bring nearby supplemental explanations into this blockquote format without reformatting unrelated primary content.
- Extract distinct methods, applicability conditions, reusable conclusions, and error traps from examples and exercises, then integrate them into the relevant knowledge topics. Do not organize the body with labels such as `例题结论` (example conclusions), `习题迁移` (exercise transfer), or problem numbers. Omit isolated numerical answers, option letters, and answers that require an omitted problem statement.
- When a concrete example is necessary to explain a method, put a short, self-contained illustration in a blockquote with the minimum conditions and reasoning needed to understand it. Do not copy full problem statements or create answer lists.
- Organize chapter sections by knowledge topic. Place cross-chapter connections, method selection, and self-check reminders beside the knowledge they support; merge repeated content instead of adding separate summary sections.
- Use concept or method names for meaningful short lead-ins when helpful. Add a heading only for a distinct knowledge topic; do not add table-of-contents levels merely to distinguish examples, exercises, or reminders. Supplemental explanations follow the blockquote rules above.

## Emphasis Marks

- Use `**...**` bold for named theorems, formulas, methods, and core concepts wherever they appear in prose, and for meaningful short lead-ins at the start of a bullet or paragraph. In Chinese notes, place the full-width colon outside the bold span and include any numbering inside it. Do not introduce recurring editorial labels just to apply bold formatting.
- Use `==...==` highlight only for error-trap phrases inside caution blockquotes. Keep at most one highlight per leaf heading, and choose the phrase deliberately as a complete clause instead of applying it mechanically.
- Never place emphasis marks inside `$...$` inline math, `$$` display blocks, headings, or table rows. Keep each marker pair on a single line. Do not nest marks inside an existing bold span and avoid adjacent `****`.
- Emphasis marks are additive formatting only and never override the content-layer rules above: primary textbook content stays in the body, and supplemental explanation stays in blockquotes.

## Maintenance

- Keep the Typora `[TOC]` marker at the top of long notes instead of maintaining a duplicate manual outline.
- After the content of each leaf heading, keep three blank lines before the next heading, matching the reference note format. Do not append a blank paragraph after the final line of the file.
- Cite definitions, formulas, theorems, important conclusions, and error traps where possible as `printed book page / PDF page`. The PDF page is the actual page index shown by the reader. Put example and exercise identifiers only in source blockquotes at the end of the relevant knowledge topic, together with the page references; never use them as headings, bold labels, or body item names.
- Check completeness by knowledge coverage: retain distinct knowledge, methods, formulas, applicability conditions, and necessary corrections, with their source references. Merge repeated methods and omit problem-specific numerical answers. Do not retain redundant content merely to cover every problem number. Renumber headings consecutively when merging sections.
- Update only the chapter currently under review. Preserve the user's additions, deletions, annotations, ordering, and personal wording, and merge around them instead of replacing the note wholesale.
- Apply the emphasis conventions above to new chapter content as it is written. Do not restyle existing unrelated chapters wholesale without an explicit request.
- Before finishing, check that math segments contain no `**` or `==`, that marker pairs are balanced, and that no `***` or `****` sequences were introduced.
- Review each topic for independent readability: no editorial process labels, problem-number-driven answer lists, or missing conditions. Confirm that source identifiers occur only in source blockquotes and that distinct knowledge has not been lost during consolidation.

## Writing Examples

Reject body entries such as `Exercise 9: the answer is a certain number` or `Textbook extract: definition ...`: the first gives an answer without reusable knowledge, and the second adds an editorial label instead of stating the knowledge directly.

The following illustrates direct knowledge, a useful explanation, and a source at the end. It is not a mandatory paragraph template; omit unnecessary explanations and replace source placeholders with verified references when writing actual notes.

**Trace and squared norm**: For a real column vector $\alpha$, $\operatorname{tr}(\alpha\alpha^{\mathrm T})=\alpha^{\mathrm T}\alpha=\|\alpha\|^2$.

> The diagonal entries of the outer product are the squares of the vector's components; adding them gives its squared norm.
>
> Source: verified printed book page / PDF page; relevant exercise identifier.
