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
surfaces and diffed token-by-token on 2026-10-05; the three Decipher III sequences match
`data/ciphers.json` exactly (two historical transcription errors on solved `2-1` — obs 306
`338→388` caught 2026-10-05 and obs 169 `330→830` identified in Eckman's reconstruction and
blind-verified 2026-11-05 — are documented in `docs/decipher-ii.md` and `data/ii1_corrections.json`).

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
so **3-2 and 3-3 must be searched against both Group A and Group C** (in Decipher II's
rulebook, the four 11-author groups A/B/C/D mapped 1-to-1 onto the four messages —
`2-1` = C, `2-2` = B, `2-3` = D, `2-4` = A — making a 1-to-1 split across Group A and
Group C likely here too, though unconfirmed without the unreleased clues).

## What has been eliminated

**Qualification added 2026-11-03 — read before relying on any elimination below.**
Every elimination in this section was produced by the 21-family *sliding* sweep, which
contains no `S || reverse(S)` palindromic construction. Eckman's reconstruction of 2-1
([doi:10.5281/zenodo.23844582](https://doi.org/10.5281/zenodo.23844582)) establishes that
Holland *did* use that construction, and 153 of 2-1's 314 integers exceed its 492-letter
source — so a sliding-only sweep returns a noise-band negative even on the correct book
and passage. `engine.search_anchored` now covers the construction (`docs/methodology.md`
gap 3). Status of the re-earning:

- **Re-tested under both search shapes** (all negative; see `results/RUN_LOG.md`
  2026-11-03, 2026-11-07, and 2026-11-12 entries):
  - *Doctor Zhivago*, *Foundation*, *I, Robot*, *The Thorn Birds*, and *Cat's Cradle* —
    the five era-verified whole-book paperback scans (*Cat's Cradle* Dell `#11149`,
    59th printing Nov 1984, recovered `181/181` body pages at `92.21%` mean confidence
    and `127/127` chapters on 2026-11-12; swept negative across all 21 sliding + 21
    anchored-palindromic families, exact physical `line-first`/`line-last`, 127-title
    chains, 3-band index-elastic drift, and skip-trigram Viterbi scattered-null scans;
    best `3-1` = −8.7948).
  - **All 58 public-domain / Poe corpus files** — Poe (complete works + 9 splits),
    Faulkner (*The Sound and the Fury*, *Soldiers' Pay*, *As I Lay Dying*), ten
    pre-1931 Christies, Sandburg (*Rootabaga*), five early O'Neill plays, cummings
    (*The Enormous Room*), and the 2-4 public-domain corpus (232 text×cipher runs,
    0 empty-search warnings, all negative, commit `e6de31f`, 2026-11-07).
  - Palindromic chapter-title chains (`chapter-titles-palindrome` in `solver/sweep.py`
    and `Chars|PalFwdRev` in `solver/toc_and_clue_tester.py`).
- **Anchored palindromic family coverage:** `--all-palindromic` in `solver/sweep.py`
  extends `engine.search_anchored` across all 21 rule families (verified on *Cat's Cradle*,
  2026-11-12); earlier 2026-11-03/07 batch runs covered the default 3-family anchored
  set (`letters`, `first-letters`, `last-letters`). See
  [`decipher-ciphertext-patterns.md`](decipher-ciphertext-patterns.md) for structural
  profiles of 3-1, 3-2, and 3-3 (including 3-3's strict without-replacement property
  and the word-initial `E`-depletion analysis).

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
2. **Kurt Vonnegut** for 3-1 — *Cat's Cradle* (Dell Nov 1984) eliminated 2026-11-12;
   *Slaughterhouse-Five* remains top priority (10 numbered chapters where Chapter 10 is
   simultaneously `"10"` and `"End"`, matching Holland's anti-war voice).
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
window: Decipher III was still being sold new in November 1991 at $13.99. See
`docs/sources.md` for the archives checked.

**Primary creator context from Karen Puzzles' 2021 correspondence with Warren Holland Jr.:**
*(Correction: an earlier note here confused the Decipher creator **Warren Holland Jr.**—who
was 29 in 1983 and corresponded directly with Karen Kavett by email for her 2021 Decipher II/III
video—with his father, Warren L. Holland Sr., whose December 2017 obituary is listed in
`docs/sources.md`.)* In his emails to Karen (`-XnCfS3ee8c`), Holland confirmed five primary
facts that frame the remaining search:
1. **None of the three Decipher III ciphers were ever solved.**
2. **The 4th runoff cipher was already created and locked in before launch**—the contest was
   wound down rather than extended because Decipher, Inc. had grown rapidly (*How to Host a
   Murder*, etc.), reviewing monthly submissions was consuming too much of his time, and the
   accounting firm handling entries was overwhelmed.
3. **Original solution & clue records sit deep in warehouse storage** (not destroyed, though
   Holland noted it was unlikely he would go digging for 35-year-old boxes).
4. **Author selection:** When shown the author lists, Holland said he was reading so heavily
   from all of those authors in the mid-1980s that he could no longer recall offhand which
   specific titles he pulled keys from (confirming keys came from pre-1985 / pre-1987 books
   he personally read).
5. **Late cipher Easter egg:** Years later, Decipher included a playable cipher Easter egg on
   a card in its *Fight Club* trading card game (unusable in gameplay until decoded).

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
