"""Regression tests for the Decipher solver.

Five kinds of check, all must pass before any sweep result is trusted:

1. decipher-I-example — the real worked example printed in the Decipher III
   rulebook (pages 3-4): the 56 keyed words of Cosmos ch.6 and the three sample
   ciphers that all encode CODES. Copyright-free and independent of our corpus.
2. puzzle 2-2 — the 42 Catch-22 chapter titles in data/catch22_chapter_titles.json,
   concatenated, reversed, then the decode read backwards. The book text is not
   required.
3. puzzle 2-1 — the 492-letter Gulliver's Travels passage in
   data/gulliver_ii1_passage.txt, doubled into a 984-position palindromic key, with
   the two working corrections from data/ii1_corrections.json. Asserted against the
   source, key and plaintext SHA-256 values published by Eckman (2026,
   doi:10.5281/zenodo.23844582) and independently reproduced by solver/verify_ii1.py.
   The decoded message is never printed or stored, only hashed.
4. palindromic gate and positive control — the length gate must admit the real 2-1
   source, and the anchored search must actually LOCATE that passage inside a larger
   text and outrank every other paragraph in it. Wiring a family up is not the same
   as it firing.
5. round-trip per rule family — encode a genuine English plaintext into cipher
   numbers against a stream built by that family, then require search_stream to
   rank the true numbering start #1 and reproduce the plaintext exactly, in both
   stream directions and both plaintext directions.

Run from the repository root, or from anywhere:

    uv run python solver/validate.py

Checks 3-5 need texts/model/*.txt and texts/pd/hardy_110.txt from
solver/fetch_texts.py. The CODES example and puzzle 2-2 do not.
"""
import hashlib
import json
import sys
import unicodedata
from pathlib import Path

import engine
import rules
import sweep
import analyze_ciphertexts
import drift_diagnostic
import null_diagnostic

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


def test_the_source_elimination():
    """The 'Michener, The Source' theory for 2-4 fails on chain length alone."""
    blob = json.loads((ROOT / "data" / "the_source_chapter_titles.json").read_text(encoding="utf-8"))
    ciphers = json.loads((ROOT / "data" / "ciphers.json").read_text(encoding="utf-8"))
    chain = rules.chapter_title_chain(blob["titles"])
    check("The Source: 17 chapter titles", len(blob["titles"]) == 17,
          f"got {len(blob['titles'])}")
    for name in ("2-4", "3-1", "3-2", "3-3"):
        ciph = [n for n in ciphers[name] if isinstance(n, int)]
        check(f"The Source title chain too short for {name} "
              f"(chain={len(chain)} < max={max(ciph)})",
              len(chain) < max(ciph))


II1_SOURCE_SHA = "9eeff566fe707e39486c1bb119d5c82f19566772706342c44803d6079faef29d"
II1_KEY_SHA = "571b2327a0ef55d6fc74394b228ffc59e24a00f2ef6f670beb1fa08879eb5466"
II1_PLAIN_SHA = "859f2c3458025e03ad8a425b8e9b9e16f152927b8b34e33300ad1d49d065ee1f"


def sha_letters(s):
    """SHA-256 over uppercase ASCII letters, no trailing newline."""
    return hashlib.sha256(s.encode("ascii")).hexdigest()


def ii1_working_cipher():
    """2-1 as printed, with the two documented working corrections applied.

    data/ciphers.json deliberately keeps the ORIGINAL transcription - observation
    169 is still 330 there - so the historical record and the fingerprint test stay
    honest about what was typed at the time. The 830 reading was graded probable by
    the published reconstruction and was blind-verified from the puzzle image on
    2026-11-05 (results/RUN_LOG.md): four fresh contexts, unanimous 830, with the
    genuine 330 at position 148 read correctly in the same crop. The corrections
    live in their own file, mirroring the published reconstruction's separation.
    """
    ciphers = json.loads((ROOT / "data" / "ciphers.json").read_text(encoding="utf-8"))
    spec = json.loads((ROOT / "data" / "ii1_corrections.json").read_text(encoding="utf-8"))
    working = list(ciphers["2-1"])
    for c in spec["corrections"]:
        working[c["position"] - 1] = c["corrected"]
    return working


def test_puzzle_21(scorer):
    """Solved puzzle 2-1: a 492-letter passage doubled into a 984-position key.

    Eckman (2026, doi:10.5281/zenodo.23844582) reconstructed this; solver/
    verify_ii1.py verifies it independently against his published hashes. These
    checks keep the result wired into the regression suite so the palindromic
    family cannot silently rot.

    The decoded message is never printed or stored here - only its SHA-256. It is
    third-party expression that the author does not redistribute, and neither do we.
    """
    path = ROOT / "data" / "gulliver_ii1_passage.txt"
    if not path.is_file():
        sys.exit(f"Missing {path}. See docs/decipher-ii.md for provenance.")
    raw = path.read_text(encoding="utf-8")

    source = engine.letters_only(raw)
    nfkd = "".join(c for c in unicodedata.normalize("NFKD", raw).upper() if "A" <= c <= "Z")
    check("2-1: engine.letters_only agrees with the paper's NFKD normalization "
          "on this witness", source == nfkd,
          "differs - an accented witness would need the NFKD path")
    check("2-1: passage normalizes to 492 letters", len(source) == 492,
          f"got {len(source)}")
    check("2-1: source SHA-256 matches the published value",
          sha_letters(source) == II1_SOURCE_SHA, sha_letters(source)[:16])

    key = engine.palindromic_key(source)
    check("2-1: doubled key has 984 positions", len(key) == 984, f"got {len(key)}")
    check("2-1: key SHA-256 matches the published value",
          sha_letters(key) == II1_KEY_SHA, sha_letters(key)[:16])
    check("2-1: slots n and 985-n address the same letter",
          all(key[n - 1] == key[985 - n - 1] for n in range(1, 493)))

    working = ii1_working_cipher()
    dec = engine.decode_palindromic(source, working)
    check("2-1: doubled key resolves all 314 observations",
          len(dec) == 314 and "?" not in dec, f"len={len(dec)}")
    check("2-1: plaintext SHA-256 matches the published value",
          sha_letters(dec) == II1_PLAIN_SHA, sha_letters(dec)[:16])

    # CALIBRATION CAVEAT, asserted so it cannot silently drift. The true 2-1
    # plaintext scores about -8.14, which is BELOW the -7.9..-8.0 prose band the
    # thresholds were calibrated on and only ~0.06 above the -8.2 look threshold.
    # The message is verse, and the model is built from five prose novels. Any
    # threshold reasoning that assumes a correct decode lands at -7.9 is wrong by
    # a fifth of the entire signal-to-noise gap. See docs/methodology.md.
    score = scorer.score(dec)
    check("2-1: true plaintext clears the look threshold but sits BELOW the prose "
          "English band (verse, not prose)", -8.2 < score < -8.0, f"score={score:.3f}")
    windowed = scorer.score_best_window(dec)
    check("2-1: window score clears its own -8.1 floor by less than 0.05",
          -8.1 < windowed < -8.0, f"win={windowed:.3f}")


def test_palindromic_gate():
    """The length gate must admit the real 2-1 source and reject what cannot work."""
    lo, hi = rules.palindromic_length_gate(980)
    check("gate: 2-1 admits the true 492-letter source", lo <= 492 <= hi, f"[{lo},{hi}]")
    check("gate: 2-1 also admits the 490-letter Wikisource variant, so the "
          "near-miss can be scored rather than silently skipped", lo <= 490 <= hi)
    check("gate: lower bound is the tightest length whose doubling reaches max_n",
          2 * lo >= 980 and 2 * (lo - 1) < 980, f"lo={lo}")
    check("gate: upper bound excludes the degenerate forward-only case",
          hi == 979 and 2 * hi >= 980, f"hi={hi}")
    for name, max_n in (("2-4", 1053), ("3-1", 516), ("3-2", 416), ("3-3", 721)):
        lo_n, hi_n = rules.palindromic_length_gate(max_n)
        check(f"gate: {name} range is non-empty and reaches max_n",
              lo_n <= hi_n and 2 * lo_n >= max_n, f"[{lo_n},{hi_n}] max={max_n}")


def test_palindromic_positive_control(scorer):
    """The anchored search must LOCATE the 2-1 passage among real competitors.

    Wiring a family up is not the same as it firing. The passage has to be found at
    the exact length 492 out of every (sentence start, length) pair in the gate, and
    outrank all of them.

    Two earlier versions of this control were wrong and are recorded here so the
    mistake is not repeated. The first used texts/pd/hardy_110.txt as filler and
    passed vacuously: that file is verse, its 2,933 "paragraphs" are 54-67 letter
    stanzas, and exactly one unit in 180k characters fell inside the [490,979] gate
    - the answer itself. The second anchored on paragraph runs, which measurement
    showed yields ZERO candidates for the 2-1 and 2-4 gates across three texts,
    because these books average ~48 letters per paragraph. A control with no
    competitors proves nothing, so the size of the search space is asserted too.
    """
    passage = (ROOT / "data" / "gulliver_ii1_passage.txt").read_text(encoding="utf-8")
    prose = ROOT / "texts" / "model" / "pride_1342.txt"
    if not prose.is_file():
        sys.exit(f"Missing {prose}. Run: uv run python solver/fetch_texts.py")
    filler = prose.read_text(encoding="utf-8", errors="replace")
    text = filler[:40000] + "\n\n" + passage + "\n\n" + filler[40000:90000]

    working = ii1_working_cipher()
    max_n = max(working)
    lo, hi = rules.palindromic_length_gate(max_n)
    lengths = list(range(lo, hi + 1))

    stream = engine.letters_only(text)
    starts = [s[0] for s in rules.sentence_boundary_starts(text)]
    check("positive control: the sentence-start anchor set is non-trivial",
          len(starts) >= 100, f"{len(starts)} starts over {len(stream)} letters")

    by_mean, by_window = engine.search_anchored(
        stream, working, scorer, starts, lengths, top_k=25)
    pairs = by_mean[0]["pairs"] if by_mean else 0
    check("positive control: the search space is large, not vacuous",
          pairs >= 10000, f"{pairs} (start,length) pairs")

    best = by_mean[0]
    target = engine.letters_only(passage)
    got = stream[best["start"]:best["start"] + best["length"]]
    check("positive control: the top-ranked pair recovers L=492 exactly",
          best["length"] == 492, f"L={best['length']} start={best['start']}")
    check("positive control: the top-ranked passage IS the Swift source",
          got == target, f"len={len(got)}")
    runner_up = by_mean[1]["score"] if len(by_mean) > 1 else float("-inf")
    check("positive control: the winner separates from the runner-up",
          best["score"] > runner_up, f"best={best['score']:.3f} next={runner_up:.3f}")
    check("positive control: the winner clears the -8.2 look threshold",
          best["score"] > -8.2,
          f"mean={best['score']:.3f} win={best['windowed']:.3f}")
    dec = engine.decode_stream(engine.palindromic_key(got), working, offset=1)
    check("positive control: recovered plaintext hash matches the published value",
          sha_letters(dec) == II1_PLAIN_SHA, sha_letters(dec)[:16])
    win_best = by_window[0]
    check("positive control: the window-ranked list also surfaces the true passage",
          win_best["length"] == 492 and win_best["start"] == best["start"],
          f"win top: start={win_best['start']} L={win_best['length']} "
          f"win={win_best['windowed']:.3f}")


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

    # Documented limitation of rigid/windowed statistics: with nulls scattered or
    # periodic, no contiguous window of the decode is null-free, so neither
    # score_best_window nor the whole-decode mean recovers the English band.
    # Scattered/periodic nulls are handled separately by solver/null_diagnostic.py
    # (tested below in test_extended_palindromic_and_null_viterbi).
    scattered = list(plain)
    rng2 = random.Random(7)
    for _ in range(len(plain) // 8):
        scattered.insert(rng2.randrange(len(scattered)), rng2.choice("XQZJ"))
    scattered = "".join(scattered)
    check("limitation: scattered nulls are NOT recoverable by windowed scoring "
          "(expected to fail the band, documenting the gap)",
          scorer.score_best_window(scattered, frac=0.6) < clean - 0.6,
          f"scattered windowed={scorer.score_best_window(scattered, frac=0.6):.3f}")


def test_ciphertext_patterns_and_drift(scorer):
    """Verify structural invariants, palindromic fold statistic, and 3-band drift recovery."""
    ciphers = analyze_ciphertexts.load_ciphers(apply_ii1_corrections=True)
    s21 = analyze_ciphertexts.analyze_one("2-1", ciphers["2-1"])
    s24 = analyze_ciphertexts.analyze_one("2-4", ciphers["2-4"])
    s33 = analyze_ciphertexts.analyze_one("3-3", ciphers["3-3"])
    s31 = analyze_ciphertexts.analyze_one("3-1", ciphers["3-1"])
    check("2-1: working cipher has 261 unique ints and palindromic fold peak 10 at R=984",
          s21["unique_ints"] == 261 and s21["fold_peak"] == 10
          and s21["fold_best_r"] == 984 and s21["fold_perm_p"] < 0.005,
          f"unique={s21['unique_ints']} fold={s21['fold_peak']}@{s21['fold_best_r']} p={s21['fold_perm_p']}")
    check("2-4: flat palindromic fold scan (peak<=2) despite 13 same-direction |d|=1 pairs",
          s24["fold_peak"] <= 2 and s24["fold_perm_p"] > 0.5 and s24["step1_count"] == 13,
          f"fold={s24['fold_peak']} p={s24['fold_perm_p']} step1={s24['step1_count']}")
    check("3-3: strictly zero repeated integers across 156 numeric tokens",
          s33["extra_repeat_uses"] == 0 and s33["unique_ints"] == 156,
          f"unique={s33['unique_ints']} repeats={s33['extra_repeat_uses']}")
    check("3-1: only 4 repeat collisions across 164 numeric tokens + adjacent 487,487",
          s31["extra_repeat_uses"] == 4 and (26, 487) in s31["same_adjacent_pairs"],
          f"repeats={s31['extra_repeat_uses']} adj={s31['same_adjacent_pairs']}")

    # Exact-length stream check (len(stream) == max_n, previously skipped by need=max_n+1)
    hardy = (ROOT / "texts" / "pd" / "hardy_110.txt").read_text(encoding="utf-8")
    wstream = engine.first_letters(hardy)
    plain = engine.letters_only(
        "The secret message was hidden inside the first letters of every single word in the chapter"
    )
    ciph_nums = encode(plain, wstream, 1000)
    check("drift-setup: synthetic word-first cipher encoded", ciph_nums is not None)
    if ciph_nums is not None:
        exact_len_slice = wstream[1000 : 1000 + max(ciph_nums)]
        res_exact = []
        engine.search_stream(exact_len_slice, ciph_nums, scorer,
                             max_n=max(ciph_nums), label="exact", results=res_exact)
        check("engine: exact-length stream (len == max_n) is searched, not skipped",
              len(res_exact) > 0 and res_exact[0][2] == 0 and res_exact[0][0] > -8.0,
              f"hits={len(res_exact)} top_score={res_exact[0][0]:.3f}")

        # Simulate 2 dropped OCR/edition words inside the key window (1 in Band 1, 1 in Band 2)
        max_c = max(ciph_nums)
        b1_drop = 1000 + (max_c // 3) + 5
        b2_drop = 1000 + (2 * max_c // 3) + 5
        corrupted = (
            wstream[:b1_drop]
            + wstream[b1_drop + 1 : b2_drop]
            + wstream[b2_drop + 1 : 3500]
        )
        hits = drift_diagnostic.search_elastic_stream(
            corrupted, ciph_nums, scorer, max_step=2, label="first-letters", top_k=3
        )
        top_h = hits[0]
        check("drift-diagnostic: 2 dropped mid-passage words collapse rigid score to noise",
              top_h["rigid_score"] < -8.5,
              f"rigid={top_h['rigid_score']:.3f}")
        check("drift-diagnostic: 3-band index elasticity recovers clean English band & start",
              top_h["elastic_score"] > -8.05 and top_h["start"] == 1000
              and top_h["drift_bands"] == (0, -1, -2) and top_h["decode"] == plain,
              f"elastic={top_h['elastic_score']:.3f} start={top_h['start']} drift={top_h['drift_bands']}")

        # Verify false-positive ceiling on an unrelated slice of the novel
        wrong_slice = wstream[5000:8000]
        noise_hits = drift_diagnostic.search_elastic_stream(
            wrong_slice, ciph_nums, scorer, max_step=2, label="first-letters", top_k=3
        )
        check("drift-diagnostic: unrelated novel slice stays well below look threshold",
              noise_hits[0]["elastic_score"] < drift_diagnostic.ELASTIC_LOOK,
              f"best_noise={noise_hits[0]['elastic_score']:.3f}")


def test_extended_palindromic_and_null_viterbi(scorer):
    """Verify 21-family phase-resolved anchored palindromes and skip-trigram Viterbi nulls."""
    import random
    import numpy as np

    hardy = (ROOT / "texts" / "pd" / "hardy_110.txt").read_text(encoding="utf-8")
    sent_chars = rules.sentence_char_offsets(hardy)
    para_chars = rules.paragraph_char_offsets(hardy)
    sent_set = set(sent_chars)
    body_para_starts = [p for p in para_chars if p in sent_set]

    by_fam = {}
    for fam, phase, sub, st in rules.anchored_palindromic_substreams(hardy, include_extended=True):
        by_fam.setdefault(fam, []).append((phase, sub, set(st)))

    direct_all = rules.all_rules(hardy[body_para_starts[25]:])
    check("extended-palindromic: all 21 rule families emitted by anchored_palindromic_substreams",
          set(by_fam.keys()) == set(direct_all.keys()),
          f"count={len(by_fam)}")

    exact_para = []
    for fam, direct_stream in sorted(direct_all.items()):
        prefix = direct_stream[:240]
        ok = any(
            any(sub[s : s + len(prefix)] == prefix for s in st_set if s + len(prefix) <= len(sub))
            for _, sub, st_set in by_fam[fam]
        )
        if not ok:
            exact_para.append(fam)
    check("extended-palindromic: all 21 families match direct passage extraction at mid-book boundary",
          len(exact_para) == 0,
          f"mismatches={exact_para}")

    direct_mid = rules.all_rules(hardy[sent_chars[123]:])
    exact_mid = []
    for fam, direct_stream in sorted(direct_mid.items()):
        if fam in ("line-first", "paragraph-first"):
            continue
        prefix = direct_stream[:200]
        ok = any(
            any(sub[s : s + len(prefix)] == prefix for s in st_set if s + len(prefix) <= len(sub))
            for _, sub, st_set in by_fam[fam]
        )
        if not ok:
            exact_mid.append(fam)
    check("extended-palindromic: all 19 sentence-granular families match mid-paragraph sentence start",
          len(exact_mid) == 0,
          f"mismatches={exact_mid}")

    # End-to-end strided S || reverse(S) round-trip at a NON-ZERO modulo-3 phase
    snippet = hardy[:18000]
    sn_starts = rules.sentence_boundary_starts(snippet)
    sn_chars = rules.sentence_char_offsets(snippet)
    chosen_char = None
    chosen_l0 = None
    for (l0, _), c_off in zip(sn_starts[15:], sn_chars[15:]):
        if (l0 + 2) % 3 != 0 and len(rules.every_nth_letter(snippet[c_off:], 3)) >= 320:
            chosen_char = c_off
            chosen_l0 = l0
            break
    check("extended-palindromic: found non-zero-phase sentence start for every3-letter",
          chosen_char is not None, f"l0={chosen_l0} phase={(chosen_l0 + 2) % 3 if chosen_l0 else None}")
    if chosen_char is not None:
        src_3 = rules.every_nth_letter(snippet[chosen_char:], 3)[:260]
        pal_key_3 = engine.palindromic_key(src_3)
        plain_pal = engine.letters_only(
            "When the lantern went out along the ridge they waited together in silence until daybreak came over the hills"
        )
        # Homophonic encoding using BOTH halves of S || reverse(S): [1..260] and [261..520]
        rng_pal = random.Random(11)
        pos_h1 = {ch: [i + 1 for i, c in enumerate(pal_key_3[:260]) if c == ch] for ch in set(plain_pal)}
        pos_h2 = {ch: [260 + i + 1 for i, c in enumerate(pal_key_3[260:]) if c == ch] for ch in set(plain_pal)}
        half = len(plain_pal) // 2
        if all(pos_h1[ch] and pos_h2[ch] for ch in set(plain_pal)):
            ciph_pal3 = (
                [rng_pal.choice(pos_h1[ch]) for ch in plain_pal[:half]]
                + [rng_pal.choice(pos_h2[ch]) for ch in plain_pal[half:]]
            )
        else:
            ciph_pal3 = None
        check("extended-palindromic: encoded strided S||rev(S) cipher reaches > len(S)",
              ciph_pal3 is not None and max(ciph_pal3) > 260,
              f"L=260 max_n={max(ciph_pal3) if ciph_pal3 else None}")
        if ciph_pal3 is not None:
            hits_def, _, _ = sweep.sweep_text(snippet, ciph_pal3, scorer, top=5,
                                              palindromic=True, all_palindromic=False)
            hits_ext, _, _ = sweep.sweep_text(snippet, ciph_pal3, scorer, top=5,
                                              palindromic=True, all_palindromic=True)
            check("extended-palindromic: 3-family default misses non-zero-phase every3-letter S||rev(S), "
                  "--all-palindromic recovers it #1",
                  hits_def[0]["score"] < -8.4 and hits_ext[0]["score"] > -8.0
                  and hits_ext[0]["decode"] == plain_pal
                  and hits_ext[0]["rule"].startswith("every3-letter-p"),
                  f"default={hits_def[0]['score']:.3f} ext={hits_ext[0]['score']:.3f} rule={hits_ext[0]['rule']}")

    # Skip-trigram Viterbi scattered-null checks
    plain_std = engine.letters_only(
        "The ship went down in the fog and nobody ever found the bell again"
    )
    row_clean = (np.frombuffer(plain_std.encode(), dtype=np.uint8).astype(np.int64) - 65)[None, :]
    vit_zero = float(null_diagnostic.viterbi_null_score_matrix(row_clean, scorer, max_consec=0)[0])
    vit_clean = float(null_diagnostic.viterbi_null_score_matrix(row_clean, scorer)[0])
    rec_sc, rec_str, rec_skips = null_diagnostic.reconstruct_null_stripped(plain_std, scorer)
    check("null-diagnostic: zero-skip DP matches TrigramScorer.score and vectorized DP matches backpointer",
          abs(vit_zero - scorer.score(plain_std)) < 1e-9
          and abs(vit_clean - rec_sc) < 1e-9 and vit_clean >= vit_zero,
          f"zero_skip={vit_zero:.4f} rigid={scorer.score(plain_std):.4f} vit={vit_clean:.4f}")

    plain_null_base = engine.letters_only(
        "The ship went down in the fog and nobody ever found the bell again "
        "though Captain Brinkley searched the harbor until dawn with lanterns"
    )
    rng_x = random.Random(7)
    scat_list = list(plain_null_base)
    for _ in range(len(plain_null_base) // 8):
        scat_list.insert(rng_x.randrange(len(scat_list)), rng_x.choice("XQZJ"))
    scat_str = "".join(scat_list)
    sc_x, cl_x, sk_x = null_diagnostic.reconstruct_null_stripped(scat_str, scorer)
    check("null-diagnostic: recovers 12.5% scattered XQZJ nulls into English band while preserving OOV stem",
          sc_x > null_diagnostic.NULL_LOOK and "BRINKLE" in cl_x
          and "THEBELLAGAIN" in cl_x and scorer.score(scat_str) < -9.0,
          f"null_score={sc_x:.3f} rigid={scorer.score(scat_str):.3f} skips={len(sk_x)}")

    rng_az = random.Random(42)
    per_az = []
    for i_c, ch in enumerate(plain_null_base):
        per_az.append(ch)
        if (i_c + 1) % 8 == 0:
            per_az.append(rng_az.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    per_str = "".join(per_az)

    wstream = engine.first_letters(hardy)
    key_win = wstream[1200 : 1200 + 600]
    by_ch = {}
    for idx_k, ch_k in enumerate(key_win, 1):
        by_ch.setdefault(ch_k, []).append(idx_k)
    rng_enc = random.Random(99)
    ciph_per = [rng_enc.choice(by_ch[c]) if c in by_ch else c for c in per_str]
    check("null-diagnostic: encoded periodic-A-Z-null cipher into 600-word novel window",
          any(isinstance(t, int) for t in ciph_per))
    nhits = null_diagnostic.search_null_tolerant_stream(
        wstream[:2500], ciph_per, scorer, label="first-letters", top_k=3
    )
    top_n = nhits[0]
    check("null-diagnostic: stream search locates periodic uniform A-Z null cipher #1 at true start",
          top_n["start"] == 1200 and null_diagnostic.is_null_lead(top_n)
          and top_n["rigid_score"] < -8.8 and "BRINKLE" in top_n["cleaned"],
          f"null={top_n['null_score']:.3f} rigid={top_n['rigid_score']:.3f} start={top_n['start']}")

    noise_nhits = null_diagnostic.search_null_tolerant_stream(
        wstream[4000:6500], ciph_per, scorer, label="first-letters", top_k=3
    )
    check("null-diagnostic: unrelated novel slice triggers zero false-positive null leads",
          not any(null_diagnostic.is_null_lead(h) for h in noise_nhits),
          f"best_noise={noise_nhits[0]['null_score']:.3f} skips={noise_nhits[0]['n_skipped']}")


def main():
    test_codes_example()
    test_puzzle_22()
    test_the_source_elimination()
    test_palindromic_gate()
    scorer = make_scorer()
    test_puzzle_21(scorer)
    test_palindromic_positive_control(scorer)
    test_round_trips(scorer)
    test_null_tolerance(scorer)
    test_ciphertext_patterns_and_drift(scorer)
    test_extended_palindromic_and_null_viterbi(scorer)
    print()
    if failures:
        print(f"{len(failures)} FAILURES: {failures}")
        sys.exit(1)
    print("ALL VALIDATION CHECKS PASSED")


if __name__ == "__main__":
    main()
