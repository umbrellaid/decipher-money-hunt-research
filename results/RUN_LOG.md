# Run log — every sweep ever run against the open ciphers

Calibration for all rows: genuine English ≈ **−7.9…−8.0** per trigram; noise ≤ **−8.6**.
For the secondary `win` (best-window) column the noise floor is ≈ **−8.1**.
A candidate is only interesting above −8.2 (`score`) with a readable decode.

## Campaign 1 — 2026-10-04 (5 rule families)

| Cipher | Corpus | Positions tested | Best score | Verdict |
|---|---|---|---|---|
| 3-1 | Poe complete works, 2 passes | ~5M | −8.84 | Poe eliminated |
| 2-4 | 31 PD texts (Hawthorne, Hardy, EBB, Verne, Whitman, Thoreau) | ~5M | −8.87 | 6 PD authors eliminated |
| 3-2 / 3-3 | 18 PD texts (Faulkner, Christie ×10, Sandburg, O'Neill ×5, cummings) | ~5M | −8.60 / −8.70 | PD side eliminated |
| all three | 35 chapter-title chains (the Catch-22 rule) | — | −9.00 | chain family eliminated |

Logs: `sweep_logs/sweep_pd_log.txt`; tops in `sweep_*_pd.json`, `sweep_*_chains.json`,
`sweep_31_poe.json`.

## Campaign 2 — 2026-10-05 (21 rule families)

Rule families: the base five (`letters`, `first-letters`, `last-letters`, `line-first`,
`line-last`) plus `everyN-letter`, `everyN-wordfirst`, `everyN-wordlast` for N ∈ {2,3,5,10},
`word2th-letter`, `word3th-letter`, `sentence-first`, `paragraph-first`; every numbering
start; streams forward and reversed; plaintext scored both directions.

| Cipher | Corpus | Wall time | Best `score` | Best `win` | Verdict |
|---|---|---|---|---|---|
| 2-4 | 31 PD texts | (part of 1452 s) | −8.7683 `hawthorne_512:every3-wordlast` | −8.2267 `verne_83:every2-wordlast` | no hit |
| 3-1 | Poe, 9 texts | 279 s | −8.8389 `pg2150/25525:last-letters` | −8.4668 | Poe eliminated under 21 families |
| 3-2 | 21 PD texts | (part of 1452 s) | −8.5379 `christie_69087:every2-wordlast` | −8.1082 `faulkner_75170:every2-wordlast` | no hit |
| 3-3 | 21 PD texts | (part of 1452 s) | −8.6957 `christie_61168:last-letters` | −8.1450 `faulkner_se_asilaydying:last-letters` | no hit |

Every top-10 decode in `sweep_logs/sweep3_log.txt` is vowel-heavy gibberish
(e.g. `FFTEDESTDYSMAFISEESSDENYTFDENDSEAELSNEDOFTEFEEEE`); the few `win` values near
−8.1 come from `*-wordlast` streams, which are letter-density artifacts, not English.
Tops in `sweep3_24.json`, `sweep3_31.json`, `sweep3_32.json`, `sweep3_33.json`.

**Conclusion:** the public-domain eliminations of 2026-10-04 survive a 4× wider rule
set. The remaining suspects for every open cipher are in-copyright authors
(`data/author_lists.json`), and the way forward is `docs/check-your-own-book.md`.

## Validation

`solver/validate.py`, 98 checks (`sweep_logs/validate_out.txt`):

- 4 checks on the Decipher III rulebook's worked example (Cosmos ch. 6 passage,
  three ciphers → CODES);
- 2 checks on puzzle 2-2: the *Catch-22* chapter-title chain is long enough, and
  the reversed chain, with the decode read backwards, is the Lennon message;
- 5 checks recording the "The Source" (Michener) elimination for 2-4: 17 chapter
  titles, and a 258-letter chain that is arithmetically too short for 2-4, 3-1,
  3-2 and 3-3 (added 2026-10-10);
- 84 encode→search→decode round trips, 21 rule families × four direction
  combinations, each requiring the true numbering start to rank #1;
- 3 null-tolerance checks: windowed scoring recovers clustered nulls, windowed
  scoring rejects uniform noise, and scattered nulls are not recoverable by any
  implemented statistic.

An earlier log recorded trimmed-mean checks as passing. That statistic was removed
on 2026-10-05 because pure noise scored inside the English band. The log file
matches the current script.

## Rejected ideas (recorded so they are not retried blindly)

- **Trimmed-mean trigram scoring** for null tolerance: pure noise scores ≈ −7.3 under
  it, inside the English band. Removed 2026-10-05.
- **archive.org controlled digital lending** as a text source: loans never expose
  `_djvu.txt` (401 even mid-loan). Tested 2026-10-04 with a logged-in account.
- **DRM ebook purchases**: every legitimate edition of the priority titles is Adobe
  DRM; buying them yields no machine-usable text.

## 2026-10-10 — source mining, no new sweeps

No solver runs today; `validate.py` re-run only to confirm the tree is unchanged
(98/98 PASS, including five new checks that pin the *The Source* elimination).
Archival work instead:

- Read the full Baldwin & Sherman *Cryptologia* 14(3) paper from the free UMBC scan.
  Footnote 7 (journal p. 278) is the "public domain" referee note; p. 278–281 give
  the contest timeline (36 winners × $3,251.71, >1,000 entries, ~250,000 hotline
  calls, Michener on the Decipher I author list) and the July 6, 1989 Holland phone
  call in which Holland **denies** the Holland-surname/Cosmos-chapter-6 connection
  ("simply coincidences"). Extracted into `docs/decipher-i.md`.
- Extracted all 13 pages of Karen's Scribd "Decipher II and III Puzzles" guide,
  which led to her public Drive archive "Decipher Puzzles". The winner-article
  scans there rebuilt the Decipher II timeline and prizes (2-1 split 4 ways,
  Feb 1986; 2-2 Sept 1986; 2-3 vault Oct 31 1986, Brown sole winner) and supplied
  the surviving hotline clues for 2-1, 2-2 ("The first is the last") and 2-3.
  The Milwaukee Sentinel Sharlet Brown article that @Mintpuppy17 was hunting on
  microfilm is in that archive. All recorded in `docs/decipher-ii.md` and
  `docs/sources.md`.
- **"The Source" (Michener) 2-4 theory eliminated**: 17 chapter titles → 258-letter
  chain via `solver/rules.py chapter_title_chain`, vs. 2-4 max index 1053; Michener
  is not on the printed 2-4 author list; and the winner-photo book was checked
  against the partial 2-3 solution by Karen with no match (a prop).
- The five Decipher III newspaper clippings in Karen's archive contain **no monthly
  clue columns** — ads only. The clue-column hunt moves to subscription archives.

## Campaign 3 — 2026-10-17 (Gemini-suggested ToC + clue hypotheses)

External analysis from a Google Gemini thread read against this repo (full provenance
and corrections in `results/gemini-toc-test-2026-10-17.md`). Tester:
`solver/toc_and_clue_tester.py` with the full-ciphertext driver
`solver/run_full_ciphertexts.py` (the Gemini original embedded truncated ciphertext
prefixes; the driver substitutes this repo's complete `data/ciphers.json`).

| Cipher | Key streams tested | Best result | Verdict |
|---|---|---|---|
| 2-4 | 9 ToCs × ~536 streams × 5 drift × 2 dirs (+ no-100s null variant) | gibberish | no ToC key |
| 3-1 | same, incl. repeat-487 double-letter bonus | gibberish | no ToC key |
| 3-2 | same | gibberish | no ToC key |
| 3-3 | same | gibberish | no ToC key |
| 2-2 control | Catch-22 chain, reversed | decodes (`IYMEMOJY...LENNON...`) | pipeline works; key list is 487 vs documented 478 letters *(superseded — reconciled to 484, see evening entry below)* |

Corrections established while verifying: N_max is 1053 / 516 / 416 / 721 for
2-4 / 3-1 / 3-2 / 3-3 (Gemini's truncated sets implied 1050 / 513 / 415 / 721).
Full-ciphertext cribs: 3-1 = E,E,E,Z,E,E; 3-2 = E,Y,E,Y,E (repeating).

Conclusion: ToC-only keys eliminated for the 9 embedded candidate books; body-text
scanning per `docs/check-your-own-book.md` remains the path, with Chapter 10 /
final-chapter priority per the 3-1 clues ("10" / "End.").

## 2026-10-17 evening — zero-Z crib pre-filter (from Gemini follow-up Q&A)

New tool `solver/zero_z_prefilter.py`: the 3-1 literal Z cribs (E,E,E,Z,E,E) imply the
keytext window holds no Z, so any scanned chapter with Z inside the first 516 chars or
first 516 words is eliminated for 3-1 without a decode run. Demo on the existing corpus:
31/49 PD texts and 8/9 Poe texts flagged — directionally consistent with the earlier
PD/Poe eliminations. Ready for first real chapter scans: point `--scan-dir` at a folder
of OCR'd `.txt` files. Full Q&A documentation lands with the evening commit.

## 2026-10-17 evening (cont.) — follow-up Q&A round, 484-letter key reconciled

Four follow-up Q&As with the same Gemini thread (Q4 on the Argon High model; Q1–Q3
under a Flash-Lite fallback). Full texts: working copies `gemini-q1-answer.md` …
`gemini-q4-answer.md`; summaries in `results/gemini-toc-test-2026-10-17.md`
("Follow-up Q&A"). No new sweep runs; strategy changes only.

- **Catch-22 control key reconciled at 484 letters** (was: "487 vs documented
  478"). Max codenumber 477 = final N of "The Texan"; letters AXETEHT at
  reversed-key positions 478–484 unused; the fix was "Piltchard & Wren" (printed
  title, & stripped) in place of "Piltchard and Wren". Self-test now decodes
  exactly `INMEMORYOFJOHNLENNONNOBODYTOLDMETHEREDBEDAYSLIKETHESE`
  (Control Bigram Fit 0.741, 100% coverage). Stale NOTEs in
  `solver/run_full_ciphertexts.py` and the Campaign-3 row above corrected.
- **Extraction-family priority flipped to word-level first** (Q4): both solved
  body-text precedents (Decipher I / 2-3) were first-letter-of-word keys
  (1 codenumber = 1 word); only ToC puzzle 2-2 was character-level. Body scans
  now test word-level families before character-level, per-cipher order in
  `results/scanning-checklist-2026-10-17.md` §D. (Gemini's hotline-clue
  quotations unverified against primary sources.)
- **Scan-list corrections applied** (Q3, unverified): Foundation Ch. 10 = Part
  III "The Mayors" ch. 2 (continuous numbering 1–19); Zhivago gains Part 17
  (poems); Cat's Cradle / Union Club Ch. 10 too short alone ⇒ scan Ch. 10–15
  contiguously; All the President's Men DROPPED; Shōgun deprioritized for
  3-1/3-2, kept for 3-3/2-4. Checklist copied to
  `results/scanning-checklist-2026-10-17.md`.
- Solver re-verified after the comment edits:
  `uv run solver/run_full_ciphertexts.py --top 3` — self-test line and 0.741
  fit unchanged.
