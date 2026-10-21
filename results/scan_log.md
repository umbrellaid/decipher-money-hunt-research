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
