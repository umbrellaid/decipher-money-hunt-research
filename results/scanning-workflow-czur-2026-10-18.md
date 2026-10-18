# CZUR Aura Scanning Workflow — Decipher Money Hunt body scans
**Date:** 2026-10-18 · **Scanner:** CZUR Aura (14 MP, A3/A4, 3-laser curve flattening; ASIN B0B2WBG8P9 — confirmed against your manual `CZUR Aura Software Manual(Windows).pdf` and your own comparison notes)
**Pipeline target:** the repo's `solver/body_scan.py` expects **one plain-text file per chapter** (`texts/<book>/ch09.txt`, `ch10.txt`, …, natural-sort order = reading order). We get there in three stages: **JPG scans → Python OCR → per-chapter .txt**.

---

## 1. Answers to your three questions

1. **PDF or individual images? → Individual JPGs.** The CZUR scanner natively saves JPG; that is exactly what I want. Do **not** export PDF from the CZUR software — the Python OCR stage works page-image by page-image so every page can be quality-checked and re-OCR'd individually. (Optionally also make a searchable PDF for your own reading, but the pipeline ignores it.)
2. **OCR with CZUR or Python? → Python.** Turn CZUR's OCR off. Our cipher work needs word-level streams (first-letter-of-word keys, contiguous-chapter windows), so I OCR with Tesseract in Python using **word bounding boxes** — that lets us catch gutter-swallowed letters, verify word order, and re-run problem pages. CZUR's built-in ABBYY OCR gives us a flowing document with no per-word QA hooks.
3. **Which settings?** Section 2 below — everything is from the Aura software manual (v4.9 software, `CZUR_Scanner_Setup_RLS_V4.9...` you already have).

## 2. CZUR Aura settings (set once, use for all five books)

From the software's **Scanner settings** menu (manual §2.4.2) and **Scan** screen (§2.3):

| Setting | Value | Why |
|---|---|---|
| Scan mode | **Facing Pages** (two pages per capture, auto-split) | Halves the work; Aura's 3-laser flattening handles the paperback curve |
| Curve flattening / laser lines | **ON** (default in Facing Pages mode) | Mass-market spines curve hard at the gutter — this is the Aura's whole advantage |
| DPI | **350** (highest preset; manual §2.4.2 allows custom up to 1000 — don't bother) | ~2× the resolving power we need for 8–10 pt paperback type after flattening |
| Resolution | **Device default (max)** | Never downsample at capture |
| Image format | **JPG, quality: Best** | JPG is the Aura's only native format; Best avoids compression mush on serifs |
| Color mode | **Color** — NOT Auto Enhance, NOT B&W | B&W thresholding deletes faint gutter characters; Auto Enhance clips tones. We binarize adaptively in Python where we can see what we're doing |
| Exposure | **Auto** | Only nudge manual if pages are badly yellowed |
| Frequency | **60 Hz** (US lighting) | Prevents banding flicker from room lights |
| Paging setting | **Left page first** | So auto-numbering matches reading order |
| Naming rule | Sequential, zero-padded if offered (`scan001…`) | File order must equal page order |
| Finger removal / cots | Use the press tool or cots; leave recognition clearing ON | Fingers at the gutter are the main defect source |
| OCR in CZUR | **OFF** | We OCR in Python (see §1.2) |
| Watermark / Handwritten erase / Auto-crop extras | **OFF** | No destructive filters |

Physical setup: black desk mat under the book, room lights on + Aura's own lamp, book centered under the laser lines, press the spine gently flat with the cots/tool — do not crack 40-year-old glue spines; a 15–20° gutter curve is fine, the flattening handles it.

**Save path:** set the scan save folder to `C:\c_working_area\puzzle_work\scans\<book>\raw\` (I'll create the structure below in §4).

## 3. Which book to start with (scanner shakedown)

**Start with Foundation (Del Rey 1986).** Reasons: smallest book (285 pp), top-tier 3-1 candidate, clean numbered chapter structure, and it's the book whose scan settings everything else inherits. If the eBay books arrive first, do the shakedown on whichever arrives first — the settings don't change.

### Shakedown scope — deliberately small
1. Scan **one full chapter only**: the **10th numbered chapter** (Foundation numbers chapters within each Part; count chapter headings from page 1 of the story — it's Part II, ch. 5 "…", roughly mid-book).
2. Plus the **final chapter** (end of Part V).
3. Plus **one page before and after** each chapter (margin for window-overlap logic).
4. Expected: ~15–25 facing-page captures (30–50 individual page JPGs).

Then stop and hand it to me. I will:
- run the Python OCR stage (Tesseract, word-box mode) on those pages,
- show you OCR-vs-photo spot checks and an error-rate estimate,
- adjust preprocess settings (binarization, gutter mask) if needed,
- only then do we scan whole books.

## 4. Full-book scan plan (after shakedown passes)

Per book, scan in this order (from `scanning-checklist-2026-10-17.md`):

| Book | Priority scan | Notes |
|---|---|---|
| Foundation | Ch. 10 **+ final chapter**, then Ch. 1 | small book; if time permits scan the whole thing — only 285 pp |
| I, Robot | 10th section = final story ("The Evitable Conflict"), then 1st story | linked stories, chapter = story |
| Doctor Zhivago | **Part 10 "On the High Road"**, **Part 16 "Epilogue"**, Part 15 "The Ending", Part 17 poems | 1960 Signet: verify Part numbering on the ToC page and scan the ToC too |
| Cat's Cradle | Ch. 10–15 contiguous (micro-chapters ~400 words each) + final chapter (127 "The End") | chapters are 1–2 pages — fastest book to scan whole; consider scanning all 127 chapters |
| Thorn Birds | Ch. 10 window + final chapter of the last Part | 7 named Parts; big book — targeted scans only |

Folder convention:
```
C:\c_working_area\puzzle_work\scans\
  foundation\raw\scan001.jpg …      (CZUR saves here)
  foundation\txt\ch01.txt …         (Python OCR output, one file per chapter)
  i_robot\raw\…   i_robot\txt\…
  zhivago\raw\…   zhivago\txt\…
  cats_cradle\raw\…  cats_cradle\txt\…
  thorn_birds\raw\…  thorn_birds\txt\…
```
The `txt\<book>` folders feed `uv run solver/body_scan.py --scan-dir <path>` directly.

## 5. What happens on my side when scans arrive

1. `solver/ocr_ingest.py` (I'll write it at shakedown time): Tesseract OCR with word bounding boxes → per-chapter `.txt`, plus a QA report (low-confidence words, gutter-line flags, page order check).
2. Quality gate: ≥99% character accuracy on a spot-checked page before proceeding; re-scan problem pages at the gutter with extra pressure if a whole line edge is missing.
3. Then `body_scan.py` word-level-first runs, zero-Z pre-filter for 3-1, S100 probe for 2-4 — exactly as documented in `results/scanning-checklist-2026-10-17.md`.

## 6. One-time software prerequisites (I'll handle when you give the word)
- Tesseract OCR for Windows (free UB Mannheim build) — needed by the Python OCR stage. Not required for the shakedown scan itself, so you can scan first.
- The repo's `body_scan.py` is already committed and verified (run log 2026-10-17/18).

## 7. Open questions for you
1. **Scan timing:** when a book arrives, do you want to do the shakedown scan yourself with this doc, or have me on the line (this chat) walking through it live? Either works — the doc is complete, but live lets me see the first JPGs immediately.
2. **Whole-book vs targeted:** Cat's Cradle is worth scanning whole (tiny chapters). For the others, targeted chapters per §4 unless you'd rather scan entire books for completeness — your call, it's your time at the scanner.
3. Confirm the books' printing lines when they arrive (copyright page photo, one shot each): I need "Del Rey July 1986" on Foundation and "Signet … February 1960 (or later printing)" on Zhivago to lock era-correctness before we trust results.
