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

### Basic Mathematics I — partial verification 2026-09-19

`27张宇基础30讲高数.docling.json` was partially rebuilt with vision
transcription. PDF pages 1–284 have high-fidelity LaTeX, including handwritten
margin notes, with formulas and `$` / `$$` delimiters verified. Pages 285–586
retain RapidOCR text and may have broken formulas; check those formulas against
the source PDF.

The caches for `27张宇基础30讲线代`, `27张宇基础30讲概率`, and the four 王道 408 books
remain unfixed. Body prose is mostly usable, but figure regions and formulas
may contain OCR errors.

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

### 数学一基础缓存——2026-09-19 部分核验

`27张宇基础30讲高数.docling.json` 部分换用视觉模型转写：PDF 第 1–284 页为高保真 LaTeX 转写，含手写旁注，公式与 `$` / `$$` 分隔符已经核验；第 285–586 页仍为 RapidOCR 文本，公式可能损坏，须对照源 PDF。

《27张宇基础30讲线代》《27张宇基础30讲概率》与王道 408 四本的缓存尚未修复。正文文字基本可用，但插图区域和公式仍可能有 OCR 错误。

### 408 背诵手册——2026-09-22 核验

`27计算机网络背诵手册(公众号：里昂408考研）.docling.json` 经视觉转写流程从扫描版源 PDF `408/27计算机网络背诵手册(公众号：里昂408考研）.pdf` 重建，并核验覆盖 125 / 125 页。源 PDF 由 125 页 192 ppi 整页位图构成，没有文本层。

书上的标题、表格、公式、脚注、统考真题框与图注按原样转写。图内按顺序记录可辨认的标签，再附一段只陈述可见信息的说明。水印、二维码和页脚页码不转写；跨页表格标注续表。页码关系为 `书内印刷页码 + 5 = PDF 页码`（印刷 20 = PDF 25）；PDF 第 2–5 页为目录，第 125 页为「艾宾浩斯遗忘曲线」附录，两者均无印刷页码。

波形图与组帧图（图 2.3、图 2.4、图 3.3、图 3.12）的逐位比特序列低于源位图可分辨极限，图块只列出可辨认的标签，不提供逐位数值。
