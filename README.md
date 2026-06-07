# PostgraduateExamPrep

11408 考研备考仓库，用来管理重点教材索引、每日学习记录、阶段复盘和强化阶段的教材笔记。

考试科目：政治、英语一、数学一、408 计算机学科专业基础综合（数据结构、组成原理、操作系统、计算机网络）。

仓库的目标很简单：把备考过程留下来。每天可以用自然语言简单汇报学习情况，由 agent 整理成结构化记录；复习到教材某一章时，再把这一章的知识点整理进对应书籍的 Markdown 笔记。考后如果需要复盘整段路线，或者整理经验帖，可以直接从这些记录里回看。

说明：教材 PDF 体积较大，且可能涉及版权问题，本仓库默认不把 PDF 提交到 GitHub。PDF 可以放在本地 `DigitalBooks/` 对应目录中，agent 在本地工作时再读取。

## 目录结构

```text
PostgraduateExamPrep/
  AGENTS.md                 # 给 agent 的全局规则
  README.md                 # 仓库说明
  StudyProgress/            # 学习进度、路线规划、复盘
    README.md
    ProgressIndex.md        # 备考路线总览
    Roadmap.md              # 阶段规划和策略调整
    DailyLogs/              # 每日学习记录
    Reviews/                # 周复盘和阶段复盘
  DigitalBooks/             # 本地教材目录和教材笔记
    README.md
    408/
    math/
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

每日记录保留原始汇报，也会整理出今日概览、分科记录、问题与调整、明日优先级。用户没有提供的数据写 `未说明`，不自行补全。

### 备考路线复盘

`StudyProgress/ProgressIndex.md` 是总览入口，用来回看整段备考过程。  
`StudyProgress/Roadmap.md` 记录阶段规划、目标、节点和策略调整。  
`StudyProgress/Reviews/` 用来放周复盘和阶段复盘，不需要每天维护。

### 教材查阅

`DigitalBooks/` 中的 PDF 是本地重点参考教材。它们不是全部备考资料，只是需要反复查阅的部分。PDF 文件默认被 `.gitignore` 忽略，不随仓库上传。

当前 408 四本书和数学三本书都已在 `DigitalBooks/Cache/` 中建立逐页 OCR 缓存。查教材时优先用缓存定位候选 PDF 页：

```powershell
python scripts/query.py "关键词"
python scripts/query.py "关键词" --book "线代" --page-only
```

当用户问“书上怎么说”“这个知识点在哪一页”“教材如何定义”时，agent 必须先查本地 OCR 缓存，再按需要核对对应 PDF 页面后回答。回答要标明书名、章节或小节，并且页码必须同时给出并标注 `书内印刷页码` 和 `PDF 页码`。如果某一类页码暂时不能确认，要明确说明；如果没有在当前教材中确认，就直接说明，不能编页码、编原文、编结论。

### 强化阶段教材笔记

强化阶段复习到某本书某一章时，可以让 agent 整理这一章：

```text
整理《数据结构》第 2 章
```

整理结果放在：

```text
DigitalBooks/BookNotes/对应书名.md
```

每本书只建一个 Markdown 文件，按章节逐步更新。这个文件不是一次性全书总结，而是复习到哪章就更新哪章。用户会自己删改、添加和重排笔记，agent 必须保留这些人工修改，只做增量整理。

## Agent 接手规则

新对话或其他 agent 接手本仓库时，先读：

1. `AGENTS.md`
2. `README.md`
3. 处理学习进度时读 `StudyProgress/README.md`
4. 查教材或整理教材笔记时读 `DigitalBooks/README.md`

不要依赖历史聊天记录。本仓库里的 Markdown 文件就是可迁移的项目上下文。

## 关键约束

- 学习进度只写入 `StudyProgress/`。
- 教材 PDF 和教材派生笔记只放在 `DigitalBooks/`。
- 不移动、重命名或删除教材 PDF，除非用户明确要求。
- 不伪造教材内容、页码、例题、结论或学习进度。
- 不覆盖用户手动写过的笔记和日志。
- 修改文件后说明具体改了哪些路径。

## 当前状态

这个仓库已经具备基础结构，可以直接用于：

- 每日自然语言学习汇报
- 自动生成每日学习记录
- 维护备考总览和路线规划
- 周复盘与阶段复盘
- 教材 PDF 查阅
- 强化阶段逐章整理教材笔记
