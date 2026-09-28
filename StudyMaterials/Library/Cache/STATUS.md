# OCR Cache Verification Status / OCR 缓存核验状态

These are dated verification records moved from the Library guide. Paths below
are relative to `StudyMaterials/Library/`. They describe the cache at the
recorded time; recheck a cache after it changes. Cache matches remain candidate
pages and do not replace source-PDF verification.

以下为从资料库指南移来的历史核验记录；下文路径均相对于 `StudyMaterials/Library/`。记录仅说明所列日期的缓存状态，缓存修改后须重新核验。缓存命中仍只定位候选页，不能代替源 PDF 核对。

## English

### Intensive Mathematics I — verified 2026-08-14

These caches were rebuilt with a vision-model transcription pipeline:

| Source PDF | Cache JSON | Page coverage |
| --- | --- | ---: |
| `27武忠祥《高等数学辅导讲义.严选题》.pdf` | `27武忠祥《高等数学辅导讲义.严选题》.docling.json` | 219 / 219 |
| `27武忠祥高数辅导讲义-强化.pdf` | `27武忠祥高数辅导讲义-强化.docling.json` | 315 / 315 |
| `27版李林880题《数一解析册》.pdf` | `27版李林880题《数一解析册》.docling.json` | 416 / 416 |
| `27线代杨《满分线性代数》强化讲义.pdf` | `27线代杨《满分线性代数》强化讲义.docling.json` | 318 / 318 |
| `【A4紧凑版】李林880数一线概篇做题本.pdf` | `【A4紧凑版】李林880数一线概篇做题本.docling.json` | 82 / 82 |
| `【A4紧凑版】李林880数一高数篇做题本.pdf` | `【A4紧凑版】李林880数一高数篇做题本.docling.json` | 98 / 98 |
| `张宇1000题_数一_试题册.pdf` | `张宇1000题_数一_试题册.docling.json` | 195 / 195 |
| `张宇100题_数一_解析册.pdf` | `张宇100题_数一_解析册.docling.json` | 568 / 568 |

The source PDFs are under `Math/Intensive/`, with caches under
`Cache/Math/Intensive/`. Nine pages have no transcribed text; visual inspection
confirmed each is blank, a back cover, or a text-free transition page. All PDF
pages are therefore covered. Formulas were transcribed as LaTeX with balanced
`$` / `$$` delimiters and no unresolved `[?]` markers.

### 线代杨强化讲义 — full visual re-verification 2026-09-26

`27线代杨《满分线性代数》强化讲义.docling.json` was re-verified page by page
against 180 dpi renders of all 318 PDF pages, in 12 parallel batches. 174 pages
needed corrections and were re-transcribed at high fidelity, with doubtful
regions re-checked at 300–900 dpi zooms. Coverage is unchanged at 318 / 318
pages; only PDF page 318 (blank back cover) has no text.

The main error classes fixed were: wrong or missing matrix entries and lost
matrix structure (diagonal / anti-diagonal / block matrices flattened to
column vectors); wrong digits, signs, subscripts, and exam-paper codes; wrong
or dropped Chinese characters; content invented by the earlier transcription
(whole hallucinated pages among the 思维导图 appendix, e.g. PDF pages 310–311);
missing boxes, captions, and branches in the mind-map appendix; and isolated
formatting breaks. Two pages had caches unrelated to the printed page and were
replaced wholesale.

Style conventions were kept as found: fullwidth punctuation inside math,
lone-`=` continuation lines in displays, `\tag{n}` for circled equation
numbers, letter `O` for the bold zero matrix, and `【例】【思路】【解】【评注】`
markers. The book's own printing typos were verified at high zoom and kept as
printed. Post-fix checks confirmed balanced `$` / `$$` delimiters, matched
`\begin` / `\end` environments, and no `[?]` or garbled markers.

### 王道2027计算机网络复习指导 — full visual re-verification 2026-09-27

`2027计算机网络_高清带书签版.docling.json` (RapidOCR cache) was re-verified page
by page against 180 dpi renders of all 316 PDF pages, in 12 parallel batches.
285 pages had transcription errors and were re-transcribed at high fidelity,
with doubtful regions re-checked at 450 dpi zooms. Coverage is unchanged at
316 / 316 pages; every page has text. Printed page numbering is
`书内印刷页码 + 12 = PDF 页码` for body pages; PDF pages 1–12 are front matter
(cover, 前言, 目录).

The main error classes fixed were: whole dropped lines and sentences (paragraph
openings, exam-question stems, and worked-answer steps); lost superscripts,
subscripts, and formula structure (now LaTeX with `$` / `$$`); figure interiors
flattened into label soup (restored as ordered legible labels plus a short
description); garbled tables and double-column option lists (rebuilt as
Markdown tables); and glyph confusions (顿→帧, O/0, l/1, rn→m English garble
such as intermet→internet, missing spaces in English terms, Roman-numeral soup,
stray page-furniture digits). The book's own printing oddities were verified at
high zoom and kept as printed (e.g. 奈式准则 PDF p.52, italic WRTT PDF p.119,
BPG路由1/2 PDF p.207, printed italic r PDF p.138). Post-fix checks confirmed
balanced `$` / `$$` delimiters, matched `\begin` / `\end` environments, no
`[?]` markers, and no diagnostic leftovers.

### 李林880线概篇做题本 — full visual re-verification 2026-09-28

`【A4紧凑版】李林880数一线概篇做题本.docling.json` (vision-transcribed cache) was
re-verified page by page against 180 dpi renders of all 82 PDF pages, with
doubtful regions re-checked at 360–576 dpi zooms. 78 of 82 pages changed; PDF
pages 1 (cover), 2 (目录), 19, and 80 needed no edit. Coverage is unchanged at
82 / 82 pages.

The main error classes fixed were: diagonal / staircase matrices flattened into
column vectors (PDF pages 31, 32, 38 — e.g. a diagonal `B` with entries
`b, b, c` transcribed as a full 2×2 matrix, `\Lambda` with entries `0, 1, -1`
as a 3×1 column vector); `\ddots` written into omitted-row cells the book
prints empty (pages 4–6, 35); invented content (added `^T` superscripts on
page 20, an extra "为" after `A\sim B` on page 31); dropped characters (page 15
仅, page 44 矩, page 74 着), a wrong character (page 67 检验→检测), a dropped
sample value (page 79), option labels transcribed as `(A)` where the book
prints `A.`, and single bars `|PX|^2` where the book prints the norm
`\|PX\|^2` (page 40). The book's own printing errata were verified at high
zoom and kept as printed (e.g. page 17's unclosed bracket, page 74's
"设 $(X_1,\ X_2,$ 则为总体").

Punctuation was normalized to the book's own convention: halfwidth sentence
periods `.`, halfwidth parentheses for item numbers, choice blanks, and option
labels, fullwidth commas between Chinese clauses — the earlier transcription
had mixed fullwidth `。` `（ ）` `．`. Post-fix checks confirmed balanced `$` /
`$$` delimiters, matched `\begin` / `\end` environments, no `[?]` markers, and
no leftover fullwidth periods or brackets.

### Basic Mathematics I — partial verification 2026-09-19

`27张宇基础30讲高数.docling.json` was partially rebuilt with vision
transcription. PDF pages 1–284 have high-fidelity LaTeX, including handwritten
margin notes, with formulas and `$` / `$$` delimiters verified. Pages 285–586
retain RapidOCR text and may have broken formulas; check those formulas against
the source PDF.

The caches for `27张宇基础30讲线代`, `27张宇基础30讲概率`, and the remaining
three 王道 408 books (数据结构, 操作系统, 计算机组成原理) remain unfixed;
`2027计算机网络` was fully re-verified on 2026-09-27. Body prose is mostly
usable, but figure regions and formulas may contain OCR errors.

### 408 Recitation Handbook — verified 2026-09-22

`27计算机网络背诵手册(公众号：里昂408考研）.docling.json` was rebuilt from
`408/27计算机网络背诵手册(公众号：里昂408考研）.pdf`, a 125-page scan of 192 ppi
page bitmaps without a text layer, using vision transcription. Coverage was
verified at 125 / 125 pages.

Printed headings, tables, formulas, footnotes, exam-question boxes, and figure
captions were transcribed as printed. Figure interiors record the legible labels
in order and a short description of visible content. Watermarks, QR codes, and
footer page numbers were omitted; continued tables were marked. Page numbering
is `书内印刷页码 + 5 = PDF 页码` (printed 20 = PDF 25). PDF pages 2–5 contain the
table of contents, and page 125 is the 艾宾浩斯遗忘曲线 appendix; neither has a
printed page number.

Per-position bit sequences in figures 图 2.3, 图 2.4, 图 3.3, and 图 3.12 are below
the source bitmap's resolution. Their figure blocks list only legible labels,
not digit-by-digit values.

## 简体中文

### 数学一强化缓存——2026-08-14 核验

以下缓存经视觉模型转写流程重建并校验：

| 源 PDF | 缓存 JSON | 页数覆盖 |
| --- | --- | ---: |
| `27武忠祥《高等数学辅导讲义.严选题》.pdf` | `27武忠祥《高等数学辅导讲义.严选题》.docling.json` | 219 / 219 |
| `27武忠祥高数辅导讲义-强化.pdf` | `27武忠祥高数辅导讲义-强化.docling.json` | 315 / 315 |
| `27版李林880题《数一解析册》.pdf` | `27版李林880题《数一解析册》.docling.json` | 416 / 416 |
| `27线代杨《满分线性代数》强化讲义.pdf` | `27线代杨《满分线性代数》强化讲义.docling.json` | 318 / 318 |
| `【A4紧凑版】李林880数一线概篇做题本.pdf` | `【A4紧凑版】李林880数一线概篇做题本.docling.json` | 82 / 82 |
| `【A4紧凑版】李林880数一高数篇做题本.pdf` | `【A4紧凑版】李林880数一高数篇做题本.docling.json` | 98 / 98 |
| `张宇1000题_数一_试题册.pdf` | `张宇1000题_数一_试题册.docling.json` | 195 / 195 |
| `张宇100题_数一_解析册.pdf` | `张宇100题_数一_解析册.docling.json` | 568 / 568 |

源 PDF 位于 `Math/Intensive/`，缓存位于 `Cache/Math/Intensive/`。共有 9 页没有转写文本；目视核验确认均为空白页、封底或无正文的过渡页，因此覆盖全部 PDF 页面。公式以 LaTeX 转写，`$` / `$$` 分隔符配平，没有未解决的 `[?]` 标记。

### 线代杨强化讲义——2026-09-26 全量目视复核

`27线代杨《满分线性代数》强化讲义.docling.json` 已按 180 dpi 渲染图对全部 318 页逐页复核（12 个并行批次）。其中 174 页存在转写错误，已按高保真重新转写，存疑区域再以 300–900 dpi 放大核对。页数覆盖不变，仍为 318 / 318；仅 PDF 第 318 页（空白封底）无文本。

修复的主要错误类型：矩阵条目错漏与矩阵结构丢失（对角、副对角、分块矩阵被压平成列向量）；数字、符号、下标与真题年份/卷种错漏；中文字错漏；早期转写凭空捏造的内容（思维导图附录中整页幻觉文本，如 PDF 第 310–311 页）；思维导图附录缺失的框、图注与分支；以及零散格式破坏。其中两页缓存与印刷页面完全无关，已整页替换。

转写约定保持原样：公式内全角标点、推导中单独成行的 `=` 续行、`\tag{n}` 对应圈码编号、粗体零矩阵记作字母 `O`、【例】【思路】【解】【评注】标记。原书自身的印刷错误经高倍放大确认后按原样保留。修复后校验确认 `$` / `$$` 分隔符配平、`\begin` / `\end` 环境配对、无 `[?]` 或乱码标记。

### 王道2027计算机网络复习指导——2026-09-27 全量目视复核

`2027计算机网络_高清带书签版.docling.json`（RapidOCR 缓存）已按 180 dpi 渲染图对全部 316 页逐页复核（12 个并行批次）。其中 285 页存在转写错误，已按高保真重新转写，存疑区域再以 450 dpi 放大核对。页数覆盖不变，仍为 316 / 316，每页均有文本。正文页码关系为 `书内印刷页码 + 12 = PDF 页码`；PDF 第 1–12 页为前置部分（封面、前言、目录）。

修复的主要错误类型：整行整句丢失（段落开头、题干、答案解析步骤）；上下标与公式结构丢失（现改为 LaTeX 的 `$` / `$$` 转写）；插图内部被压成标签堆（恢复为按序可辨标签＋简短说明）；表格与双栏选项排版混乱（重建为 Markdown 表格）；字形混淆（顿→帧、O/0、l/1、英文 rn→m 如 intermet→internet、英文术语丢空格、罗马数字乱码、页脚杂字）。原书自身的印刷特征经高倍放大确认后按原样保留（如 奈式准则 PDF 第52页、斜体 WRTT PDF 第119页、BPG路由1/2 PDF 第207页、印刷斜体 r PDF 第138页）。修复后校验确认 `$` / `$$` 分隔符配平、`\begin` / `\end` 环境配对、无 `[?]` 标记、无诊断残留。

### 李林880线概篇做题本——2026-09-28 全量目视复核

`【A4紧凑版】李林880数一线概篇做题本.docling.json`（视觉转写缓存）已按 180 dpi 渲染图对全部 82 页逐页复核，存疑区域再以 360–576 dpi 放大核对。82 页中 78 页有修改；PDF 第 1 页（封面）、第 2 页（目录）、第 19、80 页无需改动。页数覆盖不变，仍为 82 / 82。

修复的主要错误类型：对角/阶梯排版矩阵被压平成列向量（PDF 第 31、32、38 页，如对角元 `b, b, c` 的矩阵被写成满 2×2 矩阵、对角元 `0, 1, -1` 的 `\Lambda` 被写成 3×1 列向量）；省略行的空白格处多写 `\ddots`（第 4–6、35 页）；凭空添加的内容（第 20 页多加 `^T` 上标、第 31 页 `A\sim B` 后多出「为」字）；漏字（第 15 页「仅」、第 44 页「矩」、第 74 页「着」）、错字（第 67 页「检验」应为「检测」）、漏样本值（第 79 页）、选项标签 `(A)` 应为 `A.`；范数记号 `|PX|^2` 应为 `\|PX\|^2`（第 40 页）。原书自身的排印错误经高倍放大确认后按原样保留（如第 17 页未闭合括号、第 74 页「设 $(X_1,\ X_2,$ 则为总体」）。

标点统一为原书体例：句末半角句点 `.`、题号/选择空/选项标签用半角括号、中文子句间全角逗号——旧缓存混用了全角 `。` `（ ）` `．`。修复后校验确认 `$` / `$$` 分隔符配平、`\begin` / `\end` 环境配对、无 `[?]` 标记、无残留全角句号或括号。

### 数学一基础缓存——2026-09-19 部分核验

`27张宇基础30讲高数.docling.json` 部分换用视觉模型转写：PDF 第 1–284 页为高保真 LaTeX 转写，含手写旁注，公式与 `$` / `$$` 分隔符已经核验；第 285–586 页仍为 RapidOCR 文本，公式可能损坏，须对照源 PDF。

《27张宇基础30讲线代》《27张宇基础30讲概率》与王道 408 其余三本（数据结构、操作系统、计算机组成原理）的缓存尚未修复；《2027计算机网络》已于 2026-09-27 全量复核。正文文字基本可用，但插图区域和公式仍可能有 OCR 错误。

### 408 背诵手册——2026-09-22 核验

`27计算机网络背诵手册(公众号：里昂408考研）.docling.json` 经视觉转写流程从扫描版源 PDF `408/27计算机网络背诵手册(公众号：里昂408考研）.pdf` 重建，并核验覆盖 125 / 125 页。源 PDF 由 125 页 192 ppi 整页位图构成，没有文本层。

书上的标题、表格、公式、脚注、统考真题框与图注按原样转写。图内按顺序记录可辨认的标签，再附一段只陈述可见信息的说明。水印、二维码和页脚页码不转写；跨页表格标注续表。页码关系为 `书内印刷页码 + 5 = PDF 页码`（印刷 20 = PDF 25）；PDF 第 2–5 页为目录，第 125 页为「艾宾浩斯遗忘曲线」附录，两者均无印刷页码。

波形图与组帧图（图 2.3、图 2.4、图 3.3、图 3.12）的逐位比特序列低于源位图可分辨极限，图块只列出可辨认的标签，不提供逐位数值。
