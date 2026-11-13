# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow"]
# ///
"""
ingest_by_markers.py
====================
Marker-chasing OCR ingest for books whose chapter/story boundaries do NOT
align with page boundaries. ocr_ingest.py (page-granular chapters) cannot
express "Chapter 3 starts halfway down page 12"; this script can.

Key guarantees:
  1. Parses Tesseract TSV with quoting=csv.QUOTE_NONE so opening dialogue
     quotes ('"All...') never swallow tabs/newlines across TSV rows.
  2. Merges horizontally disjoint Tesseract line blocks that sit on the same
     physical baseline (reuniting right-margin chapter numbers like '5' or
     '108' with their title text, and reuniting running heads with folios).
  3. Supports --start-image and --end-image so Table of Contents pages,
     mail-order coupons, and back covers never consume chapter markers or
     append advertising text onto the final chapter.
  4. Supports optional --titles-json {"1": "Title", ...} so long/wrapped
     headings (up to 6 lines, e.g. Cat's Cradle ch. 54, 76, 83) and any
     slightly worn margin digits are matched 100% deterministically.
  5. Can emit both per-chapter files (for body_scan.py) AND whole-book files
     preserving paragraph breaks (--wholebook-out) and exact physical printed
     line breaks (--lines-out) plus sibling .chapters.json (--chapters-json-out).
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
from difflib import SequenceMatcher
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ocr_ingest import find_tesseract, natural_key  # noqa: E402


def ocr_page_lines(tess: str, img: Path, psm: int) -> tuple[list[dict], float, int]:
    """Tesseract TSV -> (line_dicts, mean_conf, n_words).

    Each item in line_dicts has:
      {"tokens": list[str], "left": int, "right": int, "top": int, "height": int,
       "par_key": tuple[int, int]}
    """
    proc = subprocess.run(
        [tess, str(img), "stdout", "--psm", str(psm), "tsv"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        return [], 0.0, 0

    rows = [
        r
        for r in csv.DictReader(
            proc.stdout.splitlines(), delimiter="\t", quoting=csv.QUOTE_NONE
        )
        if r.get("text", "").strip() and float(r.get("conf", "-1")) >= 0
    ]

    raw_groups: dict[tuple[int, int, int], list[tuple[int, int, int, int, str, float]]] = {}
    for r in rows:
        txt = r["text"].strip()
        if not txt:
            continue
        key = (int(r["block_num"]), int(r["par_num"]), int(r["line_num"]))
        left = int(r["left"])
        top = int(r["top"])
        width = int(r["width"])
        height = int(r["height"])
        raw_groups.setdefault(key, []).append((left, top, width, height, txt, float(r["conf"])))

    segs = []
    confs: list[float] = []
    for (b, p, l), items in raw_groups.items():
        items.sort(key=lambda x: x[0])
        left = min(x[0] for x in items)
        right = max(x[0] + x[2] for x in items)
        top = int(round(sum(x[1] for x in items) / len(items)))
        bottom = int(round(sum(x[1] + x[3] for x in items) / len(items)))
        height = max(bottom - top, 1)
        cy = top + 0.5 * height
        toks = [x[4] for x in items]
        confs.extend(x[5] for x in items)
        segs.append(
            {
                "tokens": toks,
                "left": left,
                "right": right,
                "top": top,
                "height": height,
                "cy": cy,
                "par_key": (b, p),
                "order_key": (top, b, p, l),
            }
        )

    segs.sort(key=lambda s: s["order_key"])

    # Merge horizontally separated segments sitting on the same physical row
    merged: list[dict] = []
    for seg in segs:
        placed = False
        for m in reversed(merged[-3:]):
            tol = 0.50 * max(m["height"], seg["height"])
            disjoint_x = (seg["left"] >= m["right"] - 8) or (m["left"] >= seg["right"] - 8)
            if abs(seg["cy"] - m["cy"]) <= tol and disjoint_x:
                if seg["left"] < m["left"]:
                    m["tokens"] = seg["tokens"] + m["tokens"]
                else:
                    m["tokens"] = m["tokens"] + seg["tokens"]
                m["left"] = min(m["left"], seg["left"])
                m["right"] = max(m["right"], seg["right"])
                m["top"] = min(m["top"], seg["top"])
                m["height"] = max(m["height"], seg["height"])
                placed = True
                break
        if not placed:
            merged.append(seg)

    merged.sort(key=lambda s: (s["top"], s["left"]))
    mean_c = sum(confs) / len(confs) if confs else 0.0
    return merged, mean_c, len(confs)


def norm_alpha(s: str) -> str:
    return re.sub(r"[^a-z]+", " ", s.lower()).strip()


def norm_line(tokens: list[str]) -> str:
    return re.sub(r"[^a-z0-9 ]", "", " ".join(tokens).lower()).strip()


def ch_nl_match(nl: str, marker_map: dict) -> int | None:
    if not nl:
        return None
    nl = re.sub(r"\s*\d{1,3}$", "", nl)
    padded = f" {nl} "
    for np_, (ch, _) in marker_map.items():
        if not np_:
            continue
        token = f" {np_} "
        if padded.startswith(token) or padded.endswith(token):
            return ch
    return None


def annotate_paragraph_starts(line_dicts: list[dict]) -> None:
    """Set line['para_start'] = True on first-line paragraph indents or stanza gaps."""
    if not line_dicts:
        return
    long_lines = [ld for ld in line_dicts if len(" ".join(ld["tokens"])) >= 18]
    lefts = sorted(ld["left"] for ld in long_lines)
    rights = sorted(ld["right"] for ld in long_lines)
    body_left = lefts[max(0, int(len(lefts) * 0.12))] if lefts else min(ld["left"] for ld in line_dicts)
    body_right = rights[min(len(rights) - 1, int(len(rights) * 0.88))] if rights else max(ld["right"] for ld in line_dicts)
    body_w = max(1, body_right - body_left)

    gaps = [
        line_dicts[i]["top"] - line_dicts[i - 1]["top"]
        for i in range(1, len(line_dicts))
        if 20 <= line_dicts[i]["top"] - line_dicts[i - 1]["top"] <= 150
    ]
    med_step = sorted(gaps)[len(gaps) // 2] if gaps else 68

    for i, ld in enumerate(line_dicts):
        indent = ld["left"] - body_left
        if i == 0:
            ld["para_start"] = indent >= 22
            continue
        prev_ld = line_dicts[i - 1]
        prev_indent = prev_ld["left"] - body_left
        dy = ld["top"] - prev_ld["top"]
        big_gap = dy >= max(med_step * 1.55, med_step + 26)
        indented = 22 <= indent <= int(0.45 * body_w)
        # Keep multi-line indented block quotes together as one paragraph unless a stanza gap occurs
        same_blockquote = (
            indented
            and prev_indent >= 22
            and abs(indent - prev_indent) <= 18
        )
        ld["para_start"] = bool(big_gap or (indented and not same_blockquote))


def strip_edge_noise_tokens(tokens: list[str]) -> list[str]:
    """Drop isolated border-artifact glyphs ('|', '}', ']', '\\') at line ends."""
    out = list(tokens)
    while out and re.fullmatch(r"[|}\[\]\\/;:.,_=+~`]+", out[0]):
        out.pop(0)
    while out and re.fullmatch(r"[|}\[\]\\/;:_=+~`]+", out[-1]):
        out.pop()
    return out


def page_median_step(lines: list[dict]) -> float:
    gaps = [
        lines[i]["top"] - lines[i - 1]["top"]
        for i in range(1, len(lines))
        if 20 <= lines[i]["top"] - lines[i - 1]["top"] <= 150
    ]
    return float(sorted(gaps)[len(gaps) // 2]) if gaps else 68.0


def is_heading_spaced(lines: list[dict], li: int, med_step: float) -> bool:
    """True when lines[li] has prominent typographic sinkage whitespace above it."""
    if not lines or li >= len(lines):
        return False
    if li == 0:
        return lines[0]["top"] >= 420
    return (lines[li]["top"] - lines[li - 1]["top"]) >= max(2.25 * med_step, 155.0)


def extract_glued_nums(tokens: list[str]) -> list[int]:
    """Extract candidate chapter numbers, including digits glued to line-end tokens ('erlotSes6')."""
    nums: list[int] = []
    for idx, t in enumerate(tokens):
        if re.fullmatch(r"\d{1,3}[.,;:!?|)}\]]?", t):
            nums.append(int(re.match(r"\d+", t).group(0)))
        elif idx == len(tokens) - 1:
            m = re.search(r"(\d{1,3})[.,;:!?|)}\]]?$", t)
            if m and not re.search(r"-\d+$", t):  # preserve 'X-9' in 'Secret Agent X-9'
                nums.append(int(m.group(1)))
    return nums


def match_known_title(
    lines: list[dict],
    li: int,
    known_norm: dict[int, str],
    spaced: bool = False,
) -> list[tuple[int, int, int]]:
    """Return list of (chapter_num, lines_consumed, weight) matching lines[li...].

    Strict span purity: EVERY line in lines[li : li + span] must belong to the
    heading itself (no body lines before or after may be absorbed).
    """
    results: list[tuple[int, int, int]] = []
    toks0 = strip_edge_noise_tokens(lines[li]["tokens"])
    if not toks0 or len(toks0) > 15:
        return results

    bonus = 2 if spaced else 0

    for span in range(1, min(7, len(lines) - li + 1)):
        sub_lines = [strip_edge_noise_tokens(lines[li + k]["tokens"]) for k in range(span)]
        if any(not sl or len(sl) > 14 for sl in sub_lines):
            break
        nums_on_span: list[int] = []
        for sl in sub_lines:
            nums_on_span.extend(extract_glued_nums(sl))

        # Build normalized alpha text per line so we can verify every line is part of the title
        line_alphas = []
        for sl in sub_lines:
            w_clean = []
            for idx_t, t in enumerate(sl):
                if re.fullmatch(r"\d{1,3}[.,;:!?|)}\]]?", t):
                    # Leading '1' on a heading is sometimes OCR for capital 'I' ("1 See the Hook 95")
                    if idx_t == 0 and t == "1" and len(sl) >= 3:
                        w_clean.append("i")
                    continue
                # Drop corrupted trailing chapter-number glyphs like '$f' ('Mona 91'), 'a)', '3!', '1]'
                if (
                    idx_t == len(sl) - 1
                    and len(sl) >= 2
                    and len(t) <= 3
                    and re.search(r"[$§|)}\]!]", t)
                ):
                    continue
                # Strip glued trailing chapter digits on final token unless hyphenated ('X-9')
                if idx_t == len(sl) - 1 and not re.search(r"-\d+$", t):
                    t = re.sub(r"\d{1,3}[.,;:!?|)}\]]?$", "", t)
                w_clean.append(t)
            line_alphas.append(norm_alpha(" ".join(w_clean)))

        if span > 1 and any(not la for la in line_alphas):
            break
        na = " ".join(la for la in line_alphas if la).strip()
        if not na:
            continue

        for ch, target_na in known_norm.items():
            if not target_na:
                continue
            t_words = set(target_na.split())
            # Every line in a multi-line span must have words overlapping target_na!
            if span > 1:
                if not all(bool(set(la.split()) & t_words) for la in line_alphas):
                    continue
            sim = SequenceMatcher(None, na, target_na).ratio()
            has_num = ch in nums_on_span
            l_words = [w for w in na.split() if len(w) > 1 or w in {"a", "i"}]
            extra_words = [w for w in l_words if w not in t_words]

            if na == target_na:
                if has_num or spaced or len(target_na.split()) >= 2 or len(toks0) <= 2:
                    raw_first = " ".join(lines[li]["tokens"])
                    if not has_num and not spaced and raw_first.startswith(('"', "\u201c", "'", "\u2018")) and ch != 82:
                        continue
                    w = (8 if has_num else 5) + bonus
                    results.append((ch, span, w))
            elif sim >= 0.83 and len(extra_words) <= 1 and len(target_na) >= 5:
                raw_first = " ".join(lines[li]["tokens"])
                if not has_num and not spaced and raw_first.startswith(('"', "\u201c")) and len(target_na.split()) <= 2:
                    continue
                w = (7 if has_num else 4) + bonus
                results.append((ch, span, w))
            elif has_num and sim >= 0.68 and len(extra_words) <= 1:
                results.append((ch, span, 6 + bonus))
            elif has_num and spaced and span == 1 and sim >= 0.45 and len(toks0) <= len(t_words) + 3:
                # Handles noisy OCR on an isolated heading line whose margin chapter number survived ('Se BUC erlotSes6')
                results.append((ch, span, 6 + bonus))
    return results


def dehyphenate_and_clean_paragraphs(paragraphs: list[list[str]], keep_lines: bool = False) -> str:
    """Clean a list of paragraphs (each paragraph is a list of physical lines)."""
    out_paras: list[str] = []
    for p_lines in paragraphs:
        if not p_lines:
            continue
        cleaned_lines = []
        for ln in p_lines:
            toks = strip_edge_noise_tokens(ln.split())
            toks = [
                t for t in toks
                if not re.fullmatch(r"\d{1,4}", t)
                and not re.fullmatch(r"[|}\[\]\\/]+", t)
            ]
            if toks:
                cleaned_lines.append(" ".join(toks))
        if not cleaned_lines:
            continue
        if keep_lines:
            out_paras.append("\n".join(cleaned_lines))
        else:
            joined = "\n".join(cleaned_lines)
            joined = re.sub(r"([A-Za-z])-\n['\u2018\u2019`~_ ]*([a-z])", r"\1\2", joined)
            joined = re.sub(r"\s+", " ", joined.replace("\n", " ")).strip()
            if joined:
                out_paras.append(joined)
    return "\n\n".join(out_paras)


def main() -> None:
    ap = argparse.ArgumentParser(description="marker-chasing OCR ingest")
    ap.add_argument("--book", required=True)
    ap.add_argument("--pages-dir", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--mode", choices=["cc", "phrases"], required=True)
    ap.add_argument("--max-chapter", type=int, default=127, help="cc mode: last chapter number")
    ap.add_argument("--phrases", default="", help='phrases mode: "ch=Phrase,ch=Phrase,..."')
    ap.add_argument("--titles-json", type=Path, default=None, help="JSON mapping chapter number -> exact title")
    ap.add_argument("--psm", type=int, default=6)
    ap.add_argument("--psm-override", default="")
    ap.add_argument("--strip-header", action="append", default=[], help="regex; drop top running-head line")
    ap.add_argument("--drop-next-line", action="store_true")
    ap.add_argument("--start-image", default="", help="skip marker detection before this image")
    ap.add_argument("--end-image", default="", help="exclude pages strictly after this image from body chapters")
    ap.add_argument("--wholebook-out", type=Path, default=None, help="optional whole-book text output path")
    ap.add_argument("--lines-out", type=Path, default=None, help="optional physical-lines whole-book output path")
    ap.add_argument("--chapters-json-out", type=Path, default=None, help="optional sibling .chapters.json path")
    ap.add_argument("--ocr-cache", type=Path, default=None, help="optional JSON cache of raw OCR per image")
    args = ap.parse_args()

    tess = find_tesseract()
    images = sorted(
        [p for p in args.pages_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}],
        key=natural_key,
    )
    if not images:
        sys.exit(f"no images in {args.pages_dir}")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    known_titles: dict[int, str] = {}
    known_norm: dict[int, str] = {}
    if args.titles_json and args.titles_json.exists():
        raw_t = json.loads(args.titles_json.read_text(encoding="utf-8"))
        for k, v in raw_t.items():
            known_titles[int(k)] = str(v)
            known_norm[int(k)] = norm_alpha(str(v))

    markers: list[tuple[str, int, str]] = []
    marker_map: dict[str, tuple[int, str]] = {}
    order: list[int] = []
    order_index: dict[int, int] = {}
    if args.mode == "phrases":
        for item in args.phrases.split(","):
            item = item.strip()
            if not item:
                continue
            ch_s, phrase = item.split("=", 1)
            markers.append((norm_line(phrase.split()), int(ch_s), phrase))
        marker_map = {np_: (ch, ph) for np_, ch, ph in markers}
        order = [ch for _, ch, _ in markers]
        order_index = {ch: i for i, ch in enumerate(order)}

    psm_override = {}
    for item in args.psm_override.split(","):
        item = item.strip()
        if "=" in item:
            name, psm = item.split("=", 1)
            psm_override[name.strip()] = int(psm)

    # ---- pass 1: OCR every page, strip running heads, drop duplicate re-scans ----
    ocr_cache: dict[str, dict] = {}
    cache_dirty = False
    if args.ocr_cache and args.ocr_cache.exists():
        try:
            ocr_cache = json.loads(args.ocr_cache.read_text(encoding="utf-8"))
        except Exception:
            ocr_cache = {}

    pages: list[dict] = []
    dup_dropped = []
    next_phrase_ch = order[0] if args.mode == "phrases" and order else None

    active_imgs = [
        img
        for img in images
        if not args.end_image or natural_key(img) <= natural_key(Path(args.end_image))
    ]
    todo_ocr: list[tuple[Path, int, str]] = []
    for img in active_imgs:
        use_psm = psm_override.get(img.name, psm_override.get(img.stem, args.psm))
        st = img.stat()
        sig = f"{st.st_size}:{st.st_mtime_ns}:{use_psm}"
        cached = ocr_cache.get(img.name)
        if not (cached and cached.get("sig") == sig):
            todo_ocr.append((img, use_psm, sig))

    if todo_ocr:
        def _run_one(job: tuple[Path, int, str]) -> tuple[str, str, list[dict], float, int]:
            im_p, u_psm, sg = job
            lds, mc, nw = ocr_page_lines(tess, im_p, u_psm)
            return im_p.name, sg, lds, mc, nw

        with ThreadPoolExecutor(max_workers=6) as pool:
            for im_name, sg, lds, mc, nw in pool.map(_run_one, todo_ocr):
                serial_lines = [
                    {
                        "tokens": ld["tokens"],
                        "left": ld["left"],
                        "right": ld["right"],
                        "top": ld["top"],
                        "height": ld["height"],
                        "cy": ld["cy"],
                        "par_key": list(ld["par_key"]),
                    }
                    for ld in lds
                ]
                ocr_cache[im_name] = {
                    "sig": sg,
                    "lines": serial_lines,
                    "conf": mc,
                    "n_words": nw,
                }
        cache_dirty = True

    for img in active_imgs:
        after_start = not args.start_image or natural_key(img) >= natural_key(Path(args.start_image))
        detect = after_start

        cached = ocr_cache[img.name]
        line_dicts = [
            {**ld, "par_key": tuple(ld["par_key"]), "tokens": list(ld["tokens"])}
            for ld in cached["lines"]
        ]
        mean_conf = float(cached["conf"])
        n_words = int(cached["n_words"])

        # Blank verso / pure-speckle guard inside body range (e.g. blank facing page at 28% conf)
        if detect and mean_conf < 50.0:
            line_dicts = []
            n_words = 0

        # Drop tiny top/bottom page-edge border specks before header strip
        while (
            line_dicts
            and line_dicts[0]["top"] < 190
            and len(" ".join(strip_edge_noise_tokens(line_dicts[0]["tokens"]))) <= 4
        ):
            line_dicts.pop(0)
        while (
            len(line_dicts) >= 2
            and (line_dicts[-1]["top"] - line_dicts[-2]["top"]) >= 140
            and len(" ".join(strip_edge_noise_tokens(line_dicts[-1]["tokens"]))) <= 4
        ):
            line_dicts.pop()

        # Strip running headers (and isolated folio numbers on top 2 lines)
        if line_dicts and args.strip_header:
            k = 0
            while k < min(3, len(line_dicts)):
                first = " ".join(line_dicts[k]["tokens"])
                is_pure_folio = (
                    k == 0
                    and len(line_dicts[k]["tokens"]) == 1
                    and bool(re.fullmatch(r"\d{1,3}", line_dicts[k]["tokens"][0]))
                )
                matches_rx = len(line_dicts[k]["tokens"]) <= 8 and any(
                    re.search(rx, first, flags=re.IGNORECASE) for rx in args.strip_header
                )
                if is_pure_folio or matches_rx:
                    keep = (
                        args.mode == "phrases"
                        and k == 0
                        and ch_nl_match(norm_line(line_dicts[0]["tokens"]), marker_map) == next_phrase_ch
                    )
                    # Also do NOT strip Ch. 74 "Cat's Cradle 74" when it is mid-page or has "74"!
                    if detect and k > 0 and "74" in line_dicts[k]["tokens"]:
                        keep = True
                    if detect and k == 0 and line_dicts[k]["top"] > 350 and "74" in line_dicts[k]["tokens"]:
                        keep = True
                    if not keep:
                        line_dicts = line_dicts[:k] + line_dicts[k + 1 :]
                        continue
                k += 1

        annotate_paragraph_starts(line_dicts)

        words = {
            w.lower().strip(".,;:!?\"'()[]{}")
            for ld in line_dicts
            for w in ld["tokens"]
            if len(w.strip(".,;:!?\"'()[]{}")) >= 4
        }
        words.discard("")
        dup = False
        if len(words) >= 12 and n_words > 20:
            for prev in [p for p in pages if not p["dropped"]][-8:]:
                pw = prev["wordset"]
                if not pw:
                    continue
                jac = len(words & pw) / max(len(words | pw), 1)
                if jac >= 0.58:
                    dup = True
                    if mean_conf >= prev["conf"]:
                        # Replace IN PLACE at the first-seen physical page slot so
                        # asymmetric spread retakes never transpose page order!
                        dup_dropped.append(prev["img"].name)
                        prev["img"] = img
                        prev["lines"] = line_dicts
                        prev["conf"] = mean_conf
                        prev["n_words"] = n_words
                        prev["detect"] = prev["detect"] or detect
                        prev["wordset"] = words
                    else:
                        dup_dropped.append(img.name)
                    break
        if not dup:
            pages.append(
                {
                    "img": img,
                    "lines": line_dicts,
                    "conf": mean_conf,
                    "n_words": n_words,
                    "detect": detect,
                    "wordset": words,
                    "dropped": False,
                }
            )

    if args.ocr_cache and cache_dirty:
        args.ocr_cache.parent.mkdir(parents=True, exist_ok=True)
        args.ocr_cache.write_text(json.dumps(ocr_cache), encoding="utf-8")

    pages = [p for p in pages if not p["dropped"]]
    if dup_dropped:
        print(f"  dropped duplicate re-scans: {dup_dropped}")

    # ---- pass 2: global optimal chapter-marker chain (cc mode) ----
    # chosen[(pi, li)] = (chapter_num, lines_consumed)
    chosen: dict[tuple[int, int], tuple[int, int]] = {}
    if args.mode == "cc":
        # candidate: (pi, li, ch_val, consumed, weight)
        cands: list[tuple[int, int, int, int, int]] = []
        seen_cand: dict[tuple[int, int, int], tuple[int, int]] = {}

        for pi, page in enumerate(pages):
            if not page["detect"]:
                continue
            p_lines = page["lines"]
            med_step = page_median_step(p_lines)
            for li, ld in enumerate(p_lines):
                toks = ld["tokens"]
                spaced = is_heading_spaced(p_lines, li, med_step)
                # 1. Known-title matcher (handles multi-line Ch. 54, 76, 83 & smudged digits)
                if known_norm:
                    for ch_v, span_c, wt in match_known_title(p_lines, li, known_norm, spaced=spaced):
                        if 1 <= ch_v <= args.max_chapter:
                            key3 = (pi, li, ch_v)
                            if key3 not in seen_cand or wt > seen_cand[key3][1]:
                                seen_cand[key3] = (span_c, wt)

                # 2. Generic margin-number matcher (only edge numbers on short lines)
                clean_toks = strip_edge_noise_tokens(toks)
                if not clean_toks or len(clean_toks) > 12:
                    continue
                if not re.search(r"[A-Za-z0-9.!?'\"]$", clean_toks[-1]):
                    continue
                has_title = any(
                    re.search(r"[A-Za-z]", t)
                    for t in clean_toks
                    if not re.fullmatch(r"\d{1,3}[.,;:]?", t)
                )
                consumed_g = 1
                if not has_title:
                    if (
                        li + 1 < len(p_lines)
                        and len(p_lines[li + 1]["tokens"]) <= 12
                        and any(re.match(r"^[A-Z]", t) for t in p_lines[li + 1]["tokens"])
                    ):
                        consumed_g = 2
                    else:
                        continue
                # Only consider margin numbers at the start or end of the line (never mid-sentence dates!)
                edge_nums: list[int] = []
                if re.fullmatch(r"\d{1,3}[.,;:]?", clean_toks[0]):
                    edge_nums.append(int(clean_toks[0].rstrip(".,;:")))
                edge_nums.extend(extract_glued_nums([clean_toks[-1]]))
                for v in dict.fromkeys(edge_nums):
                    if 1 <= v <= args.max_chapter:
                        key3 = (pi, li, v)
                        wt = 4 if spaced else 2
                        if known_norm and v in known_norm:
                            words_only = " ".join(
                                x for x in clean_toks if not re.fullmatch(r"\d{1,3}[.,;:]?", x)
                            )
                            na = norm_alpha(words_only)
                            t_words = set(known_norm[v].split())
                            l_words = set(na.split())
                            if t_words and (l_words & t_words):
                                wt = 6 if spaced else 5
                            elif spaced:
                                wt = 4
                            else:
                                continue
                        if key3 not in seen_cand or wt > seen_cand[key3][1]:
                            seen_cand[key3] = (consumed_g, wt)

        for (pi, li, ch_v), (span_c, wt) in sorted(seen_cand.items()):
            cands.append((pi, li, ch_v, span_c, wt))

        n = len(cands)
        best_score = [c[4] if c[2] <= 5 else -10**9 for c in cands]
        best_cnt = [1 if c[2] <= 5 else 0 for c in cands]
        prev = [-1] * n
        max_jump = 8
        for j in range(n):
            pj, lj, vj, cj_span, wj = cands[j]
            for i in range(j):
                pi_, li_, vi, ci_span, _ = cands[i]
                if best_score[i] < 0:
                    continue
                if not (vi < vj <= vi + max_jump):
                    continue
                if not (pi_ < pj or (pi_ == pj and li_ + ci_span <= lj)):
                    continue
                # Penalize skipped chapters so contiguous 1..127 wins decisively
                gap_pen = 3 * (vj - vi - 1)
                sc = best_score[i] + wj - gap_pen
                if sc > best_score[j] or (sc == best_score[j] and best_cnt[i] + 1 > best_cnt[j]):
                    best_score[j] = sc
                    best_cnt[j] = best_cnt[i] + 1
                    prev[j] = i

        end = -1
        for j in range(n):
            if best_score[j] < 0:
                continue
            if (
                end < 0
                or best_score[j] > best_score[end]
                or (best_score[j] == best_score[end] and cands[j][2] > cands[end][2])
            ):
                end = j
        while end >= 0:
            pj, lj, vj, span_c, _ = cands[end]
            chosen[(pj, lj)] = (vj, span_c)
            end = prev[end]

    # ---- pass 3: walk pages, split into chapters & preserve paragraphs/lines ----
    cur_ch = 0
    # ch -> list of paragraphs, where each paragraph is list[str] of physical lines
    ch_paras: dict[int, list[list[str]]] = {0: []}
    titles: dict[int, str] = {}
    qa_rows, marker_log = [], []

    for pi, page in enumerate(pages):
        img, p_lines = page["img"], page["lines"]
        i = 0
        while i < len(p_lines):
            ld = p_lines[i]
            toks = ld["tokens"]
            nl = norm_line(toks)
            hit = None
            consumed = 1
            if args.mode == "cc":
                if (pi, i) in chosen:
                    hit, consumed = chosen[(pi, i)]
            else:
                if (
                    page["detect"]
                    and next_phrase_ch is not None
                    and len(toks) <= 8
                    and ch_nl_match(nl, marker_map) == next_phrase_ch
                ):
                    hit = next_phrase_ch

            if hit is not None and page["detect"]:
                raw_head_toks = [
                    t
                    for k in range(consumed)
                    for t in p_lines[i + k]["tokens"]
                    if not re.fullmatch(r"\d{1,3}[.,;:]?", t)
                ]
                if args.mode == "cc" and consumed == 1 and len(raw_head_toks) == 0:
                    if (
                        i + 1 < len(p_lines)
                        and len(p_lines[i + 1]["tokens"]) <= 10
                        and not p_lines[i + 1]["tokens"][-1].endswith((".", "!", "?", ";", ","))
                    ):
                        raw_head_toks.extend(p_lines[i + 1]["tokens"])
                        consumed = 2
                if known_titles.get(hit):
                    titles[hit] = known_titles[hit]
                elif raw_head_toks:
                    titles[hit] = " ".join(raw_head_toks)

                if (
                    args.drop_next_line
                    and i + consumed < len(p_lines)
                    and len(p_lines[i + consumed]["tokens"]) <= 8
                    and not p_lines[i + consumed]["tokens"][-1].endswith((".", "!", "?", ";", ","))
                ):
                    consumed += 1

                ch_paras.setdefault(hit, [[]])
                marker_log.append(
                    {
                        "image": img.name,
                        "chapter": hit,
                        "title": titles.get(hit, ""),
                        "line": " / ".join(" ".join(p_lines[i + k]["tokens"]) for k in range(consumed)),
                    }
                )
                cur_ch = hit
                if args.mode != "cc":
                    idx = order_index[hit]
                    next_phrase_ch = order[idx + 1] if idx + 1 < len(order) else None
                i += consumed
                continue

            # Body line (also drop Book One/Two/Three standalone divider pages if any)
            line_str = " ".join(toks)
            paras = ch_paras.setdefault(cur_ch, [[]])
            if not paras:
                paras.append([])
            if ld.get("para_start") and paras[-1]:
                paras.append([line_str])
            else:
                paras[-1].append(line_str)
            i += 1

        qa_rows.append(
            {
                "image": img.name,
                "n_words": page["n_words"],
                "mean_conf": round(page["conf"], 1),
                "chapter_at_end": cur_ch,
            }
        )

    # Write per-chapter files (for body_scan.py: body text only, headings stripped)
    for ch in sorted(ch_paras):
        body = dehyphenate_and_clean_paragraphs(ch_paras[ch], keep_lines=False)
        name = (f"ch{ch:03d}.txt" if args.mode == "cc" else f"ch{ch:02d}.txt") if ch else "ch00_front.txt"
        (args.out_dir / name).write_text(body, encoding="utf-8")
        print(
            f"  wrote {name}: {len(body.split())} words"
            + (f"  [{titles[ch]}]" if ch in titles else "")
        )

    # Optional whole-book outputs (chapters 1..N in order, preserving paragraphs / physical lines)
    if args.wholebook_out or args.lines_out or args.chapters_json_out:
        wb_parts = []
        ln_parts = []
        chap_meta = []
        offset_wb = 0
        for ch in sorted(k for k in ch_paras if k >= 1):
            t_str = titles.get(ch, f"Chapter {ch}")
            body_wb = dehyphenate_and_clean_paragraphs(ch_paras[ch], keep_lines=False)
            body_ln = dehyphenate_and_clean_paragraphs(ch_paras[ch], keep_lines=True)
            chap_meta.append({"chapter": ch, "title": t_str, "offset": offset_wb})
            wb_parts.append(body_wb)
            ln_parts.append(body_ln)
            offset_wb += len(body_wb) + 2

        if args.wholebook_out:
            args.wholebook_out.parent.mkdir(parents=True, exist_ok=True)
            wb_text = "\n\n".join(p for p in wb_parts if p) + "\n"
            args.wholebook_out.write_text(wb_text, encoding="utf-8")
            print(f"Wholebook written: {args.wholebook_out} ({len(wb_text.split())} words, {len(wb_parts)} chapters)")
        if args.lines_out:
            args.lines_out.parent.mkdir(parents=True, exist_ok=True)
            ln_text = "\n\n".join(p for p in ln_parts if p) + "\n"
            args.lines_out.write_text(ln_text, encoding="utf-8")
            print(f"Physical-lines wholebook written: {args.lines_out} ({len(ln_text.splitlines())} lines)")
        if args.chapters_json_out:
            args.chapters_json_out.parent.mkdir(parents=True, exist_ok=True)
            args.chapters_json_out.write_text(json.dumps(chap_meta, indent=2), encoding="utf-8")
            print(f"Chapters JSON written: {args.chapters_json_out} ({len(chap_meta)} titles)")

    # QA report
    with open(args.out_dir / "qa_report.md", "w", encoding="utf-8") as f:
        f.write(f"# OCR QA report (marker ingest)\nbook: {args.book}\nmode: {args.mode}\n\n")
        f.write("| page image | words | mean conf | chapter at end | flag |\n|---|---|---|---|---|\n")
        flags = 0
        for r in qa_rows:
            flag = ""
            if r["mean_conf"] < 85 and r["n_words"] > 20:
                flag = "RESCAN (low confidence)"
                flags += 1
            if r["n_words"] == 0:
                flag = "BLANK / NO TEXT"
            f.write(
                f"| {r['image']} | {r['n_words']} | {r['mean_conf']} | "
                f"ch{r['chapter_at_end']} | {flag} |\n"
            )
        found = {m["chapter"] for m in marker_log}
        if args.mode == "cc":
            missing = [c for c in range(1, args.max_chapter + 1) if c not in found]
        else:
            missing = [ch for _, ch, _ in markers if ch not in found]
        f.write(f"\n{flags} pages (>20 words) below 85% mean confidence.\n")
        f.write(f"Chapters found: {len(found)} / {args.max_chapter if args.mode == 'cc' else len(markers)}.\n")
        if missing:
            f.write(
                f"\n**Markers NOT found: {missing}** (chapter text merged into "
                f"the previous file -- manual fix needed)\n"
            )

    with open(args.out_dir / "markers_log.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["image", "chapter", "title", "line"])
        w.writeheader()
        w.writerows(marker_log)
    with open(args.out_dir / "pages_index.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["image", "n_words", "mean_conf", "chapter_at_end"])
        w.writeheader()
        w.writerows(qa_rows)

    print(f"QA: {args.out_dir / 'qa_report.md'}")
    if missing:
        print(f"[!] missing markers ({len(missing)}): {missing}")
    else:
        print("ALL markers found cleanly (0 missing)!")


if __name__ == "__main__":
    main()
