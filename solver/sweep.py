"""Sweep a book text against the Decipher ciphers.

Usage:
    uv run python sweep.py TEXT.txt [...] [--cipher 3-1|3-2|3-3|2-4|all] [--top 10]

`all` is the four open ciphers: 2-4, 3-1, 3-2, 3-3. Name 2-1, 2-2, or 2-3
explicitly to sweep a solved message.

If TEXT.chapters.json or, for TEXT.clean.txt, TEXT.chapters.json sits beside
the file, the concatenated chapter titles are tested as the extra rule
`chapter-titles`. That is the Catch-22 rule. The 21 families in rules.py are
unchanged.

The English model is only the five books in texts/model/ (see
data/pg_manifest.json). The documented score bands were calibrated on that
model. The command exits if texts/model/ is empty.

Calibration: a genuine-English decode scores about -7.9 to -8.0 per trigram;
random noise sits at -8.6 and below. Anything above -8.2 deserves a look, and
anything above -8.0 should be checked by hand against the physical book.
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


def sweep_text(raw, cipher, scorer, top, extra_rules=None):
    max_n = max(t for t in cipher if isinstance(t, int))
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
    for score, rule, off, direction, plaindir in results[:top]:
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
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("texts", nargs="+")
    ap.add_argument("--cipher", default="all")
    ap.add_argument("--top", type=int, default=10)
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
            hits = sweep_text(raw, CIPHERS[key], scorer, args.top, extra)
            print(f"== {path} vs cipher {key}")
            for h in hits[: args.top]:
                flag = "  <-- CHECK THIS" if h["score"] > -8.2 else ""
                if flag:
                    any_hit = True
                print(f"  {h['score']:8.4f} win={h['windowed']:8.4f} "
                      f"{h['rule']:18s} "
                      f"start={h['start']:7d} {h['direction']:8s} {h['plaintext_direction']}"
                      f"{flag}")
                print(f"      {h['decode'][:70]}")
    if not any_hit:
        print("\nNo candidate reached the genuine-English band. Under the tested rule "
              "families this text does not contain the key stream.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
