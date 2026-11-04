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
| Decipher II 2-1 | continuous letters of a passage, normalized to 492 letters, **then that sequence concatenated with its own reversal** to give a 984-position palindromic key (published reconstruction 2026-10-31, `docs/decipher-ii.md`) | Swift, *Gulliver's Travels*, Part III ch. 2 (the tailor paragraph) |
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
   shift numbering. The sliding offset absorbs small shifts **only when the variant is
   outside the keyed passage**; a variant *inside* the passage is not absorbed, because
   it displaces every position after it and no single global offset can repair both
   sides of the gap. This is no longer a theoretical worry. Eckman's 2-1 reconstruction
   (`docs/decipher-ii.md`, 2026-11-03) measured it: the Alden (1911) witness of the
   tailor paragraph reads "take **my** measure" and normalizes to **492** letters, which
   is the printed clue; the Wikisource transcription attributed to an 1801 edition omits
   "my" and gives **490**. Two 492-letter windows cut from the shorter text then agree
   with the true decoding at **55/314** and **260/314** observations respectively — each
   aligned on a different side of the two-letter gap. **A two-letter variant between
   printings of the correct book is enough to make the correct book score as noise.**
   Practical consequence: a sweep may only use a text whose witness is pinned to a
   specific printing, and a negative obtained from a single unspecified e-text does not
   reach the book. `260/314` is the number to remember — a near-miss that high is
   evidence of a textual variant, not evidence against the book.
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

   **The palindromic key `S || reverse(S)`: anticipated here, implemented against the
   wrong granularity (corrected 2026-11-03).** Eckman's 2-1 reconstruction establishes
   that Holland built a 984-position key by appending a 492-letter passage's reversal to
   itself, so that slots `n` and `985−n` address the same letter.

   *This repository already had the shape.* `solver/body_scan.py:157-168` has carried
   three "halfway / out-and-back" streams since 2026-10-17 — `HalfFirstLast`,
   **`HalfFwdRev = firsts + firsts[::-1]`** and `HalfOddEven` — under a code comment
   quoting the 2-1 clue *"One way gets you half way there"* and reasoning that
   "N_max 980 = 2 x 490 implies a single place read two ways". The doubling inference was
   right two weeks before the reconstruction was published. Eckman completed it; this
   repository did not, and no priority is claimed here.

   *Why it still could not have found 2-1* — four concrete defects, all verified against
   the current source:
   1. `HalfFwdRev` is built from `firsts = [w[0] for w in words]`, i.e. the first letter
      of every **word**. 2-1's key is the continuous **letters** of a passage, doubled.
      `chars = T.clean_alpha(text)` is computed at `body_scan.py:137` and used only for
      the zero-Z count; no half-stream is ever built from it.
   2. The unit is a **chapter window**. `body_scan.py` enumerates concatenated chapter
      windows and never anchors on paragraphs, so it cannot produce a 492-letter passage
      key at any setting. The gate `if len(words) >= 240` is a window-level word count,
      not a passage length.
   3. None of it is reachable from `solver/rules.py` or `solver/sweep.py`. `all_rules` is
      21 families, none palindromic, and the sweep's `direction="from-end"` is
      whole-stream reversal — it preserves length, producing `reverse(S)`, not
      `S || reverse(S)`. Every corpus elimination in `docs/decipher-iii.md` (Poe,
      Faulkner, the pre-1931 Christies, Sandburg, O'Neill, cummings, the chapter-title
      chains) was produced by that path and is logged as "21 rule families".
   4. `sweep.py`'s `if len(stream) <= max_n: continue` guard tests the *undoubled*
      length, so even a correctly built palindromic stream would be filtered on the
      wrong quantity.

   The false negative survives all four corrections. Measured against our own
   `data/ciphers.json`, 2-1 has 314 integers with max **980**, and **152 of 314 (48 %)
   exceed 492**. Under the plain `letters` family the sweep slides a window over the whole
   book, so a window starting at the tailor paragraph decodes indices 1–492 correctly —
   but indices 493–980 belong to the *reversal*, not to text continuing forward past the
   passage, and no offset of a forward stream reproduces them. **Had we swept the correct
   *Gulliver's Travels* text at the correct paragraph, roughly half the message would have
   come out right and the mean trigram score would still have landed in the noise band — a
   false negative on the right book, the right passage and the right starting offset.**
   That retroactively weakens every negative in `results/` for the open ciphers — 2-4
   (max index 1053), 3-1 (516), 3-2 (416) and 3-3 (721) were all swept without a
   palindromic family on continuous letters. Those eliminations need re-earning or
   explicit re-qualification.

   Note that `260/314`-style partial agreement (gap 1) and a ~50 %-correct decode (this
   gap) are distinguishable: the former is a textual-variant signature, the latter a
   wrong-construction signature. Building the family properly needs (a) every base family
   emitted in doubled form, (b) paragraph- and chapter-level anchoring rather than
   sliding offsets, since the σ mapping is not expressible as `start + n − 1`, and (c) a
   length gate derived from the cipher — only `L` in `[ceil(max_n/2), max_n]` is worth
   testing, because above `max_n` the construction degenerates to plain forward and is
   already covered. That gate replaces `len(words) >= 240` and keeps cost tractable
   (2-4 → L∈[527,1052], 3-1 → [258,515], 3-2 → [208,415], 3-3 → [361,720]). It also
   halves the source length a candidate passage must supply to cover a given max index,
   which widens the candidate set. Until it lands, treat "no hit under the 21 families" as
   covering one fewer construction than the solved precedents actually use.

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
