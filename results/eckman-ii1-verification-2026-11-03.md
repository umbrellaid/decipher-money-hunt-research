# Independent verification of the Eckman 2-1 reconstruction (2026-11-03)

**Verdict: the reconstruction reproduces exactly, and our own ciphertext
transcription is confirmed against it. A third textual witness is reported that
the published paper does not cover.**

Eckman, C. A. (2026). *An Independent Reconstruction of Decipher II, Message 1
(1985–86).* Zenodo, 31 Oct 2026. https://doi.org/10.5281/zenodo.23844582
Software: https://github.com/chriseckman/decipher-ii1-reconstruction (v1.0.0, MIT).

> **This document was revised on 2026-11-05** after the author published
> **Addendum 1: Independent Replication, Textual Witnesses, and Clue Interpretation**,
> Zenodo, 4 Nov 2026, https://doi.org/10.5281/zenodo.23963541. The addendum confirmed
> every check below and corrected four claims this document originally made. The
> corrections are applied inline and flagged; see `results/RUN_LOG.md`, 2026-11-05, for
> the full list. Where this document and the addendum differ, the addendum is the more
> carefully qualified source.

## Method — no third-party code was executed

`solver/verify_ii1.py` reimplements the construction from the paper's own
specification (§3.1) and compares the results against the paper's published
SHA-256 values. Nothing is imported from the author's repository and `decode.py`
was never run. A match is therefore **two independent implementations agreeing**,
which is stronger evidence than executing the author's decoder and reading PASS.

```
uv run solver/verify_ii1.py        # 19 checks, all pass, exit 0
```

Inputs held here: `data/gulliver_ii1_passage.txt` (the Alden 1911 witness,
downloaded from his `inputs/source_transcription.txt`; as downloaded it is 627
bytes, LF-only, SHA-256 `8bfcfb35…`) and `data/ii1_corrections.json` (his
correction spec, verbatim). The decoded message is **never printed, written or
stored** — only its length and SHA-256. See "Rights" below.

The repository has no `.gitattributes`, so that fixture may be checked out with
CRLF on Windows and its raw byte hash is not stable across platforms. This does
not affect any check: `verify_ii1.py` hashes the **normalized** letter sequence,
and normalization strips every non-A–Z character including `\r`. The byte hash
above is recorded as download provenance only, not as an assertion.

## Results

| Check | Result |
|---|---|
| Passage normalizes (NFKD → uppercase → A–Z) to 492 letters | **PASS** |
| SHA-256 of `S` = `9eeff566…` | **PASS** |
| `K = S \|\| reverse(S)` has 984 positions | **PASS** |
| SHA-256 of `K` = `571b2327…` | **PASS** |
| Slots `n` and `985−n` address the same letter | **PASS** |
| Turnaround duplicates the last source letter at slots 492/493 | **PASS** |
| All 314 observations resolve inside the key (max 980 ≤ 984) | **PASS** |
| SHA-256 of the 314-letter plaintext = `859f2c34…` | **PASS** |
| **Our original 314-value transcription matches his input fingerprint `1e60d5d6…`** | **PASS** |
| Canonical form is exactly 1,530 ASCII bytes | **PASS** |
| 259 distinct original values / 261 distinct corrected values | **PASS** |
| Correction obs 169 `330→830` | applied here |
| Correction obs 306 `338→388` | already applied in this repository (2026-10-05) |

### The transcription cross-check is the substantive result

Two transcriptions of the 2-1 ciphertext now exist: ours, read from the printed
puzzle surface at 3× magnification on 2026-10-05, and his, taken via Karen
Kavett's public compilation. **They agree on 313 of the 314 values.** The one
difference is observation 306, where we hold `388` and Kavett's compilation holds
`338`; the puzzle photograph supports `388`, which is what this repository recorded
on 2026-10-05.

The fingerprint test compares the *pre-correction* sequences, so it reverts
observation 306 to Kavett's `338` before hashing; that reproduces his published
input hash `1e60d5d6…` exactly. Saying "all 314 agree" — as the first version of
this document did — is true only of that reverted comparison and is misleading
about the two records as they stand.

**Corrections made 2026-11-05 after Addendum 1**
([doi:10.5281/zenodo.23963541](https://doi.org/10.5281/zenodo.23963541)), which
reviewed this document. Three qualifications on the word "independent" above, all
accepted:

1. **The reading is independent; the source is not.** Our 2026-10-05 re-transcription was
   made from the Decipher II puzzle front/back images in Kavett's shared archive — those
   files and their message mapping are documented in `docs/decipher-ii.md` ("A
   transcription correction made here") and linked from `docs/sources.md`. Eckman's
   photograph comes from the same compilation. So this is a second *reading* of the same
   images, not a reading of a separate physical copy, and it corroborates the
   transcription rather than the printed puzzle. Our earlier phrase "two independent
   transcriptions" needed that qualifier.
2. The re-transcription was compared token by token against a previously stored
   sequence of **undocumented origin**, so independence from Kavett's typed
   transcription rests on our own account, not on anything a third party can check.
3. Two readings agreeing shows neither that the printed puzzle is free of error nor
   that observation 169 is resolved. As written on 2026-11-03 this was correct: our
   reading supported `330` and `830` was only *probable*. **Superseded 2026-11-05:**
   a blind reading of the sheet by four fresh contexts returned `830` unanimously,
   with the genuine `330` at position 148 read correctly in the same crop as an
   in-image control (`results/RUN_LOG.md`, 2026-11-05). Our stored `330` was the
   error, and point 1 above — that a shared error cancels in a fingerprint
   comparison — is precisely how it hid.

Consequently this cross-check **reduces** the concern of a typing error peculiar to
Kavett's compilation, and it corroborates the `388` reading at observation 306 —
but it does not close `docs/methodology.md` gap 2 for 2-1 as firmly as the first
version of this document claimed, and it does not close gap 2 at all for the four
unsolved ciphers, which have no second reading of any kind.

## New finding: a third witness at 491 letters

The paper compares two witnesses of the tailor paragraph — Alden (1911) at 492
normalized letters, and a Wikisource transcription attributed to an 1801 edition
at 490. **Project Gutenberg #829, the e-text most likely to be swept, gives 491**,
and differs from Alden at *two* independent places:

| Divergence | Alden (492) | Gutenberg 829 (491) | Effect |
|---|---|---|---|
| Alden position **94–95** (one-based) | `take my measure` | `take measure` | −2 letters |
| Gutenberg position **232** (zero-based) = Alden 234/235 (one-based) | `with rule and compasses` | `with a rule and compasses` | +1 letter |

The two position columns above use **different bases**, which the first version of
this table presented as if they were comparable. They are stated explicitly here.
Addendum 1 confirms the substance: the deletion of MY removes Alden positions 94–95,
and because the next word MEASURE also begins with M the first *differing* letter is
at position 95; the inserted A occupies Gutenberg position 232 (zero-based).

Net −1 → 491. The first divergence is at normalized position **95**, so every
observation above 94 in the forward half misaligns — which is most of the
message. Reproduce with:

```
uv run solver/check_ii1_witness.py     # exits 1: this witness fails the 492 clue
```

This is a *stronger* demonstration of `docs/methodology.md` gap 1 than the paper's
own two-witness comparison, because it lands on the default free e-text. The "492"
clue is a printing discriminator, and the most widely distributed electronic
witness satisfies neither published reading. Any past or future sweep of Gutenberg
829 against 2-1 would miss on alignment before the question of rule family arose.

## One correction to a figure we published

In the reply on issue #1 and in `docs/methodology.md` we stated that **152** of 314
observations exceed 492. That is correct for the *original* transcription, which
is what `data/ciphers.json` holds at observation 169 (`330`). Under the working
corrections, observation 169 becomes `830`, which crosses the halfway point, so
the reconstruction's own input has **153** of 314 in the reversal half. Both
figures are now asserted explicitly in `verify_ii1.py` so the effect of that one
correction is visible rather than incidental. Neither figure changes the
false-negative conclusion in `docs/methodology.md` gap 3.

## What this does and does not establish

**Established:** the 492/984 palindromic construction, the σ mapping, and the
314-character decode all reproduce from an independent implementation; our
ciphertext transcription is confirmed by a second witness; a third 491-letter
textual variant exists in the standard free e-text.

**Not established:** that this is the designer's actual procedure. The author is
explicit that the reconstruction does not identify Holland's physical edition or
his rule for choosing among eligible numerical positions. The `330→830` reading at
observation 169 was graded *probable* here on 2026-11-03 because every supporting
reading was candidate-aware; **that conditionality was discharged on 2026-11-05** by a
blind reading of the sheet — four fresh contexts, no candidate values, unanimous
`830`, with an in-crop `330` control read correctly (`results/RUN_LOG.md`,
2026-11-05). The complete 314-character result is therefore no longer conditional on
an unverified reading, though it rests on image evidence from one model family rather
than on human inspection of the physical piece.

## Rights

The Swift passage is a transcription of public-domain text from the Alden (1911)
witness and is safe to hold and redistribute; no scan or editorial apparatus is
included. The decoded message is third-party expression that the author
deliberately does not redistribute, and neither do we — `verify_ii1.py` reports its
length and SHA-256 only. Historical solution credit remains with Eileen Novak and
the three other successful 1986 contestants.
