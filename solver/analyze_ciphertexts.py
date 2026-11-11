"""Structural and statistical pattern analysis of the seven Decipher ciphertexts.

Compares the three solved Decipher II ciphertexts (2-1, 2-2, 2-3) against the
four unsolved ciphertexts (2-4, 3-1, 3-2, 3-3) in data/ciphers.json without
requiring any copyrighted book text.

Usage:
    uv run solver/analyze_ciphertexts.py
    uv run solver/analyze_ciphertexts.py --json
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CIPHERS_PATH = ROOT / "data" / "ciphers.json"

CIPHER_ORDER = ("2-1", "2-2", "2-3", "2-4", "3-1", "3-2", "3-3")
SOLVED_SET = {"2-1", "2-2", "2-3"}


def analyze_one(name: str, seq: list[int | str]) -> dict:
    n_total = len(seq)
    nums = [t for t in seq if isinstance(t, int)]
    num_positions = [(i + 1, t) for i, t in enumerate(seq) if isinstance(t, int)]
    lit_positions = [(i + 1, str(t)) for i, t in enumerate(seq) if isinstance(t, str)]

    counts = collections.Counter(nums)
    unique_nums = len(counts)
    n_nums = len(nums)
    extra_uses = n_nums - unique_nums
    min_n = min(nums)
    max_n = max(nums)

    # Integer IoC
    ioc_int = (
        sum(v * (v - 1) for v in counts.values()) / (n_nums * (n_nums - 1))
        if n_nums > 1
        else 0.0
    )

    # Repeated integers with 1-based positions
    repeats = {}
    for val, cnt in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        if cnt > 1:
            pos_list = [p for p, t in num_positions if t == val]
            repeats[val] = pos_list

    # Adjacent numeric step differences (only when consecutive tokens are both ints)
    adj_diffs = []
    step1_pairs = []
    same_pairs = []
    for i in range(len(seq) - 1):
        a, b = seq[i], seq[i + 1]
        if isinstance(a, int) and isinstance(b, int):
            d = b - a
            adj_diffs.append(d)
            if d == 0:
                same_pairs.append((i + 1, a))
            elif abs(d) == 1:
                step1_pairs.append((i + 1, a, b))

    # Consecutive +/-1 runs of length >= 3 (e.g. 737, 738, 739)
    runs_pm1 = []
    i = 0
    while i < len(seq):
        if not isinstance(seq[i], int):
            i += 1
            continue
        j = i
        while (
            j + 1 < len(seq)
            and isinstance(seq[j + 1], int)
            and seq[j + 1] - seq[j] in (1, -1)
            and (j == i or (seq[j + 1] - seq[j]) == (seq[j] - seq[j - 1]))
        ):
            j += 1
        if j - i + 1 >= 3:
            runs_pm1.append((i + 1, seq[i : j + 1]))
        i = j + 1 if j > i else i + 1

    # Century-band clustering check (inspired by 2-3's 7-token century blocks)
    same_century_adj = sum(
        1
        for k in range(len(seq) - 1)
        if isinstance(seq[k], int)
        and isinstance(seq[k + 1], int)
        and (seq[k] // 100) == (seq[k + 1] // 100)
    )
    adj_int_pairs = len(adj_diffs)
    same_century_rate = same_century_adj / adj_int_pairs if adj_int_pairs else 0.0

    # Multiples of 100 and 10
    mult_100 = [t for t in nums if t % 100 == 0]
    mult_10 = [t for t in nums if t % 10 == 0]

    # Quartile distribution across [1, max_n]
    q_counts = [0, 0, 0, 0]
    for t in nums:
        q = min(3, int((t - 1) * 4 / max_n))
        q_counts[q] += 1

    # Above-midpoint fraction (palindromic check: in uniform [1..2L], ~50% > L)
    above_half = sum(1 for t in nums if t > max_n / 2) / n_nums

    # Expected birthday collisions if drawn uniformly WITH replacement from [1..max_n]
    # E[unique] = M * (1 - (1 - 1/M)^N) => E[extra_uses] = N - E[unique]
    exp_unique_uniform = max_n * (1.0 - ((max_n - 1) / max_n) ** n_nums)
    exp_extra_uniform = n_nums - exp_unique_uniform

    # Literal-anchored short windows (within +/- 3 of any literal token)
    lit_windows = []
    for pos1, ch in lit_positions:
        idx0 = pos1 - 1
        lo = max(0, idx0 - 3)
        hi = min(len(seq), idx0 + 4)
        lit_windows.append(
            {
                "pos": pos1,
                "literal": ch,
                "window_start": lo + 1,
                "tokens": seq[lo:hi],
            }
        )

    return {
        "cipher": name,
        "status": "SOLVED" if name in SOLVED_SET else "OPEN",
        "total_tokens": n_total,
        "numeric_tokens": n_nums,
        "literal_count": len(lit_positions),
        "literals": lit_positions,
        "min_n": min_n,
        "max_n": max_n,
        "unique_ints": unique_nums,
        "extra_repeat_uses": extra_uses,
        "expected_extra_if_uniform": round(exp_extra_uniform, 1),
        "coverage_of_max_n": round(unique_nums / max_n, 4),
        "ioc_int": round(ioc_int, 6),
        "same_adjacent_pairs": same_pairs,
        "step1_adjacent_pairs": step1_pairs,
        "step1_count": len(step1_pairs),
        "monotonic_pm1_runs_ge3": runs_pm1,
        "same_century_adj_rate": round(same_century_rate, 3),
        "mult_100_count": len(mult_100),
        "mult_100_tokens": mult_100,
        "mult_10_count": len(mult_10),
        "quartiles": q_counts,
        "above_half_rate": round(above_half, 3),
        "repeats": repeats,
        "literal_windows": lit_windows,
    }


def print_report(stats: list[dict]) -> None:
    print("=" * 94)
    print("DECIPHER CIPHERTEXT STRUCTURAL COMPARISON (SOLVED 2-1..2-3 vs. OPEN 2-4, 3-1..3-3)")
    print("=" * 94)
    hdr = (
        f"{'ID':<4} {'State':<6} {'Len':>4} {'Nums':>4} {'Lits':>4} "
        f"{'Min':>4} {'Max':>5} {'Uniq':>4} {'Reps':>4} {'E[Rep]':>6} "
        f"{'|d|=1':>5} {'SameC%':>6} {'x100':>4} {'>Max/2':>6}"
    )
    print(hdr)
    print("-" * 94)
    for s in stats:
        print(
            f"{s['cipher']:<4} {s['status']:<6} {s['total_tokens']:>4} "
            f"{s['numeric_tokens']:>4} {s['literal_count']:>4} "
            f"{s['min_n']:>4} {s['max_n']:>5} {s['unique_ints']:>4} "
            f"{s['extra_repeat_uses']:>4} {s['expected_extra_if_uniform']:>6.1f} "
            f"{s['step1_count']:>5} {s['same_century_adj_rate']*100:>5.1f}% "
            f"{s['mult_100_count']:>4} {s['above_half_rate']*100:>5.1f}%"
        )

    for s in stats:
        if s["status"] == "SOLVED":
            continue
        print("\n" + "=" * 94)
        print(
            f"OPEN CIPHER {s['cipher']} — {s['total_tokens']} tokens "
            f"({s['numeric_tokens']} ints in [{s['min_n']}..{s['max_n']}], "
            f"{s['literal_count']} literals)"
        )
        print("=" * 94)
        q = s["quartiles"]
        print(f"  Quartiles across [1..{s['max_n']}]: Q1={q[0]}, Q2={q[1]}, Q3={q[2]}, Q4={q[3]}")
        print(
            f"  Repeat collisions: {s['extra_repeat_uses']} actual vs "
            f"{s['expected_extra_if_uniform']:.1f} expected under uniform random draws"
        )
        if s["repeats"]:
            rep_str = ", ".join(f"{k}@{v}" for k, v in s["repeats"].items())
            print(f"  Repeated numbers (value@[1-based pos]): {rep_str}")
        else:
            print("  Repeated numbers: NONE (strictly without replacement!)")
        if s["same_adjacent_pairs"]:
            print(f"  Adjacent identical pairs (double letter): {s['same_adjacent_pairs']}")
        if s["step1_adjacent_pairs"]:
            print(f"  Adjacent +/-1 step pairs ({s['step1_count']}): {s['step1_adjacent_pairs']}")
        if s["monotonic_pm1_runs_ge3"]:
            print(f"  Monotonic +/-1 runs (len>=3): {s['monotonic_pm1_runs_ge3']}")
        if s["mult_100_tokens"]:
            print(f"  Multiples of 100 ({s['mult_100_count']}): {s['mult_100_tokens']}")
        if s["literals"]:
            print(f"  Literals (1-based pos, char): {s['literals']}")
            for lw in s["literal_windows"]:
                print(
                    f"    pos {lw['pos']:>3} ('{lw['literal']}'): "
                    f"tokens[{lw['window_start']}..]={lw['tokens']}"
                )


def print_corpus_stats() -> None:
    import engine

    model_files = sorted((ROOT / "texts" / "model").glob("*.txt"))
    if not model_files:
        print("\n[!] texts/model/*.txt not present; skip empirical corpus stats.")
        return
    texts = [p.read_text(encoding="utf-8", errors="replace") for p in model_files]
    wstream = "".join(engine.first_letters(t) for t in texts)
    cstream = "".join(engine.letters_only(t) for t in texts)
    print("\n" + "=" * 94)
    print(f"EMPIRICAL KEY-WINDOW SUPPLY IN ENGLISH PROSE ({len(wstream):,} words / {len(cstream):,} chars)")
    print("=" * 94)
    for wlen, label in ((416, "3-2 max=416"), (516, "3-1 max=516"), (721, "3-3 max=721")):
        w_wins = [wstream[i : i + wlen] for i in range(0, len(wstream) - wlen, 200)]
        c_wins = [cstream[i : i + wlen] for i in range(0, len(cstream) - wlen, 500)]
        e_w = sorted(s.count("E") for s in w_wins)
        y_w = sorted(s.count("Y") for s in w_wins)
        z0_w = sum(1 for s in w_wins if "Z" not in s) / len(w_wins)
        y0_w = sum(1 for s in w_wins if "Y" not in s) / len(w_wins)
        e_c = sorted(s.count("E") for s in c_wins)
        z0_c = sum(1 for s in c_wins if "Z" not in s) / len(c_wins)
        print(
            f"  {label}: WORD-INITIAL 'E' median={e_w[len(e_w)//2]} "
            f"(p10..p90={e_w[len(e_w)//10]}..{e_w[9*len(e_w)//10]}), "
            f"'Y' median={y_w[len(y_w)//2]} (zero-Y={y0_w*100:.1f}%), zero-Z={z0_w*100:.1f}% | "
            f"CHAR-STREAM 'E' median={e_c[len(e_c)//2]}, zero-Z={z0_c*100:.1f}%"
        )

    # Enumerate frequent 4-letter A-E-B-A words / substrings for 3-1's [335, 'E', 308, 335]
    word_counts: collections.Counter[str] = collections.Counter()
    for t in texts:
        for w in re.findall(r"[A-Za-z]+", t):
            word_counts[w.upper()] += 1
    aeba_words = [
        (w, cnt)
        for w, cnt in word_counts.most_common()
        if len(w) == 4 and w[1] == "E" and w[0] == w[3] and w[0] != w[2] and cnt >= 5
    ]
    print(f"  3-1 [335,'E',308,335] (A-E-B-A) top whole words in corpus: {aeba_words[:15]}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="Emit full JSON summary")
    ap.add_argument("--corpus-stats", action="store_true", help="Include empirical texts/model supply stats")
    args = ap.parse_args()

    ciphers = json.loads(CIPHERS_PATH.read_text(encoding="utf-8"))
    stats = [analyze_one(cid, ciphers[cid]) for cid in CIPHER_ORDER]
    if args.json:
        print(json.dumps(stats, indent=2))
    else:
        print_report(stats)
        if args.corpus_stats:
            print_corpus_stats()


if __name__ == "__main__":
    main()
