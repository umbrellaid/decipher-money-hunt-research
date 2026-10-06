# Methodology — how the book-cipher attack works

## The mechanic

Every Decipher message is a list of numbers (plus a few literal letters). Each number
names a position in a hidden **key stream**: a sequence of letters extracted from some
published book under some rule. Number `n` yields the stream's `n`-th letter; literal
letters in the cipher stand for themselves. Solving means finding (book, rule, starting
position, direction) such that the decoded letters are English.

The four solved precedents fix the rule families the creator actually used:

| Puzzle | Key stream rule | Key text |
|---|---|---|
| Decipher I (1983) | first letter of every word, numbered consecutively from a start word, continuous across lines | Carl Sagan, *Cosmos*, ch. 6 (skip first 36 words) |
| Decipher II 2-1 | continuous letters of a passage | Swift, *Gulliver's Travels* |
| Decipher II 2-2 | chapter titles concatenated, then the whole string **reversed** | Heller, *Catch-22* |
| Decipher II 2-3 | first letter of every word of one chapter | Clavell, *Tai-Pan*, ch. 5 |

The Decipher III rulebook (pp. 3–4) prints the Decipher I construction and a 56-word
worked passage with three sample ciphers for the word CODES. That example is the
solver's zero-dependency regression test (`solver/validate.py`).

## Rule families implemented (`solver/rules.py`)

Base five (used by all published sweeps): `letters`, `first-letters`, `last-letters`,
`line-first`, `line-last`.
Added 2026-10-05, driven by the printed clues "10" and "End": `everyN-letter`,
`everyN-wordfirst`, `everyN-wordlast` for N in {2,3,5,10}; `word2th-letter`,
`word3th-letter`; `sentence-first`; `paragraph-first`.
Every stream is additionally tested **reversed** (the "End" clue and the 2-2 precedent)
and the plaintext is scored in **both reading directions** (2-2's plaintext read
backwards relative to its numbering). The numbering start slides over every possible
offset, because Holland did not always begin at position 1.

## Scoring and calibration

Decodes are scored by mean trigram log-probability under an English model built from
five Project Gutenberg classics (`data/pg_manifest.json`, group `model`). Calibration,
established on the solved Puzzle 2-2 and re-confirmed by `validate.py`:

- genuine English, 50–170 letters: **≈ −7.9 to −8.0** per trigram;
- wrong key / noise: **≈ −8.6 and below**.

The gap is large relative to the per-trigram averaging, so a top hit in the noise band
is a *definitive negative* for that (text, rule family) pair, not a weak signal.

The Decipher III rulebook warns that plaintexts may contain inserted meaningless
letters ("nulls"). One null-tolerant statistic survived testing:
`TrigramScorer.score_best_window`, the best contiguous window of the decode, which
rescues **clustered** nulls and still rejects uniform noise (both properties are
asserted in `solver/validate.py`; treat −8.1 as its noise floor).

A trimmed-mean variant (average of the best 60–70 % of trigram logs) was implemented,
tested and **removed on 2026-10-05**: pure-noise decodes score ≈ −7.3 under it, inside
the genuine-English band, so it cannot separate signal from noise and would have
produced false positives. And neither statistic can rescue **scattered or periodic**
nulls, because then no window of the decode is null-free; `validate.py` asserts this
as a documented limitation. A scattered-null plaintext would need partial-word
back-solving, which is not implemented — it is the most valuable unimplemented idea
in this repository.

## What a negative result proves — and what it does not

A sweep that ends in the noise band proves: *under the implemented rule families, at
any numbering start, in either direction, this exact text does not contain the key
stream.* It does **not** prove the book is innocent, because of three known gaps:

1. **Edition variance.** The MIT paper on Decipher I stresses that different printings
   shift numbering. The sliding offset absorbs small shifts; a revised or abridged
   edition can still miss.
2. **OCR/typing errors** in the supplied text corrupt the key region.
3. **Rule families still missing.** Page-level numbering, and nulls interleaved
   with the key itself. Chapter-title chains, the reversed *Catch-22* rule that
   solved puzzle 2-2, are tested when a `.chapters.json` file sits beside the
   book. `solver/sweep.py` reads `BOOK.chapters.json` when the sweep file is
   `BOOK.txt` or `BOOK.clean.txt`. `solver/normalize_text.py
   --chapters` writes that file for headings that start with CHAPTER, BOOK,
   PART, or SECTION. Titles that are only a name have to be written in by hand.
   The 21 families in `solver/rules.py` are the body-text rules. Puzzle 2-2 is
   checked from `data/catch22_chapter_titles.json` inside `solver/validate.py`.

## Reproducing everything

From the repository root (needs [uv](https://docs.astral.sh/uv/)):

```
uv run python solver/fetch_texts.py        # public-domain corpus + scoring model
uv run python solver/validate.py           # 93 regression checks, must all pass
uv run python solver/sweep.py mybook.txt --cipher 3-1 --top 10
```

`--cipher all` sweeps the four open ciphers (2-4, 3-1, 3-2, 3-3). The scorer
reads only `texts/model/`, the five books named in `data/pg_manifest.json`, and
exits if that folder is missing. Score bands were calibrated on that model.
`solver/fetch_texts.py` exits 1 if a Gutenberg download fails. It saves the
Gutenberg file as shipped, which is the form the published logs used. Pass
`--normalize` only when you want the header stripped. That changes every-Nth
letter phase, so those files will not match `results/`.

`solver/normalize_text.py` cleans OCR output and extracts chapter headings; see
`docs/check-your-own-book.md` for the full workflow from phone photos to a verdict.
