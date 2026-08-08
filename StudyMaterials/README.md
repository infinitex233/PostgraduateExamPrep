# StudyMaterials

English | [简体中文](README.zh-CN.md)

This directory separates reusable study sources from the notes and mistake books derived from them. Repository-wide policy remains in [AGENTS.md](../AGENTS.md).

## Directory Layout

```text
StudyMaterials/
  README.md
  README.zh-CN.md
  Library/                     # Textbooks, OCR caches, and English materials
  BookNotes/                   # Rolling notes organized by textbook
  MistakeBook/                 # Rolling mistake books organized by subject
```

## Guides

- [Study Library](Library/README.md): local textbooks, OCR caches, textbook lookup, cache generation, evidence verification, and English materials.
- [Book Notes](BookNotes/README.md): one rolling Markdown note per textbook, maintained chapter by chapter.
- [Mistake Books](MistakeBook/README.md): one rolling Markdown mistake book per concrete subject, organized by chapter and knowledge point.

Read this file first, then follow the guide that owns the target directory. Keep source materials in `Library/`, textbook notes in `BookNotes/`, and mistake questions in `MistakeBook/`.

## Shared Rules

- Keep every PDF below `StudyMaterials/` local and out of Git.
- Verified OCR cache JSON under `Library/Cache/` may be tracked after checking completeness and contents.
- Preserve user-authored notes, mistake entries, annotations, ordering, and personal wording.
- Do not rename, move, edit, or delete source materials unless explicitly requested.
- Keep source evidence separate from derived notes and report missing evidence instead of inventing details.
