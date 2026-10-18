# Puzzle 2-4 numeric microstructure — verified 2026-10-18

Positions and values below are computed directly from `data/ciphers.json`
(170 tokens, all numeric, N_max = 1053). They correct the token positions in
Gemini's Q7 answer, which worked from a 154-token transcription — **all of its
claimed values are real, but its positions undercount by 1–16 tokens** (its
"154 tokens" vs the repo's 170). Gemini's quoted final tokens
(...149, 162, 128, 320, 104, 34, 33) match the repo tail exactly.

## Multiples of 100

- Tokens **20–27**: 400, 500, 400, 100, 200, 400, 800, 600 (pattern
  X-A-X-B-C-X-D-E: X = key[400] at positions 1, 3, 6), plus 300 at token 31.
- Only 9 multiples of 100 exist in the whole cipher (the 8-run + 300).
- 2-3 precedent (solved): its round numbers 2000/2020/2030/2090 are genuine
  homophones, not nulls (plaintext "…I AM BLIND…", `docs/decipher-ii.md`) —
  so treat the 2-4 run as real plaintext letters under the primary hypothesis.

## Consecutive runs (1-based positions, repo numbering)

| Feature | Values | Position of first token |
|---|---|---|
| Ascending triple | 737, 738, 739 | 9 |
| Ascending triple | 154, 155, 156 | 67 |
| Ascending triple | 544, 545, 546 | 154 |
| Ascending pair | 301, 302 | 93 |
| Ascending pair | 268, 269 | 137 |
| Ascending pair | 287, 288 | 140 |
| Ascending pair | 780, 781 | 151 |
| Descending pair | 1050, 1049 | 2 (right at the start) |
| Descending pair | 688, 687 | 129 |
| Descending pair | 34, 33 | 169 (the last two tokens) |

## Repdigits

999 @43, 666 @85, 111 @88, 222 @89 (111 and 222 are adjacent), 99 @161, 33 @170.

## "Zero-middle" (X0Y) numbers

Tokens with value ≥ 100 and tens digit 0: **39 of 170 (22.9%)** — well above
the ~10% chance expectation for a uniform 1–1053 range. Includes the run at
tokens 71–80: 803, 806, 308, 208, 404, 704, 809, 919, 909, 961. This is the
strongest argument for the null-injection hypothesis (strip X0Y tokens and
rescore); the counter-argument is solved 2-3, whose round numbers were genuine.

## Hypotheses (Gemini Q7 ranking, positions corrected)

1. **Standard 1D key + deliberate "show-off" homophone picks (~55%)** — a human
   encrypting by hand picks visually striking available numbers (grid edges,
   consecutive runs, repdigits) when the key chart allows. The triples then
   decode to genuine 3-letter plaintext sequences that appear contiguously in
   the key stream — usable as an instant stream pre-filter.
2. **Null/decoy injection (~30%)** — strip multiples of 100 (implemented:
   `Puzzle_2-4_No100s`) or strip all X0Y tokens, then rescore.
3. **100-per-chapter block key (~15%)** — codenumbers 1–100 = first 100
   words/letters of Ch. 1, 101–200 = Ch. 2, … 1001–1053 = Ch. 11. (Pure
   Page×Offset multiplication is ruled out: 1049 is prime.)

Scanner support: `solver/body_scan.py` prints the S100 probe
(K[400]K[500]K[400]K[100]K[200]K[400]K[800]K[600]) under every 2-4 hit and
generates the 2-1-style halfway streams; the triples/S100 filters are applied
by eye from the report for now.
