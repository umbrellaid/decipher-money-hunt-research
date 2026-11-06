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

## 2026-10-27 (final) — IA pre-screen of 5 unrestricted reference texts: no hits

Ran the full cipher scan over the five unrestricted IA novel texts (Capote *In Cold Blood*,
Uris *Exodus* + *Trinity*, Plath *The Bell Jar*, Follett *Pillars of the Earth*), split into
section files by heading detection (running-head title changes, chapter lines, date headers,
4k-word fallback chunks). **No readable plaintext for 2-4/3-1/3-2/3-3 in any of them**; all
top scores are in the noise band (0.70-0.75, character-level). Results:
`results/ia_prescreen_2026-10-27.txt`.

**Standing interpretation rule for these pre-screens:** a POSITIVE would have been an
immediate escalation signal (buy era-correct copy, scan, confirm); a NEGATIVE carries ZERO
elimination weight — different edition, IA OCR noise, and approximate section anchoring
would all mask a real key. These five authors remain untested at elimination grade. The
texts' ongoing value is QA comparison against David's own scans.

## 2026-10-30 — Ebook pre-screen of 7 new-release titles: no hits, density gauge clean

David-supplied plain-text ebooks (OceanofPDF-style dumps, edition unknown), split per
`texts/ia-prescreen-2026-10-30/split_batch.py` and scanned with `body_scan.py` (full
outputs: `results/ia_prescreen_2026-10-30_*.txt`):

- Vonnegut *Slaughterhouse-Five* (10 ch), Heller *Something Happened* (9 ch),
  Irving *The World According to Garp* (19 ch), L'Amour *The Walking Drum* (57 ch),
  Updike *The Witches of Eastwick* (3 ch) — real chapter anchors chased.
- Clavell *Shogun* and Ludlum *The Bourne Identity* — body text has NO headings at all
  (chapter numbers exist only in the ToC); split into 25 equal ~4k-word chunks like the
  10-27 ICB precedent.

**Result: no readable plaintext for 2-4 / 2-4-No100s / 3-1 / 3-2 / 3-3 in any of the 7
books.** Every max score sits on a WordLast/Stride stream (1.3-2.3) with vowel-salad
previews — the known word-ending letter-density artifact; no WordFirst (solved-family)
stream entered the Tier-1 top 10 in any book×cipher combo. Lexicon scan over all 150
reported rows per book found zero English-like previews.

**Density gauge (David's Asimov question):** WordLast artifact ceilings here
(1.5-2.3) are identical in kind and size to Capote 1.71-1.95 (10-29 ICB scan), Orwell
2.31, Galápagos 2.22 and Foundation's Edge 2.08 (10-29) — i.e. the artifact is a
property of ordinary English prose under this scorer, NOT an Asimov signature. Prose
stats (60k-word sample; avg word len / avg sentence len / TTR): Foundation 4.10/11.9/0.19;
batch range 4.21-4.52 / 9.9-18.2 / 0.12-0.17. Nothing in the batch is an outlier;
Witches is 45% dialogue (least dense of anything scanned so far), Bourne/Shogun are
short-sentence action prose. Conclusion: none of the seven writes "too dense" for the
letter-stream families by any measure we can calibrate.

Same standing rule as 10-27: NEGATIVE = zero elimination weight (unknown edition,
ebook front-matter junk, approximate anchoring for the two chunked books). No purchase
signal generated by this screen.

## 2026-10-30 (round two) — 19-title ebook pre-screen: no hits

Second batch of David-supplied plain-text ebooks (`texts/ia-prescreen-2026-10-30-r2/`,
splitter `split_batch_r2.py`, outputs `results/ia_prescreen_r2_*.txt`). One file was
EXCLUDED: `Norman Mailer: A Double Life` is a Mailer *biography* (Michael Lennon), not a
Mailer text — no keytext property. Mailer still needs *The Executioner's Song* or
*The Naked and the Dead* (1948 — check PD status for a free sweep).

Coverage and anchoring per book:
- Real chapter anchors chased: Roots (120 CHAPTER files), Look Homeward Angel (40,
  "Chapter1" no-space), Godfather (32), Gorky Park (17, word numbers), Best and
  Brightest attempted (chase hit ToC; body chunked 25x13.6k), Cancer Ward (21, "N. Title"
  after fixing a "13...." no-space pattern miss; first chase had swallowed the Part-Two
  ToC), White House Years (27 roman-numeral + title), Naked Sun (18), Affluent Society
  (24, "N. Title"), Thorn Birds (19 standalone numbers; gap rule fixed to 150 after ch15
  missed at 200).
- Headingless body -> 25 equal chunks: All the President's Men, Best and the Brightest
  (modern reprint: McCain foreword + reading-guide junk stripped; body = lines
  147-4705), Blackford Oakes omnibus, Look Homeward Angel, Hotel New Hampshire, Rabbit
  Run (numbers stop at ch3), Osterman Weekend, The Right Stuff ("N - Title" heads use a
  non-ASCII dash), Anderson Tapes (chase found only 4), RN (30 chunks), Grapefruit
  (4 chunks, 363 words each — whole book ~1,500 words).

**Result: no readable plaintext for 2-4 / 2-4_No100s / 3-1 / 3-2 / 3-3 in any of the 19
books.** All 3,610 scored rows pass a common-word lexicon scan with zero hits; every
per-puzzle max is a WordLast/Stride artifact (1.3-2.4) with vowel-salad previews, same
as every prose baseline to date. Notable: Thorn Birds ebook (clean digital text) is
negative for 2-4, matching the 10-27 CZUR-scan negative — the OCR-noise caveat on
McCullough can be downgraded; the earlier "mid-book Parts 5-6" worry is now covered by
clean text. Rabbit Run (2-4's "$5 experiment" lead) is negative under ebook-grade
anchoring.

Same standing rule: NEGATIVE = zero elimination weight (unknown editions, chunked
anchoring for 9 of 19). Authors now screened at text grade: Group B 3-1 down to Nixon /
Woodward / Ono / Halberstam only (Heller, Vonnegut, Ludlum, Capote, Uris, Pasternak,
Asimov, Poe all tested). Groups A/C for 3-2/3-3 now text-screened: Orwell, Clavell,
Follett, Plath + (today) Wolfe, Sanders, Buckley, Galbraith, Solzhenitsyn, Kissinger,
Haley, Puzo, Cruz Smith; PD sweeps done: Faulkner, Christie(pre-1931), Sandburg,
O'Neill, cummings + Thomas Wolfe's Look Homeward Angel via ebook text. Remaining
untested: Mailer, Cosby (scarce), plus non-list long-shots.

## 2026-10-30 (round two addendum) — Mailer: Naked and the Dead screened, negative

Sourced from IA `nakeddead0000unse` (Holt, Rinehart & Winston — true first-edition
text; item is *not* access-restricted, djvu OCR grade, 272k words). Split part-aware
("Part One..Fifteen" resets the chapter chase; 19 files — some later-part chapter heads
OCR-garbled and merged, full text still covered). body_scan over all five ciphers:
**no readable plaintext; every max is a WordLast artifact (1.5-2.2), lexicon scan clean.**
Text: `texts/ia-prescreen-2026-10-30-r2/Naked_and_the_Dead_-_Norman_Mailer.txt`,
output `results/ia_prescreen_r2_naked-dead.txt`.

*The Executioner's Song* is NOT openly available (all 7 IA copies access-restricted,
401 on the text file) — it needs David's ebook-source route if we want it screened.
Correction to the earlier note: *The Naked and the Dead* (1948) is NOT public domain
(95-year term -> 2044); it was screened here as an IA OCR prescreen, same grade as the
other IA texts. With Mailer covered at this grade, every name on the printed Group A/B/C
author lists has now been text-screened at least once except Cosby (texts scarce).

## 2026-10-30 (round two addendum 2) — Executioner's Song screened, negative; ebook files organized

David supplied the plain text of *The Executioner's Song* (Mailer 1979). Split part-aware
(Book/Part/Chapter hierarchy; 44 chapter files; ch01 head verified at "THE FIRST WEEK").
body_scan over all five ciphers: **no readable plaintext; maxes 1.6-2.0 WordLast artifacts,
lexicon scan clean.** Output `results/ia_prescreen_r2_executioners-song.txt`.

Both Mailer keytexts now screened at text grade. Ebook/IA source texts relocated to
`private/ebooks/{round1-decipher-candidates,round2-decipher-candidates,internet-archive}/`
(Downloads/text_ebooks* consolidated and removed; the 934MB colleenmccullough IA item moved
to `private/ia-archives/mccullough-ia-item/` — deletion not done, David to decide).
Working copies remain in the repo's gitignored `texts/` folders for the solver pipeline.

## 2026-10-31 — 'group B / 10 / End' anchor sweep on the 35 private ebooks: all negative

New tool `solver/anchor_sweep.py`: anchors the book-cipher numbering origin at the
structural points implied by the Decipher III initial clue ("The author you seek to
find the key is from the group that's labeled B. / 10 / End") — ch10 slice,
part2-ch10, epilogue/afterword ("End"), tenth sentence from book end, chapter-(N-10)
to end — with +-30 window for OCR slop, engine from-end direction covering
backward-from-anchor reading, and five streams per slice (letters; word-first and
word-last letters under split and merge tokenization). All four open ciphers
(2-4, 3-1, 3-2, 3-3), 827,422 scored decodes across 35 books.

**Result: no decode approaches English — global max -8.7294 (Hotel New Hampshire
epilogue, wl-split, 3-2); genuine-English band is -7.9..-8.0 and the look threshold
is -8.2.** Coverage caveats: several books expose only sent10end (Slaughterhouse-Five
has no chapter heads; Naked Sun / Capote / Plath / Updike / Mailer-biography OCR did
not yield parseable chapter 10); White House Years yielded no anchor. Group B's Poe
and Pasternak have no text in the corpus, so they remain unscreened at anchor grade.
Residual interpretations of '10 / End' not covered here: hotline-message numbering
(clue recordings lost) and print-edition-only anchors (OCR edition differences).
Output `results/anchor_sweep_2026-10-31.txt`.

## 2026-10-31 (later) — full sliding-origin sweep of the 4 era-verified physical scans: all negative

**Correction to the anchor-sweep entry above and to
`money-hunt-work/llm-handoff-cipher-next-steps.md`:** the claim that "Group B's Poe
and Pasternak have no text in the corpus" is wrong. Poe is at `texts/poe/` (9 whole
works) and Pasternak at `texts/doctor-zhivago/` (17 parts + front matter, Signet
First Printing Feb 1960, era-verified from the copyright-page scan). Neither is an
open acquisition.

**Why anchor_sweep was NOT extended to them:** `engine.last_letters()` is
last-letter-of-each-word, i.e. identical to anchor_sweep's `wl-split` stream, and
`first_letters()` is `wf-split`. Poe was already swept in campaigns 1-2 under all 21
rule families with the numbering origin slid across the whole book (~5M positions,
best -8.84). A fixed structural anchor is a strict *subset* of a sliding origin, so
an anchor run over `texts/poe` or `texts/pd` adds no coverage. The real gap was the
reverse one.

**The actual gap:** `body_scan.py` tests contiguous windows of <=6 chapters;
`sweep.py` slides the origin across the entire book. The five CZUR scans had only
ever been through `body_scan.py`, because `sweep.py` needs whole-book text and the
scans are stored one file per chapter. New tool `solver/build_whole_books.py`
concatenates `texts/<book>/ch*.txt` in natural-sort (reading) order into
`texts/wholebooks/`, then `normalize_text.py --chapters` makes them sweep-ready and
enables the chapter-title-chain rule.

**Gap detection is load-bearing:** `cats-cradle` was excluded as NOT SWEEP-ABLE -
only 46 of 127 micro-chapters were scanned (the targeted ch10-15 window), so
whole-book word numbering would be invalid past the first gap. Sweeping it would
have produced a meaningless negative. `foundation_new`, `foundation_v1_2026-10-21`
and `the-thorn-birds-old-2026-10-24` were skipped as superseded.

| Book (words) | 3-1 | 2-4 | 3-2 | 3-3 |
|---|---|---|---|---|
| doctor-zhivago (210,857) | -8.9155 | -8.7425 | **-8.5048** | -8.7935 |
| foundation2 (79,303) | -9.0193 | -8.9522 | -8.6936 | -8.8716 |
| i-robot (71,590) | -9.0252 | -8.9094 | -8.6663 | -8.7983 |
| the-thorn-birds (250,331) | -8.8842 | -8.5396 | -8.5141 | -8.5145 |

**Result: no readable plaintext in any of the 16 book x cipher combinations.**
Global best `score` is -8.5048 (Zhivago / 3-2 / last-letters / start 48736
from-end rev); the look threshold is -8.2 and genuine English is -7.9..-8.0. Every
preview is vowel-salad. The four highest `win` values (-8.0667 i-robot 3-2,
-8.2015 Thorn Birds 2-4, -8.2463 foundation2 2-4, -8.2482 Thorn Birds 3-3) sit at
the documented ~-8.1 `win` noise floor and are all on the `*-wordlast` /
`last-letters` families that campaign 2 already identified as letter-density
artifacts, not English. `foundation2.chapters.json` yields a 35-letter title chain -
far too short for any cipher (min max-index 416), so no chain test was meaningful.

**Grade of these negatives.** Stronger than anything previously recorded for these
four texts (full sliding origin x 21 families x 4 direction combos, on era-verified
editions, vs. windowed body_scan only). But still not hard eliminations: OCR noise
persists (Zhivago's inner margins are tight and its poems italic - the reason
RUN_LOG grades it "strong negative" rather than "eliminated"), and the standing rule
applies that a miss on a printing that is not the one Decipher used proves nothing.
Foundation and I, Robot were already hard-eliminated for 3-1 independently, by the
zero-Z necessary condition (51/51 and 111/153 windows fail); this run adds coverage
for 2-4/3-2/3-3 on those two.

Runtime ~572 s for all 16 combinations. Output `results/wholebook_sweep_2026-10-31.txt`.

## 2026-11-03 — Eckman's 2-1 reconstruction verified independently: PASS, plus a third witness at 491 letters

**Not a sweep — a verification.** Christopher A. Eckman published a technical
reconstruction of Decipher II Message 1 on 2026-10-31
([doi:10.5281/zenodo.23844582](https://doi.org/10.5281/zenodo.23844582)) and opened
issue #1 / PR #2 on this repository; the PR was merged as `33d5517`. 2-1's mechanism
is therefore no longer undocumented, which retires the 2026-10-18 negative above it.

`solver/verify_ii1.py` reimplements the construction from the paper's §3.1
specification and compares against the paper's published SHA-256 values. **No
third-party code was imported or executed** — a match is two independent
implementations agreeing. **19/19 checks pass.** Full write-up:
`results/eckman-ii1-verification-2026-11-03.md`.

Two results matter beyond confirming his work:

1. **Our 2-1 ciphertext transcription is corroborated — corrected wording, see below.**
   The canonical fingerprint of our *pre-correction* sequence (observation 306 reverted
   from our `388` to the `338` recorded in Kavett's compilation) reproduces his published
   input hash `1e60d5d6…` exactly. Ours was read from the printed surface at 3× on
   2026-10-05; his came via Karen Kavett's public compilation. As records they stand, the
   two agree on **313 of 314** observations. `docs/methodology.md` gap 2 (OCR/typing
   error) is therefore **substantially reduced for 2-1, not closed**, and remains fully
   open for the four unsolved ciphers, which have no second reading of any kind.
2. **A third textual witness exists, and it is the default free e-text.** The paper
   compares Alden 1911 (492 normalized letters) against a Wikisource/1801 transcription
   (490). Project Gutenberg #829 gives **491**, differing from Alden at two independent
   places: `take my measure` → `take measure` (−2) at **Alden positions 94–95
   (one-based)**, and `with rule and compasses` → `with a rule and compasses` (+1) at
   **Gutenberg position 232 (zero-based)** = Alden 234/235. Those two positions use
   different bases; an earlier version of this entry quoted "94" and "232" side by side
   as if comparable. The first *differing* letter is at position **95**, so most of the
   forward half misaligns. Reproduce with `uv run solver/check_ii1_witness.py` (exits 1:
   the witness fails the 492 clue). This is a harder demonstration of gap 1 than the
   paper's own comparison, because it lands on the e-text anyone would reach for first.

One figure we published is corrected here: **152** of 314 observations exceed 492 in the
*original* transcription; under the working corrections observation 169 becomes `830` and
crosses the halfway point, giving **153**. Both are now asserted in `verify_ii1.py`.
Neither figure changes the gap-3 false-negative conclusion.

**Grade.** The 2-1 reconstruction is confirmed and can be relied on downstream, with one
stated condition: the complete 314-character decode is conditional on the `330→830`
reading at observation 169, which the author grades *probable* rather than verified (his
supporting readings were candidate-aware, not blind). Our decode reproduces his published
plaintext hash, so it inherits that conditionality. The designer's physical edition and
his procedure for choosing among eligible numerical positions remain unestablished.

No decoded plaintext is stored anywhere in this repository; `verify_ii1.py` reports its
length and SHA-256 only.

## 2026-11-03 (later) — anchored palindromic re-sweep of the 4 era-verified scans: all negative

**Purpose.** Every negative recorded above for 2-4, 3-1, 3-2 and 3-3 was produced by the
21-family sliding sweep, which contains no `S || reverse(S)` construction — the one
Holland is now *known* to have used on 2-1. This re-earns those negatives for the new
family. Run: `solver/sweep.py` over the same four `texts/wholebooks/*.clean.txt` files as
the 2026-10-31 campaign, `--cipher all`, output
`results/palindromic_sweep_2026-11-03.txt`.

**Result: no readable plaintext in any of the 16 book × cipher combinations.**
**197,924,977 anchored (start, length) pairs** were searched and **zero** candidates
cleared the −8.2 mean threshold. No search space was empty — `sweep.py` reports the pair
count per family and warns when it is zero, and it never fired.

| Book | Cipher | Anchored pairs | Best mean | 2026-10-31 baseline | Δ |
|---|---|---:|---:|---:|---:|
| doctor-zhivago | 2-4 | 19.13 M | −8.7425 | −8.7425 | **+0.0000** |
| doctor-zhivago | 3-1 | 9.39 M | −8.8585 | −8.9155 | +0.0570 |
| doctor-zhivago | 3-2 | 7.57 M | −8.5048 | −8.5048 | **+0.0000** |
| doctor-zhivago | 3-3 | 13.10 M | −8.6955 | −8.7935 | +0.0980 |
| foundation2 | 2-4 | 12.42 M | −8.7341 | −8.9522 | +0.2181 |
| foundation2 | 3-1 | 6.11 M | −8.8937 | −9.0193 | +0.1256 |
| foundation2 | 3-2 | 4.93 M | −8.4293 | −8.6936 | +0.2643 |
| foundation2 | 3-3 | 8.52 M | −8.8632 | −8.8716 | +0.0084 |
| i-robot | 2-4 | 9.28 M | −8.8505 | −8.9094 | +0.0589 |
| i-robot | 3-1 | 4.57 M | −8.8424 | −9.0252 | +0.1828 |
| i-robot | 3-2 | 3.68 M | −8.5275 | −8.6663 | +0.1388 |
| i-robot | 3-3 | 6.36 M | −8.7032 | −8.7983 | +0.0951 |
| the-thorn-birds | 2-4 | 36.11 M | −8.5375 | −8.5396 | +0.0021 |
| the-thorn-birds | 3-1 | 17.73 M | −8.5923 | −8.8842 | +0.2919 |
| the-thorn-birds | 3-2 | 14.30 M | **−8.2702** | −8.5141 | +0.2439 |
| the-thorn-birds | 3-3 | 24.73 M | −8.5145 | −8.5145 | **+0.0000** |

Global best mean is **−8.2702** (Thorn Birds / 3-2 / `last-letters-palindrome`), still
below the −8.2 look threshold and on a known letter-density artifact family. Three cells
reproduce the 2026-10-31 baseline to four decimal places (**Δ = +0.0000**), which is the
regression proof that the `_cipher_layout` refactor and the `sweep.py` rewrite did not
perturb the validated sliding path; a separate `--sliding-only` run on foundation2 / 3-1
reproduced −9.0193 / win −9.0380 / `letters` / start 340069 exactly as logged.

**Two calibration findings that change how every score in this file should be read.**

1. **The windowed statistic's −8.1 noise floor does not survive a book-length search.**
   It was calibrated in `validate.py` on 120 letters of uniform random noise. Over 198 M
   real candidates, the best window score on a decode that is plainly not English reached
   **−8.078** (`letters`, Thorn Birds / 3-2, reversed) and **−7.7448** on the artifact
   families — the latter inside the genuine-English band. The **true 2-1 plaintext windows
   at −8.077**. Taking a maximum over ~10⁸ windows finds the distribution's tail whatever
   the text is, so signal and noise collapse. `sweep.py` now requires the mean to clear
   −8.6 before a window-band flag is raised; the mean still separates them (−8.144 true vs
   −8.7465 false).
2. **The −7.9…−8.0 "genuine English" band was calibrated on prose.** The true 2-1 message
   is verse and scores **−8.144**, below the band and only 0.056 above the look threshold.
   A correct decode of a poetic plaintext will not look like the calibration table says a
   correct decode looks. Asserted in `validate.py::test_puzzle_21` so it cannot drift.

**Provenance note on the log file.** `results/palindromic_sweep_2026-11-03.txt` was
written by `sweep.py` *before* correction 1 was applied, so it still contains two
`<-- CHECK THIS (window band only)` flags — `first-letters-palindrome` at mean −9.5932
(Zhivago / 3-2) and `letters` at mean −8.7465 (Thorn Birds / 3-2), both vowel salad on
inspection. Current `sweep.py` raises no flag for either, because both means are below
−8.6. The scores, rankings and pair counts in the log are unaffected; only the flag text
differs. Re-running would change those two lines and nothing else.

**Grade of these negatives.** These four books are now negative under both search shapes —
sliding (21 families, both directions, every offset) and anchored palindromic (3 families,
every sentence start, every exact length in the gate). That is materially stronger than the
2026-10-31 grade. Still not hard eliminations, for three reasons recorded in
`docs/methodology.md`: the OCR-noise caveat on Zhivago's inner margins persists; the
standing edition rule means a miss on a printing that is not Holland's proves nothing; and
the anchored scan covers only `letters`, `first-letters` and `last-letters`, so **it says
nothing about the other 18 families in palindromic form** — the every-Nth and
word-Nth-letter constructions remain untested against this mechanism.

**Not swept: `texts/cats-cradle`.** `build_whole_books.py --list` reports it **NOT
SWEEP-ABLE — 82 missing chapters** (2, 6, 12, 15, 16, 18, 19, 20, 21, 24, 25, 26, …). A
book cipher's indices address the complete text, so a concatenation with gaps yields wrong
numbering past the first gap and any negative from it would be meaningless. Vonnegut is
ranked #2 for 3-1 in `docs/decipher-iii.md`; closing that gap is a scanning task, not a
compute task.

Runtime ≈ 75 min wall, ≈ 68 min CPU. No decoded plaintext from any open cipher is stored;
the previews above are the noise-band strings the sweep itself printed.

## 2026-11-04 — cats-cradle: the "82 missing chapters" were a bad split, not missing scans

**Root cause found, and it was not the scanner.** `texts/cats-cradle` (v1) was OCR'd from
`scanning/book-scans/cats-cradle-2026-10-26/pages_v1/`, which is **ScanTailor Advanced's
mangled output**: each half-image crop is roughly twice a page wide (pre-scale ~1,977–2,017
px where a real page is ~1,040), so every crop held most of *both* pages. Line structure
collapsed, the ingest's Jaccard ≥ 0.75 dedup silently dropped the redundant halves, and
chapters 90–126 landed in `ch090.txt` as a single 15,690-word line. The 82 "missing"
chapters were a filing artifact.

The correct split — `preprocess_spreads.py` output, page widths ~1,020–1,040 px — was
already on disk in `pages/` and had **never been OCR'd**. Verified visually:
`pages/image00114_1L.jpg` is a complete, sharp page 174 with every line end intact, while
the raw spread `raw/image00114.jpg` shows the book fully in frame with hands only at the
edges. **The raw scans are fine; no re-scan is needed for text recovery.**

**Re-ingest** (`ingest_by_markers.py --mode cc` against `pages/`, output
`texts/cats-cradle-v2`): 97 chapter files, missing chapters **82 → 31**
(3, 5, 12, 25, 29, 40, 41, 46, 49, 54, 55, 59, 65, 67, 71, 78, 79, 81, 83, 85, 90, 92,
96, 100, 103, 106, 107, 109, 114, 118, 120). `build_whole_books.py` now marks v1
SUPERSEDED by v2. **Still NOT SWEEP-ABLE.**

**Why not push the last 31.** Their text IS present in the OCR (probe-matched 14/31), just
merged into the preceding chapter. Anchoring them from a clean reference text recovers at
best ~half and risks mis-anchors, because the OCR is only ~85–90 % accurate at word level —
the same probe matches only 11/41 on chapters known to be present. A book cipher needs
exact letters, so a 10–15 % word-error text cannot carry a sweep regardless of how it is
split. Closing this needs a re-scan with flatter pages and more light, or a better OCR
pass, not better splitting.

**One fix tried and reverted.** A colour-based hand exclusion in `preprocess_spreads.py`
(paper reads R−B −8…−12, skin +8…+21; grayscale cannot separate them, both ≈ 200) collapsed
every spread to a ~700 px "single" region, because the cool test fragmented the column
profile. The hand-inflated span (~2,530 px vs ~2,080) only adds a sliver of the facing
page, which the gutter-noise stripping already tolerates. The attempt is documented in the
function's docstring so it is not re-debugged.

**Consequence for 3-1.** Vonnegut remains untestable at whole-book grade from our own
scan. *Cat's Cradle* stays ranked but un-swept; the gap is a scanning/OCR-quality task.

## 2026-11-05 — Addendum 1 published in response to our verification; four of our claims corrected

**Not a sweep.** Eckman published **Addendum 1: Independent Replication, Textual Witnesses,
and Clue Interpretation**, Zenodo, 4 Nov 2026, CC-BY-4.0,
[doi:10.5281/zenodo.23963541](https://doi.org/10.5281/zenodo.23963541)
(`paper/addenda/ADDENDUM_01.md` in his repository). It responds directly to our
2026-11-03 verification and to the comments on issue #1.

**What it confirms about our work.** He reran `solver/verify_ii1.py` and
`solver/check_ii1_witness.py` at commit `d0f7d83` **without modification and confirmed all
19 checks**; confirmed the Gutenberg #829 witness at 491 letters and both wording
differences; confirmed our 152-original / 153-corrected reachability figures. He also
classifies every claim by evidential basis — **"Supported"** (visible in our public code,
data or commit history) versus **"Reported"** (our account, not reproduced) — which is a
discipline worth adopting here.

**Stronger edition-drift numbers than the original paper.** Retaining Alden addressing, the
Gutenberg witness reproduces **63/314** letters and Wikisource **55/314**; applying the
construction at each witness's own length (982 and 980 slots respectively), Gutenberg
reproduces **72/314** and Wikisource **40/314**. A two-letter wording variant destroys
roughly four fifths of the message under either addressing. `docs/methodology.md` gap 1
updated.

**Four of our published claims were wrong and are corrected in this commit.**

| # | We said | Correction |
|---|---|---|
| 1 | `HalfFwdRev` present "since 2026-10-17" | Commit `7ac346b` is dated **2026-10-18**; the Gemini Q&A prompting it was the evening of the 17th |
| 2 | The two transcriptions "agree on all 314 values" | **313 of 314.** Observation 306 differs: we hold the photograph-supported `388`, Kavett's compilation holds `338`. "All 314" was true only of the fingerprint test, which reverts 306 to `338` first |
| 3 | `338` is the "**as-printed**" value at observation 306 | The print shows **388** — our own 2026-10-05 finding. `338` is the value recorded in **Kavett's compilation**. Our wording contradicted our own documentation |
| 4 | The clue readings are "contemporaneous **corroboration**" of the mechanism | His experiment records show "492" and "One way gets you half way there" **influenced the construction's discovery**. They are clue-*consistent* interpretations, not independent confirmation. Framing withdrawn in `docs/decipher-ii.md` |

Also corrected: divergence positions were quoted as "94" (one-based Alden) and "232"
(zero-based Gutenberg) side by side, as if the bases matched.

**His three qualifications on our transcription, all accepted.** The *reading* is
independent but the *source* is not: our 2026-10-05 re-transcription was made from the
Decipher II puzzle front/back images in Kavett's shared archive, documented in
`docs/decipher-ii.md` and linked from `docs/sources.md`, and his photograph comes from the
same compilation — so this is a second reading of the same images, corroborating the
transcription rather than the printed puzzle. It was compared token by token against a
previously stored sequence of **undocumented origin**, so independence from Kavett's typed
text rests on our own account and is not checkable by anyone else. And two readings agreeing
shows neither that the printed puzzle is error-free nor that observation 169 is resolved.
Gap 2 is therefore recorded as **substantially reduced for 2-1, not closed**.

**Still open on both sides.** Observation 169 (`330` transcribed, `830` probable, not
independently established — the whole 314-character decode is conditional on it);
**"S.I.N."**, unexplained by both projects; the designer's edition and his procedure for
choosing among eligible numerical positions. The cheapest decisive next step is a **blind**
reading of observation 169 from the puzzle photograph, with no knowledge of the expected
value — his `830` rests on candidate-aware readings, ours on the same image.

Addendum 1 discloses that Claude Code (Anthropic) inspected the sources, ran the verification
computations and drafted the text under the author's direction; our own repository makes the
equivalent disclosure. Per `AGENTS.md`, AI-authored factual claims from either side are
unverified until cross-checked against primary sources. The addendum has not been peer
reviewed, and neither has the original report.
