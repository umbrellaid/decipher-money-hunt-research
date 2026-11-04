# Independent verification of the Eckman 2-1 reconstruction (2026-11-03)

**Verdict: the reconstruction reproduces exactly, and our own ciphertext
transcription is confirmed against it. A third textual witness is reported that
the published paper does not cover.**

Eckman, C. A. (2026). *An Independent Reconstruction of Decipher II, Message 1
(1985–86).* Zenodo, 31 Oct 2026. https://doi.org/10.5281/zenodo.23844582
Software: https://github.com/chriseckman/decipher-ii1-reconstruction (v1.0.0, MIT).

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

Two independent transcriptions of the 2-1 ciphertext now exist: ours, read from
the printed puzzle surface at 3× magnification on 2026-10-05, and his, taken via
Karen Kavett's public compilation. **They agree on all 314 values** — the
canonical fingerprint of our original sequence, with observation 306 reverted to
its as-printed `338`, reproduces his published input hash exactly.

This is the first time the 2-1 numerical ciphertext has been confirmed by a
second independent reading. It retires the `338`/`388` question entirely and it
means `docs/methodology.md` gap 2 (OCR/typing errors) is closed *for 2-1*. It does
not close gap 2 for the four unsolved ciphers, which have no second witness.

## New finding: a third witness at 491 letters

The paper compares two witnesses of the tailor paragraph — Alden (1911) at 492
normalized letters, and a Wikisource transcription attributed to an 1801 edition
at 490. **Project Gutenberg #829, the e-text most likely to be swept, gives 491**,
and differs from Alden at *two* independent places:

| Position | Alden (492) | Gutenberg 829 (491) | Effect |
|---|---|---|---|
| 94 | `take my measure` | `take measure` | −2 letters |
| 232 | `with rule and compasses` | `with a rule and compasses` | +1 letter |

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
his rule for choosing among eligible numerical positions, and the `330→830`
reading at observation 169 remains *probable* — his supporting readings were
candidate-aware rather than blind. Our decode reproduces his published hash, so it
inherits that conditionality: **the complete 314-character result is conditional on
the 830 reading.** A `330` reading leaves one character differing.

## Rights

The Swift passage is a transcription of public-domain text from the Alden (1911)
witness and is safe to hold and redistribute; no scan or editorial apparatus is
included. The decoded message is third-party expression that the author
deliberately does not redistribute, and neither do we — `verify_ii1.py` reports its
length and SHA-256 only. Historical solution credit remains with Eileen Novak and
the three other successful 1986 contestants.
