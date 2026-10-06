"""Regression tests for the Decipher solver.

Three kinds of check, all must pass before any sweep result is trusted:

1. decipher-I-example — the real worked example printed in the Decipher III
   rulebook (pages 3-4): the 56 keyed words of Cosmos ch.6 and the three sample
   ciphers that all encode CODES. Copyright-free and independent of our corpus.
2. puzzle 2-2 — the 42 Catch-22 chapter titles in data/catch22_chapter_titles.json,
   concatenated, reversed, then the decode read backwards. The book text is not
   required.
3. round-trip per rule family — encode a genuine English plaintext into cipher
   numbers against a stream built by that family, then require search_stream to
   rank the true numbering start #1 and reproduce the plaintext exactly, in both
   stream directions and both plaintext directions.

Run from the repository root, or from anywhere:

    uv run python solver/validate.py

The round trips need texts/model/*.txt and texts/pd/hardy_110.txt from
solver/fetch_texts.py. The CODES example and puzzle 2-2 do not.
"""
import json
import sys
from pathlib import Path

import engine
import rules

ROOT = Path(__file__).resolve().parent.parent

PASS, FAIL = "PASS", "FAIL"
failures = []


def check(name, ok, detail=""):
    print(f"[{PASS if ok else FAIL}] {name}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(name)


COSMOS_PASSAGE = (
    "first ages of the world, the islanders either thought themselves to be the "
    "only dwellers upon the earth, or else if there were any other, yet they could "
    "not possibly conceive how they might have any commerce with them, being severed "
    "by the deep and broad sea, but the aftertimes found out the invention of ships"
)
CODES_CIPHERS = [
    [31, 14, 15, 8, 41],
    [37, 52, 44, 20, 56],
    [28, 55, 15, 18, 47],
]


def test_codes_example():
    stream = engine.first_letters(COSMOS_PASSAGE)
    ok_len = len(stream) == 56
    check("codes-example: stream length is 56 keyed words", ok_len, f"got {len(stream)}")
    for i, ciph in enumerate(CODES_CIPHERS, 1):
        dec = engine.decode_stream(stream, ciph, offset=1)
        check(f"codes-example: cipher {i} decodes to CODES", dec == "CODES", f"got {dec!r}")


PUZZLE_22_PLAIN = "INMEMORYOFJOHNLENNONNOBODYTOLDMETHEREDBEDAYSLIKETHESE"


def test_puzzle_22():
    """Solved puzzle 2-2: reversed chapter-title chain, plaintext read backwards."""
    blob = json.loads((ROOT / "data" / "catch22_chapter_titles.json").read_text(encoding="utf-8"))
    cipher = json.loads((ROOT / "data" / "ciphers.json").read_text(encoding="utf-8"))["2-2"]
    chain = rules.chapter_title_chain(blob["titles"])
    check("2-2: chapter-title chain covers the largest cipher number",
          len(chain) >= max(cipher), f"chain={len(chain)} max={max(cipher)}")
    dec = engine.decode_stream(chain[::-1], cipher, offset=1)[::-1]
    check("2-2: reversed Catch-22 titles decode to the Lennon message",
          dec == PUZZLE_22_PLAIN, dec)


def make_scorer():
    model = sorted((ROOT / "texts" / "model").glob("*.txt"))
    if not model:
        sys.exit(
            "No scoring model in texts/model/. "
            "Run: uv run python solver/fetch_texts.py"
        )
    texts = [p.read_text(encoding="utf-8") for p in model]
    return engine.TrigramScorer(texts)


def encode(plain, stream, start):
    """Greedy multiple-substitution encoding: smallest increasing numbers whose
    stream letters spell `plain`, with cipher number 1 pointing at stream[start]
    (0-based), matching search_stream's `idx = start + n - 1` convention."""
    nums, cur = [], start
    for ch in plain:
        idx = stream.find(ch, cur)
        if idx < 0:
            return None
        nums.append(idx - start + 1)
        cur = idx + 1
    return nums


def round_trip(scorer, family, stream, plain, start, reverse_stream, reverse_plain):
    s = stream[::-1] if reverse_stream else stream
    nums = encode(plain, s, start)
    if nums is None:
        return None
    max_n = max(nums)
    results = []
    engine.search_stream(s, nums, scorer, max_n=max_n, step=1,
                         label=family, results=results, top_k=None)
    best = results[0]
    dec = engine.decode_stream(s, nums, offset=1 - start)
    if reverse_plain:
        dec = dec[::-1]
    want = plain[::-1] if reverse_plain else plain
    return best, dec == want


def test_round_trips(scorer):
    hardy = ROOT / "texts" / "pd" / "hardy_110.txt"
    if not hardy.is_file():
        sys.exit(f"Missing {hardy}. Run: uv run python solver/fetch_texts.py")
    text = hardy.read_text(encoding="utf-8")
    plain = engine.letters_only(
        "It was a fine summer morning and the road lay white between the hedges"
    )[:64]
    allrules = rules.all_rules(text)
    for family, stream in sorted(allrules.items()):
        if len(stream) < 4000:
            check(f"round-trip {family}", False, "stream too short to test")
            continue
        for rev_stream in (False, True):
            for rev_plain in (False, True):
                res = round_trip(scorer, family, stream, plain, 1500,
                                 rev_stream, rev_plain)
                tag = f"round-trip {family} rev_stream={rev_stream} rev_plain={rev_plain}"
                if res is None:
                    check(tag, False, "could not encode")
                    continue
                best, exact = res
                ok = exact and best[2] == 1500
                check(tag, ok, f"top offset={best[2]} score={best[0]:.3f}")


def test_null_tolerance(scorer):
    import random
    plain = engine.letters_only(
        "The ship went down in the fog and nobody ever found the bell again"
    )
    clean = scorer.score(plain)

    # Windowed scoring rescues CLUSTERED nulls only.
    clustered = plain[: len(plain) * 2 // 3] + "XQZJXQZJXQZJXQZJ" + plain[len(plain) * 2 // 3:]
    windowed_c = scorer.score_best_window(clustered, frac=0.5)
    check("null-tolerance: clustered nulls recover English band (windowed)",
          windowed_c > clean - 0.6,
          f"clean={clean:.3f} whole={scorer.score(clustered):.3f} windowed={windowed_c:.3f}")

    # ...and the windowed statistic must still reject noise, or it is useless.
    rng = random.Random(1)
    noise = "".join(rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(120))
    check("null-tolerance: windowed score rejects uniform noise",
          scorer.score_best_window(noise, frac=0.6) < -8.1,
          f"noise windowed={scorer.score_best_window(noise, frac=0.6):.3f}")

    # Documented limitation, asserted as a property of the statistics rather than
    # of the solver: with nulls scattered or periodic, no window of the decode is
    # null-free, so neither score_best_window nor the whole-decode mean recovers
    # the English band. A scattered-null plaintext would need partial-word
    # back-solving, which is not implemented. See docs/methodology.md.
    scattered = list(plain)
    rng2 = random.Random(7)
    for _ in range(len(plain) // 8):
        scattered.insert(rng2.randrange(len(scattered)), rng2.choice("XQZJ"))
    scattered = "".join(scattered)
    check("limitation: scattered nulls are NOT recoverable by windowed scoring "
          "(expected to fail the band, documenting the gap)",
          scorer.score_best_window(scattered, frac=0.6) < clean - 0.6,
          f"scattered windowed={scorer.score_best_window(scattered, frac=0.6):.3f}")


def main():
    test_codes_example()
    test_puzzle_22()
    scorer = make_scorer()
    test_round_trips(scorer)
    test_null_tolerance(scorer)
    print()
    if failures:
        print(f"{len(failures)} FAILURES: {failures}")
        sys.exit(1)
    print("ALL VALIDATION CHECKS PASSED")


if __name__ == "__main__":
    main()
