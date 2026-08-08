# StudyMaterials

[English](README.md) | 简体中文

本目录将可重复使用的学习源资料，与基于源资料整理的教材笔记和错题本分开保存。仓库级规则仍以 [AGENTS.md](../AGENTS.md) 为准。

## 目录结构

```text
StudyMaterials/
  README.md
  README.zh-CN.md
  Library/                     # 教材、OCR 缓存和英语资料
  BookNotes/                   # 按教材组织的滚动笔记
  MistakeBook/                 # 按具体科目组织的滚动错题本
```

## 使用说明

- [学习资料库](Library/README.zh-CN.md)：本地教材、OCR 缓存、教材检索、缓存生成、证据核验和英语资料。
- [教材笔记](BookNotes/README.zh-CN.md)：每本教材维护一份 Markdown 笔记，并按章节持续更新。
- [错题本](MistakeBook/README.zh-CN.md)：每个具体科目维护一份 Markdown 错题本，并按章节和知识点归类。

先阅读本文件，再按照目标目录对应的说明操作。源资料放在 `Library/`，教材笔记放在 `BookNotes/`，错题放在 `MistakeBook/`。

## 共通规则

- `StudyMaterials/` 下所有 PDF 均只保存在本地，不得提交。
- `Library/Cache/` 下经过完整性和内容检查的 OCR 缓存 JSON 可以由 Git 跟踪。
- 保留用户编写的笔记、错题、标注、排序和个人表述。
- 未经明确要求，不重命名、移动、修改或删除源资料。
- 保持源证据与派生笔记分离；证据缺失时说明限制，不自行编造。
