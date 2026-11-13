# Top 10 Ranked Paperback Scan Priority List (Updated 2026-11-12)

Practical scanning order for the next round of physical book scans (CZUR Aura or overhead
phone/book scanner), incorporating:

1. **Five completed whole-book physical paperback sweeps** recorded in [`results/RUN_LOG.md`](../results/RUN_LOG.md):
   - *Foundation* (Del Rey 1986)
   - *I, Robot* (Fawcett Crest 1970)
   - *Doctor Zhivago* (Signet 1960)
   - *The Thorn Birds* (Avon `0-380-01817-9`)
   - ***Cat's Cradle*** (Dell `#11149`, `0-440-11149-8`, 59th printing Nov 1984 — **recovered
     2026-11-12 directly from existing 2026-10-26 raw captures** at `92.21%` mean confidence,
     `181/181` body pages, `127/127` chapters; swept negative across all 21 sliding + 21
     palindromic families, physical `line-first`/`line-last`, 127-title chains, 3-band drift,
     and scattered-null diagnostics — **no re-scan needed!**)
2. **Ciphertext structural laws** from [`docs/decipher-ciphertext-patterns.md`](decipher-ciphertext-patterns.md):
   - **`3-1` (Group B, pre-1987, `max = 516`, clues `"10"` & `"End"`):** almost strict
     without-replacement (`4` repeats across 164 numeric tokens), word-initial `'E'`
     depletion (`5` literal `'E'`s), zero-`'Z'` key window (`1` literal `'Z'` at pos 98),
     doubled letter at `487, 487` (pos 26–27), and pattern `A E B A` at `335, 'E', 308, 335`.
   - **`2-4` (Decipher II Group A, pre-1985, `max = 1053`):** zero literal letters, flat
     palindromic fold curve (`2@1083`, `p = 1.00` — strongly favoring a single-direction
     ~1,053+ unit stream), three consecutive `+1` triples (`737–739`, `154–156`, `544–546`),
     and the 8-token round-hundred run at positions 20–27.
   - **`3-2` (Group A or C, pre-1987, `max = 416`):** alternating `E, Y, E, Y, E` literals,
     short key window (~1.7 pages of words or ~0.3 pages of characters).
   - **`3-3` (Group A or C, pre-1987, `max = 721`):** strictly **zero repeated integers**
     across all 156 numeric tokens + `3` literal `'E'`s (~2.9 pages of words or ~0.6 pages
     of characters).
3. **Author carryover & proven Warren Holland tastes:** Holland reused favorite genres and
   carried authors across Decipher II and III (Ludlum appears on **both** `2-4` Group A and
   `3-1` Group B; Capote and Uris carried over from Decipher II Group B into `3-1` Group B;
   Heller solved `2-2` and headlines Decipher III Group A; Clavell solved `2-3` and sits on
   Decipher III Group C).

---

## Fast Two-Stage Scan Protocol (Save Hours Per Book)

Because the largest codenumber across all four open ciphers is `1053` (~4.2 paperback pages
under word-initial extraction, <1 page under continuous-character extraction), **you do not
need to scan 400–1,000 pages blind before testing a book**:

1. **Stage 1 — 15-Minute Structural Spot-Scan (~12–20 pages):**
   Scan the copyright page, Table of Contents, opening 5 pages of Chapter 1, opening +
   closing 5 pages of Chapter/Part 10 (for `3-1`), and closing 6 pages of the final
   chapter/epilogue (`"End"`). Spot-check OCR against the page photos to **99%+ word
   accuracy**, then run:
   ```bash
   uv run python solver/normalize_text.py mybook.txt --chapters
   uv run python solver/sweep.py mybook.clean.txt --cipher all --all-palindromic --top 10
   uv run python solver/drift_diagnostic.py mybook.clean.txt --cipher all --sentence-chars --top 5
   uv run python solver/null_diagnostic.py mybook.clean.txt --cipher all --sentence-chars --top 5
   ```
2. **Stage 2 — Full Paperback Scan:**
   If the book stays high-priority and Stage 1 is negative (remember Decipher I skipped 36
   words into *Cosmos* Ch. 6 and `2-3` used *Tai-Pan* Ch. 5), scan the full volume cleanly
   and run the four commands above to record a definitive whole-book elimination.

*(Why physical era printings still matter even where modern ebooks/borrows were prescreened
earlier: the October 2026 digital prescreens ran `body_scan.py` on unpinned modern digital
files — 9 of which lacked chapter headings — and never ran whole-book `sweep.py`,
`--all-palindromic`, `drift_diagnostic.py`, or `null_diagnostic.py` on 1980s paperback
plates.)*

---

## The Top 10 Scan List

| Rank | Book & Author | Target Cipher(s) | Era Paperback to Scan | Fast Spot-Scan Pages First | Why This Rank |
|---:|---|---|---|---|---|
| **1** | ***The Bourne Identity*** — Robert Ludlum (1980) | **`2-4` AND `3-1`** (Dual hit!) | **Bantam mass-market (1981–1984 printing)** | Preface/Prologue + **Ch. 1** (6 pp) + **Ch. 10** (first & last 5 pp) + **Ch. 39 / Epilogue** (last 6 pp) | **Highest-leverage single book left:** Ludlum is the *only* in-copyright author on **both** Decipher II Group A (`2-4`, pre-1985) and Decipher III Group B (`3-1`, pre-1987). One pre-1985 Bantam paperback tests two unsolved puzzles at once. |
| **2** | ***Foundation's Edge*** — Isaac Asimov (1982) | **`3-1`** (Group B) | **Del Rey mass-market (Nov 1983–1986 printing)** | ToC + **Ch. 10 `"Table"`** (first & last 5 pp) + **Ch. 20 `"Conclusion"`** (first & last 5 pp) | *Foundation* and *I, Robot* are now eliminated. *Foundation's Edge* was Asimov's 1982–83 NYT #1 bestseller comeback, and its ToC hits both `3-1` clues squarely: Ch. 10 (`"Table"`) and final Ch. 20 (`"Conclusion"` = `"End"`). |
| **3** | ***Slaughterhouse-Five*** — Kurt Vonnegut (1969) | **`3-1`** (Group B) | **Dell / Laurel mass-market (pre-1987 printing)** | **Ch. 10 in full** (~10 pp — *both* `"10"` and `"End"` simultaneously!) + **Ch. 1** (first 6 pp) | With *Cat's Cradle* now cleanly eliminated from the Oct 26 scans, *Slaughterhouse-Five* is the top remaining Vonnegut candidate: **exactly 10 numbered chapters**, making Chapter 10 **both** `"10"` and `"End"` in one short chapter (~215 pp total). |
| **4** | ***The Union Club Mysteries*** — Isaac Asimov (1983) | **`3-1`** (Group B) | **Fawcett Crest mass-market (Nov 1984 printing)** | ToC + **Stories #10–#12** (`"Gift"` onward, ~12 pp to clear 516 words) + **Story #30 `"There Was a Young Lady"` & Afterword** | Story #10 (`"Gift"`) is literally a cipher-solving mystery (originally published in June 1981 as *"Decipher Deception"*). Tiny page count for a clean 99%+ OCR pass through the full whole-book `sweep.py` + `drift`/`null` pipeline. |
| **5** | ***The World According to Garp*** — John Irving (1978) | **`2-4`** (Group A) | **Pocket Books mass-market (1979–1984 printing)** | ToC + **Ch. 1** (6 pp) + **Ch. 10** (6 pp) + **Ch. 19 `"Life After Garp"`** (first & last 6 pp) | With *The Thorn Birds* swept negative, *Garp* is the #1 dedicated `2-4` literary bestseller: massive late-1970s paperback phenomenon whose satirical voice aligns closely with *Catch-22* and *Bloom County*. |
| **6** | ***Rabbit Is Rich*** *(or Rabbit, Run)* — John Updike (1981) | **`2-4`** (Group A) | **Fawcett Crest mass-market (1982–1984 printing)** | Opening 6 pp of each of the **5 untitled sections** + final 6 pp of Section V (~36 pp total) | Updike is listed **#1** in Decipher II Group A (`data/author_lists.json`). *Rabbit Is Rich* won the 1982 Pulitzer just before Decipher II's creation and has no chapter titles — matching `2-4`'s 1,053-unit body-passage signature. |
| **7** | ***In Cold Blood*** — Truman Capote (1965) | **`3-1`** (Group B) | **Signet mass-market (pre-1987 printing)** | Opening 5 pp of Parts I–IV (`The Last to See Them Alive`, `Persons Unknown`, `Answer`, `The Corner`) + final 6 pp of **Part IV `"The Corner"`** | Capote is a **carryover author** from Decipher II Group B (`2-2`) into Decipher III Group B (`3-1`), signaling Holland already had a Capote paperback in his reference stack. Compact ~340-page book. |
| **8** | ***Catch-22* (body text!) or *Good as Gold*** — Joseph Heller (1961 / 1979) | **`3-2`** (Group A) | **Dell mass-market (*Catch-22*) / Pocket Books (*Good as Gold*), pre-1987** | **Ch. 1**, **Ch. 10**, and **Ch. 42 `"Catch-22"`** (final chapter, 5 pp) | Holland already used *Catch-22*'s chapter titles for `2-2` and put Heller right at the top of Decipher III Group A (`3-2`, `max = 416` — only ~1.7 pages of words!). Our repo only holds *Catch-22*'s 42 titles, **never its body prose**. |
| **9** | ***King Rat* or *Shōgun*** — James Clavell (1962 / 1975) | **`3-3`** (Group C) | **Dell mass-market (pre-1987 printing)** | *King Rat*: Ch. 1, Ch. 10, & final Ch. (~18 pp); *Shōgun*: Ch. 1 (6 pp), Ch. 10 (6 pp), & final Ch. 60 (last 6 pp) | Holland used Clavell's *Tai-Pan* Ch. 5 for `2-3` and put Clavell on Decipher III Group C (`3-3`, `max = 721`, strictly 0 repeats). Spot-scanning chapter openings/endings tests `3-3` in 20 minutes without committing to 1,200 pages of *Shōgun* up front. |
| **10** | ***The Walking Drum* (or *Hondo*)** — Louis L'Amour (1984 / 1953) | **`2-4`** (Group A) | **Bantam mass-market (1984–1985 printing; *Hondo* Bantam pre-1985)** | *The Walking Drum*: **Ch. 1** (6 pp) + **Ch. 57** (final 6 pp); *Hondo*: **Ch. 1** (6 pp) + final Ch. (6 pp) | L'Amour sits on Decipher II Group A (`2-4`); *The Walking Drum* was his huge 1984 historical adventure bestseller right as Decipher II was compiled, while *Hondo* (~190 pp) is his classic fast-to-scan paperback. *(Runner-up for `3-1` Group B carryover: Leon Uris, **Exodus** or **Trinity**, Bantam.)* |

---

## Quick Pre-Scan Checklist When Returning to the Scanner

1. **Check edition date on the copyright page first:** `<= 1984/1985` for `2-4` candidates;
   `<= 1986` for Decipher III (`3-1`, `3-2`, `3-3`) candidates (later printings from the
   **same mass-market plates** share identical word order and only matter if line-level
   rules are tested).
2. **Keep CZUR curve flattening ON, CZUR built-in OCR OFF, 350 DPI color JPG Best:** run
   Python Tesseract post-processing and **never skip the 3-page visual QA gate** (verify
   >= 99% word accuracy, especially near the inner gutter, before running sweeps).
3. **Run all three solver tools on every `.clean.txt`:**
   - `solver/sweep.py --cipher all --all-palindromic` (21 sliding + 21 phase-resolved
     palindromic families + chapter-title chains)
   - `solver/drift_diagnostic.py --cipher all --sentence-chars` (guards against 1–4 word/char
     edition or OCR shifts inside `[1..max_n]`)
   - `solver/null_diagnostic.py --cipher all --sentence-chars` (guards against ~10–15%
     scattered or periodic plaintext nulls)
