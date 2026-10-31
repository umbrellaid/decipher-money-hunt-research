# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy"]
# ///
"""anchor_sweep.py — 'group B / 10 / End' anchor sweep (2026-10-31)
#
# The Decipher III initial clue for 3-1 is: "The author you seek to find the
# key is from the group that's labeled B. / 10 / End" (data/author_lists.json).
# This script tests whether any candidate book's TEXT, when numbered from a
# structurally-defined ANCHOR POINT, decodes the open ciphers (2-4, 3-1, 3-2,
# 3-3) as English. Anchors = the 8 interpretations compiled from the Argon
# consult (see money-hunt-work/llm-handoff-cipher-next-steps.md), minus the
# ones that degenerate to a start offset (covered by the +-window here):
#
#   ch10        Chapter 10 slice (covers: start-of-ch10, last-paragraph-of-
#               ch10 [window slide], and backward-from-end-of-ch10 [engine's
#               from-end direction])
#   part2-ch10  Chapter 10 counting headers only after a Part/Book Two start
#   epilogue    Epilogue/Afterword/Coda slice ("End" section)
#   sent10end   Tenth sentence from the end of the book, to EOF
#   chN-10      From the chapter 10-before-last header, to EOF
#
# Streams per slice: continuous letters; word-first and word-last letters;
# tokenization split ([A-Za-z]+ runs) vs merge (hyphen/apostrophe kept
# internal). Decode indexes word N -> letter (first or last) of the Nth token;
# stream position k = 0-based index into the stream (1-based numbering via
# engine offset=1, the default).
#
# Unlike sweep.py (which slides the numbering origin across the whole book
# because solved puzzles used arbitrary offsets), anchors FIX the origin at a
# structural point; we test only a small +-30-char window around it to absorb
# OCR/header slop. Short slices where the cipher's largest number runs off the
# end are silently dropped by engine (decode masked) — that is the anchor
# end-boundary semantics.
#
# Usage (from repo root):
#   uv run solver/anchor_sweep.py BOOK1.txt [BOOK2.txt ...] [--window 30]
#   uv run solver/anchor_sweep.py --all-private
# Score bands (calibrated on solved puzzles): genuine English ~ -7.9 to -8.0
# per trigram; above -8.2 deserves a look; above -8.0 should be hand-checked.
# """
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().resolve().parent))
import engine

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CIPHERS = json.load(open(ROOT / "data" / "ciphers.json", encoding="utf-8"))
OPEN_CIPHERS = ("2-4", "3-1", "3-2", "3-3")

PRIVATE_EBOOKS = Path(r"G:\qwen_workspace\personal\puzzle_work\private\ebooks")

WORD_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirtieth": 30, "fortieth": 40,
}
ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7,
         "viii": 8, "ix": 9, "x": 10, "xi": 11, "xii": 12, "xiii": 13,
         "xiv": 14, "xv": 15, "xvi": 16, "xvii": 17, "xviii": 18,
         "xix": 19, "xx": 20, "xxx": 30, "xl": 40, "l": 50}

CHAP_PAT = re.compile(
    r"^[ \t]*(?:chapter|chap\.?|section)[ \t]+([0-9]+|[IVXLCDMivxlcdm]+|[A-Za-z]+)\b[^\n]*",
    re.M | re.I)
PART_PAT = re.compile(
    r"^[ \t]*(?:part|book|pt\.?|bk\.?)[ \t]+(two|ii|2|second|three|iii|3|third|"
    r"one|1|i|first|four|iv|4|fourth)\b[^\n]*", re.M | re.I)
EPI_PAT = re.compile(
    r"^[ \t]*(epilogue|afterword|coda|postscript|envoi)\b[^\n]*", re.M | re.I)
SENT_END = re.compile(r"[.!?][\"')\]]?[ \t]+")
NUM_LINE = re.compile(r"^[ \t]*[0-9]{1,4}[ \t]*$", re.M)


def parse_num(tok):
    tok = tok.strip().lower().rstrip(".")
    if tok.isdigit():
        return int(tok)
    if re.fullmatch(r"[ivxlcdm]+", tok):
        return ROMAN.get(tok)
    return WORD_NUM.get(tok)


def light_normalize(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = NUM_LINE.sub("", text)  # drop standalone page numbers
    return text


def find_anchors(text):
    """Return {anchor_name: (start, end)} slices. Ends exclusive-ish."""
    anchors = {}
    chap_m = list(CHAP_PAT.finditer(text))
    numbered = [(m.start(), parse_num(m.group(1))) for m in chap_m]
    numbered = [(p, n) for p, n in numbered if n is not None]

    def slice_after(idx_list, i):
        start = idx_list[i]
        end = idx_list[i + 1] if i + 1 < len(idx_list) else len(text)
        return start, end

    heads = [p for p, _ in numbered]
    # TOC entries also match CHAP_PAT; a body header yields the longest slice
    # to the next header, so keep the longest-slice candidate per anchor.
    def longest(cands):
        best, blen = None, -1
        for i in cands:
            s, e = slice_after(heads, i)
            if e - s > blen:
                best, blen = (s, e), e - s
        return best

    tens = [i for i, (_, n) in enumerate(numbered) if n == 10]
    if tens:
        anchors["ch10"] = longest(tens)
    if numbered:
        nums = [n for _, n in numbered]
        target = max(nums) - 10
        cands = [i for i, (_, n) in enumerate(numbered) if n == target]
        if cands:
            # latest occurrence = body, not TOC
            i = cands[-1]
            s, _ = slice_after(heads, i)
            anchors["chN-10"] = (s, len(text))

    part_m = list(PART_PAT.finditer(text))
    part2 = [m for m in part_m if parse_num(m.group(1)) == 2]
    if part2:
        p2 = part2[0].start()
        tens2 = [i for i, (_, n) in enumerate(numbered) if n == 10
                 and numbered[i][0] >= p2]
        if tens2:
            anchors["part2-ch10"] = longest(tens2)

    epi_m = list(EPI_PAT.finditer(text))
    if epi_m:
        best = None
        blen = -1
        for m in epi_m:
            s = m.start()
            later = [c.start() for c in chap_m if c.start() > s]
            later += [p.start() for p in part_m if p.start() > s]
            e = min(later) if later else len(text)
            if e - s > blen:
                best, blen = (s, e), e - s
        anchors["epilogue"] = best

    # tenth sentence from the end
    tail = text[-60000:]
    ends = [m.end() for m in SENT_END.finditer(tail)]
    sentences = []
    prev = 0
    for m in SENT_END.finditer(tail):
        seg = tail[prev:m.start()].strip()
        if seg:
            sentences.append((prev, m.start()))
        prev = m.end()
    last_seg = tail[prev:].strip()
    if last_seg:
        sentences.append((prev, len(tail)))
    if len(sentences) >= 10:
        s10 = sentences[-10][0]
        anchors["sent10end"] = (len(text) - 60000 + s10, len(text))
    return anchors


def build_streams(s):
    out = {}
    letters = engine.letters_only(s)
    if letters:
        out["letters"] = letters
    toks_split = re.findall(r"[A-Za-z]+", s)
    toks_merge = re.findall(r"[A-Za-z]+(?:['-][A-Za-z]+)*", s)
    if toks_split:
        out["wf-split"] = "".join(t[0].upper() for t in toks_split)
        out["wl-split"] = "".join(t[-1].upper() for t in toks_split)
    if toks_merge:
        out["wf-merge"] = "".join(t[0].upper() for t in toks_merge)
        out["wl-merge"] = "".join(t[-1].upper() for t in toks_merge)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("books", nargs="*")
    ap.add_argument("--all-private", action="store_true")
    ap.add_argument("--window", type=int, default=30)
    ap.add_argument("--top", type=int, default=40)
    args = ap.parse_args()

    paths = [Path(b) for b in args.books]
    if args.all_private:
        paths = sorted(PRIVATE_EBOOKS.glob("*/*.txt"))
    if not paths:
        ap.error("no books")

    model_dir = ROOT / "texts" / "model"
    texts = [p.read_text(encoding="utf-8", errors="replace")
             for p in sorted(model_dir.glob("*.txt"))]
    scorer = engine.TrigramScorer(texts)

    max_n = {c: max(t for t in CIPHERS[c] if isinstance(t, int)) for c in OPEN_CIPHERS}
    results = []
    coverage = []
    for path in paths:
        raw = path.read_text(encoding="utf-8", errors="replace")
        text = light_normalize(raw)
        anchors = find_anchors(text)
        coverage.append((path.name, sorted(anchors)))
        for aname, span in anchors.items():
            if span is None:
                continue
            s, e = span
            # window around the anchor start; end boundary respected
            seg = text[s:e]
            for sname, stream in build_streams(seg).items():
                w = min(args.window, max(0, len(stream) - 1))
                # slide only [0, w]: anchor IS the numbering origin
                sub = stream[: w + max(max_n.values()) + 2]
                for cname in OPEN_CIPHERS:
                    label = f"{path.name}|{aname}|{sname}|{cname}"
                    engine.search_stream(sub, CIPHERS[cname], scorer,
                                         max_n[cname], step=1,
                                         label=label, results=results,
                                         top_k=args.top)

    results.sort(key=lambda r: -r[0])
    out = []
    out.append(f"# Anchor sweep 2026-10-31 — 'group B / 10 / End' interpretations")
    out.append(f"# books: {len(paths)}; ciphers: {', '.join(OPEN_CIPHERS)}")
    out.append(f"# score bands: genuine ~ -7.9..-8.0; > -8.2 look; > -8.0 hand-check")
    out.append("")
    out.append("## anchor coverage per book")
    for name, anchors in coverage:
        out.append(f"- {name}: {', '.join(anchors) if anchors else 'NO ANCHORS FOUND'}")
    out.append("")
    out.append("## top results (all)")
    for r in results[: args.top]:
        out.append(f"{r[0]:.4f}  {r[1]}  start={r[2]} dir={r[3]} plain={r[4]}")
    out.append("")
    out.append(f"total result rows: {len(results)}")
    print("\n".join(out))


if __name__ == "__main__":
    main()
