"""Rebuild the public-domain corpus from Project Gutenberg by ebook ID.

Usage:
    uv run python solver/fetch_texts.py            # download everything missing
    uv run python solver/fetch_texts.py --force    # re-download all
    uv run python solver/fetch_texts.py --normalize

Writes texts/pd/<author>_<id>.txt, texts/poe/, and texts/model/. Files are
saved as Project Gutenberg ships them, including the header. The published
elimination logs were computed on those files. Stripping the header changes
the phase of every-Nth-letter rules, so the default leaves the header in place.

--normalize runs normalize_text.py on each new download before saving. Use
that for a boilerplate-free copy. Do not compare a normalized copy with the
published logs.

Exits 1 if any Gutenberg download fails. The three Standard Ebooks files are
not on Gutenberg. The command prints their filenames and does not treat them
as download failures.
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = json.load(open(HERE.parent / "data" / "pg_manifest.json", encoding="utf-8"))
MIRROR = "https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt"


def fetch(eid):
    url = MIRROR.format(id=eid)
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--normalize", action="store_true",
                    help="strip Gutenberg boilerplate before saving")
    args = ap.parse_args()
    normalizer = None
    if args.normalize:
        from normalize_text import normalize as normalizer
        print("Normalizing downloads. Every-Nth rules will not match results/.")
    failures = []
    for group in ("pd", "poe", "model"):
        outdir = HERE.parent / "texts" / group
        outdir.mkdir(parents=True, exist_ok=True)
        for author, eid in MANIFEST[group]:
            dst = outdir / f"{author}_{eid}.txt"
            if dst.exists() and not args.force:
                continue
            try:
                text = fetch(eid)
                if normalizer is not None:
                    text = normalizer(text)
                dst.write_text(text, encoding="utf-8")
                print(f"  fetched {dst.name}")
            except Exception as exc:  # noqa: BLE001 - network is best-effort here
                failures.append(f"{author}_{eid}: {exc}")
                print(f"  FAILED {author}_{eid}: {exc}", file=sys.stderr)
    manual = MANIFEST.get("manual_standard_ebooks", [])
    if manual:
        print("\nNot on Project Gutenberg. Download the Standard Ebooks edition")
        print("(https://github.com/standardebooks) and save it in texts/pd/ under")
        print("the filename on the right, so the published logs can be compared:")
        for item in manual:
            if isinstance(item, str):
                print(f"  - {item}")
            else:
                print(f"  - {item['se_id']}  ->  texts/pd/{item['save_as']}")
    print("done")
    if failures:
        print(f"{len(failures)} download(s) failed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
