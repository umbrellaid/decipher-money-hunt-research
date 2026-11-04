# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
check_ii1_witness.py — which printing of the 2-1 source paragraph does a free
e-text actually carry?

Eckman (2026, https://doi.org/10.5281/zenodo.23844582) section 5 documents two
witnesses of the tailor paragraph from *Gulliver's Travels* Part III ch. 2: the
Alden (1911) text at **492** normalized letters, which is the printed clue, and a
Wikisource transcription attributed to an 1801 edition at **490**.

This script adds a third data point on the e-text most likely to be swept: Project
Gutenberg #829 normalizes to **491**. It differs from the Alden witness at two
independent places, so it is not simply Eckman's 490 variant either.

That matters for `docs/methodology.md` gap 1. The 492 clue discriminates between
printings, and the most widely distributed free e-text satisfies neither published
witness — so a sweep of it would have missed on alignment before any question of
rule family arose.

Network access is required. Run from the repository root:

    uv run solver/check_ii1_witness.py [--url URL]

Compares against `data/gulliver_ii1_passage.txt` and exits nonzero if the
downloaded witness does not normalize to 492 letters, which is the finding, not a
failure of the script.
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PASSAGE = ROOT / "data" / "gulliver_ii1_passage.txt"
DEFAULT_URL = "https://www.gutenberg.org/cache/epub/829/pg829.txt"
ANCHOR = "ordered a tailor to come next morning"
CLUE_LENGTH = 492


def normalize(s: str) -> str:
    """NFKD, uppercase, retain ASCII A-Z (the paper's normalization)."""
    return "".join(c for c in unicodedata.normalize("NFKD", s).upper() if "A" <= c <= "Z")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "decipher-research/1.0"})
    return urllib.request.urlopen(req, timeout=90).read().decode("utf-8", "replace")


def find_paragraph(raw: str) -> str:
    flat_anchor = ANCHOR
    for para in re.split(r"\n\s*\n", raw):
        if para.strip() and flat_anchor in para.replace("\n", " "):
            return para
    raise SystemExit(f"anchor paragraph not found: {flat_anchor!r}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=DEFAULT_URL)
    args = ap.parse_args()

    if not PASSAGE.is_file():
        sys.exit(f"Missing {PASSAGE}.")
    alden = normalize(PASSAGE.read_text(encoding="utf-8"))

    raw = fetch(args.url)
    para = find_paragraph(raw)
    other = normalize(para)

    print(f"url            : {args.url}")
    print(f"downloaded     : {len(raw)} chars")
    print(f"Alden witness  : {len(alden)} normalized letters")
    print(f"this witness   : {len(other)} normalized letters")
    print(f"delta          : {len(other) - len(alden):+d}")
    print(f"matches the 492 clue: {len(other) == CLUE_LENGTH}")

    print("\nverbatim paragraph:")
    print(para.strip())

    print("\ndifferences from the Alden witness (normalized):")
    sm = difflib.SequenceMatcher(None, alden, other, autojunk=False)
    diffs = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        diffs += 1
        print(f"  {tag:8s} Alden[{i1}:{i2}]={alden[i1:i2]!r}  other[{j1}:{j2}]={other[j1:j2]!r}")
    if not diffs:
        print("  none — identical normalization")

    print("\ndecisive phrase:")
    flat = para.replace("\n", " ").lower()
    print(f"  'take my measure' present: {'take my measure' in flat}")
    print(f"  'take measure' present   : {'take measure' in flat}")

    print("\nfirst divergence at normalized position ", end="")
    for i, (x, y) in enumerate(zip(alden, other)):
        if x != y:
            print(f"{i + 1} (Alden={x!r} other={y!r})")
            print(f"  Alden: ...{alden[max(0, i - 24):i]}[{x}]{alden[i + 1:i + 25]}...")
            print(f"  other: ...{other[max(0, i - 24):i]}[{y}]{other[i + 1:i + 25]}...")
            break
    else:
        print(f"none within the first {min(len(alden), len(other))} letters")

    return 0 if len(other) == CLUE_LENGTH else 1


if __name__ == "__main__":
    sys.exit(main())
