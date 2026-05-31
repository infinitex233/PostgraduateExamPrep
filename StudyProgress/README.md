# StudyProgress

这里用于记录考研学习进度。核心目标是：每天用自然语言简要汇报当天完成的事情，由 agent 自动整理成固定 Markdown 记录；长期沉淀后，可以复盘完整备考路线。如果最后有时间写经验帖，再从这些记录中提炼即可。

## Agent 执行约束

任何 agent 或新对话在本目录处理学习进度时，应按以下规则执行：

- 先读取根目录 `AGENTS.md` 和本文件。
- 用户用自然语言汇报当天学习情况时，默认视为“记录今日进度”。
- 每日记录统一写入 `DailyLogs/YYYY-MM/YYYY-MM-DD.md`。
- 如果月份目录不存在，先创建 `DailyLogs/YYYY-MM/`。
- 每次记录后，同步更新 `ProgressIndex.md`。
- 原始汇报必须保留，整理内容必须基于用户实际提供的信息。
- 对用户未提供的时长、数量、状态，不要自行推断，写 `未说明`。
- `ProgressIndex.md` 是总览路线图，应该能帮助用户考后回看整段备考过程。
- 日志重点是记录与复盘，不要每天强行提炼经验帖素材。
- 不要改动 `DigitalBooks/` 中的资料。

## 使用方式

你可以直接这样说：

```text
今天数学做了高数第三章 40 道题，错了 9 道；英语背了 100 个单词，阅读 1 篇；专业课看了栈和队列，整理了半小时笔记。政治没学。状态一般，数学错题还没复盘。
```

agent 应该自动完成：

- 在 `DailyLogs/YYYY-MM/YYYY-MM-DD.md` 新建或更新当天记录。
- 保留原始汇报。
- 整理成今日概览、分科记录、问题与调整、明日优先级。
- 同步更新 `ProgressIndex.md` 的总览表。

## 目录结构

```text
StudyProgress/
  README.md
  ProgressIndex.md
  Roadmap.md
  DailyLogs/
    _template.md
    YYYY-MM/
      YYYY-MM-DD.md
  Reviews/
    Weekly/
      _template.md
      YYYY-Www.md
    Stage/
      _template.md
```

## 记录原则

- 先保证每天能持续记录，不追求一开始就很详细。
- 用户没有提供的数据不要硬填，可以写 `未说明`。
- 每日记录要短，重点放在完成事项、问题、下一步。
- 周复盘和阶段复盘用于看趋势，不必每天维护。
- 经验帖不是记录系统的主目标；如果以后需要，可以从总览、周复盘和阶段复盘中提炼。
