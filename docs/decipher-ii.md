# Decipher II (1985) — three solved, one solved-then-lost

**Status: 2-1, 2-2, 2-3 SOLVED during the contest; 2-4 solved by an unknown entrant and
the solution has since been lost.** Wikipedia's wording is exact: "all four embedded
puzzles were solved, though the solution to the last puzzle has since been lost."

## The four messages

| # | Winner | Key text | Key rule | Plaintext |
|---|---|---|---|---|
| 2-1 | Eileen Novak (+3 others; prize split 4 ways, $6,250 each) | Swift, *Gulliver's Travels* | continuous letters of a passage | a poem about *Bloom County* |
| 2-2 | Tom Chirpich | Heller, *Catch-22* | chapter titles concatenated, string **reversed** | "In memory of John Lennon…" |
| 2-3 | Sharlet Brown (sole correct entrant, full $25,000) | Clavell, *Tai-Pan*, ch. 5 | first letter of every word | "I am paralyzed… it is nuclear war." |
| 2-4 | unknown | **unknown** | unknown | **unknown** |

## Contest timeline, rebuilt from the winner articles (2026-10-10)

Karen's Drive archive (`docs/sources.md`) holds the actual winner-article scans:

- **2-1**: Novak bought the game in August 1985 and solved it on Valentine's Day
  1986; the $25,000 message prize was split among four correct entrants ($250 cash +
  $6,000 check, delivered inside a 400-lb ice sculpture of a dollar sign).
  *Statesman Journal* (Salem, OR), March 25, 1986, "Decipher II game pays off in
  cold cash". At that date $75,000 remained.
- **2-2**: Chirpich (Memphis State chemistry professor; also one of the 36 Decipher
  I winners) solved it by September 1986; AP wire story, e.g. *The Leaf-Chronicle*
  (Clarksville, TN), September 27, 1986. The AP piece gives a figure seen nowhere
  else: Holland "put up **$117,000** in prizes for solving the original version of
  Decipher." One 2-2 clue was **"The first is the last."**
- **2-3**: the accountants opened the entry vault in Virginia on **October 31,
  1986**; Brown (West Allis, WI) was the *only* correct entrant for message three
  and took the full $25,000. *Milwaukee Sentinel*, "She cracks code to win $25,000"
  (Thomas Collins), c. November 1986. Her two monthly hotline clues were:
  **"The letter used most often in the number three is very important to the key"**
  and **"D as in decipher."** (E = 5th letter → chapter 5; D = first letter of
  "decipher" → number the first letter of each word.) She was still working on 2-4
  at the time. This is the article the YouTube commenter @Mintpuppy17 was hunting in
  the Milwaukee Journal Sentinel microfilm — **found**, no library card needed.
- **2-4**: solved by an unknown entrant after that; the solution is lost.

The 2-1 clues preserved in Karen's solutions guide: *"The key to message one, you
see, is from the authors in group C"* · *"492"* · *"A single place has a certain
pattern to create the key"* · *"One way gets you half way there"* · *"S.I.N."*
The 2-1 author list from the same guide: Emily Dickinson, Ernest Hemingway, Sylvia
Plath, Jonathan Swift, Herman Wouk, Victor Hugo, John Steinbeck, Margaret Mitchell,
William Shakespeare, T.S. Eliot, Abraham Lincoln.

The full 2-3 plaintext (per Karen's guide, which transcribed the winner's sheet):
*"I am paralyzed. If I let it touch me I cry. I can comprehend but I cannot act on
my comprehension. I am blind. I am scared. Its aloofness and power is so great, its
magnitude so complete, its consequences so disastrous, its inevitability so real, I
get lost in helplessness but I cannot. I am every human being on Earth and it is
nuclear war."*

Each message carried a $25,000 prize pool, split among all correct entrants (2-1 was
split four ways). 2-2 and 2-3 are why the solver tests reversed streams
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

## "The Source" theory — eliminated 2026-10-10

A YouTube comment theory (@jcortese3300, endorsed by Karen) proposes Michener's
*The Source* as the 2-4 key, or as a pointer layer to one of the eleven listed
authors. Three independent arguments kill it:

1. **Arithmetic.** *The Source* has 17 chapter titles; the *Catch-22*-style
   title-chain rule (`solver/rules.py chapter_title_chain`) yields only **258
   letters**, while 2-4's max index is **1053**. A title chain cannot be the key.
2. **The author list.** Michener is not among the eleven printed 2-4 authors.
   (He *was* on Decipher I's 21-author list — Baldwin & Sherman p. 278 — which is
   likely where the association comes from.)
3. **The photo explained.** The theory's origin is the Sharlet Brown winner photo,
   where *The Source* sits open on her kitchen table. Karen's solutions guide
   checked the visible passage (p. 263, "Level X: In the Gymnasium") against the
   partial solution and found no match; her conclusion: the book was most likely
   just a prop for the photo, and she has emailed the photographer to confirm.

The theory survives only as a passage-level key, which would require the book's
full text — but argument 2 already excludes Michener from 2-4 regardless.

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
