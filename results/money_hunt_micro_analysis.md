# Money Hunt — scripted micro-analyses

Regenerated from the image spelling `AWITHIAKNANNAI`. `STAFFS5F` is omitted.
It came from a note that described the wrong page. The script that produced
this file is not in this repository: it was a one-off interactive analysis,
not a reusable pipeline — its inputs are the spellings named here (checked
against the scans) and its outputs are reproduced verbatim so anyone can
re-verify them by hand or rerun the tests in any scripting environment. See
`docs/money-hunt-transcription-errata.md`.

All results are mechanical; interpretation notes are flagged as such.

## 1. Anagram tests on the deliberate misspellings

Exact anagrams and 'entry + leftover letters' matches against US states,
Canadian provinces/territories and place names.

### Page p5
- (watch dial skips 4 — not a word)

### Page p6
- `AWITHIAKNANNAI` exact: none
  - contains `HAWAII` + leftover `AAIKNNNT`
- `PARCHESI` exact: none
- `SOLITOIER` exact: none

### Page p7
- `BRUME` exact: none
- `FLOPCORN` exact: none

### Page p17
- `SVEET` exact: none

### Page p27
- `STYNBANG` exact: none

### Page p28
- `TAHG` exact: none

## 2. Calculator-upside-down readings of the page-28 price tags

Rotation map: 0=O 1=I 2=Z 3=E 4=H 5=S 6=G 7=L 8=B 9=G, M=W.

- `5537` -> `LESS`
- `618` -> `BIG`
- `334` -> `HEE`
- `16M` -> `WGI`
- `149145` -> `SHIGHI`
- `5537 618` -> `BIGLESS`
- `334 618` -> `BIGHEE`

Known-good controls: 5537 -> LESS and 618 -> BIG (both reproduce).

## 3. Number clusters as indices

### p15 (Y=4X+1)
- alphabet (1=A): [9] -> `I`
- acrostic EMPIRESTATEBUILDINGNYUSA: [9] -> `A`
- state admission order: [9] -> `NEWHAMPSHIRE`
- states alphabetical: [9] -> `FLORIDA`

### p22 hats
- alphabet (1=A): [5, 33, 34] -> `E..`
- acrostic EMPIRESTATEBUILDINGNYUSA: [5, 33, 34] -> `R..`
- state admission order: [5, 33, 34] -> `CONNECTICUTOREGONKANSAS`
- states alphabetical: [5, 33, 34] -> `CALIFORNIANORTHCAROLINANORTHDAKOTA`

### p23 stanchions A
- alphabet (1=A): [1, 5, 7, 2] -> `AEGB`
- acrostic EMPIRESTATEBUILDINGNYUSA: [1, 5, 7, 2] -> `ERSM`
- state admission order: [1, 5, 7, 2] -> `DELAWARECONNECTICUTMARYLANDPENNSYLVANIA`
- states alphabetical: [1, 5, 7, 2] -> `ALABAMACALIFORNIACONNECTICUTALASKA`

### p23 stanchions B
- alphabet (1=A): [6, 10, 4] -> `FJD`
- acrostic EMPIRESTATEBUILDINGNYUSA: [6, 10, 4] -> `ETI`
- state admission order: [6, 10, 4] -> `MASSACHUSETTSVIRGINIAGEORGIA`
- states alphabetical: [6, 10, 4] -> `COLORADOGEORGIAARKANSAS`

### p27
- alphabet (1=A): [60, 60, 7890] -> `...`
- acrostic EMPIRESTATEBUILDINGNYUSA: [60, 60, 7890] -> `...`
- state admission order: [60, 60, 7890] -> `...`
- states alphabetical: [60, 60, 7890] -> `...`

### p6 bingo
- alphabet (1=A): [2, 5, 7, 28] -> `BEG.`
- acrostic EMPIRESTATEBUILDINGNYUSA: [2, 5, 7, 28] -> `MRS.`
- state admission order: [2, 5, 7, 28] -> `PENNSYLVANIACONNECTICUTMARYLANDTEXAS`
- states alphabetical: [2, 5, 7, 28] -> `ALASKACALIFORNIACONNECTICUTNEVADA`

## 4. Page-12 WASHINGTON vs the acrostic

Reading-order position of page 12 is 23; acrostic letter there is 'S'.
Candidate rules by which WASHINGTON could supply 'S':

- 3rd letter of WASHINGTON = S  (index 3)
- last letter of the postal code WA? no (A)
- admission order 42 -> alphabet[42] out of range; acrostic[42] out of range
- 'Specifically at' place name starting with S (e.g. a Seattle/Spokane site)

Interpretation note: the only clean fit is 'third letter', which is
unmotivated; more likely the acrostic letter comes from the SPECIFIC place
on each page rather than the state. Left open pending STATE_ANALYSIS.md.
