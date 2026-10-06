# Decipher II (1985) — three solved, one solved-then-lost

**Status: 2-1, 2-2, 2-3 SOLVED during the contest; 2-4 solved by an unknown entrant and
the solution has since been lost.** Wikipedia's wording is exact: "all four embedded
puzzles were solved, though the solution to the last puzzle has since been lost."

## The four messages

| # | Winner | Key text | Key rule | Plaintext |
|---|---|---|---|---|
| 2-1 | Eileen Novak | Swift, *Gulliver's Travels* | continuous letters of a passage | a poem about *Bloom County* |
| 2-2 | Tom Chirpich | Heller, *Catch-22* | chapter titles concatenated, string **reversed** | "In memory of John Lennon…" |
| 2-3 | Sharlet Brown | Clavell, *Tai-Pan*, ch. 5 | first letter of every word | "I am paralyzed… it is nuclear war." |
| 2-4 | unknown | **unknown** | unknown | **unknown** |

Each message carried $25,000. 2-2 and 2-3 are why the solver tests reversed streams
and both plaintext directions. The 2-2 key was a reversed chain of chapter titles.
That rule is not one of the 21 families in `solver/rules.py`.

## 2-2, checked in the solver

`solver/validate.py` rebuilds the key from the 42 chapter titles in
`data/catch22_chapter_titles.json`. The letters of those titles are concatenated,
the string is reversed, and the decoded letters are read backwards. The result is

`INMEMORYOFJOHNLENNONNOBODYTOLDMETHEREDBEDAYSLIKETHESE`

which is the solved message, *In memory of John Lennon nobody told me there'd be
days like these*. The book text is not in this repository. An earlier offline run
planted that same stream among 1,910,457 decoy numbering starts. It ranked **#1**,
at −7.99 against −8.06 for the best decoy. That calibration (English ≈ −7.9…−8.0,
noise ≤ −8.6) is what makes every "no hit" below meaningful. The rank run is not
repeated by `validate.py`. The decode is.

## 2-4: what is now eliminated

Cipher 2-4 is 170 numbers, max index 1053. Its author list (Karen's document) is eleven
names; six are public domain and have been swept exhaustively:

- **Eliminated** (31 texts × 21 rule families × every offset × both directions, plus
  chapter-title chains): Nathaniel Hawthorne, Thomas Hardy, Elizabeth Barrett
  Browning, Jules Verne, Walt Whitman, Henry David Thoreau. Best score across all of
  it: **−8.77**, deep in the noise band.
- **Remaining suspects, all in copyright:** John Updike, Colleen McCullough,
  John Irving, Robert Ludlum, Louis L'Amour.

So the lost solution's key is most likely a pre-1985 novel by one of those five.
`docs/check-your-own-book.md` is the route; a used *Rabbit, Run* or *The Thorn Birds*
is a $5 experiment.

## A transcription correction made here

On 2026-10-05 every one of the seven Decipher sequences was re-transcribed
independently from the printed puzzle surfaces and diffed against `data/ciphers.json`.
Six matched exactly; **2-1 had one error** — index 305 was stored as 338 but the
printed puzzle reads 388 (confirmed at 3× magnification). It is corrected in this
repository. 2-1 is a solved puzzle, so nothing downstream depended on it, but any
future re-validation of 2-1 against the Swift key would otherwise have failed for a
non-mechanical reason.

In the shared scans, `Decipher-III-puzzle-front.jpg` is the side printed "continued
from the front," and `Decipher-III-puzzle-back.jpg` is the side printed "continued
on the back." For Decipher II, the file named `-front` holds Message 1 only, and
the file named `-back` holds Messages 2, 3, and 4. Read the message numbers on the
scan. The filenames are a poor guide to which physical side is which.
