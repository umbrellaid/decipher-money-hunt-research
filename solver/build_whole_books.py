"""Concatenate per-chapter scan dirs into whole-book texts for sweep.py.

sweep.py slides the numbering origin across an entire book; body_scan.py only
tests contiguous windows of <=N chapters. The era-verified CZUR scans in
texts/<book>/ are stored one file per chapter, so they have never been through
a full sliding-origin sweep. This builds texts/wholebooks/<book>.txt so they
can be.

Chapter numbering matters: a book cipher's indices address the complete text,
so a concatenation with missing chapters yields wrong numbering past the first
gap. Gaps are therefore reported and the book is marked NOT SWEEP-ABLE rather
than silently swept.

Usage (from repo root):
    uv run solver/build_whole_books.py            # build all, report
    uv run solver/build_whole_books.py --list     # report only, write nothing
"""
import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TEXTS = ROOT / "texts"
OUT = TEXTS / "wholebooks"

# Not books, or superseded, or already swept at whole-book grade.
SKIP_DIRS = {
    "model",        # trigram scorer corpus - must never be swept
    "pd",           # 49 PD texts, already whole-book files, swept campaigns 1-2
    "poe",          # 9 whole-work files, swept campaigns 1-2 (~5M positions)
    "wholebooks",   # our own output
}
SKIP_PREFIXES = ("ia-prescreen",)          # ebook/IA grade, already screened
SUPERSEDED = {                              # replaced by a later rescan
    "foundation_new": "foundation2",
    "foundation_v1_2026-10-21": "foundation2",
    "the-thorn-birds-old-2026-10-24": "the-thorn-birds",
    # v1 was OCR'd from ScanTailor's mangled split (each half-image held most of
    # BOTH pages); v2 re-OCR'd the correct preprocess_spreads output and recovered
    # 51 of the 82 lost chapter markers. Still not contiguous - see scan_log.
    "cats-cradle": "cats-cradle-v2",
}

CHAP_FILE = re.compile(r"^ch(\d+)(?:_.*)?\.txt$", re.I)


def natkey(p):
    m = CHAP_FILE.match(p.name)
    return (0, int(m.group(1)), p.name) if m else (1, 0, p.name)


def chapter_files(d):
    return sorted((p for p in d.iterdir() if CHAP_FILE.match(p.name)), key=natkey)


def find_gaps(files):
    """Missing integers in the ch-numbering, and any non-ch* file skipped."""
    nums = [int(CHAP_FILE.match(p.name).group(1)) for p in files]
    missing = []
    if nums:
        lo, hi = min(nums), max(nums)
        seen = set(nums)
        missing = [n for n in range(lo, hi + 1) if n not in seen]
    dupes = sorted({n for n in nums if nums.count(n) > 1})
    return missing, dupes


def wordcount(s):
    return len(re.findall(r"[A-Za-z]+", s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="report only, write nothing")
    args = ap.parse_args()

    dirs = sorted(
        d for d in TEXTS.iterdir()
        if d.is_dir()
        and d.name not in SKIP_DIRS
        and not d.name.startswith(SKIP_PREFIXES)
    )

    if not args.list:
        OUT.mkdir(exist_ok=True)

    rows = []
    for d in dirs:
        files = chapter_files(d)
        note = ""
        if d.name in SUPERSEDED:
            note = f"SUPERSEDED by {SUPERSEDED[d.name]}"
        if not files:
            loose = sorted(p.name for p in d.glob("*.txt"))
            rows.append((d.name, 0, 0, [], [], note or f"no ch*.txt (has: {', '.join(loose[:4])}...)"))
            continue
        missing, dupes = find_gaps(files)
        text = "\n".join(
            p.read_text(encoding="utf-8", errors="replace") for p in files
        )
        wc = wordcount(text)
        if note:
            pass
        elif missing:
            note = f"NOT SWEEP-ABLE - {len(missing)} missing chapter(s): {missing[:12]}{'...' if len(missing) > 12 else ''}"
        elif dupes:
            note = f"CHECK - duplicate chapter numbers {dupes}"
        else:
            note = "contiguous - sweep-able"
        rows.append((d.name, len(files), wc, missing, dupes, note))
        if not args.list and not missing and not dupes and d.name not in SUPERSEDED:
            dst = OUT / f"{d.name}.txt"
            dst.write_text(text, encoding="utf-8")

    w = max(len(r[0]) for r in rows)
    print(f"{'book dir'.ljust(w)}  files    words  verdict")
    print("-" * (w + 60))
    for name, nf, wc, missing, dupes, note in rows:
        print(f"{name.ljust(w)}  {nf:5d}  {wc:7d}  {note}")
    if not args.list:
        built = sorted(p.name for p in OUT.glob("*.txt")) if OUT.exists() else []
        print(f"\nwrote {len(built)} whole-book text(s) to {OUT.relative_to(ROOT)}: {', '.join(built)}")
        print("next: uv run solver/normalize_text.py texts/wholebooks/<book>.txt --chapters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
