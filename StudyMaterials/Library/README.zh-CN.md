# 学习资料库

[English](README.md) | 简体中文

本目录保存 11408 备考所需的本地教材、分类 OCR 缓存和英语一资料。顶层资料结构见 [StudyMaterials 说明](../README.zh-CN.md)，仓库级规则仍以 [AGENTS.md](../../AGENTS.md) 为准。

## 目录结构

```text
Library/
  README.md
  README.zh-CN.md
  408/                         # 本地 408 教材 PDF
  Math/
    Basic/                     # 数学一基础阶段 PDF
    Intensive/                 # 数学一强化阶段 PDF
  Cache/                       # 分类 OCR 缓存，可以由 Git 跟踪
    408/
    Math/
      Basic/
      Intensive/
  English/
    WritingTemplates/
      index.html               # Git 跟踪的浏览器版本
      index.pdf                # 本地生成的 PDF
```

## 版本控制规则

教材和生成的 PDF 可能体积较大或涉及版权。`StudyMaterials/` 下的所有 PDF 均只保存在本地，不得提交。`Cache/` 下经过校验的 OCR 缓存 JSON 属于派生数据，可以由 Git 跟踪。适合版本控制的英语复习成品，例如 `English/WritingTemplates/index.html`，也可以跟踪。

暂存缓存文件前，应确认文件完整、可读，且不包含临时或诊断内容。不得提交凭据、Cookie、浏览器配置、个人导出文件或机器专用诊断信息。

## 缓存布局与格式

缓存目录会镜像教材的科目、阶段和嵌套源目录。例如，`Math/Intensive/SetA/` 下的 PDF 会把缓存写入 `Cache/Math/Intensive/SetA/`。两个缓存构建器都使用 `scripts/cache_layout.py` 完成该映射。

主要逐页缓存格式为：

```json
{
  "book": "书名",
  "total_pages": 100,
  "pages": [
    {"page_no": 1, "text": "..."}
  ]
}
```

`scripts/query.py` 会递归读取 `StudyMaterials/Library/Cache/**/*.docling.json`。它同时兼容逐页格式和包含结构化 `texts` 条目的旧 Docling JSON，并优先使用分类副本而不是旧式扁平重复缓存。

## 查询缓存

解释器按根 README「运行环境」执行：Windows 直接用 `python`（或 `py -3`）；WSL/Linux 优先 `./.venv/bin/python`，否则 `python3`。

打开大型 PDF 前，先检索本地缓存：

```bash
python scripts/query.py "关键词"
python scripts/query.py "关键词" --book "数据结构"
python scripts/query.py "关键词" --book "线代" --page-only
python scripts/query.py "关键词" --book "高数" --context 2
python scripts/query.py --list-books
```

缓存未命中不能证明教材没有该内容。先尝试同义词、缩短关键词或拆分查询，再检查可能的 PDF 页；仍无法确认时，明确说明缓存未能证实。

## 生成缓存

默认使用 PyMuPDF + RapidOCR 逐页流程：

```bash
python scripts/page_ocr.py "StudyMaterials/Library/408/某书.pdf"
python scripts/page_ocr.py "StudyMaterials/Library/Math/Intensive/某书.pdf"
python scripts/page_ocr.py --all
```

构建器会递归发现 PDF，优先提取内嵌文本，对扫描页回退到 OCR，能够续跑未完成的 JSON 检查点，并跳过完整缓存。内嵌文本层会先做乱码检测（私有区字形、替换符、可读字符占比），损坏的文本层（如 `f(x)` 提取成 `f  x `）会被弃用并改用 OCR，避免污染缓存。

对扫描版数学书（公式密集、RapidOCR 会丢失积分号与分式结构），把问题页渲染成图片后直接阅读，重新转写为高保真文本。输出目录需先创建（例如 `mkdir -p tmp/vision-pages`）；渲染页属一次性产物，用后删除：

```bash
pdftoppm -f 161 -l 188 -r 180 -png "StudyMaterials/Library/408/某书.pdf" tmp/vision-pages/p
```

分批读取渲染出的页面图片，逐页转写为 LaTeX 公式的 Markdown，然后把该页范围合并回 `.docling.json` 缓存，保留 `total_pages` 与页级结构。只修复需要修复的页面，缓存其余部分保持不动。

`scripts/docling_cache.py` 是兼容旧缓存的替代流程，会生成 Docling JSON 和 Markdown。保留它是为了兼容已有缓存，但不要将其描述为默认流程。完整缓存构建可能处理数 GB 的本地 PDF，不应作为普通文档检查或提交前检查运行。

## 已核验的数学强化缓存

以下数学一强化阶段缓存已于 2026-08-14 用视觉模型转写流程重建并通过校验：

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

源文件位于 `Math/Intensive/`，对应缓存位于 `Cache/Math/Intensive/`。这些书共有 9 个页面没有转写文本；目视核验确认均为空白页、封底或无正文的过渡页，因此缓存仍覆盖全部 PDF 页面。公式以 LaTeX 转写，`$` / `$$` 分隔符全部配平，且无未解决的 `[?]` 标记。

## 部分核验的数学基础缓存

`27张宇基础30讲高数.docling.json` 已于 2026-09-19 部分换用视觉模型转写流程：PDF 第 1–284 页为高保真 LaTeX 转写（含手写旁注，公式、`$` / `$$` 分隔符均已核验）；第 285–586 页仍为 RapidOCR 原始文本，公式可能损坏。查询命中第 285 页及以后时，必须打开源 PDF 核对公式。

《27张宇基础30讲线代》《27张宇基础30讲概率》与 408 四本的缓存尚未修复，正文文字基本可用，但插图区域与公式仍可能有 OCR 错误。

## 证据与页码

OCR 缓存命中只定位候选 PDF 页。以下情况必须打开源 PDF 核对：

- 精确原文或直接引用
- 公式、符号、表格或图示
- 例题细节
- 书内印刷页码
- OCR 表述含糊的结论

教材特定回答应尽量标明书名和章节，并区分：

- `书内印刷页码`：教材页面上印刷的页码
- `PDF 页码`：PDF 阅读器和缓存中的实际页面序号

任一值无法确认时必须明确说明。不得编造教材原文、位置、例题、公式或结论。

## 英语资料

`English/` 保存英语一源资料和派生复习成品。当前作文模板输出为：

```text
English/WritingTemplates/
  index.html
  index.pdf
```

从截图或 PDF 转写时，应保持源文件顺序和有效学习内容，删除水印、平台界面、批改装饰、截图噪声和 OCR 调试信息。

若 `index.html` 更新且用户需要 PDF 版本，应重新生成 `index.pdf`，使两种格式保持一致。该 PDF 继续受仓库级忽略规则保护，只保存在本地。

## 清理与安全

- 未经明确要求，不重命名、移动、修改或删除源 PDF。
- 源资料与教材笔记、错题本分开保存。
- 使用后删除 PDF 渲染页、截图、OCR 诊断、PID 文件、临时服务和其他一次性产物。
- 源证据缺失或含糊时说明限制，不自行补全。
