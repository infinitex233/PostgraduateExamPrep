# StudyMaterials

[English](README.md) | 简体中文

本目录保存 11408 备考中需要反复检索的重点教材、本地 OCR 缓存、滚动更新的教材笔记和英语资料。它是精选的工作资料库，不是所有备考资源的完整归档。

仓库级规则以 `../AGENTS.md` 为准。本文件负责教材检索、缓存生成、证据核对、教材笔记和英语成品的具体操作规则。

## 版本控制规则

教材 PDF 体积较大且可能涉及版权，只保存在本地对应目录，不得提交。`Cache/` 下通过校验的 OCR 缓存属于派生数据，可以提交，使本地教材检索无需完整重建缓存。

Git 还可以跟踪脚本、Markdown 笔记、说明文档，以及适合版本控制的复习成品，例如英语作文模板的 HTML 版本。

## 目录结构

```text
StudyMaterials/
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
  BookNotes/                   # 每本教材一份滚动 Markdown 笔记
  English/
    WritingTemplates/
      index.html               # Git 跟踪的浏览器版本
      index.pdf                # 本地生成的 PDF
```

缓存分类会保留源文件分类及其嵌套父目录。例如，`Math/Intensive/SetA/` 下的 PDF 会把缓存写入 `Cache/Math/Intensive/SetA/`。两个缓存构建器共用 `scripts/cache_layout.py` 完成该映射。

## 缓存格式

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

`scripts/query.py` 会递归读取 `StudyMaterials/Cache/**/*.docling.json`，同时兼容上述格式和包含结构化 `texts` 条目的旧 Docling JSON。

## 查询缓存

当用户询问教材如何表述、某知识点在哪里或定义是什么时，先检索本地缓存：

```bash
python scripts/query.py "关键词"
python scripts/query.py "关键词" --book "数据结构"
python scripts/query.py "关键词" --book "线代" --page-only
python scripts/query.py "关键词" --book "高数" --context 2
python scripts/query.py --list-books
```

缓存未命中不能证明教材没有该内容。先尝试同义词、缩短关键词或拆分查询，再检查可能的 PDF 页；仍无法确认时，明确说明当前缓存未能证实。

## 生成缓存

默认使用 PyMuPDF + RapidOCR 逐页流程：

```bash
python scripts/page_ocr.py "StudyMaterials/408/某书.pdf"
python scripts/page_ocr.py "StudyMaterials/Math/Intensive/某书.pdf"
python scripts/page_ocr.py --all
```

该脚本递归发现 PDF，优先提取内嵌文本，对扫描页回退到 OCR，能够续跑未完成的 JSON 检查点，并跳过完整缓存。

`scripts/docling_cache.py` 是兼容旧缓存的替代流程，会同时生成 Docling JSON 和 Markdown。保留它是为了兼容已有缓存，但不要将其描述为默认的逐页工作流。

完整缓存构建可能处理数 GB 的本地 PDF，不应作为普通文档检查或提交前检查运行。

## 当前数学强化缓存

以下数学一强化阶段本地新增资料已于 2026-07-13 完成缓存并通过校验：

| 源 PDF | 缓存 JSON | 页数覆盖 |
| --- | --- | ---: |
| `27版李林880题《数一解析册》.pdf` | `27版李林880题《数一解析册》.docling.json` | 416 / 416 |
| `张宇100题_数一_解析册.pdf` | `张宇100题_数一_解析册.docling.json` | 568 / 568 |
| `张宇1000题_数一_试题册.pdf` | `张宇1000题_数一_试题册.docling.json` | 195 / 195 |

源文件位于 `Math/Intensive/`，对应缓存位于 `Cache/Math/Intensive/`。前两本书共有 6 个页面没有 OCR 文本；目视核验确认它们是空白页或无正文的过渡页，因此缓存仍完整覆盖全部 PDF 页面。PDF 仍仅保存在本地，通过校验的缓存 JSON 可以提交。

## 证据与页码

OCR 缓存命中只定位候选 **PDF 页**，不是最终证据。

以下情况必须打开源 PDF 核对：

- 精确原文或直接引用
- 公式、符号、表格或图示
- 例题细节
- 书内印刷页码
- OCR 表述含糊的结论

教材特定回答应尽量标明书名和章节，并区分：

- `书内印刷页码`：教材页面上印刷的页码
- `PDF 页码`：PDF 阅读器和缓存中的页面序号

任一页码无法确认时必须明确说明。不得凭记忆编造教材原文、页码、例题、公式或结论。

## 逐章教材笔记

`BookNotes/` 中每本教材维护一份滚动 Markdown 笔记。笔记在复习过程中按章节更新，不一次性总结整本书。

用户请求整理某章时：

1. 定位对应源 PDF 和相关页面。
2. 打开或创建 `BookNotes/<书名>.md`。
3. 只更新当前复习的章节。
4. 对已有章节增量合并已核实内容，不整章覆盖。
5. 保留用户的增删、排序、标注和个人表述。
6. 将已核实的教材内容与解释或补充分开。
7. 对定义、公式、定理、例题、关键结论和易错点尽量保留页码。

优先整理知识框架、关键定义、常考题型、易错点和解题入口。笔记服务于复习，不复刻教材全文。

## 英语资料

`English/` 保存英语一源资料和派生复习成品。当前作文模板输出为：

```text
English/WritingTemplates/
  index.html
  index.pdf
```

从截图或 PDF 转写时，应保持源文件顺序和有效学习内容，删除水印、平台界面、批改装饰、截图噪声和 OCR 调试信息。

若 `WritingTemplates/index.html` 更新且用户需要 PDF 版本，应重新生成 `WritingTemplates/index.pdf` 以保持两种格式一致。由于 `StudyMaterials/` 下所有 PDF 都被忽略，该 PDF 仅保存在本地。

## 清理与安全

- 未经用户明确要求，不重命名、移动或删除源 PDF。
- 源资料与派生笔记分开保存。
- 不提交 PDF。缓存文件在确认结构、完整性和内容后可以提交。
- 使用后删除 PDF 渲染页、截图、OCR 诊断、临时服务、PID 文件和其他一次性产物。
- 源证据缺失或含糊时说明限制，不自行补全。
