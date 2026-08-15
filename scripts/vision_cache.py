"""High-quality vision-based page-level cache builder for scanned math books.

Renders PDF pages and transcribes them with a vision model (gpt-5.6-terra →
gpt-5.6-luna via the multimodal-vision toolkit) into the page-level
`.docling.json` cache that `scripts/query.py` reads. Intended for books whose
embedded text layer is broken (garbled font mappings) or whose math layout
RapidOCR cannot preserve — the two failure modes behind the old garbled caches.
For cheap offline builds of clean PDFs, keep using `scripts/page_ocr.py`.

Usage:
    python scripts/vision_cache.py "StudyMaterials/Library/Math/Intensive/某书.pdf"
    python scripts/vision_cache.py "某书.pdf" --first 6 --last 219 --batch 2
    python scripts/vision_cache.py "某书.pdf" --chain-offset 3   # 多流并发时错开起始 key
    python scripts/vision_cache.py "某书.pdf" --reverse-providers
    python scripts/vision_cache.py --all --batch 2

Concurrency: run several instances on the same PDF with disjoint --first/--last
ranges (one sidecar checkpoint per instance is NOT supported — use one instance
per range); or run several books in parallel, giving each a different
--chain-offset so streams start on different keys.

Checkpointing: every finished batch is appended to
`<cache-dir>/<stem>.vision-ckpt.json`. When the requested range is fully
covered, the checkpoint is merged into `<stem>.docling.json` (pages in range are
replaced; pages the model left empty keep their old text) and the checkpoint is
removed. Re-running resumes from the checkpoint, so a network outage loses at
most one batch. A run that finishes with pages still missing exits with code 2.

Dependencies: the multimodal-vision toolkit. Point MULTIMODAL_VISION_DIR at its
checkout, default `/home/infinitex/code/multimodal-vision`. Keys and endpoints
come from its config.py (cc-switch codex group); API access normally needs the
local proxy unless --no-proxy is passed.
"""

import argparse
import json
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

from cache_layout import (
    CACHE_DIR,
    LIBRARY_DIR,
    cache_dir_for_pdf,
    find_pdfs,
)

VISION_DIR_DEFAULT = "/home/infinitex/code/multimodal-vision"

SYSTEM_PROMPT = (
    "你是考研数学辅导书 PDF 的视觉识别引擎。用户会给你若干页书页图片,请逐页转写为干净的 Markdown。\n"
    "要求:\n"
    "1. 每页输出以 `## Page N` 开头(N 为该页的绝对页码),严格逐页分开。\n"
    "2. 完整、准确地转写所有正文与数学公式,不得省略、概括或改写公式。公式用 LaTeX:行内用 $...$,"
    "独立成行用 $$...$$;务必还原分式、根号、积分、求和、极限、上下标、希腊字母、绝对值、"
    "矩阵、分段函数等全部符号与结构。\n"
    "3. 保留章节标题、题号(如 \"1.\")、选项((A)(B)...)、答案标注(如 \"【解】(D)\")、"
    "步骤编号(如 \"(方法一)\")与最终结论。\n"
    "4. 忽略版面装饰,不要输出:空白答题区的 \"审题/答题区/笔记\" 表格、"
    "\"（读题时记录）（做题时记录）\"、页脚页码、重复的页眉章节行、"
    "水印文字(如 \"公众号:做题本集结地\"、\"公众号羊驼学长免费分享\")、纯广告页。\n"
    "5. 识别不清的字符用 [?] 标记,严禁编造。\n"
    "6. 只输出 Markdown 正文,不要任何前言、说明或道歉。"
)

_PAGE_HEAD_RE = re.compile(r"^#+\s*(?:Page\s+\d+|第\s*\d+\s*页)\s*\n?", re.M)
_CJK_BSLASH_RE = re.compile(r"\\(?=[\u4e00-\u9fff])")


def _load_vision_lib():
    """Import the multimodal-vision toolkit, resolving its directory."""
    import os
    vision_dir = Path(os.environ.get("MULTIMODAL_VISION_DIR", VISION_DIR_DEFAULT))
    if not (vision_dir / "vision_client.py").exists():
        raise SystemExit(
            f"找不到视觉识别工具包:{vision_dir}\n"
            "请设置环境变量 MULTIMODAL_VISION_DIR 指向其检出目录。"
        )
    sys.path.insert(0, str(vision_dir))
    import config
    import pdf2img
    import vision_client
    return config, pdf2img, vision_client


def _clean_text(raw: str) -> str:
    """Strip page headings, normalize, and clear model artifacts."""
    txt = raw.strip()
    txt = _PAGE_HEAD_RE.sub("", txt, count=1).strip()
    txt = txt.replace("\\dfrac", "\\frac")
    txt = _CJK_BSLASH_RE.sub("", txt)  # 清除中文前误加的反斜杠(如 \则)
    return txt


def _balance_report(pages: list[dict]) -> list[int]:
    """Return page numbers whose inline $ / display $$ delimiters don't pair up."""
    def scan(t):
        toks = []
        i = 0
        while i < len(t):
            if t.startswith("$$", i):
                toks.append(("$$", i))
                i += 2
                continue
            if t[i] == "$":
                toks.append(("$", i))
            i += 1
        stack = []
        for typ, _pos in toks:
            if stack and stack[-1][0] == typ:
                stack.pop()
            else:
                stack.append((typ, 0))
        return stack

    return [p["page_no"] for p in pages if scan(p["text"])]


def _merge_checkpoint(cache_path: Path, ckpt: dict, first: int, last: int) -> None:
    """Merge covered pages into the page-level cache JSON and drop the checkpoint."""
    if cache_path.exists():
        data = json.loads(cache_path.read_text(encoding="utf-8"))
    else:
        data = {"book": cache_path.stem, "total_pages": last, "pages": []}
    by_page = {p["page_no"]: p for p in data.get("pages", [])}

    n_replaced = 0
    for n in range(first, last + 1):
        new = _clean_text(ckpt.get(str(n), ""))
        if new:
            by_page[n] = {"page_no": n, "text": new}
            n_replaced += 1
        elif n not in by_page:
            by_page[n] = {"page_no": n, "text": ""}  # 模型未返回,留空(可用旧文回填)

    data["pages"] = [by_page[n] for n in sorted(by_page)]
    data["total_pages"] = len(data["pages"])
    cache_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    qmarks = sum(p["text"].count("[?]") for p in data["pages"])
    integs = sum(p["text"].count("\\int") for p in data["pages"])
    unbalanced = _balance_report(data["pages"])
    print(f"[merge] 替换 {n_replaced} 页 → {cache_path}", flush=True)
    print(f"[merge] [?]={qmarks} \\int={integs} 未配平页={unbalanced or '无'}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="视觉模型逐页转写 PDF 并写入 .docling.json 缓存")
    parser.add_argument("pdf", nargs="?", help="单个 PDF 路径")
    parser.add_argument("--all", action="store_true", help="处理 Library 下全部 PDF")
    parser.add_argument("--force", action="store_true",
                        help="即使缓存已完整也重建(对损坏缓存做质量修复时使用)")
    parser.add_argument("--first", type=int, default=None, help="起始页(1 起始,含)")
    parser.add_argument("--last", type=int, default=None, help="结束页(含;默认到最后一页)")
    parser.add_argument("--batch", type=int, default=4,
                        help="每批页数(默认 4;公式密集的讲义/解析册建议 2,防截断)")
    parser.add_argument("--dpi", type=int, default=150, help="渲染分辨率")
    parser.add_argument("--max-tokens", type=int, default=8192, help="每批最大输出 token")
    parser.add_argument("--timeout", type=int, default=180, help="单次 API 调用超时秒数")
    parser.add_argument("--max-retries", type=int, default=8,
                        help="单批失败最大重试次数(指数退避)")
    parser.add_argument("--chain-offset", type=int, default=0,
                        help="供应商链轮转偏移(并发多流时错开起始 key)")
    parser.add_argument("--reverse-providers", action="store_true", help="供应商链反序")
    parser.add_argument("--no-proxy", action="store_true", help="不走本地代理直连")
    parser.add_argument("--cache-dir", type=Path, default=None,
                        help="覆盖缓存输出目录(默认按 cache_layout 镜像源目录;测试用)")
    args = parser.parse_args()

    config, pdf2img, vision_client = _load_vision_lib()

    if args.all:
        pdfs = find_pdfs(LIBRARY_DIR)
    elif args.pdf:
        pdfs = [Path(args.pdf)]
    else:
        parser.print_help()
        return 1
    if not pdfs:
        print("No PDFs found")
        return 1

    rc = 0
    for pdf in pdfs:
        if args.cache_dir:
            cache_dir = args.cache_dir
        else:
            cache_dir = cache_dir_for_pdf(pdf, LIBRARY_DIR, CACHE_DIR)
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = cache_dir / f"{pdf.stem}.docling.json"
        ckpt_path = cache_dir / f"{pdf.stem}.vision-ckpt.json"

        total = pdf2img.page_count(pdf)
        first = args.first or 1
        last = min(args.last or total, total)
        if not 1 <= first <= last <= total:
            print(f"[FAIL] {pdf.name}: 页码范围 {first}-{last} 超出 1-{total}")
            rc = 1
            continue

        ckpt = {}
        if ckpt_path.exists():
            ckpt = json.loads(ckpt_path.read_text(encoding="utf-8"))

        covered = all(ckpt.get(str(n), "").strip() for n in range(first, last + 1))
        if covered and not args.force:
            _merge_checkpoint(cache_path, ckpt, first, last)
            ckpt_path.unlink(missing_ok=True)
            print(f"[DONE] {pdf.name} 页 {first}-{last} 已由 checkpoint 合并完成")
            continue
        if not covered and ckpt:
            print(f"[ckpt] {pdf.name}: 已有 {sum(1 for v in ckpt.values() if v.strip())} 页,续跑")

        # 已存在且完整且未指定范围、未 --force:跳过
        if cache_path.exists() and not args.force and not args.first and not args.last:
            try:
                existing = json.loads(cache_path.read_text(encoding="utf-8"))
                if len(existing.get("pages", [])) >= total:
                    print(f"[SKIP] {pdf.name} (缓存已完整,如需质量重建加 --force)")
                    continue
            except Exception:
                pass

        providers = config.load_providers(None)
        if args.reverse_providers:
            providers = config.load_providers([p.provider_name for p in reversed(providers)])
        elif args.chain_offset:
            k = args.chain_offset % len(providers)
            providers = config.load_providers(
                [p.provider_name for p in (providers[k:] + providers[:k])])
        models = vision_client.DEFAULT_MODELS
        proxy = None if args.no_proxy else config.get_proxy()
        print("[config] " + " → ".join(f"{p.provider_name}({p.key_hint()})" for p in providers),
              flush=True)
        print(f"[config] models: {' → '.join(models)} proxy={proxy or '(无)'}", flush=True)

        img_dir = Path(tempfile.mkdtemp(prefix="vision-cache-"))
        try:
            pages = pdf2img.render_pdf(pdf, img_dir, dpi=args.dpi, first=first, last=last)
            todo = [(str(n), p) for n, p in pages
                    if not ckpt.get(str(n), "").strip()]
            print(f"[run] {pdf.name} 页 {first}-{last},待处理 {len(todo)},batch={args.batch}",
                  flush=True)

            n_batches = 0
            n_failed = 0
            for i in range(0, len(todo), args.batch):
                chunk = todo[i:i + args.batch]
                n_batches += 1
                t0 = time.time()
                res = None
                for attempt in range(1, args.max_retries + 1):
                    try:
                        res = vision_client._send_items(
                            chunk, system=SYSTEM_PROMPT,
                            instruction="以下每张图片是一页 PDF,请按顺序逐页转写。",
                            providers=providers, models=models, proxy=proxy,
                            batch=len(chunk), split_re=vision_client._PAGE_SPLIT_RE,
                            timeout=args.timeout, max_tokens=args.max_tokens)
                        break
                    except vision_client.ApiError as e:
                        if attempt >= args.max_retries:
                            print(f"[FAIL] 第 {n_batches} 批(页 {chunk[0][0]}-{chunk[-1][0]})"
                                  f"连续 {attempt} 次失败,跳过: {e}", flush=True)
                        else:
                            wait = min(120, 15 * attempt)
                            print(f"[retry] 第 {n_batches} 批第 {attempt} 次失败({e}),"
                                  f"{wait}s 后重试", flush=True)
                            time.sleep(wait)
                if res is None:
                    n_failed += 1
                    continue
                ok = 0
                for lab, _ in chunk:
                    txt = res.get(lab, "").strip()
                    if txt:
                        ckpt[lab] = txt
                        ok += 1
                ckpt_path.write_text(json.dumps(ckpt, ensure_ascii=False, indent=1),
                                     encoding="utf-8")
                print(f"[batch {n_batches}] 页 {chunk[0][0]}-{chunk[-1][0]}: "
                      f"{time.time() - t0:.1f}s 得到 {ok}/{len(chunk)} 页,累计 "
                      f"{sum(1 for v in ckpt.values() if v.strip())}", flush=True)
        finally:
            shutil.rmtree(img_dir, ignore_errors=True)

        missing = [n for n in range(first, last + 1)
                   if not ckpt.get(str(n), "").strip()]
        if missing:
            print(f"[PARTIAL] {pdf.name}: 仍缺 {len(missing)} 页 {missing[:20]},"
                  f"重跑同命令可续", flush=True)
            rc = 2
        else:
            _merge_checkpoint(cache_path, ckpt, first, last)
            ckpt_path.unlink(missing_ok=True)
            print(f"[DONE] {pdf.name} 页 {first}-{last} 完成并合并")
    return rc


if __name__ == "__main__":
    sys.exit(main())
