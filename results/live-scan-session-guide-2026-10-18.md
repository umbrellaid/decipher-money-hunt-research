# LIVE SCAN SESSION GUIDE — agent runbook (first written 2026-10-18)
**Purpose:** when David's first book arrives, the agent (future me) runs this
guide top to bottom in the chat, prompting David step by step. David does the
physical scanning; the agent does everything digital. Break tasks into small
parts — David works best that way, and targeted beats exhaustive for the big
books. Whole-book scan is approved for the short book (Cat's Cradle) only.

## Context snapshot (read first, no searching needed)
- Project: Decipher II/III (1985–87) book ciphers. Repo:
  `C:\c_working_area\puzzle_work\puzzles_from_internet_or_mysteries\decipher-money-hunt-research`
  (git master, pushes authorized). Latest commit includes `solver/ocr_ingest.py`
  (commit ce781f4) and `solver/body_scan.py`.
- Purchases & editions: see `book-purchases-2026-10-18.md` in
  `C:\c_working_area\puzzle_work\`. Scanner settings rationale:
  `scanning-workflow-czur-2026-10-18.md` (same folder). Candidate chapters:
  repo `results/scanning-checklist-2026-10-17.md`.
- Scanner: **CZUR Aura** (14 MP), software v4.9 already on David's PC
  (`G:\qwen_workspace\personal\document_scanner_czur\`). Manual copy:
  `C:\c_working_area\puzzle_work\CZUR Aura Software Manual(Windows).pdf`.
- Tesseract v5.5.0 (eng) confirmed at `C:\Program Files\Tesseract-OCR\tesseract.exe`;
  `ocr_ingest.py` auto-finds it. Smoke test passed 2026-10-18.
- Strategy locked: word-level-first streams, contiguous chapter windows,
  zero-Z pre-filter for 3-1, S100 probe for 2-4.

## Pre-flight (agent, silent — before prompting David)
1. `cd` to repo; `uv run solver/run_full_ciphertexts.py --top 3` → must print
   `INMEMORYOFJOHNLENNONNOBODYTOLDMETHEREDBEDAYSLIKETHESE` and `Control Bigram Fit 0.741`.
2. `mkdir -p C:\c_working_area\puzzle_work\scans\<book>\raw` for the session's book.
3. Confirm tesseract: `"C:\Program Files\Tesseract-OCR\tesseract.exe" --version`.

---

## PHASE 0 — Unboxing & copyright pages (every book, as it arrives)
**Prompt David:** "Before any scanning: open each new book to the copyright
page (verso of title page) and scan/photograph it — one capture per book.
Also tell me the books arrived physically OK (no loose pages at the gutter)."
- Agent: OCR or read each copyright page; verify against expected printings:
  - Foundation → "Del Rey … July 1986" (or earlier Del Rey printing line)
  - I, Robot → Fawcett Crest, 1970 printing line
  - Doctor Zhivago → Signet … "First Printing, February 1960"
  - Cat's Cradle → Dell, any printing of ISBN 0440111498 (note printing #)
  - Thorn Birds → Avon ISBN 0380018179 (note printing #/year)
- Record results in `book-purchases-2026-10-18.md` (append "Verified" lines).
- **Gate:** if a printing is NOT era-correct, flag it — pagination may differ;
  the book can still be scanned but results get an "unverified edition" tag.

## PHASE 1 — CZUR settings (once, ~5 min)
**Prompt David through each setting** (from scanning-workflow doc §2):
Facing Pages mode · laser flattening ON · DPI 350 · JPG Best · color mode
**Color** (NOT Auto Enhance/B&W) · auto exposure · 60 Hz · left-page-first ·
CZUR OCR OFF · save path `C:\c_working_area\puzzle_work\scans\<book>\raw`.
**Prompt David:** "Do ONE test capture of any open spread now."
- Agent: check the test JPGs exist, are split left/right, readable, no glare.
- **Gate:** bad test capture → fix settings and repeat before continuing.

## PHASE 2 — Shakedown scan (Foundation, or whichever book arrived first)
**Prompt David:** "Scan ONLY these, in order, one facing-page capture at a time:
(a) the page before the 10th numbered chapter begins; (b) the whole 10th
chapter; (c) one page after it ends; (d) the final chapter the same way
(margin page before, chapter, margin page after). Tell me when done."
Expected: 15–25 captures. Agent then:
1. Write the chapter map CSV (`scans/foundation/chapters.csv`) matching actual
   capture numbers — ask David for the capture number where each chapter starts
   OR read the first line of OCR per page to find chapter heads automatically.
2. Run: `uv run solver/ocr_ingest.py --book foundation --raw-dir ... --map ...`
3. Read `qa_report.md`. Show David 2–3 OCR-vs-photo spot checks.
- **Gate:** zero RESCAN flags and clean spot checks → Phase 3. Else adjust
  (gutter pressure, psm 4, lighting) and rescan only the flagged pages
  (use the software's Reproduce/Insert feature — manual §2.2.4).

## PHASE 3 — First cipher run
Agent: `uv run solver/body_scan.py --scan-dir texts/foundation --top 10`
Report the tier-grouped hits to David in plain language. Whatever the outcome,
this calibrates the whole pipeline. Commit texts + map + qa to the repo.

## PHASE 4 — Targeted batches per book (narrowing, never whole-book except Cat's Cradle)
After every batch: OCR → body_scan → report → decide next batch on signal
(promising = high Control Bigram Fit, zero-Z pass, S100 pattern, readable crib).

| Book | Batch A (first) | Batch B | Batch C (only on signal) |
|---|---|---|---|
| Thorn Birds (2-4) | Ch. 10 + margins | final chapter of Part Seven | Ch. 1; then rest of Part One |
| Foundation (3-1) | ch. 10 + final chapter (shakedown = this) | ch. 1 | remaining chapters of Parts II & V |
| I, Robot (3-1) | final story "The Evitable Conflict" | first story "Robbie" | remaining 7 stories |
| Doctor Zhivago (3-1) | Part 10 "On the High Road" | Part 16 "Epilogue" + Part 15 "The Ending" | Part 17 poems |
| Cat's Cradle (multi) | **whole book, front to back** (127 tiny chapters, ~190 pp; fastest per page) | — | — |
Chapter-map CSV per book: agent writes it during each session from actual
capture numbers; convention `start_image,chapter,label`.

## Troubleshooting quick table
| Symptom in qa_report | Fix |
|---|---|
| RESCAN low conf, gutter words missing | more spine pressure with cots; re-shoot those pages |
| Whole line edge missing | book off-center; recenter under lasers, rescan page |
| Blur | page moved during capture; slow down, use hand pedal/button per page |
| Glare streak | tilt book slightly / dim room light, keep Aura lamp |
| mean conf < 85 everywhere | check color mode is Color, JPG Best, DPI 350 |
| Tesseract scrambles order | try `--psm 4`; if spreads weren't split, rerun with `--split-spreads` |

## Time estimates (for setting expectations with David)
Shakedown: ~30–40 min total. Each targeted batch: 10–20 min scanning +
~5 min agent processing. Cat's Cradle whole book: ~60–90 min at the scanner.

## Field notes from the first real scan (2026-10-18 — non-project book, applies to ALL future sessions)
David scanned a 277-page trade paperback ("Abundance Through Scarcity") as our
first-ever CZUR session. Two real-world things happened that we must expect
and handle in every future scan, including the cipher books:

1. **Hand in frame.** A finger/hand landed in a few captures; David noticed
   and re-shot those pages — so the RAW set contains BOTH the bad take and
   the good retake.
2. **Lost place → repeated pages.** He re-scanned some already-good pages.
   Net effect: any real scan set WILL contain duplicate pages.
   
**Handling rule (bake into every session, cipher books included):**
- Never assume image N = book page N. After OCR, extract the printed page
  number from the bottom strip of each page and group captures by it.
- Within a duplicate group keep ONE copy: highest OCR mean confidence wins
  (hand-in-frame pages OCR worse); tie-break = keep the LATER capture
  (retakes come after the mistake). List all groups in the QA report and
  tell David which image was dropped and why before deleting anything —
  move rejects to a `rejects\` subfolder, never hard-delete during the session.
- Prevention at scan time (prompt David): glance at the file-list counter
  after each capture and say the printed page number out loud; if a hand
  gets in a shot, reshoot IMMEDIATELY using the software's Reproduce
  function (manual §2.2.4) so the bad take is replaced at capture time
  instead of deduped later.
- Self-published/layout quirk seen: decorative drop caps can chop into the
  first paragraph of a chapter — OCR breaks there. Fix = agent reads those
  paragraphs from the image and hand-corrects the text. Check every
  chapter-start page for this.

## Close-out (every session)
1. Append results to repo `results/RUN_LOG.md`; commit + push (texts, maps, QA).
2. Update this guide if any setting changed.
3. Tell David plainly: what was scanned, what the cipher run showed, what's next.
