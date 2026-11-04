"""Sweep a book text against the Decipher ciphers.

Usage:
    uv run python sweep.py TEXT.txt [...] [--cipher 3-1|3-2|3-3|2-4|all] [--top 10]
                                            [--sliding-only]

`all` is the four open ciphers: 2-4, 3-1, 3-2, 3-3. Name 2-1, 2-2, or 2-3
explicitly to sweep a solved message.

Two search shapes are run. The **sliding** shape is the original one: the 21
families in rules.py with the numbering start slid across the whole text and both
stream directions tested. The **anchored** shape, added 2026-11-03 after Eckman's
2-1 reconstruction, is every one of those families doubled as `S || reverse(S)` and
anchored on paragraph boundaries, gated to the passage lengths the cipher can
address. `--sliding-only` turns the anchored shape off, which reproduces the
pre-2026-11-03 search space exactly - use it to compare against results/ logs
recorded before that date.

If TEXT.chapters.json or, for TEXT.clean.txt, TEXT.chapters.json sits beside
the file, the concatenated chapter titles are tested as the extra rule
`chapter-titles`. That is the Catch-22 rule. The 21 families in rules.py are
unchanged.

The English model is only the five books in texts/model/ (see
data/pg_manifest.json). The documented score bands were calibrated on that
model. The command exits if texts/model/ is empty.

Calibration: a genuine-English decode scores about -7.9 to -8.0 per trigram;
random noise sits at -8.6 and below. Anything above -8.2 deserves a look, and
anything above -8.0 should be checked by hand against the physical book. The
`win` column is TrigramScorer.score_best_window, which has its OWN noise floor at
about -8.1; a candidate is flagged if EITHER statistic clears its own band. A high
`win` on a low mean is the edition-drift signature described in
docs/methodology.md gap 1, and reading the mean alone would miss it.
"""
import argparse
import json
import sys
from pathlib import Path

import engine
import rules

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CIPHERS = json.load(open(ROOT / "data" / "ciphers.json", encoding="utf-8"))
OPEN_CIPHERS = ("2-4", "3-1", "3-2", "3-3")

# Documented score bands (docs/methodology.md, calibrated on solved 2-2). The two
# statistics have DIFFERENT noise floors, so a candidate must be judged against the
# band for the statistic being read. Flagging on the mean alone hid edition-drift
# near-misses, whose mean sits in the noise band while their best window is English.
MEAN_LOOK = -8.2        # mean above this deserves a look; -8.0..-7.9 is genuine English
WINDOW_NOISE = -8.1     # score_best_window noise floor

# Families whose window score is inflated by letter-density artifacts rather than by
# English. Established in the 2026-10-31 whole-book campaign (results/RUN_LOG.md):
# the four highest `win` values across 16 book x cipher combinations were all on
# `*-wordlast` / `last-letters`, and every preview was vowel salad. They are still
# worth printing - a real hit would have to beat the artifact - but they must not
# read as a lead, or the window-band flag just generates work.
WINDOW_ARTIFACT_TOKENS = ("last-letters", "wordlast")


def is_window_artifact(rule: str) -> bool:
    return any(tok in rule for tok in WINDOW_ARTIFACT_TOKENS)


def look_flag(hit) -> str:
    """The reporting flag for one candidate, or '' if it clears neither band."""
    if hit["score"] > MEAN_LOOK:
        return "  <-- CHECK THIS"
    if hit["windowed"] > WINDOW_NOISE:
        if is_window_artifact(hit["rule"]):
            return "  <-- window band, known letter-density artifact family"
        return "  <-- CHECK THIS (window band only)"
    return ""


def is_real_lead(hit) -> bool:
    """True only for a flag worth stopping the sweep over."""
    return bool(look_flag(hit)) and not is_window_artifact(hit["rule"])


def build_scorer():
    paths = sorted((ROOT / "texts" / "model").glob("*.txt"))
    if not paths:
        print(
            "No scoring model found in texts/model/.\n"
            "Run: uv run python solver/fetch_texts.py",
            file=sys.stderr,
        )
        sys.exit(1)
    texts = [p.read_text(encoding="utf-8", errors="replace") for p in paths]
    return engine.TrigramScorer(texts)


def chapters_for(text_path):
    """Chapter-title chain from a sibling JSON file, if one exists."""
    path = Path(text_path)
    candidates = [path.with_name(path.stem + ".chapters.json")]
    if path.stem.endswith(".clean"):
        base = path.stem[: -len(".clean")]
        candidates.append(path.with_name(base + ".chapters.json"))
    for cj in candidates:
        if not cj.is_file():
            continue
        data = json.loads(cj.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = data.get("titles", [])
        titles = []
        for item in data:
            if isinstance(item, str):
                titles.append(item)
            elif isinstance(item, dict) and item.get("title"):
                titles.append(str(item["title"]))
        if titles:
            return {"chapter-titles": rules.chapter_title_chain(titles)}
    return {}


def sweep_text(raw, cipher, scorer, top, extra_rules=None, palindromic=True):
    """Score `raw` against one cipher, by both search shapes.

    Sliding: the 21 families (plus any extra_rules) with the numbering start slid
    across the whole text and both stream directions tested. Anchored: every family
    in doubled `S || reverse(S)` form, anchored on paragraph boundaries and gated to
    the passage lengths this cipher can address. The anchored shape is not optional
    decoration — 153 of 2-1's 314 integers exceed its 492-letter source, so a purely
    sliding sweep returns a noise-band negative on the correct book and passage.

    `windowed` is computed across the whole retained pool, not just the reported top,
    because the mean and the window score have different noise floors (-8.6 and -8.1).
    Ranking on the mean alone is what let edition-drift near-misses be discarded
    unseen; both are returned so the caller can flag on either.
    """
    max_n = max(t for t in cipher if isinstance(t, int))
    anchored_pairs = {}
    families = rules.all_rules(raw)
    if extra_rules:
        families.update(extra_rules)
    results = []
    for rule, stream in families.items():
        if len(stream) <= max_n:
            continue
        engine.search_stream(stream, cipher, scorer, max_n=max_n, step=1,
                             label=rule, results=results, top_k=None)
        results.sort(key=lambda r: -r[0])
        del results[200:]
    results.sort(key=lambda r: -r[0])

    out = []
    for score, rule, off, direction, plaindir in results:
        stream = families[rule]
        stream = stream[::-1] if direction == "from-end" else stream
        dec = engine.decode_stream(stream, cipher, offset=1 - off)
        if plaindir == "rev":
            dec = dec[::-1]
        out.append({
            "score": round(score, 4),
            "windowed": round(scorer.score_best_window(dec), 4),
            "rule": rule, "start": off, "direction": direction,
            "plaintext_direction": plaindir, "decode": dec,
            "origin": "sliding",
        })

    if palindromic:
        starts = rules.sentence_boundary_starts(raw)
        coords = {
            "letters": [s[0] for s in starts],
            "first-letters": [s[1] for s in starts],
            "last-letters": [s[1] for s in starts],
        }
        lo, hi = rules.palindromic_length_gate(max_n)
        lengths = list(range(lo, hi + 1))
        seen = set()
        for fam in rules.anchored_scan_families():
            stream = families.get(fam)
            if not stream or not coords[fam]:
                continue
            by_mean, by_window = engine.search_anchored(
                stream, cipher, scorer, coords[fam], lengths, top_k=top)
            pairs = by_mean[0]["pairs"] if by_mean else 0
            anchored_pairs[fam] = pairs
            for h in by_mean + by_window:
                sig = (fam, h["start"], h["length"], h["plaintext_direction"])
                if sig in seen:
                    continue
                seen.add(sig)
                src = stream[h["start"]:h["start"] + h["length"]]
                key = engine.palindromic_key(src)
                dec = engine.decode_stream(key, cipher, offset=1)
                if h["plaintext_direction"] == "rev":
                    dec = dec[::-1]
                out.append({
                    "score": round(h["score"], 4),
                    "windowed": round(h["windowed"], 4),
                    "rule": f"{fam}-palindrome", "start": h["start"],
                    "length": h["length"], "direction": "anchored",
                    "plaintext_direction": h["plaintext_direction"],
                    "decode": dec, "origin": "palindromic",
                })

    out.sort(key=lambda h: -h["score"])
    return out[:top], out, anchored_pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("texts", nargs="+")
    ap.add_argument("--cipher", default="all")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--sliding-only", action="store_true",
                    help="skip the anchored palindromic family; reproduces the "
                         "pre-2026-11-03 search space, for calibration comparison")
    args = ap.parse_args()

    if args.cipher == "all":
        keys = list(OPEN_CIPHERS)
    elif args.cipher in CIPHERS:
        keys = [args.cipher]
    else:
        known = ", ".join(list(CIPHERS) + ["all"])
        print(f"Unknown cipher {args.cipher!r}. Choose from: {known}", file=sys.stderr)
        print("`all` sweeps the four open ciphers: " + ", ".join(OPEN_CIPHERS), file=sys.stderr)
        sys.exit(2)
    scorer = build_scorer()
    any_hit = False
    for path in args.texts:
        raw = Path(path).read_text(encoding="utf-8", errors="replace")
        extra = chapters_for(path)
        if extra:
            n = len(extra["chapter-titles"])
            print(f"{path}: also testing chapter-titles ({n} letters)")
        for key in keys:
            hits, pool, anchored = sweep_text(raw, CIPHERS[key], scorer, args.top,
                                              extra,
                                              palindromic=not args.sliding_only)
            n_pal = sum(1 for h in pool if h["origin"] == "palindromic")
            print(f"== {path} vs cipher {key}"
                  f"  (pool={len(pool)}, anchored palindromic={n_pal}"
                  f"{', skipped' if args.sliding_only else ''})")
            if not args.sliding_only:
                detail = ", ".join(f"{f}={n}" for f, n in anchored.items())
                print(f"   anchored (start,length) pairs searched: {detail or 'none'}")
                if not any(anchored.values()):
                    print("   WARNING: the anchored palindromic search space was EMPTY."
                          " A negative below says nothing about that construction -"
                          " do not record it as an elimination.")
            for h in hits:
                flag = look_flag(h)
                if is_real_lead(h):
                    any_hit = True
                print(f"  {h['score']:8.4f} win={h['windowed']:8.4f} "
                      f"{h['rule']:26s} "
                      f"start={h['start']:7d} L={str(h.get('length', '-')):>5s} "
                      f"{h['direction']:8s} {h['plaintext_direction']}"
                      f"{flag}")
                print(f"      {h['decode'][:70]}")
            # A near-miss can clear the window band while its mean sits in the noise
            # band, which is the edition-drift signature. Those must not be hidden
            # below the top-N-by-mean cut. `hits` is exactly pool[:top], so the
            # unreported remainder is a plain slice.
            near = [h for h in pool[args.top:] if look_flag(h)]
            near.sort(key=lambda h: -h["windowed"])
            for h in near[: args.top]:
                if is_real_lead(h):
                    any_hit = True
                print(f"  {h['score']:8.4f} win={h['windowed']:8.4f} "
                      f"{h['rule']:26s} "
                      f"start={h['start']:7d} L={str(h.get('length', '-')):>5s} "
                      f"{h['direction']:8s} {h['plaintext_direction']}"
                      f"{look_flag(h)}")
                print(f"      {h['decode'][:70]}")
    if not any_hit:
        print("\nNo candidate reached the genuine-English band on either statistic. "
              "Under the tested rule families - now including the anchored "
              "palindromic construction unless --sliding-only was given - this text "
              "does not contain the key stream.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
