# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow"]
# ///
"""
ocr_ingest.py
=============
OCR ingest for CZUR Aura scans (see scanning-workflow-czur-2026-10-18.md).

Turns a folder of CZUR page JPGs into the per-chapter plain-text files that
solver/body_scan.py consumes, plus a QA report so bad pages get re-scanned
before we trust any cipher result.

Pipeline per page image:
  tesseract <img> stdout --psm N tsv   ->   words with bounding boxes +
  per-word confidence -> lines rebuilt in reading order -> page text.

Chapters are assigned with a small CSV map the operator writes after
scanning (one row per chapter start):

    start_image,chapter,label
    scan001.jpg,1,The Psychohistorians
    scan018.jpg,2,The Encyclopedists

Every page from a start image up to (but excluding) the next start image
belongs to that chapter. Pages before the first start row go to ch00_front
(front matter — kept, body_scan ignores it unless aimed at it).

Outputs (default --out-dir texts/<book>/ under the repo root):
  ch01.txt, ch02.txt ...        clean chapter text (pages joined, dehyphenated)
  qa_report.md                  per-page mean confidence, low-confidence word
                                lists, and RESCAN flags
  pages_index.csv               image -> chapter, mean confidence

Spread handling: the CZUR Aura in Facing Pages mode normally saves one
already-split JPG per page. If a batch ever comes out as one image per
two-page SPREAD, pass --split-spreads to cut each image down the middle
(left page first).

Usage (from the repo root):
    uv run solver/ocr_ingest.py --book foundation ^
        --raw-dir C:/c_working_area/puzzle_work/scans/foundation/raw ^
        --map     C:/c_working_area/puzzle_work/scans/foundation/chapters.csv
    uv run solver/ocr_ingest.py --book cats_cradle --raw-dir ... --map ... --psm 4
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

TESSERACT_CANDIDATES = [
    os.environ.get("TESSERACT_CMD", ""),
    shutil.which("tesseract") or "",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Users\David Recor\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
]

REPO_ROOT = Path(__file__).resolve().parent.parent


def find_tesseract() -> str:
    for cand in TESSERACT_CANDIDATES:
        if cand and Path(cand).exists():
            return cand
    sys.exit(
        "tesseract binary not found. Install the UB Mannheim Windows build or "
        "set TESSERACT_CMD to the exe path."
    )


def natural_key(path: Path) -> list[int | str]:
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", path.stem)]


@dataclass
class PageResult:
    image: str
    text: str
    mean_conf: float
    n_words: int
    low_conf: list[str] = field(default_factory=list)


def split_spread(img_path: Path, tmpdir: Path) -> list[Path]:
    """Cut a two-page spread into left/right page images (left first)."""
    from PIL import Image

    im = Image.open(img_path)
    w, h = im.size
    left = im.crop((0, 0, w // 2, h))
    right = im.crop((w // 2, 0, w, h))
    lp = tmpdir / f"{img_path.stem}_L.jpg"
    rp = tmpdir / f"{img_path.stem}_R.jpg"
    left.save(lp, quality=95)
    right.save(rp, quality=95)
    return [lp, rp]


def ocr_page(tesseract: str, img: Path, psm: int, dehyphenate: bool,
             strip_header: tuple[str, ...] = ()) -> PageResult:
    """Run tesseract TSV on one page image; rebuild text in reading order.

    strip_header: regexes; if the FIRST rebuilt line matches any of them and
    is short (<= 8 tokens) it is dropped as a running header ("I, ROBOT",
    "THE HIGHWAY", "cat's cradle" after page numbers were filtered).
    """
    proc = subprocess.run(
        [tesseract, str(img), "stdout", "--psm", str(psm), "tsv"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        return PageResult(img.name, "", 0.0, 0, [f"TESSERACT_ERROR: {proc.stderr.strip()[:120]}"])

    rows = list(csv.DictReader(proc.stdout.splitlines(), delimiter="\t"))
    words = [
        r for r in rows
        if r.get("text", "").strip() and float(r.get("conf", "-1")) >= 0
    ]
    # group into lines: (block, par, line) -> list of (left, text, conf)
    # NOTE: do NOT include `top` in the key — Tesseract reports slightly
    # different top-pixel values for words on the same physical line,
    # which splits one line into many groups and scrambles word order.
    lines: dict[tuple[int, int, int], list[tuple[int, str, float]]] = {}
    line_top: dict[tuple[int, int, int], int] = {}
    for r in words:
        txt = r["text"].strip()
        # skip pure-numeric tokens and TSV artifacts (coordinate strings)
        if not txt or txt.isdigit() or re.match(r"^-?\d+$", txt):
            continue
        key = (int(r["block_num"]), int(r["par_num"]), int(r["line_num"]))
        lines.setdefault(key, []).append((int(r["left"]), txt, float(r["conf"])))
        if key not in line_top:
            line_top[key] = int(r["top"])
    ordered_keys = sorted(lines, key=lambda k: (line_top.get(k, 0), k[0], k[1], k[2]))
    out_lines: list[str] = []
    confs: list[float] = []
    low: list[str] = []
    for k in ordered_keys:
        toks = sorted(lines[k])
        line_text = " ".join(t for _, t, _ in toks)
        if (strip_header and not out_lines and len(toks) <= 8
                and any(re.search(rx, line_text) for rx in strip_header)):
            continue  # running header line: drop entirely
        confs.extend(c for _, _, c in toks)
        low.extend(t for _, t, c in toks if c < 60 and len(t) > 2)
        out_lines.append(line_text)
    text = "\n".join(out_lines)
    if dehyphenate:
        # join words broken across lines: "encyclo-\npedia" -> "encyclopedia"
        text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
        text = text.replace("\n", " ")
    else:
        text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    mean = sum(confs) / len(confs) if confs else 0.0
    return PageResult(img.name, text, round(mean, 1), len(confs), low[:25])


def load_map(map_path: Path) -> list[tuple[str, int, str]]:
    with open(map_path, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r.get("start_image")]
    return [(r["start_image"].strip(), int(r["chapter"]), r.get("label", "").strip()) for r in rows]


def main() -> None:
    ap = argparse.ArgumentParser(description="OCR CZUR scans into per-chapter txt for body_scan.py")
    ap.add_argument("--book", required=True, help="book slug, e.g. foundation")
    ap.add_argument("--raw-dir", required=True, type=Path, help="folder of CZUR JPGs in reading order")
    ap.add_argument("--map", required=True, type=Path, help="CSV: start_image,chapter,label")
    ap.add_argument("--out-dir", type=Path, default=None, help="default: <repo>/texts/<book>/")
    ap.add_argument("--psm", type=int, default=6, help="tesseract page segmentation mode (default 6)")
    ap.add_argument("--split-spreads", action="store_true", help="cut each image into left/right pages")
    ap.add_argument("--keep-hyphens", action="store_true", help="do not join line-broken words")
    ap.add_argument("--strip-header", action="append", default=[],
                    help="regex; drop the page's first line when it matches (running head). "
                         "Repeatable, e.g. --strip-header 'I,? ROBOT' --strip-header 'THE HIGHWAY'")
    ap.add_argument("--dedup", action="store_true",
                    help="drop duplicate re-scans: consecutive pages with word-set Jaccard "
                         ">= 0.75 keep only the higher-confidence capture")
    args = ap.parse_args()

    tesseract = find_tesseract()
    out_dir = args.out_dir or (REPO_ROOT / "texts" / args.book)
    out_dir.mkdir(parents=True, exist_ok=True)

    images = sorted(
        [p for p in args.raw_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}],
        key=natural_key,
    )
    if not images:
        sys.exit(f"no images found in {args.raw_dir}")

    page_files: list[Path] = []
    with tempfile.TemporaryDirectory() as td:
        tmpdir = Path(td)
        for img in images:
            if args.split_spreads:
                page_files.extend(split_spread(img, tmpdir))
            else:
                page_files.append(img)

        print(f"OCR-ing {len(page_files)} page images (psm {args.psm}) ...")
        pages = [ocr_page(tesseract, p, args.psm, not args.keep_hyphens,
                          tuple(args.strip_header)) for p in page_files]

    if args.dedup:
        # duplicate re-scans: near-identical word sets among the last few
        # pages; keep the higher-confidence capture (retakes usually follow
        # the bad take, but confidence is the safer arbiter)
        kept: list[PageResult] = []
        dropped = []
        for pr in pages:
            words = {w.lower().strip(".,;:!?\"'") for w in pr.text.split()}
            dup_of = None
            if words and pr.n_words > 20:
                for prev in kept[-3:]:
                    pw = {w.lower().strip(".,;:!?\"'") for w in prev.text.split()}
                    if pw and len(words & pw) / max(len(words | pw), 1) >= 0.75:
                        dup_of = prev
                        break
            if dup_of is None:
                kept.append(pr)
            elif pr.mean_conf >= dup_of.mean_conf:
                kept[kept.index(dup_of)] = pr  # better retake replaces the original
                dropped.append(dup_of.image)
            else:
                dropped.append(pr.image)
        print(f"dedup: dropped {len(dropped)} duplicate re-scans: {dropped}")
        pages = kept

    # chapter assignment
    starts = load_map(args.map)
    start_idx = {name: (ch, label) for name, ch, label in starts}
    chapters: dict[int, dict] = {}
    cur_ch, cur_label = 0, "front_matter"
    for pr in pages:
        if pr.image in start_idx:
            cur_ch, cur_label = start_idx[pr.image]
        entry = chapters.setdefault(cur_ch, {"label": cur_label, "pages": []})
        entry["pages"].append(pr)

    for ch in sorted(chapters):
        entry = chapters[ch]
        body = "\n\n".join(p.text for p in entry["pages"] if p.text)
        name = f"ch{ch:02d}.txt" if ch > 0 else "ch00_front.txt"
        (out_dir / name).write_text(body, encoding="utf-8")
        print(f"  wrote {name}: {len(entry['pages'])} pages, {len(body.split())} words")

    # QA report
    qa = ["# OCR QA report", f"book: {args.book}", f"psm: {args.psm}", "",
          "| page image | chapter | words | mean conf | flag |",
          "|---|---|---|---|---|"]
    rescan = 0
    page_ch = {}
    cur_ch = 0
    for pr in pages:
        if pr.image in start_idx:
            cur_ch = start_idx[pr.image][0]
        page_ch[pr.image] = cur_ch
        flag = ""
        if pr.mean_conf < 85 and pr.n_words > 20:
            flag = "RESCAN (low confidence)"
            rescan += 1
        if pr.n_words == 0:
            flag = "RESCAN (no text)"
            rescan += 1
        qa.append(f"| {pr.image} | ch{page_ch[pr.image]:02d} | {pr.n_words} | {pr.mean_conf} | {flag} |")
    qa.append("")
    for pr in pages:
        if pr.low_conf:
            qa.append(f"## low-confidence words — {pr.image}")
            qa.append(", ".join(pr.low_conf))
            qa.append("")
    (out_dir / "qa_report.md").write_text("\n".join(qa), encoding="utf-8")

    with open(out_dir / "pages_index.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["image", "chapter", "n_words", "mean_conf"])
        for pr in pages:
            w.writerow([pr.image, f"ch{page_ch[pr.image]:02d}", pr.n_words, pr.mean_conf])

    print(f"QA report: {out_dir / 'qa_report.md'}")
    print(f"pages flagged for rescan: {rescan} / {len(pages)}")


if __name__ == "__main__":
    main()
