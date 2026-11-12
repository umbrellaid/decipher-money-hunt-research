"""Scattered-null tolerant book-cipher diagnostic (skip-trigram Viterbi DP).

Why rigid and windowed trigram scoring miss scattered or periodic nulls:
    The Decipher rulebooks warn that messages may include nulls or deliberate
    misspellings. `TrigramScorer.score_best_window` rescues CLUSTERED nulls (a contiguous
    run of junk tokens at the start, middle, or end of a message) because a clean window
    survives elsewhere in the decode. When ~10-15% nulls are SCATTERED or PERIODIC across
    the message (e.g. 1 null every 8 tokens), no contiguous window is null-free: every
    null breaks three overlapping trigrams, collapsing both the whole-decode mean and
    `score_best_window` into the noise band (< -8.8).

Method (bounded skip-trigram Viterbi dynamic programming):
    Over candidate decode rows of length W, each token position may either be KEPT
    (scoring its bridging trigram `logp[c_k, c_i, c_j]` across any skipped positions) or
    SKIPPED as a null, paying a calibrated `skip_penalty` (-11.2 nats per skipped token)
    with at most `max_consec = 2` consecutive skips. Total log-probability is normalized
    by `W - 2`, matching `TrigramScorer.score` identically when zero skips are taken.

    Why `skip_penalty = -11.2` separates scattered-null English from novel noise:
    - In English prose, a single injected null corrupts three trigrams (~ -38 to -31 nats
      vs ~ -15 nats for the two bridged English trigrams); skipping it pays -11.2 once
      and restores both English trigrams (+5 to +15 nats net gain), while genuine proper
      nouns (`CAPTAINBRINKLEY`) stay intact.
    - On non-English streams from real novels (even shortest cipher 3-2, W=117, across
      raw prose letter frequencies), paying -11.2 per skipped character plus gating real
      leads to <= 20% skipped tokens keeps whole-book false positives below `NULL_LOOK`
      (-8.12), while 10-15% scattered/periodic-null English lands around -7.90..-8.05.

Usage:
    uv run python solver/null_diagnostic.py TEXT.txt [...] [--cipher 2-4|3-1|3-2|3-3|all]
                                                           [--sentence-chars] [--top 5]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

import drift_diagnostic
import engine

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CIPHERS = json.load((ROOT / "data" / "ciphers.json").open(encoding="utf-8"))
OPEN_CIPHERS = ("2-4", "3-1", "3-2", "3-3")

DEFAULT_SKIP_PENALTY = -11.2
DEFAULT_MAX_CONSEC = 2
MAX_SKIP_FRAC = 0.20
# Calibrated look threshold at skip_penalty=-11.2 (whole-book noise ceiling ~ -8.22;
# English with ~12.5% scattered/periodic nulls lands at ~ -7.90..-8.05).
NULL_LOOK = -8.12


def viterbi_null_score_matrix(
    rows: np.ndarray,
    scorer: engine.TrigramScorer,
    skip_penalty: float = DEFAULT_SKIP_PENALTY,
    max_consec: int = DEFAULT_MAX_CONSEC,
) -> np.ndarray:
    """Vectorized skip-trigram Viterbi score over a (B, W) int64 letter matrix (0..25).

    Returns a float64 array of shape (B,) normalized by (W - 2).
    """
    B, W = rows.shape
    if W < 3:
        return np.full(B, -12.0, dtype=np.float64)

    S = max_consec + 1
    NEG_INF = -1e18

    # Ring buffer of size (max_consec + 2) is sufficient, or full (W, S, B) for clarity;
    # at B=2048, W=170, S=3, (W, S, B) float64 is only 8.3 MB and fits in L3 cache.
    dp_hist = np.full((W, S, B), NEG_INF, dtype=np.float64)
    for p0 in range(min(W, max_consec + 1)):
        for s in range(S):
            p1 = p0 + 1 + s
            if p1 < W:
                dp_hist[p1, s, :] = (p0 + s) * skip_penalty

    logp = scorer.logp
    for j in range(2, W):
        rj = rows[:, j]
        for s_next in range(S):
            i = j - 1 - s_next
            if i < 1:
                continue
            ri = rows[:, i]
            ri_26_rj = ri * 26 + rj
            best = dp_hist[j, s_next, :].copy()
            step_pen = s_next * skip_penalty
            for s_prev in range(S):
                k = i - 1 - s_prev
                if k < 0:
                    continue
                prev_sc = dp_hist[i, s_prev, :]
                tri = logp[rows[:, k] * 676 + ri_26_rj]
                cand = prev_sc + tri + step_pen
                np.maximum(best, cand, out=best)
            dp_hist[j, s_next, :] = best

    final_best = np.full(B, NEG_INF, dtype=np.float64)
    for t_skip in range(min(W, max_consec + 1)):
        j = W - 1 - t_skip
        if j < 1:
            continue
        t_pen = t_skip * skip_penalty
        for s in range(S):
            np.maximum(final_best, dp_hist[j, s, :] + t_pen, out=final_best)

    return final_best / (W - 2)


def reconstruct_null_stripped(
    decoded: str,
    scorer: engine.TrigramScorer,
    skip_penalty: float = DEFAULT_SKIP_PENALTY,
    max_consec: int = DEFAULT_MAX_CONSEC,
) -> tuple[float, str, list[int]]:
    """Exact single-row Viterbi backpointer decode returning (score, cleaned, skipped_pos).

    `cleaned` contains the kept uppercase letters in order; `skipped_pos` lists the
    0-based indices in `decoded` classified as nulls.
    """
    s_up = engine.letters_only(decoded)
    W = len(s_up)
    if W < 3:
        return -12.0, s_up, []

    arr = [ord(c) - 65 for c in s_up]
    S = max_consec + 1
    NEG_INF = -1e18

    dp = [[NEG_INF] * S for _ in range(W)]
    back: list[list[tuple[int, int] | None]] = [[None] * S for _ in range(W)]

    for p0 in range(min(W, max_consec + 1)):
        for s in range(S):
            p1 = p0 + 1 + s
            if p1 < W:
                sc = (p0 + s) * skip_penalty
                if sc > dp[p1][s]:
                    dp[p1][s] = sc
                    back[p1][s] = (-1, p0)  # sentinel: first kept is p0

    logp = scorer.logp
    for j in range(2, W):
        rj = arr[j]
        for s_next in range(S):
            i = j - 1 - s_next
            if i < 1:
                continue
            ri = arr[i]
            best_sc = dp[j][s_next]
            best_bp = back[j][s_next]
            for s_prev in range(S):
                k = i - 1 - s_prev
                if k < 0 or dp[i][s_prev] <= NEG_INF / 2:
                    continue
                cand = dp[i][s_prev] + float(logp[arr[k] * 676 + ri * 26 + rj]) + s_next * skip_penalty
                if cand > best_sc:
                    best_sc = cand
                    best_bp = (i, s_prev)
            dp[j][s_next] = best_sc
            back[j][s_next] = best_bp

    best_final = NEG_INF
    best_end = (W - 1, 0)
    for t_skip in range(min(W, max_consec + 1)):
        j = W - 1 - t_skip
        if j < 1:
            continue
        for s in range(S):
            cand = dp[j][s] + t_skip * skip_penalty
            if cand > best_final:
                best_final = cand
                best_end = (j, s)

    kept_rev = []
    cur_j, cur_s = best_end
    while True:
        kept_rev.append(cur_j)
        bp = back[cur_j][cur_s]
        if bp is None:
            break
        if bp[0] == -1:
            kept_rev.append(bp[1])
            break
        cur_j, cur_s = bp

    kept = sorted(set(kept_rev))
    kept_set = set(kept)
    cleaned = "".join(s_up[idx] for idx in kept)
    skipped = [idx for idx in range(W) if idx not in kept_set]
    return best_final / (W - 2), cleaned, skipped


def search_null_tolerant_stream(
    stream: str,
    cipher: list[int | str],
    scorer: engine.TrigramScorer,
    starts: np.ndarray | None = None,
    skip_penalty: float = DEFAULT_SKIP_PENALTY,
    max_consec: int = DEFAULT_MAX_CONSEC,
    label: str = "",
    top_k: int = 10,
    chunk_starts: int = 2048,
) -> list[dict]:
    """Scan forward and reversed stream under skip-trigram Viterbi scoring."""
    lay = engine._cipher_layout(cipher)
    nums, num_cols = lay["nums"], lay["num_cols"]
    lit_mask, lit_vals, W = lay["lit_mask"], lay["lit_vals"], lay["W"]
    max_n = int(nums.max()) if len(nums) else 0

    arr_fwd = np.frombuffer(stream.encode("ascii"), dtype=np.uint8).astype(np.int64) - 65
    if ((arr_fwd < 0) | (arr_fwd > 25)).any():
        raise ValueError("stream must be uppercase A-Z only")

    hits: list[dict] = []

    def _scan_dir(arr: np.ndarray, direction: str, cand_starts: np.ndarray | None) -> None:
        n = len(arr)
        if n < max_n:
            return
        if cand_starts is None:
            st_all = np.arange(0, n - max_n + 1, dtype=np.int64)
        else:
            st_all = cand_starts[(cand_starts >= 0) & (cand_starts <= n - max_n)]
        if len(st_all) == 0:
            return

        for c0 in range(0, len(st_all), chunk_starts):
            st = st_all[c0 : c0 + chunk_starts]
            B = len(st)
            idx = st[:, None] + (nums[None, :] - 1)
            rows = np.zeros((B, W), dtype=np.int64)
            rows[:, num_cols] = arr[idx]
            rows[:, lit_mask] = lit_vals[lit_mask]

            vit_f = viterbi_null_score_matrix(rows, scorer, skip_penalty=skip_penalty, max_consec=max_consec)
            vit_r = viterbi_null_score_matrix(rows[:, ::-1], scorer, skip_penalty=skip_penalty, max_consec=max_consec)
            rig_f = engine._trigram_means(rows, scorer)
            rig_r = engine._trigram_means(rows[:, ::-1], scorer)

            use_f = vit_f >= vit_r
            vit = np.where(use_f, vit_f, vit_r)
            rig = np.where(use_f, rig_f, rig_r)

            k = min(top_k, B)
            top_idx = np.argpartition(-vit, k - 1)[:k]
            for bi in top_idx:
                pdir = "fwd" if bool(use_f[bi]) else "rev"
                s_val = int(st[bi])
                row_vals = rows[bi] if pdir == "fwd" else rows[bi, ::-1]
                raw_dec = "".join(chr(int(x) + 65) for x in row_vals)
                _, cleaned, skipped = reconstruct_null_stripped(
                    raw_dec, scorer, skip_penalty=skip_penalty, max_consec=max_consec
                )
                hits.append(
                    {
                        "null_score": round(float(vit[bi]), 4),
                        "rigid_score": round(float(rig[bi]), 4),
                        "gain": round(float(vit[bi] - rig[bi]), 4),
                        "rule": label,
                        "start": s_val,
                        "direction": direction,
                        "plaintext_direction": pdir,
                        "n_skipped": len(skipped),
                        "skipped_positions": skipped,
                        "decode": raw_dec,
                        "cleaned": cleaned,
                    }
                )

    _scan_dir(arr_fwd, "fwd", starts)
    rev_starts = None
    if starts is not None and len(stream) > 0:
        rev_starts = np.clip(len(stream) - 1 - starts, 0, max(0, len(stream) - max_n))
    _scan_dir(arr_fwd[::-1], "from-end", rev_starts)

    hits.sort(key=lambda h: -h["null_score"])
    return hits[:top_k]


def is_null_lead(hit: dict) -> bool:
    """True when a candidate clears NULL_LOOK without over-skipping or vowel-salad rules."""
    if "last-letters" in hit["rule"] or "wordlast" in hit["rule"]:
        return False
    w = max(1, len(hit["decode"]))
    if hit["n_skipped"] / w > MAX_SKIP_FRAC:
        return False
    return hit["null_score"] > NULL_LOOK


def diagnose_file(
    path: Path,
    cipher_names: tuple[str, ...],
    scorer: engine.TrigramScorer,
    include_sentence_chars: bool = False,
    include_last_letters: bool = False,
    skip_penalty: float = DEFAULT_SKIP_PENALTY,
    max_consec: int = DEFAULT_MAX_CONSEC,
    top_k: int = 5,
) -> dict[str, list[dict]]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    streams: list[tuple[str, str, np.ndarray | None]] = [
        ("first-letters", engine.first_letters(raw), None),
        ("first-letters-split-hyphen", drift_diagnostic.first_letters_split_hyphen(raw), None),
    ]
    if include_sentence_chars:
        streams.append(
            ("letters@sentence", engine.letters_only(raw), drift_diagnostic.sentence_char_starts(raw))
        )
    if include_last_letters:
        streams.append(("last-letters", engine.last_letters(raw), None))

    out: dict[str, list[dict]] = {}
    for cname in cipher_names:
        cipher = CIPHERS[cname]
        pool: list[dict] = []
        for label, s_str, st_arr in streams:
            if len(s_str) < 100:
                continue
            pool.extend(
                search_null_tolerant_stream(
                    s_str,
                    cipher,
                    scorer,
                    starts=st_arr,
                    skip_penalty=skip_penalty,
                    max_consec=max_consec,
                    label=label,
                    top_k=top_k,
                )
            )
        pool.sort(key=lambda h: -h["null_score"])
        out[cname] = pool[:top_k]
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("texts", nargs="+", type=Path, help="Plain-text files to diagnose")
    ap.add_argument("--cipher", default="all", help="2-4, 3-1, 3-2, 3-3, or all")
    ap.add_argument("--sentence-chars", action="store_true",
                    help="Also scan continuous letters at sentence starts")
    ap.add_argument("--include-last-letters", action="store_true",
                    help="Include vowel-biased word-final letters (excluded by default)")
    ap.add_argument("--skip-penalty", type=float, default=DEFAULT_SKIP_PENALTY,
                    help=f"Log-prob penalty per skipped null token (default {DEFAULT_SKIP_PENALTY})")
    ap.add_argument("--max-consec", type=int, default=DEFAULT_MAX_CONSEC,
                    help=f"Max consecutive skipped tokens (default {DEFAULT_MAX_CONSEC})")
    ap.add_argument("--top", type=int, default=5)
    args = ap.parse_args()

    cnames = OPEN_CIPHERS if args.cipher == "all" else (args.cipher,)
    scorer = drift_diagnostic.build_scorer()

    for p in args.texts:
        t0 = time.time()
        res = diagnose_file(
            p,
            cnames,
            scorer,
            include_sentence_chars=args.sentence_chars,
            include_last_letters=args.include_last_letters,
            skip_penalty=args.skip_penalty,
            max_consec=args.max_consec,
            top_k=args.top,
        )
        dt = time.time() - t0
        print(f"\n=== {p.name} ({dt:.1f}s) ===")
        for cname in cnames:
            print(f"  Cipher {cname}:")
            for h in res[cname]:
                flag = "  <-- CHECK NULL LEAD" if is_null_lead(h) else ""
                print(
                    f"    null={h['null_score']:+.4f} (rigid={h['rigid_score']:+.4f}, "
                    f"skips={h['n_skipped']}) {h['rule']}@{h['start']} "
                    f"{h['direction']}/{h['plaintext_direction']}  {h['cleaned'][:48]}...{flag}"
                )


if __name__ == "__main__":
    main()
