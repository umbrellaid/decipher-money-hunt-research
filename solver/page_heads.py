# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow"]
# ///
"""
page_heads.py
=============
Quick per-page OCR pass over preprocessed page images to help the operator
write chapters.csv maps for ocr_ingest.py.

For every page JPG it records: a head snippet (first words), a tail snippet,
and the best-guess printed page number (standalone 1-3 digit token in the
first or last few header words -- mass-market headers look like
"146 cat's cradle" / "DOCTOR ZHIVAGO 145"). Downscale factor keeps the pass
fast; this is for mapping and gap detection, not final text.

Output: <out-dir>/page_heads.csv with columns file,page_no,head,tail

Usage:
    uv run solver/page_heads.py --pages-dir <book>/pages --scale 0.5
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TESSERACT_CANDIDATES = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Users\David Recor\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
]


def find_tesseract() -> str:
    import shutil
    for cand in TESSERACT_CANDIDATES + [shutil.which("tesseract") or ""]:
        if cand and Path(cand).exists():
            return cand
    sys.exit("tesseract not found")


def natural_key(path: Path) -> list:
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", path.stem)]


def page_number(tokens: list[str]) -> str:
    """Standalone 1-3 digit number near the start or end of the header."""
    for t in tokens[:6]:
        if re.fullmatch(r"\d{1,3}", t):
            return t
    for t in reversed(tokens[-6:]):
        if re.fullmatch(r"\d{1,3}", t):
            return t
    return ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages-dir", required=True, type=Path)
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--psm", type=int, default=6)
    args = ap.parse_args()

    tess = find_tesseract()
    images = sorted(
        [p for p in args.pages_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}],
        key=natural_key,
    )
    if not images:
        sys.exit(f"no images in {args.pages_dir}")

    from PIL import Image

    rows = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "p.jpg"
        for i, img in enumerate(images, 1):
            im = Image.open(img)
            if args.scale != 1:
                im = im.resize((int(im.width * args.scale), int(im.height * args.scale)),
                               Image.LANCZOS)
            im.save(tmp, quality=85)
            proc = subprocess.run([tess, str(tmp), "stdout", "--psm", str(args.psm)],
                                  capture_output=True, text=True,
                                  encoding="utf-8", errors="replace")
            tokens = [t for t in proc.stdout.split() if t.strip()]
            clean = [t for t in tokens if not re.fullmatch(r"[^A-Za-z0-9]+", t)]
            rows.append({
                "file": img.name,
                "page_no": page_number(clean),
                "head": " ".join(clean[:14]),
                "tail": " ".join(clean[-10:]),
            })
            if i % 25 == 0:
                print(f"  {i}/{len(images)} ...", flush=True)

    out = args.pages_dir / "page_heads.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file", "page_no", "head", "tail"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out} ({len(rows)} pages)")


if __name__ == "__main__":
    main()
