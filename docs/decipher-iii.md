# Decipher III (1987) — unsolved, $100,000 never claimed

Three messages printed on a two-sided 150-piece golden jigsaw. No message was ever
solved; the contest lapsed; Wikipedia, Puzzling StackExchange and the collector forums
all agree there is no public record of a solve. The prize structure was unusual:
solving a message won only *eligibility* for a first-to-deliver runoff on a secret
fourth message, for the whole $100,000 in solid gold.

## The three ciphers (full sequences in `data/ciphers.json`)

| # | Tokens | Numbers | Max index | Literal letters | Notes |
|---|---|---|---|---|---|
| 3-1 | 170 | 164 | 516 | E×5, Z×1 | `487` twice **adjacent** → a double letter in the plaintext; 505, 285, 335 repeat |
| 3-2 | 117 | 114 | 416 | E×3, Y×2 | unusually short plaintext |
| 3-3 | 159 | 156 | 721 | E×3 | longest key-stream requirement |

All seven Decipher sequences (II and III) were re-transcribed from the printed puzzle
surfaces and diffed token-by-token on 2026-10-05; they match `data/ciphers.json`
exactly (one 2-1 error was found and fixed — see `docs/decipher-ii.md`).

## The author groups — printed in the rulebook, recovered 2026-10-05

Earlier analyses believed the A/B/C groupings existed only on the dead 1-900 hotline.
They are printed on rulebook page 6:

| # | Group A | Group B | Group C |
|---|---|---|---|
| 1 | Lawrence Sanders | Richard Nixon | Henry Kissinger |
| 2 | Joseph Heller | Bob Woodward | Thomas Wolfe |
| 3 | William F. Buckley | Robert Ludlum | Sylvia Plath |
| 4 | Aleksandr Solzhenitsyn | Kurt Vonnegut, Jr. | Alex Haley |
| 5 | Bill Cosby | Truman Capote | Norman Mailer |
| 6 | William Faulkner | Yoko Ono | Eugene O'Neill |
| 7 | Tom Wolfe | Isaac Asimov | e.e. cummings |
| 8 | Agatha Christie | Leon Uris | James Clavell |
| 9 | George Orwell | Edgar Allan Poe | Martin Cruz Smith |
| 10 | John Kenneth Galbraith | Boris Pasternak | Ken Follett |
| 11 | Carl Sandburg | David Halberstam | Mario Puzo |

Message #1's printed initial clues are: *"The author you seek to find the key is from
the group that's labeled B."* · *"10"* · *"End"*. So **3-1 = Group B**. Clues for
messages 2 and 3 were only released after message 1 was solved — which never happened —
so **3-2 and 3-3 must be searched against both Group A and Group C**.

## What has been eliminated

**Qualification added 2026-11-03 — read before relying on any elimination below.**
Every elimination in this section was produced by the 21-family *sliding* sweep, which
contains no `S || reverse(S)` palindromic construction. Eckman's reconstruction of 2-1
([doi:10.5281/zenodo.23844582](https://doi.org/10.5281/zenodo.23844582)) establishes that
Holland *did* use that construction, and 153 of 2-1's 314 integers exceed its 492-letter
source — so a sliding-only sweep returns a noise-band negative even on the correct book
and passage. `engine.search_anchored` now covers the construction (`docs/methodology.md`
gap 3). Status of the re-earning:

- **Re-tested under both search shapes** (198 M anchored pairs, all negative,
  `results/RUN_LOG.md` 2026-11-03 later entry): *Doctor Zhivago*, *Foundation*,
  *I, Robot*, *The Thorn Birds* — the four era-verified whole-book scans.
- **NOT yet re-tested**: Poe, Faulkner, the pre-1931 Christies, Sandburg, O'Neill and
  cummings below, and the chapter-title chains. Those eliminations stand on the sliding
  sweep alone and must be treated as provisional.
- **Cannot be tested at whole-book grade**: *Cat's Cradle* (Vonnegut), ranked #2 for 3-1
  below. **Corrected 2026-11-04:** the old "82 missing chapters" diagnosis was a bad
  split, not missing scans. Re-ingest reduced the boundary gap to **31 chapters**, but
  the OCR remains only about **85–90% accurate at word level**, so the text still cannot
  support an exact whole-book cipher sweep. The remaining limitation is OCR/text quality,
  not the superseded 82-chapter split diagnosis; see `results/RUN_LOG.md`.
- The anchored scan covers only `letters`, `first-letters` and `last-letters`. The
  every-Nth and word-Nth-letter families in palindromic form remain untested for
  everything, so no elimination below is complete with respect to this mechanism.

- **Edgar Allan Poe for 3-1**: complete works, 21 rule families, every numbering start,
  both directions (best −8.84, noise). Poe is not in the answer.
- **The public-domain members of Groups A and C for 3-2/3-3**: Faulkner (*The Sound and
  the Fury*, *Soldiers' Pay*, *As I Lay Dying*), ten pre-1931 Christies, Sandburg
  (*Rootabaga*), five early O'Neill plays, cummings (*The Enormous Room*) — 21 rule
  families each (best −8.54 / −8.70, noise). The Standard Ebooks file is
  `faulkner_se_soldierspay.txt`. The printed rulebook names Faulkner and does not
  print this title. The novel's title is *Soldiers' Pay*.
- Chapter-title chains (the *Catch-22* rule) for all three messages. Those results
  are in `results/sweep_*_chains.json`. `solver/sweep.py` tests that rule when a
  `.chapters.json` file is present. A run without that file does not repeat this
  elimination. Puzzle 2-2 itself is checked in `solver/validate.py`.

Full logs: `results/RUN_LOG.md`.

## What remains, ranked by prior probability

1. **Joseph Heller** and **James Clavell** — both already used as keys in Decipher II
   (2-2 and 2-3). Holland returned to favourites. Heller: *Something Happened*,
   *Good as Gold*, *God Knows*. Clavell: *Shōgun*, *Noble House*, *King Rat*.
2. **Kurt Vonnegut** for 3-1 — *Slaughterhouse-Five* matches Holland's taste for
   thematically resonant keys (war, memory); the "10" and "End" clues fit a
   chapter/word-10 or every-10th reading.
3. ~~**Isaac Asimov** for 3-1~~ — *Foundation* eliminated 2026-10-21; *I, Robot*
   (Fawcett Crest 1970) eliminated 2026-10-26: **51/51 windows fail the 3-1 zero-Z
   necessary condition** and no family decoded (RUN_LOG 2026-10-26). Remaining Asimov
   scan-list titles: *Foundation's Edge*, *Union Club Mysteries*, *The Naked Sun*.
4. The rest of Group B for 3-1 (Nixon, Woodward, Ludlum, Capote, Uris, Pasternak,
   Halberstam, Ono) and the in-copyright members of A and C for 3-2/3-3 (Sanders,
   Buckley, Solzhenitsyn, Cosby, Wolfe; Kissinger, Plath, Haley, Mailer, Smith,
   Follett, Puzo), plus post-1931 Faulkner and Christie.

Every one of these is in copyright and DRM-locked as an ebook. The route is
`docs/check-your-own-book.md`.

## The clue archive that would collapse the search

The rulebook and the 1990 *Cryptologia* review both state that Decipher, Inc.
**periodically eliminated names from the author lists** and released clues monthly to
a recorded hotline, (804) 627-GOLD, which is 804-627-4653. That number is from
1987 and is long defunct. Do not call it. A Palm Beach Post article of 20 December
1990 also printed (800) 654-3939. That number is from the same contest period and
is long defunct. Do not call it. The same clues also went to the media and to
retailers. Those monthly newspaper
clue columns (1987–1991) have never been recovered; finding even a few would cut the
33-author pool to a handful per message. Karen's own clipping archive (Drive,
"Decipher III Articles" folder, cataloged in `docs/sources.md`) was checked on
2026-10-10: it holds five 1987–1991 clippings, and **all five are retail ads or
gift-guide mentions — none prints a monthly clue**. The ads do fix the sales
window: Decipher III was still being sold new in November 1991 at $13.99. The clue
hunt therefore has to go to the subscription newspaper archives.
See `docs/sources.md` for the archives to
search. Warren Holland, the creator, died in December 2017; the company collapsed by
2008 after an internal embezzlement, so the family and any surviving company records
are the only human lead left.

**2026-11-01 — the newspaper route is closed (trial run, consumer + Publisher Extra).**
Full method and results in `docs/newspapers-com-sweep-2026-10-31.md`. Summary: the
calibration gate passed 4/6 and both misses were coverage gaps, not search blindness —
the Virginian-Pilot holds **nothing from 1964–2025** on newspapers.com (its advertised
1899–2026 span is marketing), and the Milwaukee archive has no 1986, so kit Group A
was impossible on this archive from the start. Site-wide and paper-scoped queries for
1987–1991 produced no recurring clue column; the apparent 1988-04-22..28 "Decipher
hotline" cluster across five papers resolves to a **single national Sunday ad campaign**
(Youth Beat mail-order), not syndicated editorial. The Palm Beach Post 1990-12-20
gift-guide item states the mechanism plainly: the puzzles "can be solved in sequence
from **monthly clues available on the Decipher III Hotline**". Working conclusion: the
monthly clues were a **hotline product, not a newspaper column**; newspapers carried
launch coverage, gift guides and ads. The hotline recordings are lost, so the
elimination notices that would have collapsed the author pool are now best regarded as
unrecoverable except through a human lead. One search handle remains untested outside
1984 Detroit: the column title **"Deciphering clues"** (see `docs/decipher-i.md`).

## Two honest caveats

- **Nulls.** The rulebook teases that messages may contain inserted meaningless
  letters. If they are scattered rather than clustered, no scoring statistic in this
  repository can recover them (`solver/validate.py` asserts this limitation); a
  partial-word back-solver would be needed.
- **Editions.** Numbering depends on the exact printing. A sweep miss on a late
  reprint is not proof of innocence.
