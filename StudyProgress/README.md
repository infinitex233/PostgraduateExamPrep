# StudyProgress

这里用于记录 11408 考研学习进度。核心目标是：每天用自然语言简要汇报当天完成的事情，由 agent 自动整理成固定 Markdown 记录；长期沉淀后，可以复盘完整备考路线。如果最后有时间写经验帖，再从这些记录中提炼即可。

考试科目：政治、英语一、数学一（高数/线代/概率）、408（数据结构/组成原理/操作系统/计算机网络）。日常记录按这些科目分类整理。

## Agent 执行约束

任何 agent 或新对话在本目录处理学习进度时，应按以下规则执行：

- 先读取根目录 `AGENTS.md` 和本文件。
- 用户用自然语言汇报当天学习情况时，默认视为“记录今日进度”。
- 每日记录统一写入 `DailyLogs/YYYY-MM/YYYY-MM-DD.md`，并按 `DailyLogs/_template.md` 在文件顶部写好 YAML frontmatter。
- frontmatter 是看板的数据源：科目名用统一命名，时长一律用分钟，用户没给的写 `null`，不臆造。
- 如果月份目录不存在，先创建 `DailyLogs/YYYY-MM/`。
- 每次记录后，同步更新 `ProgressIndex.md`，并运行 `python scripts/build_dashboard.py` 刷新 `dashboard.html`。
- `dashboard.html` 是生成文件；看板布局、配色、科目颜色映射和强调文字样式统一维护在根目录 `scripts/build_dashboard.py`。
- 原始汇报必须保留，整理内容必须基于用户实际提供的信息。
- 对用户未提供的时长、数量、状态，不要自行推断，写 `未说明`。
- `ProgressIndex.md` 是总览路线图，应该能帮助用户考后回看整段备考过程。
- 日志重点是记录与复盘，不要每天强行提炼经验帖素材。

## 使用方式

你可以直接这样说：

```text
今天数学做了高数第三章 40 道题，错了 9 道；英语背了 100 个单词，阅读 1 篇；专业课看了栈和队列，整理了半小时笔记。政治没学。状态一般，数学错题还没复盘。
```

agent 应该自动完成：

- 在 `DailyLogs/YYYY-MM/YYYY-MM-DD.md` 新建或更新当天记录，写好顶部 frontmatter。
- 保留原始汇报。
- 整理成今日概览、分科记录、问题与调整、明日优先级。
- 同步更新 `ProgressIndex.md` 的总览表。
- 运行 `python scripts/build_dashboard.py` 刷新 `dashboard.html` 看板。

## 看板维护

- 只从 DailyLogs 的 frontmatter 读取结构化数据，不从正文猜测精确时长或章节状态。
- 科目名必须使用模板中的统一命名；这些名称同时用于 `subject_colors` 映射。
- 当前看板保持固定布局：最近记录趋势、最近一天、统计指标、科目投入、下一步、当前推进、最近记录和节点。
- `subject_colors` 控制具体科目颜色，应在柱状图、图例、科目投入和当前推进中保持一致。
- `group_colors` 保留给大类汇总数据使用；如果以后恢复大类图表，也应从同一映射取色。
- 视觉调整优先修改 `scripts/build_dashboard.py`，再重新生成 `dashboard.html`；不要只改生成后的 HTML。
- 看板生成逻辑的轻量回归测试位于 `scripts/test_build_dashboard.py`，可用 `python -m unittest scripts.test_build_dashboard` 运行。
- 叠加柱形使用轻微透明度和白色分隔线，目的是让同一天内的科目层次更清楚，避免高饱和撞色。
- 最近一天的科目名与详情正文同尺寸、加粗，并使用看板强调色；这属于视觉样式，不影响日志数据。

## 目录结构

```text
StudyProgress/
  README.md
  ProgressIndex.md
  Roadmap.md
  dashboard.html          # 学习看板，由 scripts/build_dashboard.py 生成
  DailyLogs/
    _template.md          # 含 frontmatter 字段说明
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
- 不要改动 `StudyMaterials/` 中的资料。
