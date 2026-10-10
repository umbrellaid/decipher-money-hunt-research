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
- **Paper:** Baldwin & Sherman, *Cryptologia* (1990); link in `docs/sources.md`.

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
Two items of value: the **p. 17 referee footnote** in the Baldwin & Sherman paper
("Cosmos is copyrighted… did Holland use 'in the public domain' colloquially?") and the
**2009 Fight Klub "Decipher This" homage** — Holland's later card-game puzzle reused the
original solution text as its key ("what was once one thing is now another"), confirming
that Holland recycles his own material across puzzles.
