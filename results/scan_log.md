# Scan Run Log

Chronological log of all book scan + cipher analysis attempts.

---

## 2026-10-21 — Foundation (Isaac Asimov)

**Date/Time:** 2026-10-21, afternoon  
**Book:** *Foundation* by Isaac Asimov  
**Edition:** Del Rey/Ballantine, July 1986 mass-market paperback, ISBN 0-345-33627-5  
**Cipher target:** Decipher III 3-1 (N_max = 516)  
**Scanner:** CZUR Aura (14 MP), 350 DPI, color, JPG Best, Facing Pages mode  
**Scan folder:** `scanning/book-scans/foundation-2026-10-21/` (329 images)  
**OCR:** Tesseract v5.5.0, psm 6, via `solver/ocr_ingest.py`  
**Cipher scan:** `solver/body_scan.py --scan-dir texts/foundation --top 10`

### Chapter map
| Chapter | Label | Pages | Words |
|---|---|---|---|
| ch00 | Front matter | 29 | 7,390 |
| ch01 | Part I — The Psychohistorians | 90 | 21,960 |
| ch07 | Part II — section 7 | 10 | 2,014 |
| ch09 | Part III — section 1 | 10 | 4,758 |
| **ch10** | **Part III — section 2 (cipher target: Ch. 10)** | **10** | **4,310** |
| ch11 | Part III — section 3 | 10 | 2,548 |
| ch12 | Part III sec 4 + Part IV | 70 | 26,255 |
| ch16 | Part V — sections 1-5 | 86 | 21,263 |
| **ch17** | **Part V — section 6 (FINAL chapter, cipher target)** | **14** | **4,388** |

### Cipher 3-1 results
**No match.** Top score 1.658 (ch17 WordLast_Split, drift 0, Fwd) produced vowel-heavy gibberish:
`EOEEDEEYDKHFDLGTUUTSTEEESDDYARCMWHDTTOTPEETNSEWTTENYEEEERFDTEEPEE`

This is the known letter-density artifact of WordLast streams — NOT readable plaintext. No Tier 1, 2, or 3 stream produced anything resembling English.

22 of 39 windows flagged for Z inside the first 516 chars/words (3-1 zero-Z necessary condition). The front matter and early chapters contain Z's from the TSV artifact noise on image00140, which inflated the flag count.

### Other ciphers tested
Body scan also tested 2-4, 3-2, 3-3 — no matches for any.

### QA summary
- 26/329 pages flagged for rescan (7.9%)
- Most flags are on non-story pages (covers, author bio, back cover) or low-conf gutter pages
- image00317 (ch17, 65.3 conf) — gutter curvature on late page; may affect final chapter quality
- image00140 (ch10, first page of cipher target) — TSV coordinate artifacts leaked into OCR text
- image00180 (page 149, ch12) — doubled-letter printing defects in the physical book

### Verdict
**Foundation is ELIMINATED as a cipher 3-1 candidate** based on body-text scan. Neither Chapter 10 (Part III section 2) nor the final chapter (Part V section 6) produces readable plaintext under any tested extraction family.

---

*Future entries will be appended below this line.*

---

## 2026-10-26 — Three-book session: I, Robot + Doctor Zhivago + Cat's Cradle

**Date/Time:** 2026-10-26 (scans 15:55, processing into the evening)
**Books:** *I, Robot* (Asimov), *Doctor Zhivago* (Pasternak), *Cat's Cradle* (Vonnegut)
**Editions (verified from copyright-page scans, era-gate PASSED for all three):**
- *I, Robot* — Fawcett Crest, © 1950, Robbie renewal © 1968 (the purchased 1970 printing). Complete original hardcover text.
- *Doctor Zhivago* — Signet / New American Library, **FIRST PRINTING, FEBRUARY, 1960** (vision-read from the copyright page; printing line not OCR-legible but the imprint block is). Hayward/Harari translation.
- *Cat's Cradle* — Dell, ISBN 0-440-11149-8, © 1963 ("New Dell Edition"; any printing of these plates is era-valid for a 1985-87 puzzle).

**Cipher targets:** I Robot + Zhivago → 3-1 (primary), all; Cat's Cradle → multi (Ch. 10-15 window, Ch. 127).
**Scanner:** CZUR Aura, full-frame 4320×3240 spreads, book bottom-center on dark mat (~250 DPI effective per page after crop).
**Scan folder:** `scanning/book-scans/2026_10_26_15_55_14/` (mixed 3-book session, separated into
`cats-cradle-2026-10-26/`, `i-robot-2026-10-26/`, `doctor-zhivago-2026-10-26/`; boundaries in that folder's README).

### What was different about this session
1. **ScanTailor Advanced was tried and rejected.** 105/903 output TIFs blank, first page 99% black,
   2× upscale with baked-in bilevel. Kept in `2026_10_26_15_55_14/out/` for reference; never used.
2. **New preprocessor** `solver/preprocess_spreads.py` (v3): bright-region crop (two-tier threshold
   beats the textured mat), gutter split at span center ± p30 valley, white pad, 2× upscale.
   442 spreads → 884 pages, 0 failures, page widths ~1020-1040 px median.
3. **New marker-chasing ingest** `solver/ingest_by_markers.py`: chapters split at their actual
   heading lines (chapter numbers for Cat's Cradle, story titles for I, Robot, "CHAPTER <numeral>"
   for Zhivago), running heads stripped, duplicate re-scans dropped (Jaccard ≥ 0.75), TSV-artifact
   tokens filtered. Chapter files therefore start at the true first body word — required because
   body_scan's numbering drift is only ±2.
4. `ocr_ingest.py` gained `--strip-header` (running heads pollute letter streams — see Foundation
   caveat below).

### Chapter maps
- **texts/i-robot/** — ch00 front + ch01 Introduction (1,921 w) … ch10 The Evitable Conflict
  (8,304 w). Openings verified against the book (ch03 = "It was one of Gregory Powell's favorite
  platitudes…", ch10 = "The Co-ordinator, in his private study, had that medieval curiosity, a
  fireplace…").
- **texts/doctor-zhivago/** — ch01-ch17, all 17 parts anchored at their "CHAPTER <n>" headings
  (parts 14 and 17 needed psm-4 overrides on their opener pages). ch10 The Highway trimmed to its
  true opening "There were towns, villages, and Cossack settlements along the highway…". Part 17
  (poems) starts at HAMLET. Word counts 6k-21k per part, ~200k total.
- **texts/cats-cradle/** — 49 anchored chapter files (1,3,4,5,7,8,9,10,11,13,14,17,22,…,90) chosen
  by the DP monotone chain over chapter-number candidates; the ch10-15 cipher window is contiguous
  (ch10, ch11, ch13, ch14 anchored; 12 and 15 fold into neighbors). ch127 "The End" manually split
  from the ch090 bundle (2,558 w, opens "He was sitting on a rock…"). Chapters 91-126 remain
  merged inside ch090 (18,251→15,690 w after the split) — their heading numbers were garbled by
  OCR; only 10-15 and 127 were scan targets.

### QA summary
- I, Robot: 38/199 pages flagged RESCAN (low conf, mostly 70-84 on gutter/left pages); ~9 running-head
  word leaks. No duplicate pages detected.
- Zhivago: 2 duplicate re-scans auto-dropped (image00310_2R, image00311_1L); poems section OCR is
  the noisiest (italics + tight margins).
- Cat's Cradle: 3 single-page captures (cover etc.) fine; several micro-chapter heading numbers
  garbled (documented in markers_log.csv).
- Visual spot-checks: 8+ pages read against images across the session (covers, title/copyright
  pages, gutter problem pages, part openers) — OCR text matched page content everywhere checked.

### Foundation caveat (recorded 2026-10-26)
The 2026-10-21 Foundation texts contain TSV-artifact strings and unstripped running heads
(both bugs are fixed in the current pipeline). Its 3-1 ELIMINATION is probably still valid (the
pollution is sparse), but a re-ingest of the Foundation pages through `ingest_by_markers.py`
would make it airtight. Recommended before treating Foundation as fully closed.

---

## 2026-10-27 — Foundation + The Thorn Birds re-processed through the fixed pipeline

David asked to apply the 10-26 workflow to both earlier scan sets. No new scanning.

### Foundation (re-ingest; elimination now airtight)
- Source: the 329 pre-split page images from 2026-10-21 (Facing-Pages capture — no
  preprocessing needed; the fix was all in the ingest).
- **Corrected chapter map** (`scanning/book-scans/foundation/chapters_v2.csv`): 28 section
  anchors (ch00-ch27) vs the old 9. The old map's ch12 had absorbed 70 pages (Part III s4
  through all of Part IV). True structure: sections numbered WITHIN parts (Part III s1
  epigraph at image00128, Part IV s1 epigraph at image00198, Part V at image00230).
  Old ch10 (cipher target) = new ch07@image00140; old ch17 (final) = new ch27@image00116[316].
- Running heads stripped ("FOUNDATION"/"ISAAC ASIMOV"); leading section numerals trimmed from
  ch05/ch27. Both target openings verified ("There are many epigrams…" / "The senior lieutenant…").
- QA: 26/329 flagged (unchanged — same images; mostly front/back matter).
- **body_scan verdict: no readable plaintext for 3-1/3-2/3-3/2-4; 111/153 windows fail the
  3-1 zero-Z condition. Foundation's 3-1 ELIMINATION is CONFIRMED on clean text — the
  2026-10-26 caveat is closed.** Full output: `results/body_scan_2026-10-27_reingest_full.txt`.

### The Thorn Birds (re-ingest; 2-4 negative, noise caveat)
- Source: the 2026-10-24 "second try" 367 raw spreads (the first attempt remains unusable
  per its own SCAN_REPORT — auto-crop destroyed margins on 89% of pages).
- preprocess_spreads.py: 367 → 716 pages, 0 failures. 18 single-page captures: 13 are UNIQUE
  fills (spread skips), NOT duplicates — kept; 11 true reshoot pages removed to
  `pages-new/_dedup_rejects/` (228/229, 346/347, 357/358, 359/360, 137/138, 177/178, 223/224).
- Structure: 7 parts, running heads "YEARS NAME" (1915-1917 MEGGIE → 1965-1969 JUSTINE).
  Map: `scanning/book-scans/the-thorn-birds/chapters_v2.csv`; part starts content-verified.
- QA: **471/705 pages flagged; mean conf 77.2** (vs ~85 for the 10-26 books) — the 692-page
  paperback's gutter curve + hand shadows. 128 pages < conf 70, clustered in Part Two
  (RALPH, 41) and Part Six (DANE, 41). Rescan list for David:
  `scanning/book-scans/the-thorn-birds/RESCAN_LIST_2026-10-27.md`.
- **body_scan verdict: no readable plaintext for 2-4 (or 3-1/3-2/3-3); 26/33 windows fail
  zero-Z. Downgraded from INCONCLUSIVE to NEGATIVE-WITH-CAVEAT — if 2-4 ever narrows to
  McCullough, rescan the flagged pages first.**

---

## 2026-10-27 — The Thorn Birds FULL RESCAN (third capture pass) — 2-4 ELIMINATED-grade negative

David rescanned the entire book (369 spreads, session 2026_10_27_15_13_33) with the
checklist: top-down Aura light, hands on outer edges only, slower captures, immediate
reshoots when unsure. The pipeline (preprocess → page_heads → map → ingest --dedup)
ran unchanged; David's "insurance" reshoots were auto-deduped (9 pages).

**Quality vs the 10-24 scan (diff against the IA 1977 Harper text, same method):**

| Part | 10-24 scan | rescan | |
|---|---|---|---|
| One (Meggie) | 0.812 | **0.920** | |
| Two (Ralph) | 0.596 | **0.867** | +0.27 |
| Three (Paddy) | 0.791 | **0.906** | |
| Four (Luke) | 0.766 | 0.856 | |
| Five (Fee) | 0.766 | 0.771 | thick-book middle, diffuse 70-78 band |
| Six (Dane) | 0.739 | 0.765 | same |
| Seven (Justine) | 0.875 | 0.826 | Part-7 opener pages OCR'd worst (conf 27-54) |
| **Overall** | **0.772** | **0.844** | conf mean 77.2→84.0; <70 pages 128→27 |

Word recovery: 515k → 564k normalized words (old scan lost ~50k words in Parts 5/7).

**body_scan (results/body_scan_2026-10-27_rescan.txt): no readable plaintext for 2-4,
3-1, 3-2 or 3-3 under any tested family; 26/33 windows fail 3-1 zero-Z.** With Parts
1-4 now at 0.86-0.92 match, the negative is strong through the book's first two-thirds.
Parts 5-6 (0.77) still carry a diffuse mid-band — a theoretical hit there remains
harder to see, but at this quality the book is recorded as **2-4: NEGATIVE (near
elimination; Parts 5-6 caveat noted)**.

Reference texts used for comparison (local only, never committed): IA item
colleenmcculloug0000coll djvu.txt + PDF text layer (verified word-identical, 235,025
words both). Scans remain in scanning/book-scans/the-thorn-birds/pages-rescan;
texts/the-thorn-birds now points at the rescan ingest (old kept as
texts/the-thorn-birds-old-2026-10-24).
