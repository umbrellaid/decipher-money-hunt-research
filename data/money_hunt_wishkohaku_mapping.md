# The wishkohaku "deduction = subtraction" mapping — hypothesis record and first verification

**Origin:** YouTube comment by @wishkohaku on the Karen Puzzles Money Hunt video
(4 years ago, edited; full text in the
[comments digest](money_hunt_youtube_comments_digest.md) item 1). This is the **only
complete page→letter assignment** for all 24 path pages known to exist.

## The mechanism

The instructions and the back of the box both stress "deduction". wishkohaku reads it
literally as *subtraction*: an illustration that appears on more than one page is
copied with a deliberate alteration; the page's letter is the initial of whatever the
alteration removed (or changed).

**Worked example given:** page 13 has a "P"; page 20 has the same P with a line
through it. Page 13 is "missing the line" → "line" → **L**. The mapping assigns
page 13 → L (the L of "BUILDING").

## The mapping (as written by wishkohaku)

| Message text | Page | | Message text | Page |
|---|---|---|---|---|
| U | 15 | | B | 20 |
| S | 15 | | U | 22 |
| N | 9 | | I | **28** |
| Y | 9 | | L | 13 |
| T | 18 | | D | 16 |
| H | 24 | | I | 26 |
| E | 14 | | N | 12 |
| E | 6 | | G | 11 |
| M | 17 | | | |
| P | 21 | | | |
| I | 23 | | | |
| R | 27 | | | |
| E | 19 | | | |
| S | 7 | | | |
| T | 5 | | | |
| A | 8 | | | |
| T | **10** | | | |
| E | **25** | | | |

Reading in the poster path order: **US NY THE EMPIRE STATE BUILDING**.
Pages 15 and 9 each contribute two letters; the rest one each. Note the mapping
assumes the message begins "US NY …" (two 2-letter chunks), which conveniently absorbs
two pages into four letters.

## Verification status (2026-10-09, night)

### ✅ Worked example CONFIRMED at 300 dpi
- **Page 13** (native 300-dpi render): a plain parking-sign **P** at the right edge,
  mid-height — no diagonal line.
- **Page 20** (native 300-dpi render): **two** no-parking signs — P **with** a diagonal
  line through it (one beside the "CARS" building, one carried at lower left).
- The same symbol, one with and one without the line, exactly as the comment describes;
  and the mapping's 13→L is the letter that the worked example produces. The
  "subtraction" mechanism is therefore **demonstrated on at least this pair**.

### ✅ Page 28 → I: strong candidate found
The middle bookshelf reads **"VA DERS"** — i.e. **INVADERS** with **"IN"** missing.
Missing element = "IN" → initial **I**, matching the mapping's 28→I (the I of
"BUILDING"). Independent corroboration: the p28 deliberate-misspelling set is exactly
the kind of alteration this mechanism needs, and "VA DERS" is a clean subtraction
(unlike the substitution-type misspellings Konnan/K→C, MILD/W→M).

### ⚠️ Errata items surfaced by the same 300-dpi pass — RESOLVED 2026-10-10
4× crops from the native render settled all three: **"HUCKLEBERRY GRINS"** (for
*Huckleberry Finn*) is confirmed and joins the misspelling set; **"FLAMINGCOES"** is
actually **FLAMINGOES** (correctly spelled — out of the set); **"Snsp"** is **Snap**
(correctly spelled — out). Two further corrections: "Konnan The Immortan" → **Konnan
The Librarian** (Conan the Librarian), and "Gone Tmming" → **Hare Today – Gone Tamale**
(correctly spelled pun). Full corrected set is recorded in
[page_28](money_hunt_pages/page_28.md) and the
[errata](../docs/money-hunt-transcription-errata.md). Notably, "VA DERS" survived
re-reading and remains the page's one clean subtraction (missing "IN" → I).

### ❌ Two comment-sourced motif claims tested and falsified (survey, 2026-10-10)
The full 24-page repeated-motif survey is recorded in
[results/money_hunt_repeated_motif_survey.md](../results/money_hunt_repeated_motif_survey.md).
Net: the 2 verified letters still hold, but —
- **"milk box on 7 and 18"**: p7 shows "Whole Milk" as text only (no carton);
  no milk reference exists anywhere on p18 at native res. Pair does not exist.
- **"same armchair on 17 and 19"**: native-res crops show two *different*
  striped chairs (wing-back suite + ottoman vs worn tub chair). Not a pair.
Score after surveying all 24 pages: **2 verified, 2 tested claims false,
~6 candidate pairs still open, no candidate found for 6 pages**.

### ❓ Pages 10 → T and 25 → E: not yet testable
- Page 10 (resort pool; DOWN list 1–37; undecoded 2×4 glyph suitcase): no repeated-
  illustration partner identified yet.
- Page 25 (top-hat ACROSS grid 1–156, clues 95–97 unprinted): likewise. Note the
  unprinted clues 95–97 are a *printing* defect, not an illustration subtraction, so
  they probably do not serve as this page's "deduction".
Both require a systematic repeated-illustration survey across all 24 pages (see plan).

## Assessment

- The hypothesis is **falsifiable and partially verified** — rare for this puzzle.
- The mechanism fits the book's own vocabulary ("deduction"), fits the deliberate-
  misspelling set, and its one worked example survives checking.
- Weak points: (1) only 2 of 24 letters independently verified; (2) the "US NY" split
  is convenient; (3) the method requires every page to have at least one duplicated
  illustration with a one-element alteration — plausible for this artwork, unproven;
  (4) it predicts the final answer is the Empire State Building in words, which the
  "3 guesses" rule and the map's NYC-only resolution both argue against (see
  [money-hunt.md](../docs/money-hunt.md)).

## How to test it fully (the real project)

1. Build a per-page inventory of every illustration element that appears on ≥2 pages
   (the artwork photocopies motifs: bell, P signs, milk box, top hat, flamingos, etc.
   — several already catalogued in the state analysis).
2. For each of the 24 path pages, find its duplicated element(s) and diff them
   element-by-element.
3. Each diff should yield exactly one missing/changed element whose name starts with
   the letter the mapping predicts for that page.
4. Score: 24/24 with no forced fits = the solution mechanism; anything less and the
   mapping is at best partially right.
