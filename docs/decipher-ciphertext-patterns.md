# Ciphertext Structural Patterns, Key-Supply Laws & Open Solver Roadmap

Every conclusion in this document is derived directly from the seven verified cipher
sequences in [`data/ciphers.json`](../data/ciphers.json) and the five public-domain
reference novels in `texts/model/`. None of it depends on copyrighted candidate books,
and every statistic below can be reproduced in two seconds with:

```bash
uv run python solver/analyze_ciphertexts.py --corpus-stats
```

---

## 1. Side-by-Side Fingerprint of All Seven Ciphers

Comparing the three **solved** Decipher II messages (`2-1`, `2-2`, `2-3`) against the
four **unsolved** messages (`2-4`, `3-1`, `3-2`, `3-3`) separates their encoding habits
cleanly:

| Cipher | Status | Tokens | Ints | Literals | Range `[Min..Max]` | Unique Ints | Repeat Uses | Expected Repeats (Uniform) | `\|Δ\|=1` Adj Pairs | Same-Century Adj % | `×100` Count | `> Max/2` % |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| **2-1** | Solved (*Gulliver* char palindrome) | 314 | 314 | 0 | `1..980` | 260 | **54** | 45.2 | **20** | 24.0% | 7 | 49.4% |
| **2-2** | Solved (*Catch-22* ToC chars) | 53 | 53 | 0 | `1..477` | 50 | **3** | 2.8 | 2 | 25.0% | 0 | 35.8% |
| **2-3** | Solved (*Tai-Pan* Ch.5 word-first) | 266 | 259 | 7 (`Z,E,N,V,L,Y,U`) | `14..2420` | 233 | **26** | 13.3 | **15** | **66.9%** | 9 | 23.9% |
| **2-4** | **OPEN** (Decipher II) | 170 | 170 | 0 | `3..1053` | 161 | **9** | 12.9 | **13** | 27.8% | **9** | 47.1% |
| **3-1** | **OPEN** (Decipher III, Group B) | 170 | 164 | 6 (`E×5, Z×1`) | `11..516` | 160 | **4** | 23.4 | 2 | 28.0% | 1 | 52.4% |
| **3-2** | **OPEN** (Decipher III, Group A/C) | 117 | 112 | 5 (`E×3, Y×2`) | `5..416` | 101 | **11** | 13.7 | 2 | 24.5% | 0 | 47.3% |
| **3-3** | **OPEN** (Decipher III, Group A/C) | 159 | 156 | 3 (`E×3`) | `1..721` | **156** | **0** | 15.6 | 2 | 31.6% | 3 | 50.0% |

---

## 2. Two Major Structural Laws in Decipher III (`3-1`, `3-2`, `3-3`)

### Law A — Without-Replacement Homophone Selection (`3-3` and `3-1`)

* **Cipher `3-3` has strictly ZERO (`0`) repeated integers across all 156 numeric tokens**
  drawn from `[1..721]`. Under uniform homophone selection, 156 draws from 721 slots
  average **15.6 repeat collisions**; observing zero collisions by chance has probability
  $p \approx 2.5 \times 10^{-8}$ (less than 1 in 40 million).
* **Cipher `3-1` has only `4` repeat collisions across 164 numeric tokens** drawn from
  `[11..516]` vs. **23.4 expected** ($p < 10^{-6}$).
* **Implication:** For `3-3` (strictly) and `3-1` (almost strictly), the encoder crossed
  off each key-stream position after using it once so frequency counting on numbers could
  not gain traction.

### Law B — Why Literal `'E'` Appears in All Three Decipher III Ciphers (Word-Initial `'E'` Depletion)

At first glance, literal `'E'` tokens in `3-1` (5 times), `3-2` (3 times), and `3-3`
(3 times) look paradoxical: no 416–721 character passage of English prose lacks the
letter `'E'`. Combining **Law A (without-replacement selection)** with **empirical
letter supply** across 1,008,522 words (4.32M characters) of the `texts/model/` corpus
explains the anomaly quantitatively:

| Cipher & Max Index | Approx Plaintext `'E'` Demand (~12.7%) | Continuous-Char `'E'` Supply (Median) | **Word-Initial `'E'` Supply (Median, p10–p90)** | Word-Initial `'Z'`=0 Rate | Word-Initial `'Y'` Supply (Median, Zero Rate) |
|---|---:|---:|---|---:|---|
| **`3-2`** (`max = 416`, len 117) | ~15 `'E'`s, ~2–3 `'Y'`s | 52 `'E'`s (never depletes) | **8 `'E'`s** (`4..14`) — **short by ~3–7!** | 97.9% | **7 `'Y'`s** (`0` in 5.2% of windows) |
| **`3-1`** (`max = 516`, len 170) | ~21 `'E'`s, ~0–1 `'Z'` | 65 `'E'`s (never depletes) | **10 `'E'`s** (`5..16`) — **short by ~5–11!** | **97.4%** | 9 `'Y'`s (`0` in 3.1% of windows) |
| **`3-3`** (`max = 721`, len 159) | ~20 `'E'`s | 90 `'E'`s (never depletes) | **14 `'E'`s** (`8..22`) — **short by ~3–6!** | 96.5% | 14 `'Y'`s (`0` in 1.3% of windows) |

* **Why word-initial keys run out of `'E'`s while character keys never do:** In English,
  `'E'` makes up **12.7%** of all letters (high plaintext demand), but only **~1.9%** of
  English word tokens *start* with `'E'` (low word-initial key supply—dominated instead
  by `T, A, I, S, O, H, W`). When an encoder crosses off used word indices (as proven by
  `3-3`'s 0 repeats and `3-1`'s 4 repeats), a 516-word or 721-word passage typically
  exhausts every `'E'`-initial word before the plaintext finishes and **must emit the
  leftover `'E'`s as literal `'E'`s**!
* Simultaneously, **97.4%** of 516-word windows contain **zero `'Z'`-initial words**
  (explaining `3-1`'s literal `'Z'` at position 98), and third-person 416-word windows
  often contain only 0–1 `'Y'`-initial words (explaining `3-2`'s two literal `'Y'`s at
  positions 53 and 91 alongside three literal `'E'`s).
* *(Alternative hypothesis kept open:* If Holland instead used a character-level stream
  and deliberately planted literal `'E'`/`'Y'` tokens as decoy literals or plaintext
  delimiters—as teased by the rulebook's warning about nulls—character-level rules remain
  necessary to test. Note also that `last-letters` has abundant `'E'`s (~20% of English
  words end in `'E'`), so `last-letters` would *not* deplete `'E'` naturally.)*

### Additional Decipher III Micro-Constraints

* **All six adjacent `|Δ| = 1` pairs across Decipher III step downward (`k, k−1`):**
  * `3-1`: `(109, 108)` at pos 57–58; `(285, 284)` at pos 78–79.
  * `3-2`: `(195, 194)` at pos 26–27; `(416, 415)` at pos 107–108.
  * `3-3`: `(553, 552)` at pos 38–39; `(436, 435)` at pos 48–49.
  Six out of six step `-1` (`p = 1/32` if direction were symmetric), consistent with
  either reversed key numbering ("End" clue in `3-1`) or reversed plaintext reading (as
  in solved `2-2`).
* **Exact Crib Masks in `3-1`:**
  * **Positions 26–27 (`487, 487`):** Adjacent identical codenumber—forces a doubled
    letter in plaintext (`EE, SS, LL, OO, TT, FF, PP, RR, MM, NN, CC, DD, GG`), meaning
    key slot `487` cannot be `J, K, Q, U, V, W, X, Y` except across a word boundary.
  * **Positions 127–130 (`335, 'E', 308, 335`):** Exact 4-letter pattern **`A E B A`**
    with literal `'E'` at slot 2 and `A ≠ B` (under without-replacement preference). Top
    single-word matches in English prose: `DEAD`, `SEAS`, `REAR`, `DEED`, `SEES`,
    `TEST`, `PEEP`, `TENT`, `TEXT`, `SETS` (plus cross-word spans such as `H E R H` in
    `HER HAND` or `T E N T` in `TEN THOUSAND`).
  * **Remaining `3-1` repeats:** `505` at `[12, 147]`; `285` at `[78, 149]` (note pos
    78–79 is `285, 284`).
  * **Literal positions in `3-1`:** `'E'` at `42, 56, 90, 128, 161`; `'Z'` at `98`
    (necessary condition for non-decoy keys: key window `[1..516]` contains **zero
    `'Z'`s**).
* **Exact Repeat & Literal Masks in `3-2`:**
  * **Literals:** alternating `'E', 'Y', 'E', 'Y', 'E'` at 1-based positions
    `29, 53, 82, 91, 101` (spacings `+24, +29, +9, +10`).
  * **Repeats:** `415`×3 at `[20, 97, 108]` (with pos 107–108 = `416, 415`, the exact
    top of the `[1..416]` key range!), plus pairs `78@[33, 112]`, `84@[84, 94]`,
    `222@[16, 24]`, `225@[43, 73]`, `311@[10, 99]`, `322@[5, 113]`, `390@[25, 110]`,
    `395@[13, 65]`, `414@[12, 34]`.

---

## 3. Structural Profile of Unsolved Decipher II `2-4`

Unlike Decipher III, **`2-4` looks structurally like solved Decipher II `2-1`**:

1. **Zero literal letters** across 170 tokens (`[3..1053]`), matching `2-1` (314 tokens,
   0 literals) and `2-2` (53 tokens, 0 literals), and unlike `2-3` (7 literals, 66.9%
   same-century clustering).
2. **13 adjacent `±1` step pairs, including THREE 3-step runs:**
   * Pos 9–11: **`737, 738, 739`** (`+1, +1`)
   * Pos 67–69: **`154, 155, 156`** (`+1, +1`)
   * Pos 154–156: **`544, 545, 546`** (`+1, +1`)
   * Plus 7 two-token steps: `(1050, 1049)` at pos 2–3, `(301, 302)` at 93–94,
     `(688, 687)` at 129–130, `(268, 269)` at 137–138, `(287, 288)` at 140–141,
     `(780, 781)` at 151–152, and `(34, 33)` at 169–170.
   In solved `2-1`, Holland repeatedly copied consecutive key indices (`242, 243`,
   `530, 531, 533`) whenever 2–3 consecutive plaintext letters happened to appear
   together as a bigram/trigram (`THE`, `AND`, `ING`, `ION`, `ENT`, `HER`) in the key
   passage. In `2-4`'s true key stream, slots `154–156`, `544–546`, and `737–739` almost
   certainly spell natural English trigrams rather than random consonant clusters.
3. **The 8-token Round-Hundred Cluster at Positions 20–27:**
   * Tokens 20–27 read **`400, 500, 400, 100, 200, 400, 800, 600`** (followed shortly by
     `300` at pos 31—9 multiples of 100 in a 12-token span, vs. 0 in the remaining 158
     tokens; see [`results/puzzle-2-4-microstructure-2026-10-18.md`](../results/puzzle-2-4-microstructure-2026-10-18.md)).
   * Either (a) Holland noticed that round hundreds `100, 200, 400, 500, 600, 800` in his
     1,053-item key happened to spell an 8-letter word/phrase of pattern **`A B A C D A E F`**
     (e.g., `E V E N H E R E`, `T H T ...`, or reversed `F E A D C A B A`) and showed it
     off deliberately, or (b) positions 20–27 are an **8-token clustered null block**
     (which `TrigramScorer.score_best_window` and the `Puzzle_2-4_No100s` variant in
     `solver/toc_and_clue_tester.py` explicitly guard against).

---

## 4. Why Raw OCR & Edition Variants Fail Rigid Sweeps — and How `drift_diagnostic.py` Helps

A natural question is whether approximate pattern matching on slightly noisy OCR or a
different paperback printing can still detect the right passage. The answer depends
sharply on **how many edits** occur inside `[1..max_n]`:

* **Why even 2 dropped words break a rigid sweep:** Because cipher numbers jump across
  `[1..max_n]`, if OCR drops 1 word around index 180 and 1 word around index 360, roughly
  two-thirds of the decoded letters *scattered throughout the plaintext* shift by +1 or
  +2 words. Scattered errors ruin **both** the whole-decode trigram mean and
  `score_best_window` (verified in `solver/validate.py`: rigid score drops from `-7.275`
  to `-9.636`, deep inside noise).
* **New tool — 3-Band Index-Elastic Diagnostic (`solver/drift_diagnostic.py`):**
  Partitions `[1..max_n]` into three equal index bands and tests 25 cumulative shift
  profiles `(0, d1, d1+d2)` (`d1, d2 ∈ [-2..+2]`) vectorized at every start offset on
  `first-letters`, `first-letters-split-hyphen`, `last-letters`, and (optionally)
  `letters@sentence`:
  * **Recovers light edition/OCR drift (1–4 cumulative word/char edits):** On the
    2-dropped-word regression control in `validate.py`, `drift_diagnostic.py` restores
    `-9.636` straight back to **`-7.275`** with exact start and `drift=(0, -1, -2)`,
    while unrelated novel text stays below `-8.30` (look threshold `-8.12`).
  * **Where elasticity still hits an information-theoretic wall:** Heavy OCR corruption
    (e.g., 85–90% word accuracy = **50–75 wrong/merged words** inside a 516-word window)
    shifts indices every 7–10 words. Allowing free `±5` shifts every 10 tokens creates so
    many degrees of freedom that *any* random English novel can spell arbitrary English
    words ("monkey-at-a-typewriter" overfitting). For heavily degraded scans, cleaner OCR
    or chapter-by-chapter QA remains mandatory.

---

## 5. Open Extraction Gaps for Future Solvers & Stronger AI Models

Anyone picking up this repository has the following cleanly bounded search territory left:

1. **In-copyright era-pinned paperbacks (highest expected yield):**
   * **2-4 (pre-1985 editions):** Remaining un-swept works by Updike, L'Amour, Irving,
     Galbraith, plus alternate McCullough works beyond *The Thorn Birds*.
   * **3-1 (pre-1987 Group B, zero-`Z` 516-unit window, "10" / "End" clues):** Vonnegut
     (especially clean era-pinned *Cat's Cradle* and *Slaughterhouse-Five*), Asimov
     (*Foundation's Edge*, *The Naked Sun*, *Union Club Mysteries*), Ludlum, Capote,
     Uris, Woodward, Nixon, Halberstam, Ono.
   * **3-2 & 3-3 (pre-1987 Groups A & C, strict 0-repeat 721-unit window on 3-3):**
     Heller (*Something Happened*, *Good as Gold*, *God Knows*), Clavell (*Shōgun*,
     *Tai-Pan*, *King Rat*, *Noble House*), plus Sanders, Buckley, Solzhenitsyn, Cosby,
     Wolfe, Kissinger, Plath, Haley, Mailer, Smith, Follett, Puzo, and post-1931
     Faulkner/Christie.
2. **Unimplemented rule families (pure algorithm work, no books needed to build):**
   * **18 strided palindromic families:** `engine.search_anchored` currently tests
     `S || reverse(S)` on `letters`, `first-letters`, and `last-letters`. Extending
     sentence-start coordinate mapping to `every-Nth-letter` and `word-Nth-letter` closes
     the remaining palindromic gap noted in [`methodology.md`](methodology.md).
   * **Scattered-null partial-word back-solver:** If Holland inserted periodic or random
     nulls into Decipher III plaintexts (say 1 null every 8–10 tokens), trigram scoring
     fails (`validate.py` asserts this). A beam-search / Viterbi scorer allowing a small
     deletion penalty (`~10%` token skip rate) over a word/trigram lattice could detect
     scattered-null plaintexts without overfitting.
   * **Paratext & non-body keys:** Book dedications, epigraphs (compare Decipher I's
     Wilkins epigraph in *Cosmos*), author biographical blurbs, jacket copy, or index
     entries in specific 1980s Bantam/Dell/Fawcett mass-market printings.
