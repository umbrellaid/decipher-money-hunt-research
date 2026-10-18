# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
body_scan.py
============
Body-text scanner for OCR'd chapter files, implementing the 2026-10-17/18
Gemini follow-up strategy (see results/gemini-toc-test-2026-10-17.md,
"Follow-up Q&A", and results/scanning-checklist-2026-10-17.md):

  * WORD-LEVEL-FIRST stream ordering — both solved body-text precedents
    (Decipher I = Cosmos Ch. 6, 1,252 words; Puzzle 2-3 = Tai-Pan Ch. 5,
    2,420 words) were first-letter-of-word keys, so word-level families are
    Tier 1, word-stride variants Tier 2, and every-character streams Tier 3
    (fallback). Results are reported grouped by tier.
  * CONTIGUOUS CHAPTER WINDOWS — for micro-chapter books (Cat's Cradle
    ~400-word chapters, Union Club Mysteries 3-5-page stories) a single
    Ch. 10 cannot reach word-level N_max (416-1053 words), so consecutive
    chapter files are concatenated into windows of 1..N chapters
    (default N=6, i.e. the "scan Ch. 10-15 contiguously" advice).
  * ZERO-Z NECESSARY CONDITION for 3-1 — the literal Z cribs imply no Z in
    the first 516 chars/words of the 3-1 keytext window; violating windows
    are flagged for 3-1 (report only, unless --strict skips scoring them).

Scan-dir convention: one .txt per chapter, named so natural sort order is
reading order (e.g. ch09.txt, ch10.txt, ch11.txt ...). Windows are anchored
at every file and extend forward up to --window chapters.

Usage (from the repo root):
    uv run solver/body_scan.py --scan-dir texts/cats_cradle
    uv run solver/body_scan.py --scan-dir texts/union_club --window 6 --top 10
    uv run solver/body_scan.py --scan-dir texts/zhivago --strict
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import toc_and_clue_tester as T  # noqa: E402
from run_full_ciphertexts import load_full_ciphertexts  # noqa: E402

# Corrected N_max values (repo data/ciphers.json); 3-1 zero-Z window size
N_MAX = {"Puzzle_3-1": 516, "Puzzle_3-2": 416, "Puzzle_3-3": 721, "Puzzle_2-4": 1053}
ZERO_Z_WINDOW = 516  # 3-1 N_max


def natural_key(path: Path) -> list[int | str]:
    """Sort key so ch2 sorts before ch10 (natural/numeric ordering)."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", path.stem)]


def tier_of(stream_id: str) -> int:
    """Extraction tier encoded in the stream id (1 = word-level, 2 = word
    strides / halfway patterns, 3 = character-level fallback)."""
    if "|Chars|" in stream_id:
        return 3
    if "Stride" in stream_id or "Half" in stream_id:
        return 2
    return 1


def s100_probe(k_stream: str) -> str:
    """The 2-4 round-number probe (Gemini Q6, 2026-10-18): the 8-token run
    400,500,400,100,200,400,800,600 at 2-4 positions 20-27 maps to
    K[400]K[500]K[400]K[100]K[200]K[400]K[800]K[600] (1-based) — the bottom-right
    boxes of Holland's 10x10 key-grid pages. Returns '?'-padded string."""
    picks = (400, 500, 400, 100, 200, 400, 800, 600)
    return "".join(k_stream[n - 1] if 0 < n <= len(k_stream) else "?" for n in picks)


def build_windows(files: list[Path], max_window: int) -> list[tuple[str, str, int]]:
    """Contiguous chapter windows: (label, combined_text, n_chapters).

    Anchored at every file, extending forward 1..max_window chapters.
    """
    raws = [f.read_text(encoding="utf-8", errors="ignore") for f in files]
    stems = [f.stem for f in files]
    windows: list[tuple[str, str, int]] = []
    for i in range(len(files)):
        for size in range(1, min(max_window, len(files) - i) + 1):
            label = stems[i] if size == 1 else f"{stems[i]}..{stems[i + size - 1]}"
            windows.append((label, "\n\n".join(raws[i : i + size]), size))
    return windows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Word-level-first body scanner with contiguous chapter windows"
    )
    parser.add_argument("--scan-dir", type=Path, required=True,
                        help="Directory of OCR'd .txt chapter scans (natural sort = reading order)")
    parser.add_argument("--window", type=int, default=6,
                        help="Max contiguous chapters per window (default 6 = Ch. 10-15 advice)")
    parser.add_argument("--top", type=int, default=10,
                        help="Top hits to print per puzzle per tier (default 10)")
    parser.add_argument("--strict", action="store_true",
                        help="Skip 3-1 scoring for windows that fail the zero-Z condition")
    parser.add_argument("--skip", type=str, default="",
                        help="Comma-separated word-skip offsets to ALSO test on Tier-1 "
                             "word-level streams, e.g. --skip 8,16,36 (solved precedent: "
                             "Decipher I skipped the first 36 words of Cosmos Ch. 6 — "
                             "paper p. 279, Figure 8, docs/decipher-i.md)")
    args = parser.parse_args()

    ciphers = {k: v for k, v in load_full_ciphertexts().items()
               if k in (*N_MAX, "Puzzle_2-4_No100s")}

    files = sorted(args.scan_dir.glob("*.txt"), key=natural_key)
    if not files:
        print(f"[!] No .txt files in {args.scan_dir}")
        return

    windows = build_windows(files, max(1, args.window))
    print("=" * 96)
    print("BODY SCAN — word-level-first streams x contiguous chapter windows")
    print(f"scan-dir: {args.scan_dir}  ({len(files)} chapter files, "
          f"{len(windows)} windows of 1-{max(1, args.window)} chapters)")
    print("Tier 1 = word-level (first/last letter, incl. reversed word order) | "
          "Tier 2 = word strides + halfway patterns | Tier 3 = every character")
    print("=" * 96)

    # Per-window zero-Z status for 3-1 (necessary condition, not evidence)
    z_status: dict[str, bool] = {}
    print(f"\n{'Window':<40} | {'Ch':>2} | {'Words':>6} | {'Chars':>6} | "
          f"{'Z@516c':>6} | {'Z@516w':>6} | 3-1")
    print("-" * 96)
    all_streams: dict[str, str] = {}
    stream_window: dict[str, str] = {}
    for label, text, size in windows:
        words = T.tokenize_words(text)
        chars = T.clean_alpha(text)
        z_c = chars[:ZERO_Z_WINDOW].count("Z")
        z_w = sum(1 for w in words[:ZERO_Z_WINDOW] if "Z" in w)
        fails_z = z_c > 0 or z_w > 0
        z_status[label] = fails_z
        print(f"{label:<40} | {size:>2} | {len(words):>6} | {len(chars):>6} | "
              f"{z_c:>6} | {z_w:>6} | {'FLAG' if fails_z else 'pass'}")
        for sid, stream in T.generate_body_text_streams(label, text).items():
            all_streams[sid] = stream
            stream_window[sid] = label
        # Optional word-skip variants of the Tier-1 word-level streams
        # (Decipher I's key skipped the first 36 words of the chapter)
        skip_list = sorted({int(s) for s in args.skip.split(",") if s.strip()} - {0})
        for k in skip_list:
            if len(words) - k < 120:
                continue
            sub = words[k:]
            for fam, key in (("WordFirst", 0), ("WordLast", -1)):
                sid = f"{label}|{fam}_Joined_Skip{k}|Fwd"
                all_streams[sid] = "".join(w[key] for w in sub)
                stream_window[sid] = label
        # "Halfway / out-and-back" patterned streams (Gemini Q6: Puzzle 2-1's
        # "One way gets you half way there" — N_max 980 = 2 x 490 implies a
        # single place read two ways; candidate family for 2-4's N_max 1053)
        if len(words) >= 240:
            firsts = [w[0] for w in words]
            lasts = [w[-1] for w in words]
            half_streams = {
                "HalfFirstLast": firsts + lasts,          # pass 1 first-letters, pass 2 last-letters
                "HalfFwdRev": firsts + firsts[::-1],      # pass 1 forward, pass 2 backward
                "HalfOddEven": firsts[::2] + firsts[1::2],  # pass 1 odd words, pass 2 even words
            }
            for name, letters in half_streams.items():
                sid = f"{label}|{name}|Fwd"
                all_streams[sid] = "".join(letters)
                stream_window[sid] = label
    print("-" * 96)
    print(f"{sum(z_status.values())}/{len(windows)} windows flagged for 3-1 "
          f"(Z inside the first {ZERO_Z_WINDOW} chars/words).")

    # Scoring loop (mirrors run_full_ciphertexts.py: drift +-2, coverage >= 0.45,
    # 3-1 double-letter bonus at codenumber 487, both plaintext directions)
    print(f"\nScoring {len(all_streams)} streams x 5 drift offsets x 2 directions "
          f"against {len(ciphers)} ciphertexts...")
    results: list[T.CandidateResult] = []
    skipped_z = 0
    for p_name, ctext in ciphers.items():
        for stream_id, k_stream in all_streams.items():
            if len(k_stream) < 120:
                continue
            if args.strict and p_name == "Puzzle_3-1" and z_status[stream_window[stream_id]]:
                skipped_z += 1
                continue
            for drift in (-2, -1, 0, 1, 2):
                decoded, coverage = T.decode_with_key(ctext, k_stream, drift=drift)
                if coverage < 0.45:
                    continue
                repeat_bonus = 0.0
                if p_name == "Puzzle_3-1":
                    idx_487 = (487 - 1) + drift
                    if 0 <= idx_487 < len(k_stream) and k_stream[idx_487] in T.COMMON_DOUBLES:
                        repeat_bonus = 0.08
                for pt_dir, candidate_pt in (("Fwd", decoded), ("Rev", decoded[::-1])):
                    sc = T.score_english(candidate_pt) + repeat_bonus
                    results.append(T.CandidateResult(
                        score=sc, puzzle=p_name, stream_id=stream_id, drift=drift,
                        pt_direction=pt_dir, coverage=coverage,
                        preview=candidate_pt[:65],
                    ))
    if args.strict:
        print(f"[strict] skipped {skipped_z} 3-1 decode runs on zero-Z-failing windows")

    # Tier-grouped reporting: word-level hits surface first
    results.sort(key=lambda r: r.score, reverse=True)
    for p_name in ciphers:
        print("\n" + "=" * 96)
        print(f"TOP HITS — {p_name} (N_max = {N_MAX.get(p_name.replace('_No100s', ''), 1053)})")
        print("=" * 96)
        for tier in (1, 2, 3):
            rows = [r for r in results if r.puzzle == p_name
                    and tier_of(r.stream_id) == tier][: args.top]
            if not rows:
                continue
            tier_name = {1: "word-level", 2: "word strides / halfway patterns",
                         3: "character-level"}[tier]
            print(f"\n  Tier {tier} ({tier_name}):")
            print(f"  {'Score':>6} | {'Cov':>4} | {'Drf':>3} | {'Dir':>3} | Stream ID")
            print("  " + "-" * 90)
            for res in rows:
                print(f"  {res.score:>6.3f} | {res.coverage:>3.0%} | {res.drift:>+3d} | "
                      f"{res.pt_direction:>3} | {res.stream_id}")
                print(f"         -> {res.preview}")
                if p_name.startswith("Puzzle_2-4"):
                    probe = s100_probe(all_streams[res.stream_id])
                    print(f"         S100 probe (K[400]K[500]K[400]K[100]K[200]K[400]"
                          f"K[800]K[600]): {probe}  (XAXBCXDE pattern; X=key[400])")

    print("\nReminder: English-like bigram scores near the top are necessary, not")
    print("sufficient — eyeball every preview; vowel-heavy gibberish is a known")
    print("letter-density artifact of *-wordlast / LastLetter streams (RUN_LOG).")


if __name__ == "__main__":
    main()
