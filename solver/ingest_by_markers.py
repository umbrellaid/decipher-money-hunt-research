# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow"]
# ///
"""
ingest_by_markers.py
====================
Marker-chasing OCR ingest for books whose chapter/story boundaries do NOT
align with page boundaries. ocr_ingest.py (page-granular chapters) cannot
express "Robbie starts halfway down page 11"; this script can.

It reuses ocr_ingest.py's proven TSV line-grouping parser (imported), keeps
numeric tokens for marker detection, and splits text at chapter-heading
markers found as STANDALONE LINES:

  * --mode cc        Cat's Cradle: chapter numbers 1..N printed in the
                     margin beside the chapter-title line. The script chases
                     the expected sequence -- after chapter 25 is found,
                     only "26" counts, so page numbers and poem numbers
                     cannot false-match.
  * --mode phrases   marker = a standalone line equal to one of the given
                     phrases (case/space-insensitive), e.g. I, Robot story
                     titles, or Zhivago "CHAPTER TEN" lines.

The marker line itself and the chapter-title words are DROPPED from the
body text (body_scan streams must start at the first body word; drift is
only +-2). Running heads are stripped with --strip-header regexes exactly
like ocr_ingest.py. Pure-numeric tokens are removed from the output text.

Outputs to --out-dir: chNN.txt (or chNNN.txt), qa_report.md, pages_index.csv,
markers_log.csv.

Usage examples (from repo root):
    uv run solver/ingest_by_markers.py --book cats-cradle --mode cc \
        --max-chapter 127 --pages-dir <pages> --out-dir texts/cats-cradle \
        --strip-header "cat'?s cradle" --strip-header "CAT'?S CRADLE"

    uv run solver/ingest_by_markers.py --book i-robot --mode phrases \
        --phrases "1=Introduction,2=Robbie,3=Runaround,4=Reason,5=Catch That Rabbit,6=Liar!,7=Little Lost Robot,8=Escape!,9=Evidence,10=The Evitable Conflict" \
        --pages-dir <pages> --out-dir texts/i-robot \
        --strip-header "I,? ROBOT" --strip-header "^(Introduction|Robbie|Runaround|Reason|Catch That Rabbit|Liar!|Little Lost Robot|Escape!|Evidence|The Evitable Conflict)$"
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ocr_ingest import find_tesseract, natural_key  # noqa: E402

NUM_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17,
}


def ocr_page_lines(tess: str, img: Path, psm: int):
    """Tesseract TSV -> (lines, mean_conf, n_words). Numeric tokens KEPT."""
    proc = subprocess.run(
        [tess, str(img), "stdout", "--psm", str(psm), "tsv"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        return [], 0.0, 0
    rows = [r for r in csv.DictReader(proc.stdout.splitlines(), delimiter="\t")
            if r.get("text", "").strip() and float(r.get("conf", "-1")) >= 0]
    lines: dict[tuple[int, int, int], list[tuple[int, str, float]]] = {}
    line_top: dict[tuple[int, int, int], int] = {}
    for r in rows:
        txt = r["text"].strip()
        if not txt:
            continue
        key = (int(r["block_num"]), int(r["par_num"]), int(r["line_num"]))
        lines.setdefault(key, []).append((int(r["left"]), txt, float(r["conf"])))
        if key not in line_top:
            line_top[key] = int(r["top"])
    ordered = sorted(lines, key=lambda k: (line_top.get(k, 0), k[0], k[1], k[2]))
    out, confs = [], []
    for k in ordered:
        toks = sorted(lines[k])
        out.append([t for _, t, _ in toks])
        confs.extend(c for _, _, c in toks)
    return out, (sum(confs) / len(confs) if confs else 0.0), len(confs)


def norm_line(tokens: list[str]) -> str:
    return re.sub(r"[^a-z0-9 ]", "", " ".join(tokens).lower()).strip()


def ch_nl_match(nl: str, marker_map: dict) -> int | None:
    """Chapter whose normalized phrase appears in line `nl`, anchored at the
    start or end of the line on WORD boundaries (so "chapter fourteen" does
    not prefix-match "chapter four"), tolerant of gutter-noise tokens and a
    trailing page-number digit run like 'chapter sixteen 3'."""
    if not nl:
        return None
    nl = re.sub(r"\s*\d{1,3}$", "", nl)  # trailing page/folio number
    padded = f" {nl} "
    for np_, (ch, _) in marker_map.items():
        if not np_:
            continue
        token = f" {np_} "
        if padded.startswith(token) or padded.endswith(token):
            return ch
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description="marker-chasing OCR ingest")
    ap.add_argument("--book", required=True)
    ap.add_argument("--pages-dir", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--mode", choices=["cc", "phrases"], required=True)
    ap.add_argument("--max-chapter", type=int, default=127, help="cc mode: last chapter number")
    ap.add_argument("--phrases", default="",
                    help='phrases mode: "ch=Phrase,ch=Phrase,..." (order = reading order)')
    ap.add_argument("--psm", type=int, default=6)
    ap.add_argument("--psm-override", default="",
                    help="per-page psm overrides: 'image00404_1L=4,image00448_2R=4' "
                         "(use when one page's heading line is destroyed by psm 6 TSV "
                         "artifacts but reads cleanly under another mode)")
    ap.add_argument("--strip-header", action="append", default=[],
                    help="regex; drop first line when it matches (repeatable)")
    ap.add_argument("--drop-next-line", action="store_true",
                    help="after a marker line, also drop the next line when it is a short "
                         "non-sentence line (e.g. the italic part title under 'CHAPTER TEN')")
    ap.add_argument("--start-image", default="",
                    help="skip marker detection until this image (natural-sorted); earlier "
                         "pages go to ch00_front. Beats ToC pages that list every "
                         "chapter title and would otherwise consume all markers.")
    args = ap.parse_args()

    tess = find_tesseract()
    images = sorted([p for p in args.pages_dir.iterdir()
                     if p.suffix.lower() in {".jpg", ".jpeg", ".png"}], key=natural_key)
    if not images:
        sys.exit(f"no images in {args.pages_dir}")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    # phrase markers -> {norm_phrase: (chapter, phrase)} preserving order
    markers: list[tuple[str, int, str]] = []
    if args.mode == "phrases":
        for item in args.phrases.split(","):
            item = item.strip()
            if not item:
                continue
            ch_s, phrase = item.split("=", 1)
            markers.append((norm_line(phrase.split()), int(ch_s), phrase))
        marker_map = {np: (ch, ph) for np, ch, ph in markers}
        order = [ch for _, ch, _ in markers]
        order_index = {ch: i for i, ch in enumerate(order)}

    expected = 1                      # cc mode: next chapter number to find
    cur_ch = 0                        # 0 = front matter
    chapters: dict[int, list[str]] = {0: []}
    titles: dict[int, str] = {}
    qa_rows, marker_log = [], []
    next_phrase_ch = order[0] if args.mode == "phrases" else None
    psm_override = {}
    for item in args.psm_override.split(","):
        item = item.strip()
        if "=" in item:
            name, psm = item.split("=", 1)
            psm_override[name.strip()] = int(psm)

    # ---- pass 1: OCR every page once, strip running heads, drop duplicates ----
    pages: list[dict] = []
    dup_dropped = []
    for img in images:
        detect = (not args.start_image
                  or natural_key(img) >= natural_key(Path(args.start_image)))
        lines, mean_conf, n_words = ocr_page_lines(
            tess, img, psm_override.get(img.name, psm_override.get(img.stem, args.psm)))
        # running-head strip: check the first few lines -- gutter noise often
        # OCRs as a junk line ABOVE the header, pushing it to line 1-2
        if lines and args.strip_header:
            k = 0
            while k < min(3, len(lines)):
                first = " ".join(lines[k])
                if (len(lines[k]) <= 8
                        and any(re.search(rx, first) for rx in args.strip_header)):
                    # keep a would-be marker line: story-title headers on opener
                    # pages look exactly like running heads
                    keep = (args.mode == "phrases" and k == 0
                            and ch_nl_match(norm_line(lines[0]), marker_map) == next_phrase_ch)
                    if not keep:
                        lines = lines[:k] + lines[k + 1:]
                        continue
                k += 1
        # duplicate re-scan detection: David re-shoots pages when he loses his
        # place; a near-identical neighbor page is a dup -> keep higher conf
        words = {w.lower().strip(".,;:!?\"'") for l in lines for w in l}
        dup = False
        if words and n_words > 20:
            for prev in pages[-3:]:
                pw = prev["wordset"]
                if not pw:
                    continue
                jac = len(words & pw) / max(len(words | pw), 1)
                if jac >= 0.75:
                    dup = True
                    if mean_conf >= prev["conf"]:
                        prev["dropped"] = True   # new capture beats the old one
                        dup_dropped.append(prev["img"].name)
                        dup = False
                    break
        pages.append({"img": img, "lines": lines, "conf": mean_conf,
                      "n_words": n_words, "detect": detect, "wordset": words,
                      "dropped": dup})
        if dup:
            dup_dropped.append(img.name)
    pages = [p for p in pages if not p["dropped"]]
    if dup_dropped:
        print(f"  dropped duplicate re-scans: {dup_dropped}")

    # ---- pass 2: decide the marker set ----
    # cc mode: collect every short-line numeric candidate, then pick the
    # longest strictly-increasing chain (value jumps 1..3). A greedy chase is
    # poisoned by one false page number; the chain survives both false
    # positives and garbled numbers.
    chosen: dict[tuple[int, int], int] = {}   # (page_idx, line_idx) -> chapter
    if args.mode == "cc":
        cands: list[tuple[int, int, int]] = []  # (page_idx, line_idx, value)
        for pi, page in enumerate(pages):
            if not page["detect"]:
                continue
            for li, toks in enumerate(page["lines"]):
                if len(toks) > 7:
                    continue
                # chapter-head lines end with a word or the number; Bokonon
                # verse lines end with , ; : ) or a quote; trailing gutter
                # noise tokens ("|", ")", "]") are stripped before the check
                core = list(toks)
                while core and not re.search(r"[A-Za-z0-9]", core[-1]):
                    core.pop()
                if not core or not re.search(r"[A-Za-z0-9]\.?$", core[-1]):
                    continue
                has_title = any(re.match(r"^[A-Z]", t) for t in toks
                                if not re.fullmatch(r"\d{1,3}[.,;:]?", t))
                if not has_title:
                    # number-only line: only a marker if the next line is a
                    # short title, not the start of body text
                    if not (li + 1 < len(page["lines"])
                            and len(page["lines"][li + 1]) <= 10
                            and any(re.match(r"^[A-Z]", t)
                                    for t in page["lines"][li + 1])):
                        continue
                for t in toks:
                    if re.fullmatch(r"\d{1,3}[.,;:]?", t):
                        v = int(t.rstrip(".,;:"))
                        if 1 <= v <= args.max_chapter:
                            cands.append((pi, li, v))
        n = len(cands)
        # chains must start at a low chapter number (1-6): a stray "99" page
        # number must not seed its own chain, but the first marker itself may
        # be garbled (chapters 1-5 absorbed into front matter is recoverable)
        best = [1 if c[2] <= 6 else 0 for c in cands]
        prev = [-1] * n
        for j in range(n):
            pj, lj, vj = cands[j]
            for i in range(j):
                pi_, li_, vi = cands[i]
                if vi < vj <= vi + 5 and (pi_ < pj or (pi_ == pj and li_ < lj)) and best[i] + 1 > best[j] and best[i] > 0:
                    best[j] = best[i] + 1
                    prev[j] = i
        end = -1
        for j in range(n):
            if best[j] <= 0:
                continue
            if end < 0 or best[j] > best[end] or (best[j] == best[end]
                                                  and cands[j][2] > cands[end][2]):
                end = j
        while end >= 0:
            pj, lj, vj = cands[end]
            chosen[(pj, lj)] = vj
            end = prev[end]

    # ---- pass 3: walk pages, split chapters at markers ----
    for pi, page in enumerate(pages):
        img, lines = page["img"], page["lines"]
        i = 0
        while i < len(lines):
            toks = lines[i]
            nl = norm_line(toks)
            hit = None
            if args.mode == "cc":
                hit = chosen.get((pi, i))
            else:
                if (page["detect"] and next_phrase_ch is not None and len(toks) <= 6
                        and ch_nl_match(nl, marker_map) == next_phrase_ch):
                    hit = next_phrase_ch
            if hit is not None and page["detect"]:
                # title words: other tokens on the marker line; if the line
                # was number/title only and the next line looks like a short
                # title (<= 10 tokens, no sentence punctuation), drop it too.
                title_toks = [t for t in toks
                              if not re.fullmatch(r"\d{1,3}[.,;:]?", t)]
                consumed = 1
                if (args.mode == "cc" and len(title_toks) <= 1
                        and i + 1 < len(lines) and len(lines[i + 1]) <= 10
                        and not lines[i + 1][-1].endswith((".", "!", "?", ";", ","))):
                    title_toks = title_toks + lines[i + 1]
                    consumed = 2
                if title_toks:
                    titles[hit] = " ".join(title_toks)
                if (args.drop_next_line and i + 1 < len(lines)
                        and len(lines[i + 1]) <= 8
                        and not lines[i + 1][-1].endswith((".", "!", "?", ";", ","))):
                    consumed += 1
                chapters.setdefault(hit, [])
                marker_log.append({"image": img.name, "chapter": hit,
                                   "title": titles.get(hit, ""), "line": " ".join(toks)})
                cur_ch = hit
                if args.mode == "cc":
                    expected = hit + 1
                else:
                    idx = order_index[hit]
                    next_phrase_ch = order[idx + 1] if idx + 1 < len(order) else None
                i += consumed
                continue
            # body line
            chapters.setdefault(cur_ch, []).append(" ".join(toks))
            i += 1
        qa_rows.append({"image": img.name, "n_words": page["n_words"],
                        "mean_conf": round(page["conf"], 1),
                        "chapter_at_end": cur_ch})

    # write chapter files: drop numeric tokens and TSV-artifact letter+digit
    # concatenations ("the5", "than5" -- the known tesseract TSV leak), dehyphenate
    def clean(text: str) -> str:
        text = re.sub(r"(\w)- (\w)", r"\1\2", text)
        text = " ".join(t for t in text.split()
                        if not re.fullmatch(r"\d{1,4}[.,;:]?", t)
                        and not re.search(r"\d", t))
        return re.sub(r"\s+", " ", text).strip()

    summary = []
    for ch in sorted(chapters):
        body = clean("\n".join(chapters[ch]))
        name = (f"ch{ch:03d}.txt" if args.mode == "cc" else f"ch{ch:02d}.txt") if ch else "ch00_front.txt"
        (args.out_dir / name).write_text(body, encoding="utf-8")
        summary.append((name, len(body.split()), titles.get(ch, "")))
        print(f"  wrote {name}: {len(body.split())} words"
              + (f"  [{titles[ch]}]" if ch in titles else ""))

    with open(args.out_dir / "qa_report.md", "w", encoding="utf-8") as f:
        f.write(f"# OCR QA report (marker ingest)\nbook: {args.book}\nmode: {args.mode}\n\n")
        f.write("| page image | words | mean conf | chapter at end | flag |\n|---|---|---|---|---|\n")
        flags = 0
        for r in qa_rows:
            flag = ""
            if r["mean_conf"] < 85 and r["n_words"] > 20:
                flag = "RESCAN (low confidence)"; flags += 1
            if r["n_words"] == 0:
                flag = "RESCAN (no text)"; flags += 1
            f.write(f"| {r['image']} | {r['n_words']} | {r['mean_conf']} | "
                    f"ch{r['chapter_at_end']} | {flag} |\n")
        missing = []
        if args.mode == "cc":
            found = {m["chapter"] for m in marker_log}
            missing = [c for c in range(1, args.max_chapter + 1) if c not in found]
        else:
            found = {m["chapter"] for m in marker_log}
            missing = [ch for _, ch, _ in markers if ch not in found]
        f.write(f"\n{flags} pages flagged for rescan.\n")
        if missing:
            f.write(f"\n**Markers NOT found: {missing}** (chapter text merged into "
                    f"the previous file -- manual fix needed)\n")
    with open(args.out_dir / "markers_log.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["image", "chapter", "title", "line"])
        w.writeheader(); w.writerows(marker_log)
    with open(args.out_dir / "pages_index.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["image", "n_words", "mean_conf", "chapter_at_end"])
        w.writeheader(); w.writerows(qa_rows)

    print(f"QA: {args.out_dir / 'qa_report.md'}")
    if missing:
        print(f"[!] missing markers: {missing}")


if __name__ == "__main__":
    main()
