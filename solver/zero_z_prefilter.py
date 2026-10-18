# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
zero_z_prefilter.py
===================
Cheap crib-based pre-filter for scanned/OCR'd book chapters, implementing the
"zero-Z" idea from the 2026-10-17 Gemini follow-up (see
results/gemini-toc-test-2026-10-17.md):

  Warren Holland left literal letters (E, Z, Y...) in the ciphertext when the
  plaintext letter had no position to reference in the keytext. Puzzle 3-1
  contains literal Z's, so a 3-1 keytext should contain NO 'Z' inside its first
  N_max letters/words. Any scanned chapter whose opening window contains Z is
  flagged (strictly: rejected) for 3-1 without needing a full decode run.

For every scanned .txt this reports, per unsolved cipher:
  - Z-count inside the first N_max chars and first N_max words of each stream
  - coverage (fraction of codenumbers addressable by the stream)
  - best English fitness score across the standard stream families
  - the Puzzle 3-1 double-letter check (487,487 -> doubleable letter)

Usage (from repo root):
    uv run solver/zero_z_prefilter.py --scan-dir texts/pd
    uv run solver/zero_z_prefilter.py --scan-dir ./my_scans --strict
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import toc_and_clue_tester as T  # noqa: E402

REPO = Path(__file__).resolve().parent.parent

# Corrected N_max values (repo data/ciphers.json)
PUZZLES: dict[str, dict] = {
    "3-1": {"n_max": 516, "cribs": "E,E,E,Z,E,E (two Z's)"},
    "3-2": {"n_max": 416, "cribs": "E,Y,E,Y,E"},
    "3-3": {"n_max": 721, "cribs": "E,E,E"},
    "2-4": {"n_max": 1053, "cribs": "none (multiples-of-100 run)"},
}


def load_ciphertexts() -> dict[str, list[int | str]]:
    cj = json.loads((REPO / "data" / "ciphers.json").read_text(encoding="utf-8"))
    return {
        name: [int(t) if str(t).isdigit() else str(t) for t in cj[key]]
        for key, name in [("3-1", "3-1"), ("3-2", "3-2"), ("3-3", "3-3"), ("2-4", "2-4")]
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Zero-Z crib pre-filter for scanned chapters")
    parser.add_argument("--scan-dir", type=Path, required=True,
                        help="Directory of OCR'd .txt chapter scans")
    parser.add_argument("--strict", action="store_true",
                        help="Strict mode: any Z inside the window is a hard REJECT for 3-1")
    args = parser.parse_args()

    ciphers = load_ciphertexts()
    txt_files = sorted(args.scan_dir.glob("*.txt"))
    if not txt_files:
        print(f"[!] No .txt files in {args.scan_dir}")
        return

    print("=" * 96)
    print("ZERO-Z PREFILTER — cheap crib screening of scanned chapters")
    print("Rule: literal Z cribs in Puzzle 3-1 imply the keytext window (first N_max=516")
    print("letters/words) contains NO Z. Flagged = Z found inside the window.")
    print("=" * 96)
    header = (f"{'File':<28} | {'Z@516c':>6} {'Z@516w':>6} | {'Z@416c':>6} | {'Z@721c':>6} "
              f"| {'Z@1053c':>7} | {'Cov3-1':>6} | {'Sc3-1':>6} | {'Sc3-2':>6} | {'Verdict (3-1)'}")
    print(header)
    print("-" * 96)

    n_flagged = 0
    for f in txt_files:
        raw = f.read_text(encoding="utf-8", errors="ignore")
        streams = T.generate_body_text_streams(f.stem, raw)

        # Z-counts in the fixed windows of the char/word streams
        chars_fwd = streams[f"{f.stem}|Chars|Fwd"]
        words_fwd = T.tokenize_words(raw)
        z_516c = chars_fwd[:516].count("Z")
        z_516w = sum(1 for w in words_fwd[:516] if "Z" in w)
        z_416c = chars_fwd[:416].count("Z")
        z_721c = chars_fwd[:721].count("Z")
        z_1053c = chars_fwd[:1053].count("Z")

        # Coverage + best English score per puzzle across all streams
        best = {}
        cov31 = 0.0
        for p in PUZZLES:
            best[p] = -999.0
        for sid, stream in streams.items():
            if len(stream) < 120:
                continue
            for p, ctext in ciphers.items():
                decoded, cov = T.decode_with_key(ctext, stream, drift=0)
                if p == "3-1":
                    cov31 = max(cov31, cov)
                for cand in (decoded, decoded[::-1]):
                    sc = T.score_english(cand)
                    if sc > best[p]:
                        best[p] = sc

        reject31 = z_516c > 0 or z_516w > 0
        if reject31:
            n_flagged += 1
        verdict = "REJECT" if (reject31 and args.strict) else ("flag" if reject31 else "pass")
        print(f"{f.stem:<28} | {z_516c:>6} {z_516w:>6} | {z_416c:>6} | {z_721c:>6} "
              f"| {z_1053c:>7} | {cov31:>5.0%} | {best['3-1']:>6.2f} | {best['3-2']:>6.2f} | {verdict}")

    print("-" * 96)
    print(f"{len(txt_files)} file(s), {n_flagged} flagged (Z inside the 3-1 window).")
    print("Reminder: a 'pass' only means the zero-Z necessary condition holds — it is NOT")
    print("evidence the text is the key. A 'flag/reject' is a fast elimination for 3-1 only;")
    print("the other ciphers' literal cribs (all E's; E,Y,E,Y,E) carry no such zero-test.")


if __name__ == "__main__":
    main()
