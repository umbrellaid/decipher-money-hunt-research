# Blind-reading protocol for contested digits (2026-11-05)

**Purpose.** When two candidate readings of one glyph have already been written down
anywhere — a paper, a corrections file, a chat log, a commit message — every reader who has
seen that document is contaminated and cannot be blind. Candidate-aware readings are what
made the published `330→830` correction at Decipher II observation 169 only *probable* in
both projects' records. This protocol is how that was settled, and how any future contested
digit should be settled.

**Tooling.** `solver/blind_read.py` generates the crop and the reader prompt. It exists
because blindness has to be engineered rather than assumed; the tool enforces the four
properties below instead of leaving them to whoever runs the test.

## The four properties that make a reading blind

1. **Neutral filename.** The crop is written to a random name in the system temp directory.
   The real source file is called `Decipher-II-puzzle-front.jpg`, which tells a reader exactly
   what document it is looking at and makes the answer look-up-able.
2. **Context-free prompt.** The prompt names no project, no puzzle, no candidate values and no
   observation numbers. It asks for *every* number in the image, so the reader cannot tell which
   one is under test, and it explicitly forbids opening any other file or exploring the
   filesystem.
3. **Controls inside the crop, not in the prompt.** The band contains other glyphs that exercise
   the same confusion as the target. For observation 169 (`330` vs `830`) the crop also contains
   a genuine `330` at observation 148, two rows above. A reader that gets both right has
   demonstrated it can tell the glyphs apart in this image; a reader that gets only the target
   right has demonstrated nothing.
4. **Differently-biased readers.** `blind_read.py --variant` offers `plain`, `primed` (draws
   attention to the specific glyph confusion) and `rtl` (reads each row right-to-left then
   reverses, as an order control). Agreement across differently-biased readers is evidence;
   agreement across four identical readers is repetition.

## What was actually run for observation 169

```
uv run solver/blind_read.py \
  --source ".../Decipher-II-puzzle-front.jpg" \
  --box 300,1650,2600,2200 --scale 2
```

- Source: the Message 1 sheet (the side that holds Message 1 only), from the shared scans.
- Box covers printed observations **137–197** — six rows, with observation 169 in row 4 and the
  genuine `330` of observation 148 in row 2.
- Output 4600×1100 px, Lanczos 2×, JPEG quality 95.
- Four readers: two `plain`, one `primed`, one `rtl`. Each was a fresh context with no access to
  this repository's history.

**Result.** All four returned identical rows. All four read observation 169 as **`830`** and
observation 148 as **`330`**. The `primed` reader reported `AMBIGUOUS: none`. One `plain` reader
flagged 169 as ambiguous — a puzzle seam crosses the digit's left edge — and resolved it to 8 on
closed-left-bowls evidence. The `rtl` reader flagged three *other* seam-crossed digits as 3-vs-8
ambiguous and resolved both of them **toward 3**, which is why a systematic seam-toward-8 bias is
not supported by this crop.

Diffing the band against `data/ciphers.json`: **60 of 61 values agree**; the single difference is
observation 169. Consequences are recorded in `results/RUN_LOG.md`, 2026-11-05.

## Limits — state these whenever the result is cited

- **Four contexts of one model family are not four independent observers.** If that family
  misreads this glyph shape, all four misread it together. The controls mitigate this but do not
  eliminate it.
- **A physical artifact can bias every reader identically.** Here a seam crosses the target digit.
  The control digits argue against a directional bias, but the argument is inferential.
- **Human inspection of the physical piece remains the only stronger check.** Report the result as
  "image-verified by blind reads," never as "verified."
- The metric is agreement among readers plus agreement with a reference sequence, not ground truth.
  A shared error between the reference and all readers is invisible to this method — which is
  precisely the failure mode that hid observation 169 for a month.

## Reusing it

1. Identify the contested position and pick a crop that includes **at least one control glyph**
   exercising the same confusion. A crop containing only the target is worthless.
2. `blind_read.py --variant primed` first, to check the confusion is even resolvable at that
   scale; raise `--scale` if not.
3. Run at least three readers across at least two variants, in parallel, in fresh contexts.
4. Diff every reader's full transcription against the stored sequence, not just the target
   position. Disagreement elsewhere is information about that reader's reliability.
5. Record the crop parameters in the results file so the test is reproducible, but **never**
   commit the crop: it derives from a copyrighted scan in `private/`.
