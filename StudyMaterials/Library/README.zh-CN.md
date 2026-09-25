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
    STATUS.md                  # 带日期的核验记录
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

源 PDF 与 Git 安全规则见 [AGENTS.md](../../AGENTS.md)。`Cache/` 下经过完整性、可读性和诊断内容检查的 OCR 缓存 JSON 属于可跟踪的派生数据。适合版本控制的英语复习成品，例如 `English/WritingTemplates/index.html`，也可以跟踪。

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

以下命令使用根 README [「运行环境」](../../README.zh-CN.md#运行环境) 中选定的解释器执行。

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

对扫描版数学书（公式密集、RapidOCR 会丢失积分号与分式结构），把问题页渲染成图片后直接阅读，重新转写为高保真文本。输出目录需先创建（例如 `mkdir -p tmp/vision-pages`）；完成后只删除本次任务生成的渲染页：

```bash
pdftoppm -f 161 -l 188 -r 180 -png "StudyMaterials/Library/408/某书.pdf" tmp/vision-pages/p
```

分批读取渲染出的页面图片，逐页转写为 LaTeX 公式的 Markdown，然后把该页范围合并回 `.docling.json` 缓存，保留 `total_pages` 与页级结构。只修复需要修复的页面，缓存其余部分保持不动。

`scripts/docling_cache.py` 是兼容旧缓存的替代流程，会生成 Docling JSON 和 Markdown。保留它是为了兼容已有缓存，但不要将其描述为默认流程。完整缓存构建可能处理数 GB 的本地 PDF，不应作为普通文档检查或提交前检查运行。

## 缓存核验记录

逐本缓存的历史覆盖率与已知 OCR 限制见双语[缓存状态记录](Cache/STATUS.md)。缓存修改后须重新核验；该记录不能代替下述源 PDF 证据规则。

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

使用后只清理本次任务生成的 PDF 渲染页、截图、OCR 诊断、PID 文件和其他临时产物，保留原有临时文件。源资料和证据规则见 [AGENTS.md](../../AGENTS.md)。
