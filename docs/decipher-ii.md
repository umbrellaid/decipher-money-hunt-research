# Decipher II (1985) — three solved, one solved-then-lost

**Status: 2-1, 2-2, 2-3 SOLVED during the contest; 2-4 solved by an unknown entrant and
the solution has since been lost.** Wikipedia's wording is exact: "all four embedded
puzzles were solved, though the solution to the last puzzle has since been lost."

## The four messages

| # | Winner | Key text | Key rule | Plaintext |
|---|---|---|---|---|
| 2-1 | Eileen Novak (+3 others; prize split 4 ways, $6,250 each) | Swift, *Gulliver's Travels* | continuous letters of a 492-letter passage, doubled with its own reversal into a 984-position palindromic key | a poem about *Bloom County* |
| 2-2 | Tom Chirpich | Heller, *Catch-22* | chapter titles concatenated, string **reversed** | "In memory of John Lennon…" |
| 2-3 | Sharlet Brown (sole correct entrant, full $25,000) | Clavell, *Tai-Pan*, ch. 5 | first letter of every word | "I am paralyzed… it is nuclear war." |
| 2-4 | unknown | **unknown** | unknown | **unknown** |

## 2-1: Published technical reconstruction (2026)

On October 31, 2026, Christopher A. Eckman published a [non-peer-reviewed
technical reconstruction of Decipher II, Message 1](https://doi.org/10.5281/zenodo.23844582),
with [reproducible Python software](https://github.com/chriseckman/decipher-ii1-reconstruction)
and a [technical workflow overview](https://www.eckmandesign.com/blog/ai-workflow-automation-decipher-ii-message-1/)
(Nov 1, 2026; updated Nov 5, 2026).
The reconstruction uses the tailor paragraph from Part III, Chapter 2 of
Jonathan Swift's *Gulliver's Travels*. Normalizing the passage produces 492
letters; appending its reversal gives a 984-position numerical key. Applied
to the documented corrected working ciphertext transcription, that key
reproduces the complete 314-character message about *Bloom County*.

On November 4, 2026 he published [**Addendum 1: Independent Replication, Textual
Witnesses, and Clue Interpretation**](https://doi.org/10.5281/zenodo.23963541),
written in response to this repository's own verification
(`solver/verify_ii1.py`, `results/eckman-ii1-verification-2026-11-03.md`). It
confirms all 19 of our checks, confirms the third textual witness we identified,
quantifies edition drift more sharply than the original report, and corrects four
claims we had published. Read both documents together; the addendum is where the
evidential limits of the reconstruction are stated most carefully. See
`results/RUN_LOG.md`, 2026-11-05.

**Source witness, independently verified 2026-11-06.** The 492-letter passage comes from
Alden's *Readings in English Prose of the Eighteenth Century* (1911), printed page 97.
Eckman identified three separate digitizations that all carry the identical paragraph and
reproduce the published source SHA-256 `9eeff566…f29d`:

- Library of Congress scan, Internet Archive —
  <https://archive.org/details/readingsinenglis00alde/page/97/mode/1up> (PDF page 115)
- Cornell University Library, Internet Archive —
  <https://archive.org/details/cu31924013335579/page/97/mode/1up>
- Harvard University via Google Books —
  <https://books.google.com/books?id=oLMQAAAAYAAJ&pg=PA97>

We downloaded the djvu text of the first two ourselves and confirmed both: the passage
normalizes to exactly **492 letters** with SHA-256 `9eeff566fe707e39486c1bb119d5c82f19566772706342c44803d6079faef29d`,
byte-identical to `data/gulliver_ii1_passage.txt`. That fixture was originally copied from
the author's repository; its provenance is now primary-source verified rather than
third-party derived, and the 492 reading is confirmed across **three independently
digitized copies** of the same 1911 edition. This does not establish which physical
edition the designer used — only that the 492-letter witness is stable across
digitizations of Alden, while the Gutenberg #829 and Wikisource/1801 witnesses give 491
and 490 (`docs/methodology.md` gap 1).

Eckman's investigation independently identified the correction at observation
306 (`338` to `388`) through decoding analysis and inspection of the puzzle
photograph. During prepublication attribution review, the team found that
this repository had publicly documented the same correction earlier, in
October 2026; the paper explicitly credits that prior contribution.

The correction at observation 169 (`330` to `830`) was graded *probable* by the
original report and by Addendum 1, because every supporting reading until then was
candidate-aware. On 2026-11-05 it was **blind-verified from the puzzle image**: four
fresh contexts with no knowledge of either candidate read the band covering positions
137–197 and all four returned `830` at 169 while correctly reading the genuine `330`
at 148 in the same crop (`results/RUN_LOG.md`, 2026-11-05). The `330` in
`data/ciphers.json` is therefore a transcription error shared with Kavett's
compilation, and the 2-1 decode is no longer conditional on an unverified reading. A
human inspection of the physical piece remains the only stronger check. The
reconstruction does not establish the original designer's exact physical edition or
procedure for choosing among eligible numerical positions: the 314-token ciphertext
exercises **224 of the 492** underlying source positions (139 in the forward half, 122
in the reversal half, 37 in both; **261 of 984** key slots, leaving 268 source
positions unprobed). Two literal-plaintext details documented in Eckman's report (§3.2,
§7) also inform open-cipher solver design: the decoded verse spells *Bloom County*'s
Binkley literally as **`BRINKLEY`** and renders **`PISTACHIO`** without `YAZ` (matching
characters from Berke Breathed's July 15, 1983 strip) — which both explains why Eileen
Novak told the *Statesman Journal* she bought a *Bloom County* book *"to make sure the
names were spelled correctly"* before mailing her entry, and proves that Holland's
plaintexts can contain a 1-letter proper-noun typo (so future word-lattice or
scattered-null solvers should allow edit-1 / OOV proper-name tolerance). Historical
solution credit remains with Eileen Novak and the three other successful 1986
contestants.

## Contest timeline, rebuilt from the winner articles (2026-10-10)

Karen's Drive archive (`docs/sources.md`) holds the actual winner-article scans:

- **2-1**: Novak bought the game in August 1985 and solved it on Valentine's Day
  1986; the $25,000 message prize was split among four correct entrants ($250 cash +
  $6,000 check, delivered inside a 400-lb ice sculpture of a dollar sign).
  *Statesman Journal* (Salem, OR), March 25, 1986, "Decipher II game pays off in
  cold cash". At that date $75,000 remained. **2026-10-18: both scans fully
  transcribed** (`results/statesman-journal-1986-03-25-transcription.md`) —
  winner confirmed as **Eileen** Novak; the article gives **no extraction-rule
  detail** beyond "492" → a *Gulliver's Travels* passage and a Bloom County
  poem plaintext. That contemporary article did not describe the 2-1
  extraction rule; a modern technical reconstruction is linked above.
- **2-2**: Chirpich (Memphis State chemistry professor; also one of the 36 Decipher
  I winners) solved it by September 1986; AP wire story, e.g. *The Leaf-Chronicle*
  (Clarksville, TN), September 27, 1986. The AP piece reports that Holland "put up
  **$117,000** in prizes for solving the original version of Decipher" — a figure
  taken directly from page 2 of the Decipher II Instruction Book (*"Decipher II's
  Predecessor"*, in Karen's Drive archive), which states *"The winners shared in an
  award of over $117,000"* ($36 \times \$3,251.71 = \$117,061.56$ after accrued
  interest). One 2-2 clue was **"The first is the last."**
- **2-3**: the accountants opened the entry vault in Virginia on **October 31,
  1986**; Brown (West Allis, WI) was the *only* correct entrant for message three
  and took the full $25,000. *Milwaukee Sentinel*, "She cracks code to win $25,000"
  (Thomas Collins), c. November 1986. Her two monthly hotline clues were:
  **"The letter used most often in the number three is very important to the key"**
  and **"D as in decipher."** (E = 5th letter → chapter 5; D = first letter of
  "decipher" → number the first letter of each word.) She was still working on 2-4
  at the time. This is the article the YouTube commenter @Mintpuppy17 was hunting in
  the Milwaukee Journal Sentinel microfilm — **found**, no library card needed.
- **2-4**: solved by an unknown entrant after that (confirmed to Karen Kavett by creator
  Warren Holland Jr. in 2021, with original records buried in warehouse storage); the
  solution is lost. In the Decipher II Instruction Book (pp. 4–6, `Decipher-II-rulebook-4.jpg`..`6.jpg`
  in Karen's Drive archive), the four printed 11-author groups map 1-to-1 onto the four
  messages (`2-1` = Group C, `2-2` = Group B, `2-3` = Group D, **`2-4` = Group A**);
  monthly clues were distributed on `(804) 623-CLUE` (`804-623-2583`, long defunct — do
  not call); entries were audited by Norfolk accounting firm **Frederick B. Hill &
  Company** (1630 United Virginia Bank Building, Norfolk, VA 23514) with solutions
  locked in a New York City bank vault (18-month charity timeout); and Rule `3f`
  specifies that as each message was solved its solution was released to the media and
  mailed to anyone sending a self-addressed stamped envelope. Additional archival clues
  survive in the Decipher III rulebook: in recounting
  how Decipher I/II prizes were awarded, it mentions the giant dollar-sign ice block
  (Novak, 2-1), a huge Decipher-branded bag delivered by **armored car with armed guards**,
  and winners honored at a **New York press conference followed by dinner at Tavern on the
  Green** in Central Park—potential search handles in 1986–1987 local or trade press for
  identifying the 2-4 winner or remaining 2-1 co-winners.

The 2-1 clues are **all five printed verbatim** in the Decipher II Instruction Book
(pp. 4–5, `Decipher-II-rulebook-4.jpg` and `5.jpg`, under *"Initial Clues For Message
#1:"* — settling Addendum 1 §5's question of whether *"492"* or *"S.I.N."* came from a
later hotline recording): *"The key to message one, you
see, is from the authors in group C"* · *"492"* · *"A single place has a certain
pattern to create the key"* · *"One way gets you half way there"* · *"S.I.N."*
Directly above them (p. 4), the rulebook frames the clue list explicitly: ***"Some of
the clues may pertain to the key while others pertain to the message itself."***
The 2-1 author list (Group C, p. 4): Emily Dickinson, Ernest Hemingway, Sylvia
Plath, Jonathan Swift, Herman Wouk, Victor Hugo, John Steinbeck, Margaret Mitchell,
William Shakespeare, T.S. Eliot, Abraham Lincoln.

### The 2-1 clues, read against the now-known mechanism (2026-11-03)

Three of the five were sitting in this repository unexplained. Eckman's
reconstruction (linked above) decodes them:

| Clue | Reading now supported |
|---|---|
| *"492"* | Not a passage locator — the **letter count of the normalized source passage** `S`, i.e. the *half*-length. The key is 984 positions. |
| *"A single place has a certain pattern to create the key"* | One passage ("a single place"), and the "certain pattern" is the doubling. |
| *"One way gets you half way there"* | **The palindromic construction, stated outright.** Reading one direction covers 492 of 984 positions — exactly half. The reversal half covers the rest. |
| *"…from the authors in group C"* | Swift is in the Group C list above. Consistent, and already known. |
| *"S.I.N."* | **Still unexplained.** Because the rulebook (p. 4) states that *"Some of the clues may pertain to the key while others pertain to the message itself"* and the other four printed clues all describe the key, *"S.I.N."* may pertain to **the message/subject itself** rather than an unrecovered key rule; key-side candidates (a reversal/direction indicator, an initials acrostic over the passage or its source, or a numbering convention) also remain open. No reading is asserted here. |

`solver/body_scan.py` has inferred the doubling since **2026-10-18** (commit
`7ac346b`; the Gemini Q&A prompting it was the evening of 2026-10-17) from
"N_max 980 = 2 x 490" and the "half way there" clue, and implements `HalfFwdRev`;
it was built on word-initials over chapter windows rather than continuous letters
over a paragraph, so it could not reach this key. See `docs/methodology.md`, gap 3.

**Qualification added 2026-11-05, from Addendum 1
([doi:10.5281/zenodo.23963541](https://doi.org/10.5281/zenodo.23963541)).** These
readings are *clue-consistent interpretations*, **not independent confirmation of the
mechanism**. Eckman's own experiment records show that "492" and "One way gets you
half way there" **influenced the development of the bidirectional construction**, so
they were inputs to it rather than external evidence for it. Three of the five clues
are consistent with a key drawn from one contiguous passage and extended symmetrically
by its reversal; the first clue concerns author choice and was already compatible with
the 1986 identification of the book; **none of them establishes the designer's intent.**
An earlier version of this section, and our public comment on issue #1, called the clue
readings "contemporaneous corroboration" — that framing is withdrawn.

**Carry-over to Decipher III.** 3-1's printed clue *"End"* has until now been read
only as "test reversed streams" (`docs/methodology.md`). It has a second reading:
the **reversal half of a palindromic key**. Both readings should be tested for 3-1,
and the palindromic one is not currently covered by the sweep path.

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

- **Eliminated** (31 texts × 21 sliding rule families × every offset × both directions,
  **plus** the 2026-11-07 sentence/word-anchored palindromic `S || reverse(S)` sweep and
  chapter-title chains; see `results/RUN_LOG.md`): Nathaniel Hawthorne, Thomas Hardy,
  Elizabeth Barrett Browning, Jules Verne, Walt Whitman, Henry David Thoreau. Best score
  across all of it stays deep in the noise band.
- **Remaining suspects, all in copyright:** John Updike, Colleen McCullough (*The Thorn
  Birds* whole-book Avon scan swept negative under sliding, anchored-palindromic, and
  3-band drift rules; other pre-1985 McCullough titles remain), John Irving, Robert Ludlum,
  Louis L'Amour. See [`decipher-ciphertext-patterns.md`](decipher-ciphertext-patterns.md)
  for 2-4's structural fingerprint (zero literals, three 3-step `+1` runs `737–739`,
  `154–156`, `544–546`, and the 8-token round-hundred cluster at positions `20–27`).

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

**That re-transcription was incomplete, and this paragraph said so too confidently.**
On 2026-11-05 a blind reading of the Message 1 sheet (`results/RUN_LOG.md`,
2026-11-05) found a **second** error the 2026-10-05 pass missed: index 168 (observation
169) is stored as `330` but the sheet shows `830`. Four blind readers returned `830`
unanimously and correctly read the genuine `330` two rows above in the same crop, so
this is not a glyph-confusion artifact. The `330` is shared with Kavett's compilation,
which is why the fingerprint cross-check matched exactly — a shared error cancels.
Lesson recorded: a re-transcription diffed against the sequence it was meant to check
confirms agreement, not correctness; and a diff that finds exactly one error in 314
values should have prompted a second look at the values that matched.

In the shared scans, `Decipher-III-puzzle-front.jpg` is the side printed "continued
from the front," and `Decipher-III-puzzle-back.jpg` is the side printed "continued
on the back." For Decipher II, the file named `-front` holds Message 1 only, and
the file named `-back` holds Messages 2, 3, and 4. Read the message numbers on the
scan. The filenames are a poor guide to which physical side is which.

### 2-4 candidate status after the 2026-10-24/27 Thorn Birds scans
*The Thorn Birds* (Avon, ISBN 0380018179) body-scanned twice: 2026-10-24 (ScanTailor
route, INCONCLUSIVE) and 2026-10-27 (fixed pipeline, 7 parts, dups removed). **No
readable plaintext for 2-4 under any tested family — NEGATIVE, with an OCR-noise
caveat** (mean conf 77; 128 pages under 70, clustered in Parts Two and Six; rescan
list: `scanning/book-scans/the-thorn-birds/RESCAN_LIST_2026-10-27.md`). McCullough
drops below the untested candidates (*Rabbit, Run* etc.) but is not eliminated.
