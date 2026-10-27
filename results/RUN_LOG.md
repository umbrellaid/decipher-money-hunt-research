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

## 2026-10-18 morning — Q&A round 2 (Q5–Q8) + body scanner tooling

Four more Gemini follow-ups (Argon High; full texts in the working copies
`gemini-q5-answer.md` … `gemini-q8-answer.md`; summaries and verification
outcomes in `results/gemini-toc-test-2026-10-17.md`, "Follow-up Q&A, round 2").
No sweep runs; tooling + verified-data artifacts instead.

- **New tool `solver/body_scan.py`** — the scanning entry point: word-level-first
  stream tiers (Tier 1 first/last-letter incl. reversed word order; Tier 2
  strides + 2-1-style halfway patterns; Tier 3 character fallback), contiguous
  chapter windows (`--window`, default 6 = the Ch. 10–15 advice), zero-Z
  flagging for 3-1 (`--strict` skips decode runs on failing windows), `--skip`
  word-offset variants (Decipher I skipped the first 36 words of Cosmos Ch. 6 —
  paper p. 279 Fig. 8, per repo `docs/decipher-i.md`), and the S100 probe
  printed under every 2-4 hit. Smoke-tested on a synthetic 7-chapter fixture
  (693 streams, 27 windows).
- **`generate_body_text_streams` reordered word-level-first** in
  `solver/toc_and_clue_tester.py`; existing stream IDs untouched; added
  Split|Rev variants, reversed-word-order streams, and 2nd/10th-word strides.
  Regression-checked: `run_full_ciphertexts.py --top 3` self-test unchanged
  (484-letter key, fit 0.741, INMEMORYOFJOHNLENNON…); `zero_z_prefilter.py
  --scan-dir texts/pd` still flags 31/49.
- **Q5 epistemic correction:** Gemini's Q4 "Cosmos word-level" quote was a
  stitched reconstruction — but the substance is confirmed by the repo's own
  2026-10-10 scan notes (p. 279, Fig. 8 spec + the skip-36-words detail).
- **Q6:** 2-1's extraction formula is undocumented; the Statesman Journal
  JPEGs in Karen's Drive are the only unchecked primary source. Halfway
  streams implemented. 2-3's round numbers confirmed genuine homophones
  ("I AM BLIND") ⇒ 2-4's 100s run treated as real plaintext under H1.
- **Q7 microstructure audit:** every claimed 2-4 anomaly VALUE verified in
  `data/ciphers.json`; every POSITION was off (Gemini used a 154-token
  transcription; repo has 170). Corrected, repo-verified table committed as
  `results/puzzle-2-4-microstructure-2026-10-18.md`. 2-4 candidate ranking:
  Thorn Birds / Garp / Rabbit Is Rich / Walking Drum / Bourne.
- **Q8:** Union Club 30-title ToC matches the embedded ToC exactly; "Gift" =
  originally "Decipher Deception" (Gallery 1981, unverified) — a literal
  cipher-puzzle story at the clued position 10.
- Checklist updated (`results/scanning-checklist-2026-10-17.md` §D tooling
  note + new §E 2-4 plan with candidate table and ciphertext variants).

## 2026-10-18 late morning — Statesman Journal scans transcribed (2-1 mechanism: negative)

Pulled both crops of the 1986-03-25 *Statesman Journal* 2-1 winner article from
Karen's public Drive folder "Decipher II Articles"
(`1Hiet0dmMbgpqmo2j2FaNBc_-yUGwUijV`) and transcribed them in full:
`results/statesman-journal-1986-03-25-transcription.md`.

- **Negative headline:** the article documents NOTHING about the 2-1 extraction
  mechanism (no "S.I.N.", no "halfway" rule, no counting detail). The 2-1
  formula is now confirmed undocumented in every known public source; the
  halfway stream family in `body_scan.py` remains hypothesis-driven
  (N_max 980 = 2×490), not source-driven.
- Confirmed: winner **Eileen** Novak (not "Barbara"); four winners at $6,250
  ($250 cash + $6,000 check in a 400-lb ice dollar-sign); bought Aug 1985,
  solved Valentine's Day 1986; $75,000/3 messages remaining; Decipher II had a
  clue hotline; son's winning heuristic was "pick the least logical author"
  (she was on a Steinbeck lead; true author Swift) — consistent with Holland's
  "the obvious reading is usually wrong" design statement (paper p. 280).
- `docs/decipher-ii.md` 2-1 bullet updated with the transcription pointer.

## 2026-10-21 — Foundation body-text scan (3-1: ELIMINATED)

First physical book scan + OCR + cipher run. Isaac Asimov, *Foundation* (Del Rey,
July 1986, ISBN 0-345-33627-5). 329 CZUR Aura scans → Tesseract OCR → 9 chapter
text files → body_scan.py word-level-first pipeline.

**Targets:** Ch. 10 (global) = Part III section 2, page 109 (4,310 words);
Final chapter = Part V section 6, page 275 (4,388 words).

**3-1 result:** Top score 1.658 (ch17 WordLast_Split, drift 0, Fwd) = vowel-heavy
gibberish (`EOEEDEEYDKHFDLGTUUTSTEEESDDY...`). Known letter-density artifact —
NOT readable plaintext. No Tier 1/2/3 stream produced English.

**Other ciphers:** 2-4, 3-2, 3-3 also tested — no matches.

**Verdict: Foundation ELIMINATED as cipher 3-1 candidate.**

**Bug found and fixed:** `ocr_ingest.py` line grouping included `top` pixel value,
causing word-order scrambling. Fixed by removing `top` from grouping key.

Full findings: `results/foundation_scan_findings_2026-10-21.md`
Scan log: `results/scan_log.md`

## 2026-10-24 — The Thorn Birds body-text scan (2-4: INCONCLUSIVE)

Colleen McCullough, *The Thorn Birds* (Avon, ISBN 0-380-01817-9). Candidate for
Decipher II 2-4 (N_max=1053). Three scan attempts on the CZUR Aura:

**Attempt 1 (auto-crop ON):** 742 images. Auto-crop destroyed left margins on 89%
of pages — only 3 usable. 405 pages never captured. Total failure.

**Attempt 2 (no-processing spreads):** 367 two-page spread images. Visual quality
excellent but OCR confidence 64.7% (dark desk mat background + hand shadows).
Simple cut-in-half splitting failed.

**Attempt 2 + ScanTailor Advanced (GUI):** 734 clean single-page TIFs (split,
dewarped, dark bg removed). OCR confidence improved to 77.6% (306 pages ≥85%).
~195,000 words extracted (~97% of book). 63 blank pages rejected.

**2-4 result:** Top score 1.808 (WordLast_Joined, drift -2, Rev) = vowel-heavy
gibberish (`SBECEYEEEYTEERDNSTHATFNOEIENEYEEEED...`). All Tier 1/2/3 streams
produced letter-density artifacts. No English plaintext detected.

**3-1 result:** Also tested — no match. 3/6 windows flagged for zero-Z violation.

**Verdict: The Thorn Birds INCONCLUSIVE for 2-4.** Cannot be eliminated but no
positive signal. OCR quality (77.6% avg, 46% high-confidence) is borderline for
reliable first-letter-of-word extraction. Needs cleaner OCR or rescan.

**Bug found and fixed:** Custom `process_pipeline.py` TSV parser leaked Tesseract
coordinate data into extracted text. Fixed with three-layer defense (field
validation, pre-filter for concatenation artifacts, post-processing regex).

**Pipeline established:** CZUR "no processing" → ScanTailor Advanced GUI →
Tesseract OCR → body_scan.py. Documented in `scanning/docs/scanning-workflow-czur-2026-10-18.md` §8.
Scan files: `scanning/book-scans/the-thorn-birds-scantailor/`.

## 2026-10-26 — I, Robot / Doctor Zhivago / Cat's Cradle body-text scan (three-book session)

David's second scanner session, three books in one mixed folder (separated during processing;
pipeline details in `results/scan_log.md` 2026-10-26 entry). All editions era-verified from
copyright-page scans (I Robot = Fawcett Crest ©1950/1968 → 1970 printing; Zhivago = **Signet
First Printing February 1960**; Cat's Cradle = Dell ISBN 0-440-11149-8, ©1963 plates).

New tooling this session: `solver/preprocess_spreads.py` (replaces ScanTailor — see workflow doc
§8), `solver/ingest_by_markers.py` (marker-chasing ingest; chapter files start at the first body
word), `ocr_ingest.py --strip-header`. Full outputs:
`results/body_scan_2026-10-26_3books_full.txt`.

### I, Robot (3-1: ELIMINATED)
11 chapter files (front matter + Introduction + 9 stories, each verified to open at its true
first line; "The Evitable Conflict" = ch10). **51/51 windows fail the 3-1 zero-Z necessary
condition** (every window contains Z within its first 516 chars/words — Asimov's prose is
Z-dense). No readable plaintext for 2-4, 3-2 or 3-3 either; all top hits are the known
WordLast vowel-density artifact. **I, Robot ELIMINATED as cipher 3-1 candidate** (Group B,
Asimov). Asimov's *Foundation's Edge* / *Union Club* / *Naked Sun* remain untested on paper.

### Doctor Zhivago (3-1: no match — not fully eliminated)
All 17 parts anchored (ch10 The Highway trimmed to its true opening; ch17 poems from HAMLET).
87/93 windows fail zero-Z; the 6 passing windows (incl. ch09/ch010-anchored) produced nothing.
No readable plaintext under any tested family for 3-1/3-2/3-3/2-4. Negative under the current
rule families — but OCR noise is heavier than Foundation's (Zhivago's inner margins are tight;
poems are italic), so this is recorded as **strong negative, not elimination**. If 3-x ever
narrows to Pasternak, re-scan the target parts with more care before closing it.

### Cat's Cradle (multi: no match)
49 anchored micro-chapter files + ch127 split by hand; the ch10-15 target window is contiguous
and zero-Z-clean at its anchors. 241/261 windows zero-Z flagged, 20 pass — including the
ch009/ch010/ch013-anchored target windows — none decode. No readable plaintext for any cipher.
**Negative for 2-4 / 3-1 / 3-2 / 3-3** under tested families. Vonnegut stays open only in the
untested titles (Slaughterhouse-Five etc. — not on the scan list).

### Foundation caveat
The 2026-10-21 Foundation texts contain TSV artifacts + unstripped running heads; both bugs are
now fixed in the pipeline. Recommend re-ingesting the Foundation pages before treating its 3-1
elimination as airtight (scan_log 2026-10-26).

**Scan log:** `results/scan_log.md` 2026-10-26 entry. **Verdicts:** I Robot OUT for 3-1;
Zhivago strong-negative; Cat's Cradle negative. The 3-1 Group-B pool is now down to Heller /
Vonnegut / Ludlum / Capote / Uris / Pasternak(care) / Halberstam / Ono + the in-copyright A/C
authors.

## 2026-10-27 — Foundation + Thorn Birds re-ingest through the fixed pipeline

Both older scan sets re-processed with the 10-26 tooling (no new scans). Details in
`results/scan_log.md` 2026-10-27 entry; full solver output in
`results/body_scan_2026-10-27_reingest_full.txt`.

- **Foundation (Del Rey 1986): 3-1 ELIMINATION CONFIRMED on clean text.** 28 section
  anchors (old map merged 70 pages into ch12), running heads stripped, both cipher-target
  chapters verified at true openings. No readable plaintext under any family; 111/153
  windows fail the 3-1 zero-Z condition. The 10-26 caveat is closed.
- **The Thorn Birds (Avon): 2-4 NEGATIVE (was: INCONCLUSIVE).** 7 parts, 11 duplicate
  reshoots removed, 13 unique single-page fills kept. No readable plaintext for 2-4/3-1/3-2/3-3.
  Caveat: mean OCR conf 77 (128 pages < 70, clustered in Parts Two and Six) — rescan list
  delivered (`scanning/book-scans/the-thorn-birds/RESCAN_LIST_2026-10-27.md`). McCullough
  stays on the 2-4 board but below Thorn-Birds-first-printing-verified alternatives.

### 2026-10-27 addendum — Thorn Birds OCR quality indicator (IA diff)
Diffed our Avon scan's text against the Internet Archive's plain text of the 1977 Harper
first edition (reference only; different edition, itself OCR — combined-error floor).
Sampled word-level match: **0.77 overall; Part Two 0.60, Part Six 0.74** — independently
corroborating the QA confidence clusters. Implication recorded in the rescan list: a real
2-4 keytext inside Parts Two/Six would be nearly invisible at this noise level.

## 2026-10-27 (later) — Thorn Birds rescan: quality jump, still negative

Full-book rescan per the checklist (lighting/hands/slower). Diff vs IA reference:
overall 0.772→0.844; Part Two 0.596→0.867; conf mean 77.2→84.0; low-conf pages
128→27; word recovery +49k. body_scan on the clean text: **no readable plaintext for
2-4 or any other cipher — Thorn Birds downgraded to NEGATIVE with only a mid-book
(Parts 5-6, 0.77) caveat.** Full numbers in scan_log 2026-10-27 rescan entry.
