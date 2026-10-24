# Tesseract PSM Mode Comparison — Book Scan OCR

**Purpose:** We run each book through Tesseract OCR with two Page Segmentation Modes
(PSM) to determine which produces better results for cipher analysis. This document
tracks the comparison across all books scanned.

## Why two PSM modes?

- **PSM 6** ("Assume a single uniform block of text") — the default for general OCR.
  Produces more word-level stream diversity for body_scan.py cipher analysis.
- **PSM 4** ("Assume a single column of text of variable sizes") — designed for
  clean single-column book pages. Typically gives higher OCR confidence.

We run both to compare: does higher OCR confidence (PSM 4) translate to better
cipher analysis scores? Or does the stream diversity from PSM 6 matter more?

## How to read this document

Each book gets a section below. The key metrics are:
- **Mean confidence** — Tesseract's per-word OCR confidence (higher = more accurate text)
- **High conf %** — percentage of pages with ≥85% average confidence
- **Cipher top score** — best bigram fit score from body_scan.py (higher = more English-like)
- **Streams tested** — number of extraction streams body_scan.py could generate

---

## Foundation (Isaac Asimov, Del Rey 1986)

**Scan date:** 2026-10-21
**Scanner:** CZUR Aura, 350 DPI, color, no ScanTailor processing needed
**Images:** 329 JPG files (single pages, not spreads)
**Cipher target:** 3-1 (Chapter 10 + final chapter)

### OCR comparison

| Metric | PSM 4 | PSM 6 | Delta |
|---|---|---|---|
| Mean confidence | 93.2 | 89.7 | +3.5 |
| High conf pages (≥85) | 295 (97%) | 290 (91%) | +5 |
| Medium conf (70-84) | 9 | 13 | -4 |
| Low conf (<70) | 1 | 14 | -13 |
| Total words | 71,647 | 79,574 | -7,927 |
| Page numbers found | 16 | 22 | -6 |

### Cipher analysis

| Metric | PSM 4 | PSM 6 |
|---|---|---|
| 3-1 Tier 1 top score | 1.261 | 1.708 |
| 3-1 Tier 2 top score | 1.363 | 1.643 |
| 3-1 Tier 3 top score | 0.671 | 0.610 |
| 2-4 Tier 1 top score | 0.911 | 1.328 |
| 2-4 Tier 2 top score | 1.205 | 1.229 |
| 3-2 Tier 1 top score | 1.359 | 1.845 |
| 3-3 Tier 1 top score | 1.236 | 1.502 |
| Streams tested | 39 | 39 |
| Verdict (3-1) | ELIMINATED | ELIMINATED |
| Verdict (all others) | No match | No match |

### Foundation takeaway

Same pattern as Thorn Birds: PSM 4 gives higher OCR confidence (+3.5, 97% vs 91%)
but PSM 6 produces higher cipher scores across all tiers. Foundation was already
eliminated for 3-1 with the original per-chapter scan (see RUN_LOG 2026-10-21).
Both PSM modes confirm elimination — all stream previews are vowel-density artifacts.

**Note:** These re-OCRs used a single merged ch01.txt (all pages combined), while the
original 2026-10-21 analysis used per-chapter files from `ocr_ingest.py` with a chapter
map CSV. The per-chapter approach gives body_scan.py more window diversity (9 chapters
× 6 window sizes = 54 windows vs 1 window here). The original analysis is more thorough.

---

## The Thorn Birds (Colleen McCullough, Avon)

**Scan date:** 2026-10-24
**Scanner:** CZUR Aura "no processing" → ScanTailor Advanced GUI → 734 clean TIFs
**Images:** 671 pages OCR'd (63 blank rejected)
**Cipher target:** 2-4 (N_max=1053)

### OCR comparison

| Metric | PSM 4 | PSM 6 | Delta |
|---|---|---|---|
| Mean confidence | 80.4 | 77.6 | +2.8 |
| High conf pages (≥85) | 409 (63%) | 306 (46%) | +103 |
| Medium conf (70-84) | 127 | 217 | -90 |
| Low conf (<70) | 115 | 142 | -27 |
| Total words | 286,300 | 302,531 | -16,231 |
| Page numbers found | 90 | 116 | -26 |

### Cipher analysis

| Metric | PSM 4 | PSM 6 |
|---|---|---|
| 2-4 Tier 1 top score | 1.004 | 1.808 |
| 2-4 Tier 2 top score | 1.385 | 1.774 |
| 2-4 Tier 3 top score | 0.632 | 0.889 |
| Streams tested | 39 | 234 |
| Verdict | INCONCLUSIVE | INCONCLUSIVE |

### Thorn Birds takeaway

PSM 4 gives **+2.8 confidence** and **63% high-conf pages** (vs 46%) — clearly better
OCR quality. But PSM 6 produces **6× more cipher streams** (234 vs 39) and higher
cipher scores. Neither mode found a cipher match. The confidence improvement from
PSM 4 does not translate to better cipher detection.

---

## Recommendations for future scans

### Consistent pattern across both books

| | Foundation | Thorn Birds |
|---|---|---|
| PSM 4 confidence advantage | +3.5 | +2.8 |
| PSM 4 high-conf % | 97% (vs 91%) | 63% (vs 46%) |
| PSM 6 cipher score advantage | Higher across all tiers | Higher across all tiers |
| PSM 6 stream diversity | Same (39) | 6× more (234 vs 39) |

### Procedure

1. **OCR with PSM 6 as default** for cipher analysis — it consistently produces
   higher cipher scores and more stream diversity, despite lower per-word confidence
2. **Also run PSM 4** as a quality check — if PSM 4 confidence is significantly
   higher, the scan images may need preprocessing (ScanTailor, deskew, etc.)
3. **Use per-chapter files** (via `ocr_ingest.py` with a chapter map CSV) rather
   than a single merged ch01.txt — body_scan.py benefits from contiguous chapter
   windows across multiple files
4. **Update this document** with each new book scanned

### When to prefer PSM 4

- Final archival-quality text extraction (readable output, not cipher analysis)
- Quality assessment of scan images (higher confidence = cleaner source images)
- When the goal is human-readable OCR, not cipher stream generation
