"""Shared source discovery and cache-path rules for textbook builders."""

from pathlib import Path

SUBJECTS = ("Math", "408")


def find_pdfs(books_dir: Path) -> list[Path]:
    """Return textbook PDFs from supported source trees."""
    pdfs = []
    for subject in SUBJECTS:
        subject_dir = books_dir / subject
        if subject_dir.is_dir():
            pdfs.extend(sorted(subject_dir.rglob("*.pdf")))
    return pdfs


def cache_dir_for_pdf(pdf_path: Path, books_dir: Path, cache_root: Path) -> Path:
    """Mirror a PDF's subject, stage, and nested parent below the cache root."""
    resolved_pdf = pdf_path.resolve()
    for subject in SUBJECTS:
        subject_dir = (books_dir / subject).resolve()
        try:
            relative = resolved_pdf.relative_to(subject_dir)
        except ValueError:
            continue

        parent_parts = relative.parent.parts
        category = cache_root / subject
        return category / Path(*parent_parts)

    return cache_root


def legacy_cache_path(cache_root: Path, pdf_path: Path, suffix: str) -> Path:
    """Return the pre-categorization flat cache path for a PDF."""
    return cache_root / f"{pdf_path.stem}{suffix}"
