"""Convert PDFs to cached JSON + Markdown using docling.

Usage:
    python scripts/docling_cache.py          # convert all uncached PDFs
    python scripts/docling_cache.py --force  # re-convert all PDFs

Reads PDFs from DigitalBooks/math/ and DigitalBooks/408/.
Writes cache to DigitalBooks/Cache/{book_name}.docling.json
                          DigitalBooks/Cache/{book_name}.docling.md
"""

import argparse
import gc
import json
import os
import sys
import time

# Use HuggingFace mirror for users in China
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
# Limit ONNX Runtime threads to reduce memory pressure
os.environ.setdefault("OMP_NUM_THREADS", "1")
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption


def find_pdfs(books_dir: Path) -> list[Path]:
    pdfs = []
    for subdir in ["math", "408"]:
        d = books_dir / subdir
        if d.is_dir():
            pdfs.extend(sorted(d.glob("*.pdf")))
    return pdfs


def make_converter() -> DocumentConverter:
    pipeline = PdfPipelineOptions()
    pipeline.artifacts_path = None  # don't save intermediate artifacts
    pipeline.do_table_structure = True
    pipeline.do_ocr = True
    pipeline.generate_page_images = False
    pipeline.generate_picture_images = False
    # Reduce parallelism to avoid OOM on large PDFs
    pipeline.accelerator_options.num_threads = 1
    pipeline.ocr_batch_size = 1
    pipeline.layout_batch_size = 1
    pipeline.table_batch_size = 1

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline)
        }
    )


def pdf_to_cache(pdf_path: Path, cache_dir: Path, force: bool) -> tuple[Path, Path] | None:
    """Convert a PDF to cached JSON + Markdown. Returns (json_path, md_path) or None if skipped."""
    name = pdf_path.stem
    json_path = cache_dir / f"{name}.docling.json"
    md_path = cache_dir / f"{name}.docling.md"

    if not force and json_path.exists() and md_path.exists():
        print(f"  [SKIP] {name} — cache exists")
        return None

    print(f"  [CONVERT] {name} ({pdf_path.stat().st_size / 1024 / 1024:.1f} MB)...", flush=True)
    t0 = time.time()

    converter = make_converter()
    result = converter.convert(str(pdf_path))
    doc = result.document

    doc.save_as_json(json_path)
    doc.save_as_markdown(md_path)

    elapsed = time.time() - t0
    pages = len(doc.pages) if doc.pages else "?"
    print(f"    -> {pages} pages, {elapsed:.1f}s", flush=True)

    return json_path, md_path


def main():
    parser = argparse.ArgumentParser(description="Cache PDFs via docling")
    parser.add_argument("--force", action="store_true", help="Re-convert even if cache exists")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parent.parent
    books_dir = repo / "DigitalBooks"
    cache_dir = books_dir / "Cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    pdfs = find_pdfs(books_dir)
    if not pdfs:
        print("No PDFs found in DigitalBooks/{math,408}/")
        return

    print(f"Found {len(pdfs)} PDF(s)\n")

    converted = 0
    skipped = 0
    for pdf in pdfs:
        try:
            result = pdf_to_cache(pdf, cache_dir, args.force)
            if result:
                converted += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"    [FAIL] {pdf.stem}: {e}", flush=True)
        finally:
            gc.collect()  # free memory between PDFs

    print(f"\nDone — {converted} converted, {skipped} skipped, {len(pdfs)} total")


if __name__ == "__main__":
    main()
