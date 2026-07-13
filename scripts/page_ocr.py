"""Build page-level text caches using PyMuPDF + RapidOCR.

Uses embedded PDF text when available and falls back to OCR for scanned pages.
Processes one page at a time, periodically recreates the OCR engine to prevent
memory fragmentation, and saves intermediate results every 10 pages.

Usage:
    python scripts/page_ocr.py "StudyMaterials/Math/Intensive/某书.pdf"
    python scripts/page_ocr.py --all   # process all uncached PDFs
"""

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import fitz  # PyMuPDF
from rapidocr import RapidOCR

from cache_layout import cache_dir_for_pdf, find_pdfs, legacy_cache_path

CACHE_DIR = Path(__file__).resolve().parent.parent / "StudyMaterials" / "Cache"
ENGINE_REFRESH_INTERVAL = 20  # recreate OCR engine every N pages to avoid memory issues
IMAGE_DPI = 120  # sufficient for printed text while keeping scanned books practical
OCR_PARAMS = {
    "EngineConfig.onnxruntime.intra_op_num_threads": 8,
    "EngineConfig.onnxruntime.inter_op_num_threads": 1,
}


def process_pdf(pdf_path: Path, cache_dir: Path, resume_from: int = 0) -> Path | None:
    """Convert one PDF to cached JSON page by page.

    If resume_from > 0, loads existing checkpoint and continues from that page.
    """
    name = pdf_path.stem.replace(".docling", "")
    out_path = cache_dir / f"{name}.docling.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    total = len(doc)

    if resume_from > 0:
        with open(out_path, encoding="utf-8") as f:
            existing = json.load(f)
        pages = existing.get("pages", [])
        print(f"  Loaded {len(pages)} existing pages, resuming from page {resume_from+1}")
    else:
        pages = []

    t0 = time.time()
    engine = None
    ocr_pages_since_refresh = 0

    for i in range(resume_from, total):
        try:
            page = doc[i]
        except Exception as e:
            print(f"  p.{i+1} page access fail: {e}", flush=True)
            pages.append({"page_no": i + 1, "text": ""})
            if (i + 1) % 10 == 0 or i == total - 1:
                output = {"book": name, "total_pages": total, "pages": pages}
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(output, f, ensure_ascii=False)
            continue

        try:
            native_text = page.get_text("text", sort=True).strip()
        except Exception as e:
            print(f"  p.{i+1} text extraction fail, trying OCR: {e}", flush=True)
            native_text = ""

        if len(native_text) >= 100:
            text = native_text
        else:
            # Short embedded fragments are often only watermarks or page labels.
            try:
                if engine is None:
                    engine = RapidOCR(params=OCR_PARAMS)
                    ocr_pages_since_refresh = 0
                pix = page.get_pixmap(dpi=IMAGE_DPI)
                img_bytes = pix.tobytes("png")
                output = engine(img_bytes)
                ocr_text = "\n".join(output.txts) if output.txts else ""
                text = "\n".join(part for part in (native_text, ocr_text) if part)
                ocr_pages_since_refresh += 1
                del pix, img_bytes, output
            except Exception as e:
                print(f"  p.{i+1} OCR fail: {e}", flush=True)
                text = native_text
                # Rebuild engine immediately — a crash may leave it in a bad state.
                del engine
                gc.collect()
                engine = None
                ocr_pages_since_refresh = 0

        pages.append({"page_no": i + 1, "text": text})

        # Periodic engine refresh after actual OCR work to avoid fragmentation.
        if engine is not None and ocr_pages_since_refresh >= ENGINE_REFRESH_INTERVAL:
            del engine
            gc.collect()
            engine = None
            ocr_pages_since_refresh = 0

        # Save intermediate every 10 pages
        if (i + 1) % 10 == 0 or i == total - 1:
            elapsed = time.time() - t0
            done = len(pages)  # includes previously loaded pages
            rate = (i + 1 - resume_from) / elapsed if elapsed > 0 else 0
            non_empty = sum(1 for p in pages if p["text"].strip())
            print(f"  {done}/{total} ({rate:.1f} pg/s, {non_empty} with text)", flush=True)
            # Write checkpoint
            output = {"book": name, "total_pages": total, "pages": pages}
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False)

    doc.close()

    elapsed = time.time() - t0
    non_empty = sum(1 for p in pages if p["text"].strip())
    print(f"  Done: {non_empty}/{total} pages with text, {elapsed:.0f}s", flush=True)
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Page-by-page PDF OCR cache")
    parser.add_argument("pdf", nargs="?", help="Path to a single PDF file")
    parser.add_argument("--all", action="store_true", help="Process all PDFs")
    args = parser.parse_args()

    books_dir = Path(__file__).resolve().parent.parent / "StudyMaterials"

    if args.pdf:
        pdfs = [Path(args.pdf)]
    elif args.all:
        pdfs = find_pdfs(books_dir)
    else:
        parser.print_help()
        sys.exit(1)

    if not pdfs:
        print("No PDFs found")
        return

    print(f"Processing {len(pdfs)} PDF(s)\n")
    for pdf in pdfs:
        name = pdf.stem.replace(".docling", "")
        cache_dir = cache_dir_for_pdf(pdf, books_dir, CACHE_DIR)
        out = cache_dir / f"{name}.docling.json"
        legacy_out = legacy_cache_path(CACHE_DIR, pdf, ".docling.json")
        if not out.exists() and legacy_out.exists():
            out = legacy_out
            cache_dir = CACHE_DIR

        # Check if we can resume from checkpoint
        if out.exists():
            try:
                with open(out, encoding="utf-8") as f:
                    existing = json.load(f)
                done = len(existing.get("pages", []))
                doc = fitz.open(str(pdf))
                total = len(doc)
                doc.close()
                if done >= total:
                    print(f"  [SKIP] {name} (complete: {done}/{total})")
                    continue
                else:
                    print(f"  [RESUME] {name} ({done}/{total} done, continuing...)")
                    process_pdf(pdf, cache_dir, resume_from=done)
                    continue
            except Exception:
                pass  # corrupted file, redo from scratch

        print(f"  [OCR] {name} ({pdf.stat().st_size / 1024 / 1024:.1f} MB)")
        try:
            process_pdf(pdf, cache_dir)
        except Exception as e:
            print(f"  [FAIL] {name}: {e}", flush=True)


if __name__ == "__main__":
    main()
