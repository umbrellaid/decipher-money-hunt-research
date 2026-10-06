# Run log — every sweep ever run against the open ciphers

Calibration for all rows: genuine English ≈ **−7.9…−8.0** per trigram; noise ≤ **−8.6**.
For the secondary `win` (best-window) column the noise floor is ≈ **−8.1**.
A candidate is only interesting above −8.2 (`score`) with a readable decode.

## Campaign 1 — 2026-10-04 (5 rule families)

| Cipher | Corpus | Positions tested | Best score | Verdict |
|---|---|---|---|---|
| 3-1 | Poe complete works, 2 passes | ~5M | −8.84 | Poe eliminated |
| 2-4 | 31 PD texts (Hawthorne, Hardy, EBB, Verne, Whitman, Thoreau) | ~5M | −8.87 | 6 PD authors eliminated |
| 3-2 / 3-3 | 18 PD texts (Faulkner, Christie ×10, Sandburg, O'Neill ×5, cummings) | ~5M | −8.60 / −8.70 | PD side eliminated |
| all three | 35 chapter-title chains (the Catch-22 rule) | — | −9.00 | chain family eliminated |

Logs: `sweep_logs/sweep_pd_log.txt`; tops in `sweep_*_pd.json`, `sweep_*_chains.json`,
`sweep_31_poe.json`.

## Campaign 2 — 2026-10-05 (21 rule families)

Rule families: the base five (`letters`, `first-letters`, `last-letters`, `line-first`,
`line-last`) plus `everyN-letter`, `everyN-wordfirst`, `everyN-wordlast` for N ∈ {2,3,5,10},
`word2th-letter`, `word3th-letter`, `sentence-first`, `paragraph-first`; every numbering
start; streams forward and reversed; plaintext scored both directions.

| Cipher | Corpus | Wall time | Best `score` | Best `win` | Verdict |
|---|---|---|---|---|---|
| 2-4 | 31 PD texts | (part of 1452 s) | −8.7683 `hawthorne_512:every3-wordlast` | −8.2267 `verne_83:every2-wordlast` | no hit |
| 3-1 | Poe, 9 texts | 279 s | −8.8389 `pg2150/25525:last-letters` | −8.4668 | Poe eliminated under 21 families |
| 3-2 | 21 PD texts | (part of 1452 s) | −8.5379 `christie_69087:every2-wordlast` | −8.1082 `faulkner_75170:every2-wordlast` | no hit |
| 3-3 | 21 PD texts | (part of 1452 s) | −8.6957 `christie_61168:last-letters` | −8.1450 `faulkner_se_asilaydying:last-letters` | no hit |

Every top-10 decode in `sweep_logs/sweep3_log.txt` is vowel-heavy gibberish
(e.g. `FFTEDESTDYSMAFISEESSDENYTFDENDSEAELSNEDOFTEFEEEE`); the few `win` values near
−8.1 come from `*-wordlast` streams, which are letter-density artifacts, not English.
Tops in `sweep3_24.json`, `sweep3_31.json`, `sweep3_32.json`, `sweep3_33.json`.

**Conclusion:** the public-domain eliminations of 2026-10-04 survive a 4× wider rule
set. The remaining suspects for every open cipher are in-copyright authors
(`data/author_lists.json`), and the way forward is `docs/check-your-own-book.md`.

## Validation

`solver/validate.py`, 93 checks (`sweep_logs/validate_out.txt`):

- 4 checks on the Decipher III rulebook's worked example (Cosmos ch. 6 passage,
  three ciphers → CODES);
- 2 checks on puzzle 2-2: the *Catch-22* chapter-title chain is long enough, and
  the reversed chain, with the decode read backwards, is the Lennon message;
- 84 encode→search→decode round trips, 21 rule families × four direction
  combinations, each requiring the true numbering start to rank #1;
- 3 null-tolerance checks: windowed scoring recovers clustered nulls, windowed
  scoring rejects uniform noise, and scattered nulls are not recoverable by any
  implemented statistic.

An earlier log recorded trimmed-mean checks as passing. That statistic was removed
on 2026-10-05 because pure noise scored inside the English band. The log file
matches the current script.

## Rejected ideas (recorded so they are not retried blindly)

- **Trimmed-mean trigram scoring** for null tolerance: pure noise scores ≈ −7.3 under
  it, inside the English band. Removed 2026-10-05.
- **archive.org controlled digital lending** as a text source: loans never expose
  `_djvu.txt` (401 even mid-loan). Tested 2026-10-04 with a logged-in account.
- **DRM ebook purchases**: every legitimate edition of the priority titles is Adobe
  DRM; buying them yields no machine-usable text.
