# Errata — Money Hunt clue-book transcriptions

The page notes were produced by AI vision in early October 2026. On 2026-10-05 every
clue page was re-read from the scans in
[Karen Puzzles' Money Hunt folder](https://drive.google.com/drive/folders/1LgZD4G5UtxEaaQxZ0G3PL6Zj_DDDD3W3?usp=sharing)
and checked against those notes. **Fourteen defects were found, three of them
whole-scene misattributions.** The affected files in `data/money_hunt_pages/` are
now short stubs. Use
[`docs/money-hunt-state-analysis.md`](money-hunt-state-analysis.md), which was read
from the images, until those pages are transcribed again.

## Whole-scene misattributions (the transcription describes a different page)

1. **page_18** — describes an awning "FISH", "FRIED" window, moose-head keyhole,
   Braille "STAFF S5_F", truck, gas pump, bugle, pushcart, balloon child, masked-ball
   poster and "P" board. **None of these exist** on page 18 at 300 dpi. The Braille and
   moose items belong to some other folio and need re-attribution.
2. **page_21** — describes a street kiosk with an "ANNUAL …" booklet; the actual page
   is a saluting crowd with ONE WAY / BUS STOP signs and a circled-H building.
3. **page_10** — describes an interior window/skyline/bridge/freighter scene; the
   actual page is a resort pool carrying the DOWN crossword list (clues 1–37) and the
   glyph suitcase.

## Wrong or invented text

4. **page_20** — "1 – ENTRANCE" is not in the image; real signage is "CARS" plus two
   no-parking P signs.
5. **page_13** — claims the luggage tags show "FIRST CLASS" with no digits; the 300 dpi
   render clearly shows **FIRST CLASS 2** and **FIRST CLASS 7**.
6. **page_27** — misses the large **JAZZ** sign and invents sheet-music titles
   ("Happy Landing", "First Time") that are not visible.
7. **page_06** — masks a deliberate misspelling: the image prints **AWITHIAKNANNAI**
   (I for L), not the correct game name Awithlaknannai.
8. **page_24** — Etiquette panel reads "Be ready when it is your turn" (not "Replace
   pins in your turn"); Tips reads "Keep bowling arm straight & firm" (not "Follow
   through - straight & firm").
9. **page_05** — no "MISS MONEY HUNTER 1985" plaque, no "$1,000,000" poster and no
   "MONEY HUNT" box exist in the image; the large numeral is the calculator's
   1,000,000,000; the **VAULT** ribbon was missed.
10. **page_19** — the carved "—REST—" is not visible; the headboard shows scrollwork.

## Major omissions

11. **page_23, page_22, page_11** — each carries a full crossword clue list (23:
    121–147; 22: 73–117; 11: 38–69) that the transcription never recorded. Page 23's
    list includes clue 145 "Tennessee State University (abbr.)" and page 11's includes
    clue 55 "Belonging to the Potato State" — both literal state references.
12. **page_25** — the ACROSS list is misnumbered: what the transcription calls 1–19 are
    actually clues 98–118.
13. **page_28** — misses several spine titles (Cinderellow, Konnan The Immortan, Snsp,
    CALL OF THE MILD, FLAMINGCOES, Gone Tmming) and mis-states the volume row, which
    reads 23, 19, 21, 20, 22, … with DICTIONARY N–Z in volume 8's slot and DICTIONARY
    A–M in volume 1's slot.
14. **page_09** — understates the clocks (two faces exist: wall and tower) and calls
    the wine labels unresolvable when "POUILLY FUME" is legible at 1246 px.

## Consequence for the analysis

The state hunt in `docs/money-hunt-state-analysis.md` was run against the **images**,
not against these transcriptions, precisely because of this errata. Anyone continuing
should re-transcribe pages 5, 6, 9, 10, 11, 13, 18, 19, 20, 21, 22, 23, 24, 25, 27, and 28
from high-resolution renders before trusting page-level conclusions, and should treat
the 17 regions listed as 600-dpi re-render targets in that document as unread.
