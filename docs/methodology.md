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

**That −8.1 floor is calibrated on 120 letters of uniform random noise and does not
hold for a book-length search (measured 2026-11-03).** Over 198 M anchored
(start, length) pairs on four real novels, the best window score reached by a decode
that is plainly not English was **−8.078** (`letters`, *The Thorn Birds* vs 3-2,
reversed), and on the known letter-density artifact families it reached **−7.7448**
— inside the genuine-English band. The **true** 2-1 plaintext windows at **−8.077**.
Signal and noise are indistinguishable on that statistic at this scale, because the
maximum over ~10⁸ candidate windows finds the tail of the distribution no matter what
the underlying text is. Two consequences, both now enforced in `solver/sweep.py`:

- A window-band flag additionally requires the **mean** to be above the −8.6 noise
  floor. The mean still separates cleanly: −8.144 for the true 2-1 answer against
  −8.7465 for that false positive.
- The genuine-English band of −7.9…−8.0 was calibrated on **prose**. The true 2-1
  plaintext is **verse** and scores **−8.144**, below the band and only 0.056 above
  the −8.2 look threshold. A correct decode of a poetic message will not look like
  the calibration table says a correct decode looks. `validate.py` asserts the actual
  value so this cannot be forgotten.

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

   **Measured on our own download, 2026-11-03: there is a third witness, and it is the
   default one.** `solver/check_ii1_witness.py` fetches Project Gutenberg #829 and
   normalizes the same paragraph to **491** letters — neither Eckman's 492 (Alden 1911)
   nor his 490 (Wikisource/1801). It differs from Alden at two independent places:
   `take my measure` → `take measure` (−2) at normalized position 94, and `with rule and
   compasses` → `with a rule and compasses` (+1) at 232. The first divergence is at
   position **95**, so most of the forward half misaligns. The e-text anyone would reach
   for first fails the printed "492" clue, which makes that clue a usable *witness
   discriminator* **for 2-1**: a candidate source whose passage does not normalize to
   exactly 492 letters is the wrong printing and can be rejected before any sweep is
   attempted. The unsolved messages have **no** length clue that this repository holds:
   no clue set for 2-4 is recorded anywhere in `docs/` or `results/` (only its numeric
   microstructure, `results/puzzle-2-4-microstructure-2026-10-18.md`), and 3-1's printed
   clues are "group B" / "10" / "End", none of which is a length. 3-2 and 3-3 had no
   clues released at all, because clues for messages 2 and 3 were only issued after
   message 1 was solved and it never was. So this free pre-filter is available for 2-1
   and *not* for the four open ciphers. That asymmetry is why gap 1 bites harder on the
   open ciphers than on the solved one: for them we cannot even screen witnesses cheaply,
   and a negative stays unattributable between "wrong book", "wrong printing" and "wrong
   construction". Recovering any 2-4 clue text is therefore worth more than more sweep
   time.
2. **OCR/typing errors** in the supplied text corrupt the key region. **Closed for 2-1
   as of 2026-11-03**, and open for everything else. Our 2-1 sequence was read from the
   printed surface at 3× on 2026-10-05; Eckman's came independently via Kavett's public
   compilation. The canonical fingerprint of our original 314 values reproduces his
   published input hash `1e60d5d6…` exactly, so two independent readings agree on every
   value (`solver/verify_ii1.py`). The four unsolved ciphers have no second witness, so
   for 2-4, 3-1, 3-2 and 3-3 a single misread digit remains live and would produce
   exactly the same noise-band negative as a wrong book.
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
   wrong-construction signature.

   **Implemented 2026-11-03** as `engine.search_anchored`, driven from `sweep.py`. The
   design that shipped is not the obvious one, and the reason is measured:

   - *Paragraph anchoring was tried first and rejected.* Enumerating paragraphs, and then
     runs of 1..8 consecutive paragraphs, produced **zero** candidates for the 2-1 gate
     `[490,979]` and the 2-4 gate `[527,1052]` across three different texts (Austen,
     Melville, Hardy verse). These books average ~48 letters per paragraph — they are
     dialogue-heavy — so reaching 490 letters needs a run of roughly fifteen paragraphs.
     A search space of zero candidates still prints a confident negative, which is the
     worst possible failure mode. `sweep.py` now prints the pair count per family and
     warns loudly when it is zero.
   - *What ships instead* is an exact scan over (sentence start, passage length) pairs,
     fully vectorized: no key string is materialized, the `(batch, N)` index matrix is
     built directly from `sigma(c, L) = c if c <= L else 2L + 1 - c`. Sentence starts are
     the anchoring granularity because 2-1's passage opens on one.
   - **`L` cannot be subsampled.** Gap 1 shows a single letter's difference in the source
     destroys alignment, so every integer length in the gate is tried. Only the *starts*
     are restricted.
   - The gate is `[ceil(max_n/2), max_n - 1]`: at `L = max_n` every observation maps into
     the forward half and the construction degenerates to a plain forward stream the
     sliding sweep already covers. For 2-1 that is `[490, 979]`, which deliberately
     admits the 490-letter Wikisource variant as well as the true 492, so the near-miss
     gets scored instead of silently skipped.
   - **Coverage is three families, not 21** (`rules.anchored_scan_families`): `letters`,
     `first-letters`, `last-letters`. Those are the only ones whose stream coordinates map
     exactly onto a sentence start. The every-Nth and word-Nth-letter families stride
     through the text, so a sentence start does not land on a stream index without a
     separate mapping, and guessing it would produce a misaligned search that still looks
     like a negative. **An anchored-scan negative does not speak to those 18 families.**
     `letters` is the family 2-1 actually used.
   - Measured cost on a 579k-letter book (Austen, 7,544 sentence starts), one family,
     four open ciphers: ~147 s, ~4.0 M pairs total. `sweep.py` runs three families, so
     budget roughly 7–8 minutes per full-size book for the anchored scan alone, on top of
     the sliding sweep.
   - Positive control (`validate.py::test_palindromic_positive_control`): with the Swift
     passage embedded in Austen, the scan searches **411,918** pairs and returns the true
     passage at exactly `L=492`, ranked #1 by both the mean and the window statistic,
     separating from the runner-up by 1.2 (−8.144 vs −9.367). Two earlier versions of this
     control passed vacuously and are documented in its docstring.

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
