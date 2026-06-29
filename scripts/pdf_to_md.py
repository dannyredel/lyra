#!/usr/bin/env python
"""Convert a PDF to markdown once, optionally split by chapter — so we read text, not page images.

Why: reading PDFs through the assistant's image-based reader costs vision tokens per page. Convert
to markdown here, commit the .md, then only ever read the .md. See paper-library/PROCESSING.md.

Usage:
    python scripts/pdf_to_md.py "paper-library/pdfs/00-foundational/Causal Inference - Stefan Wager (Nov 2025).pdf"
    python scripts/pdf_to_md.py <pdf> --out paper-library/md/00-foundational/wager-causal-inference
    python scripts/pdf_to_md.py <pdf> --whole            # single file, no chapter split

Splits on level-1 table-of-contents bookmarks when present; otherwise writes one file (or use
--chunk N to split every N pages). Requires: pip install -e ".[papers]"  (pymupdf4llm + pymupdf).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def _slug(s: str) -> str:
    s = re.sub(r"[^\w\s-]", "", s).strip().lower()
    return re.sub(r"[\s_-]+", "-", s)[:60] or "section"


def convert(pdf_path: Path, out_dir: Path, whole: bool, chunk: int) -> None:
    import pymupdf  # type: ignore

    # pymupdf4llm >=1.27 bundles an onnx layout model that can fail on some machines
    # (int32/int64 dtype mismatch in table detection). Force the classic extractor and turn
    # tables off; fall back to plain pymupdf get_text if it still errors.
    try:
        import pymupdf4llm  # type: ignore
        if hasattr(pymupdf4llm, "_use_layout"):
            pymupdf4llm._use_layout = False
    except ImportError:
        pymupdf4llm = None

    def extract(doc, pages):
        if pymupdf4llm is not None:
            try:
                return pymupdf4llm.to_markdown(doc, pages=pages, table_strategy=None, show_progress=False)
            except Exception as exc:  # noqa: BLE001 — onnx/layout breakage varies by machine
                print(f"  (pymupdf4llm failed: {type(exc).__name__}; using plain text extractor)")
        # Robust fallback: plain text per page, no ML, math may be approximate.
        return "\n\n".join(doc[p].get_text("text") for p in pages)

    out_dir.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(pdf_path)
    n = doc.page_count
    toc = [] if (whole or chunk) else doc.get_toc()  # [[level, title, page1based], ...]

    # Build (title, start_page0, end_page0_inclusive) segments.
    segments: list[tuple[str, int, int]] = []
    if toc:
        tops = [(t, p - 1) for lvl, t, p in toc if lvl == 1 and 1 <= p <= n]
        for k, (title, start) in enumerate(tops):
            end = (tops[k + 1][1] - 1) if k + 1 < len(tops) else n - 1
            if end >= start:
                segments.append((title, start, end))
    if not segments:
        if chunk:
            for k, start in enumerate(range(0, n, chunk)):
                segments.append((f"pages-{start+1}-{min(start+chunk, n)}", start, min(start + chunk, n) - 1))
        else:
            segments.append((pdf_path.stem, 0, n - 1))

    print(f"{pdf_path.name}: {n} pages -> {len(segments)} segment(s) in {out_dir}")
    for k, (title, start, end) in enumerate(segments):
        pages = list(range(start, end + 1))
        md = extract(doc, pages)
        name = f"{k:02d}-{_slug(title)}.md"
        (out_dir / name).write_text(f"<!-- {pdf_path.name} | pages {start+1}-{end+1} | {title} -->\n\n{md}",
                                    encoding="utf-8")
        print(f"  wrote {name}  (pages {start+1}-{end+1})")


def main() -> None:
    ap = argparse.ArgumentParser(description="PDF -> markdown (optionally per chapter)")
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--out", type=Path, default=None, help="output dir (default: paper-library/md/<pdf-stem>)")
    ap.add_argument("--whole", action="store_true", help="one .md, ignore TOC")
    ap.add_argument("--chunk", type=int, default=0, help="split every N pages instead of by TOC")
    args = ap.parse_args()

    out = args.out or Path("paper-library/md") / _slug(args.pdf.stem)
    try:
        convert(args.pdf, out, args.whole, args.chunk)
    except ImportError:
        raise SystemExit("Missing deps. Run:  pip install -e \".[papers]\"  (pymupdf4llm + pymupdf)")


if __name__ == "__main__":
    main()
