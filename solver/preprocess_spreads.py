# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow", "numpy"]
# ///
"""
preprocess_spreads.py
=====================
CZUR Aura full-frame spread -> clean single-page JPGs for ocr_ingest.py.

Session 2026-10-26 produced 4320x3240 landscape captures with the open book
sitting bottom-center on a black desk mat (hands entering at the lower
edges). ScanTailor Advanced mangled that batch (12% blank/inverted pages,
2x upscale, baked-in bilevel), so this script replaces it with three cheap,
auditable steps per capture:

  1. locate the bright page region (paper is bright, the mat is black);
  2. find the gutter (darkest column valley near the region center) and
     split there -- or keep the whole region when no valley exists
     (covers, single-page front matter);
  3. crop, paste onto a white canvas with a small border, upscale 2x
     (pages are only ~1040 px wide in the raw frame -- roughly 250 DPI --
     and Tesseract gains several confidence points from larger glyphs).

Output naming matches ocr_ingest.py --split-spreads conventions:
  image00020_1L.jpg / image00020_2R.jpg   (split spread, left page first)
  image00021.jpg                          (no gutter found: single page)

Usage:
    uv run solver/preprocess_spreads.py --raw-dir <spreads> --out-dir <pages>
        [--thresh 70] [--margin 24] [--scale 2] [--min-valley 0.90]
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def natural_key(path: Path) -> list:
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", path.stem)]


def largest_run(mask: np.ndarray, min_len: int) -> tuple[int, int] | None:
    """Longest contiguous True run of at least min_len."""
    best: tuple[int, int] | None = None
    best_len = 0
    start = None
    for i, v in enumerate(mask):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start > best_len and i - start >= min_len:
                best, best_len = (start, i), i - start
            start = None
    if start is not None and len(mask) - start > best_len and len(mask) - start >= min_len:
        best = (start, len(mask))
    return best


def smooth(x: np.ndarray, win: int) -> np.ndarray:
    if win <= 1:
        return x
    k = np.ones(win) / win
    return np.convolve(x, k, mode="same")


def find_book_span(gray: np.ndarray) -> tuple[int, int, int] | None:
    """Column span of the open book: (c0, c1, threshold_used).

    Primary pass: paper is bright (>160) and the textured mat stays under a
    0.3 column-bright-fraction; that separates the book cleanly on body-text
    spreads. Fallback (dark covers, title pages): >100 with a 0.15 fraction,
    which is noisier but only ever runs on single-page captures.
    """
    for thr, frac in ((160, 0.3), (100, 0.15)):
        col = smooth((gray > thr).mean(axis=0), 25)
        span = largest_run(col > frac, min_len=600)
        if span is not None:
            return span[0], span[1], thr
    return None


def process_image(path: Path, out_dir: Path, thresh: int, margin: int,
                  scale: int, min_span_split: int, min_valley: float) -> dict:
    im = Image.open(path)
    gray = np.array(im.convert("L"), dtype=np.uint8)

    span = find_book_span(gray)
    if span is None:
        return {"image": path.name, "action": "SKIP (no book region found)"}
    c0, c1, thr_used = span

    row_frac = smooth((gray > thr_used)[:, c0:c1].mean(axis=1), 25)
    rspan = largest_run(row_frac > 0.25, min_len=800)
    if rspan is None:
        return {"image": path.name, "action": "SKIP (no page rows found)"}
    r0, r1 = rspan

    def save_page(box: tuple[int, int, int, int], dest: Path) -> None:
        page = im.convert("RGB").crop(box)
        pw, ph = page.size
        canvas = Image.new("RGB", (pw + 2 * margin, ph + 2 * margin), "white")
        canvas.paste(page, (margin, margin))
        if scale != 1:
            canvas = canvas.resize((canvas.width * scale, canvas.height * scale),
                                   Image.LANCZOS)
        canvas.save(dest, quality=92)

    # One page at ~250 DPI is ~1000-1300 px wide; an open spread is ~2000+.
    # Narrow span -> single-page capture (cover, front-matter page).
    if c1 - c0 < min_span_split:
        save_page((c0, r0, c1, r1), out_dir / f"{path.stem}.jpg")
        return {"image": path.name, "action": "single",
                "span_w": int(c1 - c0), "page_h": int(r1 - r0)}

    # Spread: split near the span center. Refine to the darkest column valley
    # (30th percentile -- gutter shadows hit percentiles harder than means)
    # within the central +/-12%; text density creates false valleys elsewhere.
    # Inner margins are ~150 px, so a center split cannot clip text even with
    # placement wobble.
    center = c0 + (c1 - c0) // 2
    win = int((c1 - c0) * 0.12)
    prof = smooth(np.percentile(gray[r0:r1, c0:c1], 30, axis=0).astype(np.float32), 21)
    lo, hi = center - win - c0, center + win - c0
    vi = lo + int(np.argmin(prof[lo:hi]))
    valley_ratio = float(prof[vi]) / max(float(np.median(prof)), 1.0)
    gutter = c0 + vi if valley_ratio < min_valley else center
    save_page((c0, r0, gutter, r1), out_dir / f"{path.stem}_1L.jpg")
    save_page((gutter, r0, c1, r1), out_dir / f"{path.stem}_2R.jpg")
    return {"image": path.name, "action": "split",
            "gutter_x": int(gutter), "valley_ratio": round(valley_ratio, 3),
            "span_w": int(c1 - c0), "page_h": int(r1 - r0),
            "page_w": [int(gutter - c0), int(c1 - gutter)]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    ap.add_argument("--raw-dir", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--thresh", type=int, default=70,
                    help="paper-brightness threshold 0-255 (default 70)")
    ap.add_argument("--margin", type=int, default=24,
                    help="white border in px before upscale (default 24)")
    ap.add_argument("--scale", type=int, default=2,
                    help="upscale factor (default 2)")
    ap.add_argument("--min-span-split", type=int, default=1400,
                    help="bright-span width in px at/above which a spread is split (default 1400)")
    ap.add_argument("--min-valley", type=float, default=0.88,
                    help="p30 valley/median ratio below which the valley refines the split (default 0.88)")
    args = ap.parse_args()

    images = sorted(
        [p for p in args.raw_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}],
        key=natural_key,
    )
    if not images:
        sys.exit(f"no images found in {args.raw_dir}")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for i, img in enumerate(images, 1):
        try:
            r = process_image(img, args.out_dir, args.thresh, args.margin,
                              args.scale, args.min_span_split, args.min_valley)
        except Exception as e:  # keep the batch going; QA catches bad pages
            r = {"image": img.name, "action": f"ERROR ({e})"}
        rows.append(r)
        print(f"[{i}/{len(images)}] {r['image']}: {r['action']}"
              + (f" valley={r.get('valley_ratio')}" if r.get("valley_ratio") else ""))

    with open(args.out_dir / "pages_manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["image", "action", "gutter_x",
                                          "valley_ratio", "span_w", "page_w", "page_h"])
        w.writeheader()
        w.writerows(rows)

    n_split = sum(1 for r in rows if r["action"] == "split")
    n_single = sum(1 for r in rows if r["action"] == "single")
    n_bad = sum(1 for r in rows if r["action"].startswith(("SKIP", "ERROR")))
    print(f"done: {n_split} split, {n_single} single, {n_bad} skipped/errored")
    print(f"manifest: {args.out_dir / 'pages_manifest.csv'}")


if __name__ == "__main__":
    main()
