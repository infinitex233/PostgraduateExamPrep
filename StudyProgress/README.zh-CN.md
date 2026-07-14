# StudyProgress

[English](README.md) | 简体中文

本目录用于长期记录 11408 考研学习进度。简短的自然语言汇报会整理为统一的 Markdown 日志，以支持每日复盘、阶段分析和完整备考路线回顾。

## 范围

记录覆盖政治、英语一、数学一（高数、线代、概统）和 408（数据结构、组成原理、操作系统、计算机网络）。

仓库级规则以 `../AGENTS.md` 为准。本文件负责进度记录和看板的具体操作规则。

## 目录结构

```text
StudyProgress/
  README.md
  README.zh-CN.md
  ProgressIndex.md             # 长期路线与历史汇总
  Roadmap.md                   # 目标与阶段规划
  dashboard.html               # 生成后的 Capsule 看板
  DailyLogs/
    _template.md               # 标准 frontmatter 与日志结构
    YYYY-MM/
      YYYY-MM-DD.md
  Summaries/
    Monthly/                   # 可选的月度分科汇总
  Reviews/
    Weekly/
      _template.md
      YYYY-Www.md
    Stage/
      _template.md
  Imports/                     # 用于历史补录的原始导出数据
```

## 每日记录工作流

除非用户明确表示只想讨论，否则自然语言的当日学习汇报默认视为记录请求。

每次汇报按以下流程处理：

1. 创建或更新 `DailyLogs/YYYY-MM/YYYY-MM-DD.md`。
2. 遵循 `DailyLogs/_template.md`，并保留文件顶部的 YAML frontmatter。
3. 在指定部分原样保留用户的原始汇报。
4. 只记录有依据的事实：完成事项、明确给出的时长或数量、当前状态、问题和下一步。
5. 时长使用整数分钟，科目使用下方标准名称。未知的结构化值写 `null`，未知的正文描述写 `未说明`。
6. 不臆造时长、任务数量、章节状态、完成度、情绪或计划。
7. 在 `ProgressIndex.md` 中添加或更新简洁记录。
8. 运行 `python scripts/build_dashboard.py` 重新生成 `dashboard.html`。

示例汇报：

```text
今天数学做了高数第三章 40 道题，错了 9 道；英语背了 100 个单词，阅读 1 篇；专业课看了栈和队列，整理了半小时笔记。政治没学。状态一般，数学错题还没复盘。
```

整理后的记录应保持简洁，包含今日概览、原始汇报、分科记录、复盘和下一步优先级。

## Frontmatter 约定

每日结构化指标只从 `DailyLogs/` 日志顶部的 YAML frontmatter 读取；不得从正文推断精确时长或章节进度。

以下标准科目键参与聚合和看板颜色映射，不得改名：

- `数学-高数`
- `数学-线代`
- `数学-概率`
- `专业课-数据结构`
- `专业课-组成原理`
- `专业课-操作系统`
- `专业课-计算机网络`
- `英语`
- `政治`

不得用零代替未知值。零表示用户明确说明该科当天未学习；`null` 表示用户没有提供该值。

## 索引与复盘

- `ProgressIndex.md` 是长期路线和历史总览。其月度概览与阶段性观察结构应保持稳定，因为看板会读取这些部分展示历史归档。
- `Roadmap.md` 保存目标和阶段规划，不承担每日事实记录。
- `Reviews/Weekly/` 和 `Reviews/Stage/` 只在用户请求周复盘或阶段复盘时维护，无需每日更新。
- `Summaries/Monthly/` 可提供看板历史卡片使用的月度分科汇总。
- `Imports/` 保存用于历史补录的原始导出数据，并与每日日志分开管理。

本系统的首要目标是可靠记录和复盘；经验帖素材可以在积累充分后再从记录中提炼。

## 看板数据流

生成后的看板使用两层数据：

1. 每日和当前的结构化指标只读取 `DailyLogs/**/YYYY-MM-DD.md` 的 frontmatter。
2. 历史归档和月度展示还会读取 `ProgressIndex.md` 中的稳定汇总结构，以及 `Summaries/Monthly/` 下存在的月度文件。

生成链路如下：

```text
DailyLogs frontmatter + 历史汇总
  -> scripts/build_dashboard.py
  -> scripts/build_dashboard_variants.py
  -> StudyProgress/dashboard.html
```

`scripts/build_dashboard.py` 是兼容入口和聚合层。`scripts/build_dashboard_variants.py` 负责历史数据补充、固定 1920 x 1080 Capsule 版式、字体、颜色映射、交互和旧输出清理。

## 生成与测试

修改每日日志、进度索引、月度汇总或看板代码后，重新生成看板：

```bash
python scripts/build_dashboard.py
```

修改看板代码后，先运行回归测试：

```bash
python -m unittest scripts.test_build_dashboard scripts.test_build_dashboard_variants
python scripts/build_dashboard.py
```

视觉或交互发生变化时，还需检查生成后的 HTML。

## 生成文件规则

- `dashboard.html` 是唯一保留的看板成品。
- 不得把手工修改生成后的 HTML 当作源代码变更。
- 不创建或保留 `dashboard_capsule*.html`、`dashboard_signal.html`、`DashboardTemplatePreviews.html` 等并行版本。
- 具体科目使用 `subject_colors`，大类汇总使用 `group_colors`。同一科目在图表、图例、统计和进度指示中必须保持同色。
- 除非用户明确要求结构调整，否则保持固定分页顺序和交互行为。

## 记录完整性

- 优先保证记录简洁、可持续，不为显得完整而扩写。
- 保留用户原话和手工修改。
- 区分未知信息与明确的零值。
- 每日记录只放在 `StudyProgress/`；纯进度任务不修改 `StudyMaterials/`。
- 证据不足时说明缺口，不自行推断。
