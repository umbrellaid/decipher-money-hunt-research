# Gemini ToC-and-clue test — 2026-10-17

**Source:** Google Gemini thread `gemini.google.com/app/fcdc50809f6208f7`
(prompted to read this repo and prioritize candidate key books). The consolidated
thread export was verified byte-identical to the live page; a local verification
addendum with all corrections lives in the working copy
(`gemini-code-1792283342181.md`).

## What Gemini contributed

1. **Candidate prior tables** for the Decipher III (3-1) 11-author list, weighted
   by Warren Holland's selection psychology (mainstream bestsellers only; author
   carryover/reuse across lists). Top Asimov pick: *Foundation*; top overall
   non-Asimov: Vonnegut (*Cat's Cradle*), Capote, Ludlum, Clavell-reuse, Pasternak.
2. **ToC length-floor audit** — for a *Catch-22*-style chapter-title key, the
   concatenated ToC must exceed N_max. This correctly kills *Slaughterhouse-Five*,
   *Shōgun*, *The Bourne Identity*, *Exodus*, *All the President's Men* (0 title
   letters) and *Foundation*'s 5 part titles (81 letters).
3. **Clue analysis for 3-1** (`"10"` / `"End."`): Chapter 10 / final chapter of each
   candidate is the priority body-scan target; *Foundation's Edge* Ch. 10 is
   literally titled "Table" and Ch. 20 "Conclusion"; *Cat's Cradle* Ch. 127 is
   "The End"; Pasternak is author #10 on the 3-1 list with Part 15 "The Ending".
4. **A standalone tester** (`solver/toc_and_clue_tester.py`): embeds 9 candidate
   ToCs, generates ~536 key streams (bare/Chapter-Word/Roman prefixes, full vs
   from-Ch-10 slices, chars/first-letter/last-letter, decimation by 10, fwd/rev),
   decodes with drift tolerance ±2, scores by bigram log-likelihood + IoC.

## Local verification — what changed

- **The script's ciphertexts are truncated prefixes of `data/ciphers.json`:**
  2-4 = 51/170 tokens, 3-1 = 113/170, 3-2 = 56/117, 3-3 = 130/159 (2-2 complete).
  `solver/run_full_ciphertexts.py` reruns the whole pipeline on the full texts.
- **Corrected N_max:** 2-4 = 1053 (matches the title-chain argument in commit
  5450b7d), 3-1 = 516, 3-2 = 416, 3-3 = 721.
- **New cribs visible only in the full ciphertexts:** 3-1 has six literal letters
  (E,E,E,Z,E,E — a second Z near the end of the token stream); **3-2 has five
  (E,Y,E,Y,E — a repeating E…Y, E…Y, E pattern)**, a stronger structural crib than
  the truncated E,Y pair Gemini analyzed.
- **Control-key caveat:** the embedded 42-title Catch-22 list concatenates to 487
  letters; the documented 2-2 solution key is 478. The self-test still decodes
  recognizably (`IYMEMOJYCFMAHNLENNON…` for "IN MEMORY OF JOHN LENNON…") but with
  garbled mid-text indexes. The exact 478-letter title list is still to reconcile.

## Test outcome (both truncated and full-ciphertext runs)

No embedded ToC variant solves any open cipher. All top hits are vowel-heavy
gibberish; the high `LastLetter_EndClue` scores are letter-density artifacts (the
same caveat this log records for `*-wordlast` streams). Coverage is low for most
puzzles because only the Catch-22 and Zhivago Parts+Poems "Chapter One…" streams
exceed N_max = 1053/721. The 2-4 multiples-of-100 null hypothesis produced no
readable decode either.

**Verdict:** ToC-only keys eliminated for the 9 embedded books. The standing plan
is unchanged: body-text scans of Chapter 10 openings/endings and final chapters of
the surviving candidates (`docs/check-your-own-book.md`), now with corrected
N_max values and the full crib sets.

## Files

- `solver/toc_and_clue_tester.py` — Gemini's script, unmodified (embedded ToCs + scoring).
- `solver/run_full_ciphertexts.py` — driver that swaps in this repo's full `data/ciphers.json`.
- Run: `uv run solver/run_full_ciphertexts.py --top 25` from the repo root.
