"""Search cached textbook JSON for knowledge points.

Usage:
    python scripts/query.py "二叉树"                        # search all books
    python scripts/query.py "二叉树" --book 数据结构          # filter by book name
    python scripts/query.py "二叉树" --page-only             # show page numbers only
    python scripts/query.py "二叉树" --context 2             # show 2 surrounding items

The script searches categorized page-level and legacy Docling caches, returning
matching PDF page numbers and text previews (plus section headers when the cache
format provides them).
"""

import argparse
import json
import sys
from pathlib import Path

from cache_layout import CACHE_DIR


def find_cache_files() -> list[Path]:
    """Return categorized caches, falling back to legacy flat copies."""
    files = sorted(CACHE_DIR.rglob("*.docling.json"))
    categorized_stems = {path.stem for path in files if path.parent != CACHE_DIR}
    return [
        path for path in files
        if path.parent != CACHE_DIR or path.stem not in categorized_stems
    ]


def load_book(json_path: Path) -> dict:
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def find_parent_headers(texts: list, item: dict, max_depth: int = 3) -> list[str]:
    """Walk up the parent chain to find section headers."""
    headers = []
    current = item
    for _ in range(max_depth):
        parent_ref = current.get("parent", {}).get("$ref", "")
        if not parent_ref or parent_ref == "#/body":
            break
        # Resolve reference (format: "#/texts/42")
        try:
            idx = int(parent_ref.split("/")[-1])
            parent = texts[idx]
            if parent.get("label") == "section_header":
                headers.append(parent["text"])
            elif parent.get("label") in ("list_item", "text") and parent.get("text"):
                pass  # skip non-header parents but keep walking
            current = parent
        except (ValueError, IndexError):
            break
    return list(reversed(headers))


def _search_docling(data: dict, query: str, book_name: str, context: int) -> list[dict]:
    """Search legacy Docling-format JSON."""
    texts = data.get("texts", [])
    matches = []
    for i, item in enumerate(texts):
        text = item.get("text", "")
        if not text or query.lower() not in text.lower():
            continue
        page_no = None
        prov = item.get("prov", [])
        if prov:
            page_no = prov[0].get("page_no")
        headers = find_parent_headers(texts, item)
        before = [texts[j]["text"] for j in range(max(0, i - context), i) if texts[j].get("text")]
        after = [texts[j]["text"] for j in range(i + 1, min(len(texts), i + context + 1)) if texts[j].get("text")]
        matches.append({
            "book": book_name, "page": page_no,
            "headers": headers, "label": item.get("label", ""),
            "text": text, "level": item.get("level"),
            "context_before": before, "context_after": after,
        })
    return matches


def _search_pageocr(data: dict, query: str, book_name: str, context: int) -> list[dict]:
    """Search page-level cache JSON."""
    pages = data.get("pages", [])
    matches = []
    for page in pages:
        text = page.get("text", "")
        if not text or query.lower() not in text.lower():
            continue
        lines = text.split("\n")
        for li, line in enumerate(lines):
            if query.lower() in line.lower():
                start = max(0, li - context)
                end = min(len(lines), li + context + 1)
                snippet = "\n".join(lines[start:end])
                matches.append({
                    "book": book_name, "page": page["page_no"],
                    "headers": [], "label": "",
                    "text": snippet[:200], "level": None,
                    "context_before": [], "context_after": [],
                })
    return matches


def search_book(json_path: Path, query: str, context: int = 1) -> list[dict]:
    """Search one book. Auto-detects JSON format (docling vs page-ocr)."""
    data = load_book(json_path)
    book_name = data.get("book") or data.get("name") or json_path.stem.replace(".docling", "")

    if isinstance(data.get("pages"), list):
        return _search_pageocr(data, query, book_name, context)
    else:
        return _search_docling(data, query, book_name, context)


def format_output(matches: list[dict], page_only: bool = False) -> str:
    """Format search results for display."""
    if not matches:
        return "(no matches)"

    # Group by book, then by page
    from collections import defaultdict
    by_book = defaultdict(lambda: defaultdict(list))
    for m in matches:
        by_book[m["book"]][m["page"]].append(m)

    lines = []
    for book, pages in by_book.items():
        lines.append(f"\n{'='*60}")
        lines.append(f"  {book}")
        lines.append(f"{'='*60}")

        for page in sorted(pages.keys(), key=lambda x: x or 0):
            items = pages[page]
            # Collect unique headers from all items on this page
            all_headers = []
            seen = set()
            for it in items:
                h = " > ".join(it["headers"]) if it["headers"] else ""
                if h and h not in seen:
                    seen.add(h)
                    all_headers.append(h)

            lines.append(f"\n  p.{page}")
            if all_headers:
                for h in all_headers:
                    lines.append(f"    [{h}]")

            if not page_only:
                for it in items[:5]:  # limit to 5 per page
                    level_prefix = "#" * (it["level"] or 1) if it["label"] == "section_header" else ""
                    snippet = it["text"][:120]
                    if level_prefix:
                        lines.append(f"    {level_prefix} {snippet}")
                    else:
                        lines.append(f"    ...{snippet}...")

                if len(items) > 5:
                    lines.append(f"    ... and {len(items) - 5} more matches on this page")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search cached textbooks by keyword")
    parser.add_argument("query", nargs="?", default="", help="Keyword or phrase to search for")
    parser.add_argument("--book", default=None, help="Filter by book name (partial match)")
    parser.add_argument("--page-only", action="store_true", help="Only show page numbers, not text")
    parser.add_argument("--context", type=int, default=1, help="Number of surrounding text items")
    parser.add_argument("--list-books", action="store_true", help="List all cached books")
    args = parser.parse_args()

    if args.list_books:
        print("Cached books:")
        for f in find_cache_files():
            print(f"  {f.stem.replace('.docling', '')}")
        return

    json_files = find_cache_files()
    if not json_files:
        print("No cached books found. Run scripts/page_ocr.py --all first.")
        sys.exit(1)

    if args.book:
        json_files = [f for f in json_files if args.book in f.stem]
        if not json_files:
            print(f"No cached book matching '{args.book}'")
            sys.exit(1)

    all_matches = []
    for jf in json_files:
        matches = search_book(jf, args.query, context=args.context)
        all_matches.extend(matches)

    print(format_output(all_matches, page_only=args.page_only))
    print(f"\n({len(all_matches)} matches across {len(json_files)} book(s))")


if __name__ == "__main__":
    main()
