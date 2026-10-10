# Decipher I (1983) — solved

**Status: SOLVED (1985).** The only one of the four contests with a published,
peer-reviewed solution. The published solution is the worked example the later
contests are compared with.

## The puzzle

Karen's video describes the contest as inspired by the Beale cipher papers. A golden jigsaw with a multiple-substitution cipher on the back: 376 numbers (our
transcription of message "2-1"'s predecessor; the sequence is in Karen Puzzles' master
document). Prize: $100,000, split among 36 winners at about $3,251.71 each.

## The solution

- **Solvers:** MIT graduate students Robert Baldwin and Alan Sherman, with Lisp
  programs on a Symbolics 3600, over a weekend.
- **Key text:** Carl Sagan, *Cosmos*, chapter 6.
- **Key rule:** skip the first 36 words, then number the **first letter of every word**
  consecutively, continuing across line breaks.
- **Plaintext:** e.e. cummings, "A Poet's Advice" —
  "Almost anybody can learn to think or believe or know, but not a single human being
  can be taught to feel…"
- **Paper:** Baldwin & Sherman, "How we solved the $100,000 Decipher Puzzle (16 hours
  too late)", *Cryptologia* 14(3), July 1990, pp. 258–284. Full scanned PDF is free
  at UMBC (link in `docs/sources.md`).

## What the full paper adds (read 2026-10-10)

The contest timeline (paper pp. 278–280): the original deadline of March 1, 1984
passed unsolved; the contest was extended to February 28, 1985 and then month to
month. From May 1, 1984 a recorded hotline eliminated **two authors per month** and
added $1,000/month to the prize; the 21-author list included Woody Allen, William F.
Buckley, Norman Mailer, **James Michener**, and Carl Sagan. By January 1985 the list
had narrowed to Sagan plus one other. A massive final clue in February 1985 produced
**36 correct solutions in March 1985** — each winner received $3,251.71 and a T-shirt.
The winners included a farmer, two coal miners, a college math teacher, a biochemist,
a psychologist, a medical student, and a 15-year-old girl. Holland received over
1,000 solutions in total and roughly 250,000 hotline calls.

The exact extraction spec (paper p. 279, Figure 8): the key stream is the first
letters of **all** words of *Cosmos* chapter 6, starting at page 137 with "first ages
of the world…"; hyphenated words count as one word; numerals, abbreviations,
footnotes and captions are deleted. The plaintext is a passage from "A poet's advice
to students" by **E.E. Cummings** — who is also on Decipher III's author list
(Group C), a second instance of Holland re-using his own material (cf. the Fight
Klub finding in `data/decipher_youtube_comments_digest.md`).

The referee footnote quoted in the YouTube comments is **footnote 7, journal p. 278**
(PDF page 21 of the UMBC scan), verbatim: *"An anonymous referee pointed out that
Cosmos is copyrighted and hence not in the public domain. In clue 1 did Holland use
the phrase 'in the public domain' for its colloquial meaning of 'publicly
available'?"* (The commenter's "p. 17 footnote" was a misremembering of "footnote 7".)

**The Holland-surname theory is dead.** In a July 6, 1989 phone call with Sherman
(paper p. 280), Holland said the clues were designed with multiple levels of
interpretation and the "obvious" reading is usually wrong (clue 5 = vowel vs.
consonant, not alphabet position; clue 4's cube = chapter 6; "novel" meant both
"book" and "new and unusual"). Crucially: *"The picture of a cube in Cosmos, chapter
10 and the references to the country Holland in chapter 6 were simply coincidences.
There is no relationship between Warren Holland and Colonel J. J. Holland."* So the
author-centric "the key chapter points back at the creator" strategy articulated in
the YouTube replies (@Chaotic_Pixie) is refuted by the creator himself. As of 1989
Holland had no plans for a Decipher IV; he was focused on "How to Host a Murder".

## Why it matters here

1. The Decipher III rulebook reprints this exact construction with a 56-word worked
   passage and three sample ciphers for the word CODES. That example is the solver's
   built-in regression test — see `docs/methodology.md`.
2. The contest's **elimination mechanic** is documented by the solvers themselves:
   "Two authors would be eliminated from the list each month." The same mechanic
   applied to Decipher III ("Periodically, names are eliminated from the author list",
   *Cryptologia* 14(2), 1990) — and those monthly elimination notices are the single
   most valuable unrecovered artifact for the unsolved ciphers.
3. It proves the whole class is beatable by 1980s hardware given the key text. The
   modern blocker is not computation; it is access to in-copyright books.

## The MIT paper's caution, still true

Different **printings and editions** of the same book shift the numbering. Their
program had to tolerate edition variance; ours does so with a sliding numbering start,
but a revised or abridged edition can still defeat a sweep. If you scan your own copy
of a suspect book (see `docs/check-your-own-book.md`), prefer a printing contemporary
with the contest.

## Notes from 2026-10-09 (night) — YouTube comment sweep of both Decipher videos

All 688 top-level comments on the Decipher I video and all 297 on the Decipher II/III
video were harvested (InnerTube API method) and digested in
[`data/decipher_youtube_comments_digest.md`](../data/decipher_youtube_comments_digest.md).
Two items of value: the **referee footnote** in the Baldwin & Sherman paper
("Cosmos is copyrighted… did Holland use 'in the public domain' colloquially?" —
located: footnote 7, journal p. 278, quoted above) and the
**2009 Fight Klub "Decipher This" homage** — Holland's later card-game puzzle reused the
original solution text as its key ("what was once one thing is now another"), confirming
that Holland recycles his own material across puzzles.
