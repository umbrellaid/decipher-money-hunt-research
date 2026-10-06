"""Clean a scanned/OCR'd book text into sweep-ready form.

Usage:
    uv run python normalize_text.py INPUT.txt [-o OUTPUT.txt] [--chapters]

Does four things, in this order:
  1. strips Project Gutenberg (or Standard Ebooks) licence boilerplate;
  2. folds typographic quotes/dashes/ligatures onto ASCII so letters_only()
     sees a clean A-Z stream;
  3. collapses runs of whitespace and drops empty lines;
  4. with --chapters, also writes INPUT.chapters.json listing (title, first
     char offset) for every heading it recognises, so chapter-title-chain keys
     (the Catch-22 rule) can be built.

--selftest runs a tiny built-in round trip and exits non-zero on regression.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

FOLDS = {
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "--", "\u2026": "...", "\u00a0": " ",
    "\ufb01": "fi", "\ufb02": "fl", "\uff07": "'",
}
PG_START = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.S)
PG_END = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.S)
SE_START = re.compile(r"^\s*(?:\*\*\* START OF THE PROJECT EBOOK|THE PROJECT GUTENBERG EBOOK).*?$", re.M | re.I)
HEADING = re.compile(
    r"^(?:CHAPTER|CHAP\.|BOOK|PART|SECTION)\s+(?:[IVXLC0-9]+|[A-Za-z]+)\b.*$",
    re.M | re.I,
)


def strip_boilerplate(text):
    m = PG_START.search(text)
    if m:
        text = text[m.end():]
    m = PG_END.search(text)
    if m:
        text = text[:m.start()]
    text = SE_START.sub("", text)
    return text


def fold(text):
    for a, b in FOLDS.items():
        text = text.replace(a, b)
    return unicodedata.normalize("NFKC", text)


def collapse(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def chapters(text):
    out = []
    for m in HEADING.finditer(text):
        out.append({"title": m.group(0).strip(), "offset": m.start()})
    return out


def normalize(text):
    return collapse(fold(strip_boilerplate(text)))


def selftest():
    sample = (
        "*** START OF THE PROJECT GUTENBERG EBOOK TEST ***\n"
        "CHAPTER ONE\n\nIt was a \u201cfine\u201d morning \u2014 truly.\n\n\n\n"
        "*** END OF THE PROJECT GUTENBERG EBOOK TEST ***\n"
    )
    got = normalize(sample)
    assert "START OF" not in got and "END OF" not in got, "boilerplate survived"
    assert '"fine"' in got and "--" in got, "typographic folding failed"
    assert "\n\n\n" not in got, "whitespace collapse failed"
    ch = chapters(got)
    assert ch and ch[0]["title"] == "CHAPTER ONE", "chapter detection failed"
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?")
    ap.add_argument("-o", "--output")
    ap.add_argument("--chapters", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return 0
    if not args.input:
        ap.error("input file required (or use --selftest)")
    src = Path(args.input)
    text = normalize(src.read_text(encoding="utf-8", errors="replace"))
    dst = Path(args.output) if args.output else src.with_name(src.stem + ".clean.txt")
    dst.write_text(text, encoding="utf-8")
    print(f"wrote {dst} ({len(text)} chars)")
    if args.chapters:
        cj = src.with_name(src.stem + ".chapters.json")
        cj.write_text(json.dumps(chapters(text), indent=1), encoding="utf-8")
        print(f"wrote {cj}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
