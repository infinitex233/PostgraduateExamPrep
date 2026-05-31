"""Page-by-page OCR using PyMuPDF + RapidOCR.

Memory-efficient: processes one page at a time, periodically recreates the OCR
engine to prevent memory fragmentation, saves intermediate results every 10 pages.

Usage:
    python scripts/page_ocr.py "DigitalBooks/408/王道2027计算机组成原理_高清带书签版.pdf"
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

CACHE_DIR = Path(__file__).resolve().parent.parent / "DigitalBooks" / "Cache"
ENGINE_REFRESH_INTERVAL = 20  # recreate OCR engine every N pages to avoid memory issues
IMAGE_DPI = 144  # balance between OCR quality and memory usage


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
    engine = RapidOCR()

    for i in range(resume_from, total):
        try:
            page = doc[i]
            pix = page.get_pixmap(dpi=IMAGE_DPI)
            img_bytes = pix.tobytes("png")
            output = engine(img_bytes)
            text = "\n".join(output.txts) if output.txts else ""
        except Exception as e:
            print(f"  p.{i+1} OCR fail: {e}", flush=True)
            text = ""
            # Rebuild engine immediately — a crash may leave it in a bad state
            try:
                del engine
                gc.collect()
                engine = RapidOCR()
            except Exception:
                pass

        pages.append({"page_no": i + 1, "text": text})

        # Periodic engine refresh to avoid memory fragmentation
        if (i + 1) % ENGINE_REFRESH_INTERVAL == 0:
            del engine
            gc.collect()
            try:
                engine = RapidOCR()
            except Exception:
                pass

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


def find_pdfs(books_dir: Path) -> list[Path]:
    pdfs = []
    for subdir in ["math", "408"]:
        d = books_dir / subdir
        if d.is_dir():
            pdfs.extend(sorted(d.glob("*.pdf")))
    return pdfs


def main():
    parser = argparse.ArgumentParser(description="Page-by-page PDF OCR cache")
    parser.add_argument("pdf", nargs="?", help="Path to a single PDF file")
    parser.add_argument("--all", action="store_true", help="Process all PDFs")
    args = parser.parse_args()

    books_dir = Path(__file__).resolve().parent.parent / "DigitalBooks"

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
        out = CACHE_DIR / f"{name}.docling.json"

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
                    process_pdf(pdf, CACHE_DIR, resume_from=done)
                    continue
            except Exception:
                pass  # corrupted file, redo from scratch

        print(f"  [OCR] {name} ({pdf.stat().st_size / 1024 / 1024:.1f} MB)")
        try:
            process_pdf(pdf, CACHE_DIR)
        except Exception as e:
            print(f"  [FAIL] {name}: {e}", flush=True)


if __name__ == "__main__":
    main()
