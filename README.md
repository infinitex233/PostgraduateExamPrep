# PostgraduateExamPrep

11408 考研备考仓库，用来管理重点教材索引、每日学习记录、阶段复盘和强化阶段的教材笔记。

考试科目：政治、英语一、数学一、408 计算机学科专业基础综合（数据结构、组成原理、操作系统、计算机网络）。

仓库的目标很简单：把备考过程留下来。每天用自然语言汇报学习情况，由 agent 整理成结构化记录；复习到某一章时，再把这一章的知识点整理进对应书籍的 Markdown 笔记。考后复盘路线或整理经验帖，都可以从这些记录回看。

教材 PDF 体积大、且涉及版权，默认不提交到 GitHub。PDF 放在本地 `StudyMaterials/` 对应目录，agent 本地工作时再读取。

## 目录结构

```text
PostgraduateExamPrep/
  AGENTS.md                 # 给 agent 的全局规则
  README.md                 # 仓库说明
  scripts/                  # 工具脚本（教材检索、看板生成等）
    query.py                # 检索 StudyMaterials/Cache/ 下的逐页 OCR 缓存
    page_ocr.py             # 为教材 PDF 建立逐页 OCR 缓存
    docling_cache.py        # 旧版 Docling 缓存脚本，非当前主流程
    build_dashboard.py      # 根据 DailyLogs frontmatter 生成学习看板
  StudyProgress/            # 学习进度、路线规划、复盘
    README.md
    ProgressIndex.md        # 备考路线总览
    Roadmap.md              # 阶段规划和策略调整
    dashboard.html          # 学习看板（由 build_dashboard.py 生成）
    DailyLogs/              # 每日学习记录（带 frontmatter）
    Reviews/                # 周复盘和阶段复盘
  StudyMaterials/           # 本地教材目录和教材笔记
    README.md
    408/                    # 专业课教材
    Math/                   # 数学教材
    Cache/                  # 教材逐页 OCR 缓存（*.docling.json）
    English/                # 英语资料
      WritingTemplates/     # 英语作文模板成品
        index.html          # 16:9 浏览器版作文模板
        index.pdf           # 同内容 PDF 版
    BookNotes/              # 每本书一个 md，逐章滚动更新
```

## 使用方式

### 每日学习记录

每天可以直接用自然语言汇报，例如：

```text
今天数学做了高数第三章 40 道题，错了 9 道；英语背了 100 个单词，阅读 1 篇；专业课看了栈和队列，整理了半小时笔记。政治没学。状态一般，数学错题还没复盘。
```

agent 会把它整理到：

```text
StudyProgress/DailyLogs/YYYY-MM/YYYY-MM-DD.md
```

同时更新：

```text
StudyProgress/ProgressIndex.md
```

每日记录保留原始汇报，也会整理出今日概览、分科记录、问题与调整、明日优先级。每篇日志顶部带一段 YAML frontmatter，记录日期、各科时长（分钟）、章节进度等结构化字段，供看板解析。用户没有提供的数据写 `未说明`（frontmatter 里写 `null`），不自行补全。

### 学习看板

每日数据可以一键生成可视化看板：

```bash
python scripts/build_dashboard.py
```

它扫描所有日志的 frontmatter，生成 `StudyProgress/dashboard.html`——零依赖单文件，双击即可在浏览器打开，含每日时长趋势、各科进度追踪和关键节点时间线。新增或修改日志后重新运行即可刷新。

看板的视觉样式和科目配色统一维护在 `scripts/build_dashboard.py` 中，`StudyProgress/dashboard.html` 是生成结果。调整主题、`subject_colors`、`group_colors`、强调文字颜色或图表细节时，优先修改生成脚本，再运行 `python scripts/build_dashboard.py`，不要只手改 HTML。当前看板使用纸感浅底、深色正文、柔和低饱和图表色；同一科目在柱状图、图例、科目投入和当前推进中必须保持同色。

看板生成逻辑的轻量回归测试放在 `scripts/test_build_dashboard.py`，可用 `python -m unittest scripts.test_build_dashboard` 运行。

### 备考路线复盘

- `StudyProgress/ProgressIndex.md`：总览入口，回看整段备考过程。
- `StudyProgress/Roadmap.md`：阶段规划、目标、节点和策略调整。
- `StudyProgress/Reviews/`：周复盘和阶段复盘，不必每天维护。

### 教材查阅

`StudyMaterials/` 中的 PDF 是本地重点参考教材。它们不是全部备考资料，只是需要反复查阅的部分。PDF 文件默认被 `.gitignore` 忽略，不随仓库上传。

当前 408 四本书和数学三本书都已在 `StudyMaterials/Cache/` 中建立逐页 OCR 缓存。查教材时优先用缓存定位候选 PDF 页：

```bash
python scripts/query.py "关键词"
python scripts/query.py "关键词" --book "线代" --page-only
```

当用户问“书上怎么说”“这个知识点在哪一页”“教材如何定义”时，agent 先查本地 OCR 缓存，再按需核对对应 PDF 页后回答。回答须标明书名和章节，页码须同时给出 `书内印刷页码` 和 `PDF 页码` 并清楚标注。某项暂不能确认就明说，不在当前教材中确认就直说——不编页码、不编原文、不编结论。

### 强化阶段教材笔记

强化阶段复习到某本书某一章时，可以让 agent 整理这一章：

```text
整理《数据结构》第 2 章
```

整理结果放在：

```text
StudyMaterials/BookNotes/对应书名.md
```

每本书只建一个 Markdown 文件，按章节逐步更新——复习到哪章就更新哪章，不是一次性全书总结。用户会自己删改、添加、重排笔记，agent 必须保留这些人工修改，只做增量整理。

### 英语资料与作文模板

英语资料统一放在 `StudyMaterials/English/`。当前已整理的作文模板位于：

```text
StudyMaterials/English/WritingTemplates/
  index.html
  index.pdf
```

其中 `index.html` 是 16:9 浏览器翻页版，`index.pdf` 是同内容 PDF 版，适合直接阅读、打印或移动端查看。后续如果根据新的图片或 PDF 更新作文模板，应先更新 HTML 内容，再按需重新导出 PDF，并避免把图片水印、平台标识、截图噪声写入正文。

## Agent 接手规则

新对话或其他 agent 接手本仓库时，先读：

1. `AGENTS.md`
2. `README.md`
3. 处理学习进度时读 `StudyProgress/README.md`
4. 查教材或整理教材笔记时读 `StudyMaterials/README.md`

不要依赖历史聊天记录。本仓库里的 Markdown 文件就是可迁移的项目上下文。

## 关键约束

- 学习进度只写入 `StudyProgress/`。
- 教材 PDF 和教材派生笔记只放在 `StudyMaterials/`。
- 英语资料和作文模板成品放在 `StudyMaterials/English/`。
- 不移动、重命名或删除教材 PDF，除非用户明确要求。
- 不伪造教材内容、页码、例题、结论或学习进度。
- 不覆盖用户手动写过的笔记和日志。
- 修改文件后说明具体改了哪些路径。

## 当前状态

这个仓库已经具备基础结构，可以直接用于：

- 每日自然语言学习汇报
- 自动生成每日学习记录（带结构化 frontmatter）
- 一键生成可视化学习看板（`scripts/build_dashboard.py` → `dashboard.html`）
- 维护备考总览和路线规划
- 周复盘与阶段复盘
- 教材 OCR 缓存检索与逐章整理教材笔记
- 英语作文模板的 HTML/PDF 成品维护
