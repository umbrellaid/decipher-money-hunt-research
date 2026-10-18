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
- **Control key reconciled (2026-10-17 evening Q&A):** the Catch-22 chain is
  **484 letters**, and the self-test now decodes exactly
  (`INMEMORYOFJOHNLENNONNOBODYTOLDMETHEREDBEDAYSLIKETHESE`, bigram fit 0.741,
  100% coverage). The earlier 487 came from "Piltchard and Wren" instead of the
  printed "Piltchard & Wren" (Holland strips symbols/digits: & → nothing,
  "Catch-22" → "Catch"); the documented **478** figure was erroneous — max
  codenumber 477 maps to the final N of "The Texan", leaving the letters
  A-X-E-T-E-H-T at reversed-key positions 478–484 unused by the ciphertext.

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

## Follow-up Q&A (evening of 2026-10-17)

Four follow-up questions were put to the same Gemini thread (full texts in the
working copies `gemini-q1-answer.md` … `gemini-q4-answer.md`; Q4 answered with
the Argon High model, Q1–Q3 under a Flash-Lite fallback. Gemini factual claims
below are unverified against physical copies/primary sources unless noted).

1. **Q1 — Catch-22 key length reconciled: 484 letters.** See the control-key
   bullet above: 477 = final N of "The Texan", positions 478–484 (AXETEHT)
   unused; "Piltchard & Wren", not "and"; the 478 figure was wrong. Also
   confirms Holland's stripping rule is pure `[^A-Za-z]` removal (matters for
   titles like "Secret Agent X-9" or "1 to 999").
2. **Q2 — full-ciphertext cribs.** Literal letters = letters absent from the
   keytext window. 3-1's Z cribs ⇒ zero-Z pre-filter (implemented:
   `solver/zero_z_prefilter.py`); 3-2's alternating E,Y,E,Y,E is a strict
   accept/reject filter at crib positions; priority tilts to Pasternak
   (*Doctor Zhivago*) and Vonnegut (*Cat's Cradle*).
3. **Q3 — chapter audit / scan-list corrections.** *Foundation*'s chapters run
   continuously 1–19 (Ch. 10 = Part III "The Mayors" ch. 2); add *Zhivago*
   Part 17 (poems); *Cat's Cradle* Ch. 10 (~400 words) and Union Club stories
   (3–5 pages) are too short for word-level N_max ⇒ scan Ch. 10–15
   contiguously; DROP *All the President's Men*; deprioritize *Shōgun* for
   3-1/3-2 (keep for 3-3/2-4). Applied to `results/scanning-checklist-2026-10-17.md`.
4. **Q4 — counting rule / extraction priority.** The booklets never fixed a
   counting rule — the extraction rule lived in the hotline clues. Both solved
   body-text precedents are word-level (Decipher I: first-letter-of-word,
   *Cosmos* Ch. 6, 1,252 words; 2-3: first-letter-of-word, *Tai-Pan* Ch. 5,
   2,420 words); only the ToC puzzle 2-2 was character-level. Test order for
   body scans: word-level first (3-1 last-letter/end-anchored per "End.",
   3-2/3-3/2-4 first-letter), then word-level variants (reversed, strides),
   character-level as fallback. A 5-page window (~1,400–1,750 words) covers
   every word-level N_max.

## Files

- `solver/toc_and_clue_tester.py` — Gemini's script, unmodified (embedded ToCs + scoring).
- `solver/run_full_ciphertexts.py` — driver that swaps in this repo's full `data/ciphers.json`.
- Run: `uv run solver/run_full_ciphertexts.py --top 25` from the repo root.
