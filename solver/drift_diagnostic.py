"""Index-elastic (OCR / edition-drift tolerant) book-cipher diagnostic.

Why rigid sweeps miss light OCR noise or edition variants:
    In Decipher II/III, cipher numbers jump uniformly across [1..max_n]. If OCR
    drops or splits 1-2 words mid-passage (or an edition differs by 1-2 words or
    letters, as in the 490-vs-492-letter Gulliver's Travels witness for 2-1),
    every cipher token above the edit shifts by +/-1..2. Because high-index tokens
    are interleaved throughout the plaintext, those wrong letters act like
    scattered nulls and collapse BOTH the whole-decode mean AND score_best_window
    into the noise band.

Method (3-band piecewise index elasticity):
    Partition [1..max_n] into 3 equal index bands:
        Band 0: [1 .. floor(max_n/3)]           shift = 0
        Band 1: (floor(max_n/3) .. floor(2*max_n/3)]  shift = d1 in [-max_step..+max_step]
        Band 2: (floor(2*max_n/3) .. max_n]     shift = d1 + d2 in [-2*max_step..+2*max_step]
    With max_step=2, 25 profiles (0, d1, d1+d2) are evaluated vectorized at each
    candidate start position (and on sentence-anchored character starts if
    --sentence-chars is set). Taking max over 25 profiles raises random-book noise
    by only ~0.12-0.16 nats (staying <= -8.30), while recovering a genuine passage
    with 1-2 mid-window insertions/deletions back into the -7.90..-8.12 band.

Usage:
    uv run solver/drift_diagnostic.py TEXT.txt [...] [--cipher 2-4|3-1|3-2|3-3|all]
                                                     [--sentence-chars] [--top 5]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import numpy as np

import engine
import rules

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CIPHERS = json.load((ROOT / "data" / "ciphers.json").open(encoding="utf-8"))
OPEN_CIPHERS = ("2-4", "3-1", "3-2", "3-3")

# Calibrated look threshold for max-over-25 elastic profiles (noise ceiling ~ -8.30).
ELASTIC_LOOK = -8.12


def first_letters_split_hyphen(raw: str) -> str:
    """Word initials treating hyphens and em-dashes as word separators."""
    cleaned = raw.replace("-", " ").replace("—", " ").replace("–", " ")
    return engine.first_letters(cleaned)


def build_drift_profiles(max_step: int = 2) -> np.ndarray:
    """Return (P, 3) int64 array of (0, d1, d1+d2) index shifts per band."""
    profs = []
    for d1 in range(-max_step, max_step + 1):
        for d2_rel in range(-max_step, max_step + 1):
            profs.append((0, d1, d1 + d2_rel))
    return np.array(profs, dtype=np.int64)


def search_elastic_stream(
    stream: str,
    cipher: list[int | str],
    scorer: engine.TrigramScorer,
    starts: np.ndarray | None = None,
    max_step: int = 2,
    label: str = "",
    top_k: int = 10,
    chunk_starts: int = 1500,
) -> list[dict]:
    """Vectorized 3-band index-elastic search across forward and reversed stream."""
    lay = engine._cipher_layout(cipher)
    nums, num_cols = lay["nums"], lay["num_cols"]
    lit_mask, lit_vals, W = lay["lit_mask"], lay["lit_vals"], lay["W"]
    max_n = int(nums.max()) if len(nums) else 0

    arr_fwd = np.frombuffer(stream.encode("ascii"), dtype=np.uint8).astype(np.int64) - 65
    if ((arr_fwd < 0) | (arr_fwd > 25)).any():
        raise ValueError("stream must be uppercase A-Z only")

    b1_cut = max_n // 3
    b2_cut = (2 * max_n) // 3
    band_id = np.where(nums <= b1_cut, 0, np.where(nums <= b2_cut, 1, 2))  # (M,)

    profiles = build_drift_profiles(max_step=max_step)  # (P, 3)
    P = len(profiles)
    # Shift matrix per profile across numeric cipher slots: (P, M)
    prof_shifts = profiles[:, band_id] + (nums[None, :] - 1)  # (P, M)
    zero_prof_idx = int(np.where((profiles[:, 1] == 0) & (profiles[:, 2] == 0))[0][0])

    margin = 2 * max_step
    hits: list[dict] = []

    def _scan_dir(arr: np.ndarray, direction: str, cand_starts: np.ndarray | None) -> None:
        n = len(arr)
        if n < max_n - margin:
            return
        if cand_starts is None:
            st_all = np.arange(0, max(0, n - max_n + margin + 1), dtype=np.int64)
        else:
            st_all = cand_starts[(cand_starts >= 0) & (cand_starts < n)]
        if len(st_all) == 0:
            return

        for c0 in range(0, len(st_all), chunk_starts):
            st = st_all[c0 : c0 + chunk_starts]  # (S,)
            S = len(st)
            # idx shape: (S, P, M)
            idx = st[:, None, None] + prof_shifts[None, :, :]
            valid = (idx >= 0) & (idx < n)
            ok_sp = np.all(valid, axis=2)  # (S, P)
            if not np.any(ok_sp):
                continue

            idx_clipped = np.clip(idx, 0, n - 1)
            flat_idx = idx_clipped.reshape(S * P, -1)
            rows = np.zeros((S * P, W), dtype=np.int64)
            rows[:, num_cols] = arr[flat_idx]
            rows[:, lit_mask] = lit_vals[lit_mask]

            sc_f = engine._trigram_means(rows, scorer).reshape(S, P)
            sc_r = engine._trigram_means(rows[:, ::-1], scorer).reshape(S, P)
            use_f = sc_f >= sc_r
            sc = np.where(use_f, sc_f, sc_r)
            sc = np.where(ok_sp, sc, -1e9)

            best_p = np.argmax(sc, axis=1)  # (S,)
            best_sc = sc[np.arange(S), best_p]
            rigid_sc = sc[:, zero_prof_idx]

            k = min(top_k, S)
            top_s_idx = np.argpartition(-best_sc, k - 1)[:k]
            for si in top_s_idx:
                if best_sc[si] <= -1e8:
                    continue
                pi = int(best_p[si])
                pdir = "fwd" if bool(use_f[si, pi]) else "rev"
                s_val = int(st[si])
                d0, d1, d2 = (int(x) for x in profiles[pi])

                # Reconstruct exact elastic decode string for this candidate
                slot_idx = s_val + prof_shifts[pi]
                dec_chars = ["?"] * W
                for col, sidx in zip(num_cols, slot_idx):
                    dec_chars[col] = chr(int(arr[sidx]) + 65)
                for col in np.nonzero(lit_mask)[0]:
                    dec_chars[col] = chr(int(lit_vals[col]) + 65)
                dec = "".join(dec_chars)
                if pdir == "rev":
                    dec = dec[::-1]

                hits.append(
                    {
                        "elastic_score": round(float(best_sc[si]), 4),
                        "rigid_score": round(float(rigid_sc[si]), 4),
                        "gain": round(float(best_sc[si] - rigid_sc[si]), 4),
                        "rule": label,
                        "start": s_val,  # 0-based stream coordinate (matches sweep.py)
                        "direction": direction,
                        "plaintext_direction": pdir,
                        "drift_bands": (d0, d1, d2),
                        "decode": dec,
                    }
                )

    _scan_dir(arr_fwd, "fwd", starts)
    rev_starts = None
    if starts is not None and len(stream) > 0:
        # Sentence starts do not invert cleanly without sentence ends; test full starts if small
        rev_starts = np.clip(len(stream) - 1 - starts, 0, max(0, len(stream) - 1))
    _scan_dir(arr_fwd[::-1], "from-end", rev_starts)

    hits.sort(key=lambda h: -h["elastic_score"])
    return hits[:top_k]


def sentence_char_starts(raw: str) -> np.ndarray:
    """0-based indices in letters_only(raw) that open a sentence or paragraph."""
    pts = [s[0] for s in rules.sentence_boundary_starts(raw)]
    if not pts or pts[0] != 0:
        pts = [0] + pts
    return np.array(sorted(set(pts)), dtype=np.int64)


def build_scorer() -> engine.TrigramScorer:
    paths = sorted((ROOT / "texts" / "model").glob("*.txt"))
    if not paths:
        sys.exit("No scoring model in texts/model/. Run: uv run solver/fetch_texts.py")
    return engine.TrigramScorer([p.read_text(encoding="utf-8", errors="replace") for p in paths])


def diagnose_file(
    path: Path,
    cipher_names: tuple[str, ...],
    scorer: engine.TrigramScorer,
    include_sentence_chars: bool = False,
    include_last_letters: bool = False,
    max_step: int = 2,
    top_k: int = 5,
) -> dict[str, list[dict]]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    streams: list[tuple[str, str, np.ndarray | None]] = [
        ("first-letters", engine.first_letters(raw), None),
        ("first-letters-split-hyphen", first_letters_split_hyphen(raw), None),
    ]
    if include_last_letters:
        streams.append(("last-letters", engine.last_letters(raw), None))
    if include_sentence_chars:
        s_chars = engine.letters_only(raw)
        s_starts = sentence_char_starts(raw)
        streams.append(("letters@sentence", s_chars, s_starts))
    out: dict[str, list[dict]] = {}
    for cname in cipher_names:
        cipher = CIPHERS[cname]
        pool: list[dict] = []
        for label, s_str, st_arr in streams:
            if len(s_str) < 100:
                continue
            pool.extend(
                search_elastic_stream(
                    s_str,
                    cipher,
                    scorer,
                    starts=st_arr,
                    max_step=max_step,
                    label=label,
                    top_k=top_k,
                )
            )
        pool.sort(key=lambda h: -h["elastic_score"])
        out[cname] = pool[:top_k]
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("texts", nargs="+", type=Path, help="Plain-text files to diagnose")
    ap.add_argument("--cipher", default="all", help="2-4, 3-1, 3-2, 3-3, or all")
    ap.add_argument("--sentence-chars", action="store_true", help="Also scan letters at sentence starts")
    ap.add_argument("--include-last-letters", action="store_true",
                    help="Include vowel-biased word-final letters (excluded by default)")
    ap.add_argument("--max-step", type=int, default=2, help="Max index drift per band transition (default 2)")
    ap.add_argument("--top", type=int, default=5)
    args = ap.parse_args()

    cnames = OPEN_CIPHERS if args.cipher == "all" else (args.cipher,)
    scorer = build_scorer()

    for p in args.texts:
        t0 = time.time()
        res = diagnose_file(
            p,
            cnames,
            scorer,
            include_sentence_chars=args.sentence_chars,
            include_last_letters=args.include_last_letters,
            max_step=args.max_step,
            top_k=args.top,
        )
        dt = time.time() - t0
        print(f"\n=== {p.name} ({dt:.1f}s) ===")
        for cname in cnames:
            print(f"  Cipher {cname}:")
            for h in res[cname]:
                flag = "  <-- CHECK DRIFT LEAD" if (
                    h["elastic_score"] > ELASTIC_LOOK and "last-letters" not in h["rule"]
                ) else ""
                print(
                    f"    elastic={h['elastic_score']:+.4f} (rigid={h['rigid_score']:+.4f}, "
                    f"drift={h['drift_bands']}) {h['rule']}@{h['start']} "
                    f"{h['direction']}/{h['plaintext_direction']}  {h['decode'][:48]}...{flag}"
                )


if __name__ == "__main__":
    main()
