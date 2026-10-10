# Decipher I & II/III — YouTube comment sweep digest

Source videos (Karen Puzzles):
- *The $100,000 Puzzle That Took Two Years to Solve* (Decipher I) — https://www.youtube.com/watch?v=meaUE2b5whI
- *The $100,000 Puzzles That Were NEVER SOLVED* (Decipher II & III) — https://www.youtube.com/watch?v=-XnCfS3ee8c

Sweep performed 2026-10-09 (night) with the same InnerTube continuation-API method as
the Money Hunt sweep (the comment UI does not load in the owner's browser).

Coverage: **688 of 688** top-level comments (Decipher I) and **297 of 297**
(Decipher II/III). Raw dumps live in the private workspace
(`work_p10/dec1_comments.json`, `work_p10/dec23_comments.json`) and are not published.

**Reply expansion, 2026-10-10 (Kimi session):** all reply threads were then expanded
via the InnerTube `next` endpoint (the 2026 comment format delivers text in
`commentEntityPayload` entities and nests reply continuations under
`replies.commentRepliesRenderer.subThreads`). Yield: **105 replies** across 44
threads (Decipher I) and **50 replies** across 22 threads (Decipher II/III),
100 % fetched with text, saved privately as `work_p10/dec1_replies.json` and
`work_p10/dec23_replies.json`. Findings below.

## Findings of value

1. **Baldwin & Sherman paper footnote, located** (@loqueestamal3465, Decipher I
   comments): the Cryptologia paper's p. 17 footnote quotes an anonymous referee —
   *"Cosmos is copyrighted and hence not in the public domain. In clue 1 did Holland
   use the phrase 'in the public domain' for its colloquial meaning of 'publicly
   available'?"* The commenter also notes the key insight the MIT team missed even
   after the solution was published: the author list pointed to authors **quoting**
   a public-domain text (Wilkins 1638), not to public-domain authors.
2. **Fight Klub homage** (@frostboy16, Decipher I comments): Decipher's later trading-
   card game *Fight Klub* (2009) included a card "Decipher This" encoded similarly,
   with a prize from Warren Holland and cryptic hints; it took ~2 years to solve. One
   critical clue: *"what was once one thing is now another"* — the new puzzle's key
   text was the original Decipher's **solution text**. Relevance: Holland re-uses his
   own material across puzzles, which mildly supports the "Holland returns to
   favourite authors" prior used for Decipher III (Heller/Clavell).
3. **Karen's own follow-up comment** (Decipher I, pinned-adjacent): she reconsiders
   whether the puzzle was fair at all — the key text starts mid-paragraph halfway
   through a long book, unfindable without a computer exhaustively checking every
   possibility; "it was basically impossible to be found until Holland revealed the
   final clue that massively narrowed down the possibilities." Useful framing for how
   Decipher III's much larger search space was ever meant to be tackled.
4. **Catch-22 corroboration** (@dfw-k6z, Decipher II/III comments): Group B author
   #8 is listed as Washington Irving in some lists; in *Catch-22* the protagonist's
   pseudonyms are "Washington Irving / Irving Washington", and reverse logic is a
   theme of the book — "so it's only right to have the cypher in reverse." Neat
   after-the-fact fit for the reversed chapter-title rule of 2-2. (Treat as
   apocryphal colour, not evidence.)
5. No commenter on either video claims any knowledge of the lost 2-4 solution or of
   Decipher III progress beyond what the repo already documents; no new documents,
   photos, or leads surfaced. The typewriter-ribbon cluster of comments merely
   explains the Stimson story for general viewers.

## Findings from the reply expansion (2026-10-10)

1. **The Cosmos key text was edition-dependent** (@ballookey thread, Decipher I):
   a November 1985 paperback printing of *Cosmos* opens chapter 6 with only two
   quotations — the third epigraph (the Wilkins 1638 passage used as key text) is
   missing. Karen's reply: *"Wild! I wonder why and when they cut that quote out of
   the book."* Practical consequence: anyone working Decipher III with a physical
   book must pin the **exact edition/printing**, not just the title; and the 1984
   solver pool was split by which printing they owned.
2. **Author-centric search strategy, articulated but now refuted** (@Chaotic_Pixie,
   replying under Karen's pinned fairness comment): the Decipher I key text sat in
   the chapter whose subject was named **Holland** — the creator's own surname — so
   "look at books that somehow relate to the author" is a rational first move.
   **Refuted by the creator**: in his July 6, 1989 phone call with Alan Sherman
   (Baldwin & Sherman, *Cryptologia* 14(3), p. 280), Holland stated that the
   Holland-country references in *Cosmos* chapter 6 "were simply coincidences" and
   that there is "no relationship between Warren Holland and Colonel J. J.
   Holland." Do not weight creator-surname wordplay in Decipher III priors.
3. **"The Source" theory for the lost 2-4 — ELIMINATED 2026-10-10** (@jcortese3300
   thread, Decipher II/III): the parent comment argues Michener's *The Source* was a
   Decipher II key text by its title alone ("the source of the puzzle cipher"),
   possibly as a *pointer* layer. Karen's reply blessed it ("That's a solid
   theory!"). It is now ruled out on three grounds — see `docs/decipher-ii.md`:
   (a) the 17-chapter title chain is 258 letters, far short of 2-4's max index 1053;
   (b) Michener is not one of the eleven printed 2-4 authors (he *was* on Decipher
   I's 21-author list, the likely source of the association); (c) the theory's
   origin is the Sharlet Brown winner photo, where the open *Source* was almost
   certainly a photographer's prop — Karen's own solutions guide checked the visible
   passage (p. 263) against the partial solution and found no match.
4. **Milwaukee Journal Sentinel archive lead — RESOLVED 2026-10-10** (@Mintpuppy17
   thread, Decipher II/III): the article exists in Karen's own Drive archive
   ("Decipher II Articles" folder, `Sharlet_Brown-article-crop.jpg`): *"She cracks
   code to win $25,000"*, by Thomas Collins, Milwaukee **Sentinel** (photo credit:
   Sentinel photo by Piet Van Lier), dateline West Allis, c. November 1986. It
   confirms the two hotline clues, the October 31 vault opening, and Brown as sole
   winner of message three. Transcribed in `docs/decipher-ii.md`. No microfilm trip
   needed.
5. **Decipher 2 assumed solved** (@KaseyWynne ↔ Karen, Decipher I): both assume
   Decipher 2 must have been solved or Decipher 3 would not have sold. No evidence,
   but it is the community's standing assumption and Karen's own.
6. Everything else in the 155 replies is audience chatter (typewriter-ribbon
   explanations, SSN question, K-pop, ads). No reply claims a solution, cites a new
   document, or corrects any fact in the repo.

## Signal assessment

Thin but not zero. The comment layer of both videos is now exhausted — top-level and
replies — and further community signal would have to come from elsewhere (newspapers
or the principals).

Post-sweep resolutions (2026-10-10): the referee footnote is located at footnote 7,
journal p. 278 of the UMBC scan; the *Cosmos*-epigraph edition-dependence caveat
stands; the author-centric strategy (item 2) is refuted by Holland himself; the
*The Source* theory (item 3) is eliminated; and the Milwaukee article (item 4)
turned out to be sitting in Karen's Drive archive all along.
