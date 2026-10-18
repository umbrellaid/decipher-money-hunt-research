# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
run_full_ciphertexts.py
=======================
Driver that reruns toc_and_clue_tester.py's full pipeline against the COMPLETE
ciphertexts in this repo's data/ciphers.json.

Why this exists: the Gemini-generated toc_and_clue_tester.py embeds TRUNCATED
ciphertexts (exact prefixes of this repo's full versions):
    2-4:  51 of 170 tokens (30%)
    3-1: 113 of 170 tokens (66%)
    3-2:  56 of 117 tokens (48%)
    3-3: 130 of 159 tokens (82%)
and therefore understates N_max (2-4: 1050 vs true 1053; 3-2: 415 vs true 416;
3-1: 513 vs true 516) and drops literal-letter cribs (full 3-2 has E,Y,E,Y,E).

Usage (from the repo root):
    uv run solver/run_full_ciphertexts.py --top 25
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import toc_and_clue_tester as T  # noqa: E402

REPO = Path(__file__).resolve().parent.parent


def load_full_ciphertexts() -> dict[str, list[int | str]]:
    cj = json.loads((REPO / "data" / "ciphers.json").read_text(encoding="utf-8"))
    out: dict[str, list[int | str]] = {}
    for key, name in [("2-2", "Puzzle_2-2_Control"), ("2-4", "Puzzle_2-4"),
                      ("3-1", "Puzzle_3-1"), ("3-2", "Puzzle_3-2"), ("3-3", "Puzzle_3-3")]:
        out[name] = [int(t) if str(t).isdigit() else str(t) for t in cj[key]]
    out["Puzzle_2-4_No100s"] = [
        tok for tok in out["Puzzle_2-4"]
        if not (isinstance(tok, int) and tok % 100 == 0)
    ]
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Full-ciphertext ToC & clue tester")
    parser.add_argument("--top", type=int, default=25)
    args = parser.parse_args()

    T.CIPHERTEXTS.clear()
    T.CIPHERTEXTS.update(load_full_ciphertexts())

    print("=" * 78)
    print("FULL-CIPHERTEXT RUN (repo data/ciphers.json) — length audit")
    print("=" * 78)
    for name, ct in T.CIPHERTEXTS.items():
        nums = [t for t in ct if isinstance(t, int)]
        letters = [t for t in ct if isinstance(t, str)]
        print(f"{name:<22} tokens={len(ct):>3}  N_max={max(nums):>4}  literal letters={letters}")

    tocs = dict(T.EMBEDDED_TOCS)
    all_streams: dict[str, str] = {}
    for book, title_list in tocs.items():
        all_streams.update(T.generate_toc_key_streams(book, title_list))

    print("\n" + "=" * 78)
    print("SELF-TEST: SOLVED PUZZLE 2-2 (Catch-22) with full 53-token ciphertext")
    print("=" * 78)
    ctrl_key = all_streams["Heller_Catch22_Control|Full|Bare|Chars|Rev"]
    ctrl_decoded, cov = T.decode_with_key(T.CIPHERTEXTS["Puzzle_2-2_Control"], ctrl_key, drift=0)
    ctrl_pt_rev = ctrl_decoded[::-1]
    print(f"Control Key Length : {len(ctrl_key)} chars (Coverage = {cov:.0%})")
    print(f"Control Bigram Fit : {T.score_english(ctrl_pt_rev):.3f}")
    print(f"Decoded Preview    : {ctrl_pt_rev[:60]}")
    print("NOTE: reconciled key is 484 letters: 'Piltchard & Wren' (& stripped,")
    print("not 'and') and 'Catch-22' -> 'Catch'. Codenumber 477 = final N of 'The")
    print("Texan'; letters AXETEHT at positions 478-484 are unused. The documented")
    print("478-letter figure was erroneous; the self-test above decodes exactly.")

    print("\n" + "=" * 78)
    print(f"STAGE 3 (FULL): {len(all_streams)} KEY STREAMS x 5 DRIFT OFFSETS x 2 DIRECTIONS")
    print("=" * 78)
    results: list[T.CandidateResult] = []
    for p_name, ctext in T.CIPHERTEXTS.items():
        if p_name == "Puzzle_2-2_Control":
            continue
        for stream_id, k_stream in all_streams.items():
            if len(k_stream) < 120:
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
    results.sort(key=lambda r: r.score, reverse=True)
    print(f"{'Rank':<4} | {'Score':>6} | {'Puzzle':<17} | {'Cov':>4} | {'Drf':>3} | {'Dir':<3} | Stream ID")
    print("-" * 78)
    for idx, res in enumerate(results[: args.top], start=1):
        print(f"{idx:<4} | {res.score:>6.3f} | {res.puzzle:<17} | {res.coverage:>3.0%} | "
              f"{res.drift:>+3d} | {res.pt_direction:<3} | {res.stream_id}")
        print(f"     -> {res.preview}")


if __name__ == "__main__":
    main()
