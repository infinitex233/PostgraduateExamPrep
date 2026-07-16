# PostgraduateExamPrep

[English](README.md) | 简体中文

一个面向 11408 考研的文件化学习管理系统，在同一仓库中维护每日进度、阶段规划、教材检索、复习笔记和自动生成的学习看板。

## 考试范围

本仓库覆盖 11408 方向的四类科目：

- 政治
- 英语一
- 数学一：高等数学、线性代数、概率论与数理统计
- 408 计算机学科专业基础综合：数据结构、计算机组成原理、操作系统、计算机网络

## 仓库功能

- 将简短的自然语言学习汇报整理为带结构化 YAML frontmatter 的每日 Markdown 记录。
- 维护长期进度索引、路线规划、周复盘和阶段复盘。
- 根据学习记录生成唯一的 Capsule 风格 HTML 看板。
- 打开数百 MB 的教材 PDF 前，先检索本地 OCR 缓存。
- 每本教材维护一份按复习章节滚动更新的 Markdown 笔记。
- 将英语学习源资料和派生复习成品与进度日志分开保存。

教材源 PDF 仅保存在本地。通过校验的 OCR 缓存可以与维护系统所需的脚本、学习记录、笔记、说明文档和适合版本控制的派生成品一同由 Git 跟踪。

## 目录结构

```text
PostgraduateExamPrep/
  AGENTS.md                      # 权威仓库规则
  CLAUDE.md                      # 精简的 Claude Code 入口
  README.md                      # GitHub 默认英文首页
  README.zh-CN.md                # 简体中文首页
  scripts/
    cache_layout.py              # 共用的源文件到缓存路径规则
    query.py                     # 检索分类后的 OCR 缓存
    page_ocr.py                  # 主要逐页缓存构建器
    docling_cache.py             # 兼容旧格式的 Docling 构建器
    build_dashboard.py           # 看板生成入口
    build_dashboard_variants.py  # 历史数据补充与渲染
    test_build_dashboard.py
    test_build_dashboard_variants.py
  StudyProgress/
    README.md                    # 英文进度工作流
    README.zh-CN.md              # 简体中文进度工作流
    DailyLogs/                   # 带 YAML frontmatter 的每日记录
    Summaries/                   # 稳定的月度分科汇总
    Reviews/                     # 周复盘与阶段复盘
    Imports/                     # 用于历史补录的原始导出数据
    ProgressIndex.md             # 长期路线与历史汇总
    Roadmap.md                   # 目标与阶段规划
    dashboard.html               # 生成后的 Capsule 看板
  StudyMaterials/
    README.md                    # 英文资料工作流
    README.zh-CN.md              # 简体中文资料工作流
    408/                         # 本地 408 教材 PDF
    Math/Basic/                  # 本地数学基础阶段 PDF
    Math/Intensive/              # 本地数学强化阶段 PDF
    Cache/                       # 本地分类 OCR 缓存
    BookNotes/                   # 滚动更新的教材笔记
    English/                     # 英语源资料与复习成品
```

## 每日进度

自然语言汇报会整理到：

```text
StudyProgress/DailyLogs/YYYY-MM/YYYY-MM-DD.md
```

每篇记录遵循 `StudyProgress/DailyLogs/_template.md`。每日结构化指标只读取 YAML frontmatter：未知值保持 `null`，不得根据正文推断时长或完成状态。同一次更新还会刷新 `StudyProgress/ProgressIndex.md` 和生成后的看板。

```bash
python scripts/build_dashboard.py
```

看板的历史归档与月度部分还会读取 `StudyProgress/ProgressIndex.md` 中的稳定汇总结构，以及存在时的 `StudyProgress/Summaries/Monthly/*.md`。用于历史补录的原始导出数据单独保存在 `StudyProgress/Imports/`。

完整规则见 [StudyProgress 工作流](StudyProgress/README.zh-CN.md)。

## 教材检索

打开大体积 PDF 前，先检索本地逐页缓存：

```bash
python scripts/query.py "二叉树"
python scripts/query.py "矩阵" --book "线性代数"
python scripts/query.py "极限" --book "高数" --page-only
```

使用主要 OCR 流程生成或续跑逐页缓存：

```bash
python scripts/page_ocr.py "StudyMaterials/Math/Intensive/某书.pdf"
python scripts/page_ocr.py --all
```

缓存命中只用于定位候选 PDF 页，不是最终证据。精确原文、公式、图表、例题和书内印刷页码仍须核对源 PDF；引用页码时应区分书内印刷页码与 PDF 页码。

缓存格式、查书纪律和教材笔记规则见 [StudyMaterials 工作流](StudyMaterials/README.zh-CN.md)。

## 看板检查

修改看板代码后运行：

```bash
python -m unittest scripts.test_build_dashboard scripts.test_build_dashboard_variants
python scripts/build_dashboard.py
```

`StudyProgress/dashboard.html` 是唯一保留的看板成品。正式生成时，渲染器会清理旧的并行版本。

## 仅保存在本地的内容

以下内容不得提交：

- `StudyMaterials/` 下的教材及生成 PDF
- Python 字节码、测试缓存、PDF 渲染页、截图、诊断信息和临时文件
- 凭据、浏览器配置、Cookie 和机器专用数据

`StudyMaterials/Cache/` 下通过校验的 OCR 缓存 JSON 可以提交，使教材检索无需在每台机器上重新构建全部缓存。PDF 和一次性产物仍不得进入 Git，以避免发布版权源材料或机器专用杂项。

## Agent 使用入口

修改文件前按以下顺序阅读：

1. `AGENTS.md`
2. 本 README
3. 处理日志、复盘或看板时阅读 `StudyProgress/README.md`
4. 处理教材、缓存、教材笔记或英语资料时阅读 `StudyMaterials/README.md`

`AGENTS.md` 是权威规则；`CLAUDE.md` 是精简的命令和架构参考。
