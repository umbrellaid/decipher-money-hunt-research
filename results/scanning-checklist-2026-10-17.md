# Body-Text Scanning Checklist — Decipher II 2-4 / Decipher III 3-1, 3-2, 3-3
**Generated 2026-10-17 from corrected N_max values (repo `data/ciphers.json`)**

## A. How much keytext each puzzle actually needs

N_max (largest codenumber = latest keytext position used):

| Cipher | Tokens | N_max | Chars needed (every-character extraction) | Words needed (first-letter-of-word extraction) |
|---|---|---|---|---|
| 2-4 | 170 | **1053** | 1053 chars ≈ **~205 words ≈ 0.8 page** | 1053 words ≈ **~4.2 pages** |
| 3-1 | 170 | **516** | 516 chars ≈ **~100 words ≈ 0.4 page** | 516 words ≈ **~2.1 pages** |
| 3-2 | 117 | **416** | 416 chars ≈ **~82 words ≈ 0.3 page** | 416 words ≈ **~1.7 pages** |
| 3-3 | 159 | **721** | 721 chars ≈ **~140 words ≈ 0.6 page** | 721 words ≈ **~2.9 pages** |

(Assumes ~5.1 chars/word, ~250 words/paperback page. Solved precedents: Decipher I
used ~150 words of Cosmos Ch. 6; 2-3 used ~500 words of Tai-Pan Ch. 5 — i.e. both
families are historically plausible.)

**Rule of thumb: scanning the first 5 pages AND the last 5 pages of a target
chapter covers every cipher under both extraction families.** The ToC-only
hypothesis is now eliminated (see `results/gemini-toc-test-2026-10-17.md`), so
every target below is a body-text scan.

## B. Per-book targets (Clue "10" / Clue "End." priority order)

Ch. 10 titles marked † are from Gemini's analysis and should be verified against
the physical copy when scanning.

### Isaac Asimov (Group B candidate author)
| Book | Ch. 10 target | Final-chapter target | Note |
|---|---|---|---|
| *Foundation's Edge* (1982) | Ch. 10 **"Table"** | Ch. 20 **"Conclusion"** — matches "End." | 20 short chapters; strongest Asimov pick |
| *Foundation* (1951) | Ch. 10 overall = Part III **"The Mayors"** ch. 2 † (chapters numbered continuously 1–19 across parts — earlier "Part II ch. 5" guess was wrong; Gemini Q3, unverified) | end of Part V "The Merchant Princes" | count across parts, not per-part restart |
| *I, Robot* (1950) | 10th section = **"The Evitable Conflict"** (also the last) | same | "10" and "End." both satisfied by one scan |
| *The Union Club Mysteries* (1983) | Ch. 10 **"Gift"** — a literal cipher-puzzle story; its original *Gallery* (June 1981) title was **"Decipher Deception"** † (Gemini Q8, unverified) — scan Ch. 10–15 contiguously † (story length disputed: 3–5 pp per Q3 vs 6–7 pp / ~1,500–1,800 words per Q8; either way below word-level N_max alone) | Ch. 30 "There Was a Young Lady" (+ 2-page Afterword) | 30 titled stories + Foreword/Afterword; bare ToC = 391 letters, +F/A = 408, "1 to 999" spelled out = 432 † |
| *Asimov's New Guide to Science* (1984) | Ch. 10 †"The Reactor" | final chapter | ToC sub-headers already ≥1050 letters |
| *The Naked Sun* (1957) | Ch. 10 **"A Culture Is Traced"** | Ch. 18 "A Question Is Answered" | formula titles, easy to spot-check |

### Non-Asimov
| Book | Ch. 10 target | Final-chapter target | Note |
|---|---|---|---|
| *Cat's Cradle* (Vonnegut, 1963) | Ch. 10 **"Secret Agent X-9"** — scan Ch. 10–15 contiguously † (Ch. 10 ≈ 400 words, below the 516–721 words needed for word-level extraction; Gemini Q3, unverified) | Ch. 127 **"The End"** — literal match | 127 micro-chapters; Ch. 10 is ~1 page |
| *Doctor Zhivago* (Pasternak, 1957) | Part 10 **"On the High Road"** | Part 16 "Epilogue"; also Part 15 **"The Ending"**; also scan Part 17 "The Poems of Yury Zhivago" † (25 poems, dense vocabulary; Gemini Q3, unverified) | Pasternak = author #10 on the 3-1 list |
| *In Cold Blood* (Capote, 1966) | no numbered chapters — scan start of Part III "Answer" | end of Part IV "The Corner" | carryover author (2-2 and 3-1 lists) |
| *Grapefruit* (Yoko Ono, 1964/70) | piece #10 (piece titles unnumbered in most printings — count) | final pieces | trivial to scan in full |
| *The Bourne Identity* (Ludlum, 1980) | Ch. 10 | Ch. 39 (final) | 39 untitled chapters |
| *All the President's Men* (Woodward/Bernstein, 1974) | ~~Ch. 10~~ | ~~final chapter~~ | **DROPPED** † (Gemini Q3: 16 untitled chapters, journalistic prose, no Holland-style hook; unverified) |
| *RN* (Nixon, 1978) | Part 10 †"1973" | Part 11 †"1974: Judgment" (end) | 11 parts |
| *Shōgun* (Clavell, 1975) | Ch. 10 | final chapter | top reuse candidate for 2-4 / 3-3; **deprioritized for 3-1 / 3-2** † (6 books, 60 untitled chapters, heavy OCR; Gemini Q3, unverified) |

## C. Elimination thresholds to apply during scanning

- A scanned chapter that yields **zero readable plaintext after drift ±2** under
  both families (chars / word-first / word-last, fwd/rev) is eliminated for that
  cipher — move on after 5 pages.
- Watch for the **crib anchors**: 3-1 must contain literal-position Z between two
  letters and a double letter at codenumber 487's mapping; 3-2's full crib is
  **E,Y,E,Y,E**; 3-3 has three literal E's.
- 2-4's run of multiples of 100 (400,500,400,100,200,400,800,600) either maps to
  an A-B-A-C-D-A-E-F letter pattern or they are nulls — test both.

## D. Extraction-family test order (from Gemini Q4, 2026-10-17 — Argon High)

Both solved body-text precedents (Decipher I = *Cosmos* Ch. 6; 2-3 = *Tai-Pan*
Ch. 5) were **word-level, first-letter-of-each-word** keys (1 codenumber = 1
word); only the ToC puzzle 2-2 was character-level. So for every scanned chapter
test in this order (Gemini claims unverified against primary sources):

1. **Word-level first** — 3-1: last-letter-of-word and end-anchored variants
   ("End." read as the extraction clue: last letter, or start from the chapter
   end); 3-2 / 3-3 / 2-4: first-letter-of-word first. 2-4 also with the
   100-multiples stripped as nulls.
2. **Word-level variants** — reversed word order, every-other-word /
   every-10th-word strides.
3. **Character-level fallback** — every character of the chapter opening/ending
   (fwd/rev); for 3-2 (N_max = 416, closest to 2-2's 477) also re-test ToCs,
   epigraphs, and front matter.

Window sanity check: 5 paperback pages ≈ 1,400–1,750 words ≥ every word-level
N_max (416/516/721/1053), and ≥ every character-level N_max in page 1 alone.

Implemented 2026-10-18 in `solver/body_scan.py`: Tier 1 word-level streams
(incl. reversed word order), Tier 2 strides + 2-1-style "halfway" patterns,
Tier 3 character fallback; contiguous chapter windows (`--window`, default 6);
zero-Z flagging for 3-1 (`--strict` to skip); `--skip` word-offset variants
(solved precedent: Decipher I skipped the first 36 words of Cosmos Ch. 6 —
paper p. 279, Figure 8, verified in repo `docs/decipher-i.md`); S100 probe on
all 2-4 hits.

## E. Puzzle 2-4 specific plan (from Gemini Q7, 2026-10-18 — claims unverified
except where checked against `data/ciphers.json`)

Candidates (author list survives in `data/author_lists.json`; the 6 PD authors
are already sweep-eliminated under standard rules — retest only under the
non-standard families below):

| Rank | Book | Est. † | Why |
|---|---|---|---|
| 1 | McCullough, *The Thorn Birds* (1977) | 25% | runaway mega-bestseller; 7 named chronological Parts |
| 2 | Irving, *The World According to Garp* (1978) / *The Hotel New Hampshire* (1981) | 20% | counterculture-literary sensibility matches Catch-22 / Bloom County picks |
| 3 | Updike, *Rabbit Is Rich* (1981) / *The Witches of Eastwick* (1984) | 18% | author #1 on the 2-4 list; Rabbit books have almost no chapter divisions — trivial to test whole |
| 4 | L'Amour, *The Walking Drum* (1984) / *The Lonesome Gods* (1983) | 14% | bestselling paperback author; 1984 historical-epic breakout |
| 5 | Ludlum, *The Bourne Identity* (1980) | 10% | already on the 3-1 scan list (one scan tests both); discounted by Gemini's "unused-decoy carryover" argument |

Ciphertext variants to test for 2-4 (full 170-token stream; multiples-of-100
run VERIFIED at tokens 20–27 + 300 at token 31 in `data/ciphers.json`):

1. Full ciphertext, unmodified — use the S100 pattern (X-A-X-B-C-X-D-E) and the
   three ascending triples (737,738,739 @9; 154,155,156 @67; 544,545,546 @154 —
   positions verified locally) as crib filters.
2. Multiples-of-100 stripped (already implemented as `Puzzle_2-4_No100s`).
3. X0Y-stripped (all n ≥ 100 with tens digit 0 removed — 39 of 170 tokens,
   22.9% vs ~10% expected; tests the null-injection hypothesis).
