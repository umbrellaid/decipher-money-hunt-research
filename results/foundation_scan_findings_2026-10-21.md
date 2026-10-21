# Foundation Scan Findings — 2026-10-21

## Book details
- **Title:** Foundation
- **Author:** Isaac Asimov
- **Edition:** Del Rey/Ballantine, July 1986, ISBN 0-345-33627-5
- **Era-correct for cipher 3-1:** YES (pre-1987 ✓)

## Structure discovered
Foundation numbers its chapters as **numbered sections within each Part**, not as globally numbered chapters:

| Part | Name | Pages | Sections |
|---|---|---|---|
| I | The Psychohistorians | 1–44 | 1–5 |
| II | The Encyclopedists | 45–94 | 1–3 (global 6–8) |
| III | The Mayors | 95–164 | 1–5 (global 9–13) |
| IV | The Traders | 165–194 | 1–2 (global 14–15) |
| V | The Merchant Princes | 195–285 | 1–6 (global 16–17) |

**Chapter 10 (global)** = Part III, section 2, starting at **page 109**  
**Final section (global 17)** = Part V, section 6, starting at **page 275**

## Why Foundation was NOT eliminated by the short Table of Contents
The ToC has only 5 Part names: PSYCHOHISTORIANS, ENCYCLOPEDISTS, MAYORS, TRADERS, MERCHANTPRINCES. Stripped to letters = 66 characters. Cipher 3-1 needs 516 minimum. **Every book on the scan list fails the ToC test** — the ToC-only hypothesis was broadly eliminated before body-text scanning began. Foundation stays because Asimov is a confirmed Group B candidate author for Decipher III.

## Cipher results
**NO MATCH for any tested cipher (3-1, 2-4, 3-2, 3-3).**

The body_scan.py tested 1,521 streams × 5 drift offsets × 2 directions across all chapters. The best 3-1 score was 1.658 — vowel-heavy gibberish from the WordLast stream artifact. No readable English plaintext was produced under any extraction family.

**Foundation is eliminated as a cipher 3-1 candidate.**

## Scan quality notes
- 329 CZUR Aura scans, 350 DPI, color
- 26/329 pages flagged for rescan (7.9%) — mostly non-story pages
- No hand/finger obstruction found on any story page
- image00140 (first page of ch10) has TSV coordinate artifacts leaked into OCR — Tesseract misread some page decoration or binding gutter as data strings
- image00180 (page 149, ch12) has doubled-letter printing defects in the physical book (e.g., "iis" for "is", "WWWhat" for "What") — this is a printing error in this specific copy, not a scan issue

## Lessons for future scans
1. **Chapter numbering varies by book.** Foundation uses per-Part numbering. Always verify the physical book's structure against the scanning checklist's Gemini-based estimates (marked †) before creating the chapter map CSV.
2. **The chapter map CSV needs careful boundary mapping.** Missing section boundaries caused chapters to merge (ch12 got 70 pages, ch16 got 86 pages). Future scans should identify ALL section breaks before creating the CSV.
3. **First page of chapters may have OCR artifacts** from chapter heading formatting, decorative elements, or binding gutter. Consider adding a 1-page margin before/after each chapter in the CSV.
4. **The `ocr_ingest.py` had a critical word-ordering bug** — fixed during this session (see below). Always verify OCR output readability before running cipher analysis.

## Bug fixed in ocr_ingest.py
**Bug:** The line grouping key included `int(r["top"])` (pixel y-position), but Tesseract reports slightly different `top` values for words on the same physical line. This split one line into many groups, producing severely scrambled word order.

**Fix:** Removed `top` from the grouping key. Now groups by `(block_num, par_num, line_num)` only, and tracks `top` separately for line ordering. Also added a filter to skip pure-numeric tokens (TSV artifacts).

**Remaining issue:** image00140 still has some TSV-format strings like "more5" leaking through — these are Tesseract text fields that contain a word concatenated with a digit. A more aggressive filter (e.g., skip words matching `\w+\d+`) could help but risks removing legitimate text.
