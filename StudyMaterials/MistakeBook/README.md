# Mistake Books

English | [简体中文](README.zh-CN.md)

This directory contains subject-level mistake books for questions encountered during study. Every recorded question comes from a textbook stored locally under `StudyMaterials/Library/`. Keep one rolling Markdown file for each concrete subject and append questions under the corresponding chapter or knowledge point.

## Directory Layout

```text
MistakeBook/
  README.md
  README.zh-CN.md
  Math/
    高等数学错题本.md
    线性代数错题本.md
    概率论与数理统计错题本.md
  408/
    数据结构错题本.md
    计算机组成原理错题本.md
    操作系统错题本.md
    计算机网络错题本.md
```

## Entry Format

Keep the Typora `[TOC]` marker at the top of every mistake book, followed by an H1 using the full subject name. Use headings only to organize chapters, sections, and knowledge points, numbered like the `BookNotes` files (for example `## 1. 函数极限连续`, `### 1.1 数列与函数极限`). A single question is normal document content and must not be added as a heading.

Use the following structure for each question:

```markdown
**1.1.1**

题目内容。

**答案**

最终答案。

**解析**

解题过程、关键步骤和必要说明。

> 来源：《教材完整名称》，对应章节，第 xx 题，书内第 xx 页 / PDF 第 xx 页。
```

Label questions sequentially within each section using the section number plus a running index: the first question under section 1.1 is `**1.1.1**`, the second is `**1.1.2**`. The label is bold body text, never a heading, and must not reuse the source book's question number — the original number is recorded only in the source blockquote. Place the source as the final paragraph of the entry and always format it as a Markdown blockquote beginning with `> 来源：`.

## Maintenance Rules

- Add each question under its corresponding chapter, section, or knowledge point. Create only the chapter hierarchy needed by recorded questions.
- Record only the question, answer, analysis, and source. Do not add YAML metadata, review schedules, mastery states, or links to daily study records.
- Preserve existing questions, personal annotations, ordering, and wording when updating a file. Append or merge around user-authored content instead of replacing it wholesale.
- Preserve the source order of conditions and choices. Keep formulas, symbols, tables, and diagrams accurate; use relative links when a local supporting image is genuinely required.
- Keep answers concise and put derivations, method explanations, and cautions in the analysis.
- Follow the repository's Typora-compatible mathematical notation rules. Display formulas use standalone `$$` delimiter lines and must not be placed in headings or blockquotes.
- Match the spacing style of `BookNotes`: leave three blank lines before the next heading after a populated leaf section, and leave three blank lines between adjacent questions in the same section. Do not append a blank paragraph after the final line.

## Source Verification

- Search the local OCR cache first with `scripts/query.py`, then inspect the source PDF when exact wording, formulas, diagrams, question numbers, or printed page numbers matter.
- Use the complete textbook name and record the chapter and question number when available.
- Distinguish `书内印刷页码` from `PDF 页码`. The PDF page is the actual page index shown by the reader or cache.
- If a source detail cannot be confirmed, write `未确认` instead of guessing.
- Do not rename, move, edit, or duplicate the local source PDFs while maintaining a mistake book.
