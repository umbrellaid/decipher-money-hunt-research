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
2. **Author-centric search strategy, articulated** (@Chaotic_Pixie, replying under
   Karen's pinned fairness comment): the Decipher I key text sat in the chapter whose
   subject was named **Holland** — the creator's own surname — so "look at books that
   somehow relate to the author" is a rational first move. Supports the existing
   Holland-favouritism prior (cf. the Fight Klub re-use finding in item 2 above).
3. **"The Source" theory for 2-2, endorsed by Karen** (@jcortese3300 thread,
   Decipher II/III): the parent comment (already in the top-level sweep) argues
   Michener's *The Source* is the 2-2 key text by its title alone; Karen's reply —
   *"That's a solid theory! Be sure to let me know if you dig into it and come up
   with anything!"* — upgrades it from drive-by comment to a lead she explicitly
   blessed. Still untested.
4. **Milwaukee Journal Sentinel archive lead** (@Mintpuppy17 thread, Decipher
   II/III): the 2-3 puzzle article is believed to be in the Milwaukee Journal
   Sentinel; the commenter found candidate dates in the microfilm catalog but lacks
   a Milwaukee County library card. Karen: *"I hope someone from that area sees this
   and can dig into it!"* Still open — no reply reports success.
5. **Decipher 2 assumed solved** (@KaseyWynne ↔ Karen, Decipher I): both assume
   Decipher 2 must have been solved or Decipher 3 would not have sold. No evidence,
   but it is the community's standing assumption and Karen's own.
6. Everything else in the 155 replies is audience chatter (typewriter-ribbon
   explanations, SSN question, K-pop, ads). No reply claims a solution, cites a new
   document, or corrects any fact in the repo.

## Signal assessment

Thin but not zero: item 1 gives a citable page number for the referee footnote, and
item 2 is a new data point on Holland's puzzle-design habits. Neither changes the
solver state; the Decipher III search-space problem stands exactly as documented in
[decipher-iii.md](../docs/decipher-iii.md).

The reply sweep adds two keeper facts (edition-dependence of the *Cosmos* epigraph;
Karen's endorsement of the *The Source* theory) and one open archival lead
(Milwaukee Journal Sentinel microfilm for the 2-3 article). The comment layer of
both videos is now exhausted — top-level and replies — and further community signal
would have to come from elsewhere (the archived Discord, newspapers, or the
principals).
