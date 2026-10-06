# Check your own copy of a book

The single thing standing between this solver and the remaining ciphers is **text**:
the candidate key texts are in copyright, every legitimate ebook edition is
DRM-locked, and archive.org lending exposes page images but never text. The one
clean, lawful route is the one the original solvers never needed: **buy a used
paperback you actually want to read, photograph it, OCR your own copy, and sweep it.**
You own the book; OCRing your own copy for personal research is the point of owning it.

This page is the complete loop, including the prompts to paste into whichever LLM
you use if you would rather not run the commands yourself.

## 0. Which books are worth scanning

See `docs/decipher-iii.md` and `docs/decipher-ii.md` for the ranked suspect lists.
Constraints: the key text must have been published **before 1987** (Decipher III) or
**before 1985** (Decipher II 2-4). Any printing is worth a sweep — but note that
numbering depends on the exact edition, so an early printing closest to the contest
years has the best odds, and a miss on a late reprint is not conclusive.

## 1. Photograph it

- One page per photo, overhead, page flat, even light, no shadow across the text.
- A phone scanning app (vFlat, Adobe Scan, Google PhotoScan) that de-warps and
  de-shadows is worth the five minutes.
- Photograph **everything**: title page, copyright page, contents, front matter and
  back matter. The key stream can start anywhere, and chapter-title chains need the
  contents pages.
- 300 dpi equivalent or better. Blurry digits in a footnote are exactly where keys hide.

## 2. Get text out of the photos

Pick one:

- **Your scanning app's text export** (fastest; quality varies).
- **Tesseract**: `tesseract page_001.png page_001 --psm 6`, then concatenate.
- **A multimodal LLM**, in batches of 5–10 pages, with this prompt:

> Transcribe these book pages verbatim into plain text. Keep every word, every
> line break and every chapter heading exactly as printed. Do not summarise, do not
> correct spelling, do not add commentary. Where a word is illegible write [?] on its
> own line. Output only the transcription.

Concatenate the batches in page order into one file, `mybook.txt`.

## 3. Normalise

```
uv run python solver/normalize_text.py mybook.txt --chapters
```

This strips licence boilerplate, folds typographic punctuation onto ASCII, collapses
whitespace, and writes `mybook.chapters.json` (heading titles + offsets).
`solver/sweep.py` reads that file when you sweep `mybook.txt` or `mybook.clean.txt`,
and tests the concatenated titles as the extra rule `chapter-titles`. The detector
finds lines that start with CHAPTER, BOOK, PART, or SECTION. A book whose titles
are proper names needs those titles written into the JSON by hand. Puzzle 2-2's
titles are in `data/catch22_chapter_titles.json`.

## 4. Sweep

```
uv run python solver/sweep.py mybook.clean.txt --cipher all --top 10
```

Read the two score columns:

| Column | Meaning |
|---|---|
| `score` | whole-decode trigram score. Genuine English ≈ −7.9…−8.0; noise ≤ −8.6 |
| `win` | best-window score, a secondary null-tolerant check; noise stays ≤ −8.1 |

Anything above **−8.2** in `score` is flagged `<-- CHECK THIS`. Below that, the
book is eliminated under every implemented rule family — which is still a real
result worth reporting, because it shrinks the suspect list.

## 5. Verify a candidate by hand, before believing it

A score is a hypothesis. Confirm it against the physical book:

1. Take the reported `rule` and `start`. Rebuild the stream by hand for a few dozen
   positions around `start` and check the cipher's numbers land on the printed letters.
2. Check the cipher's **literal letters** (the `E`, `Z`, `Y`, `U`, `N`, `V`, `L` tokens)
   appear exactly where the decode puts them.
3. Read the full decode. It must be a coherent English sentence, usually topical —
   the solved precedents were "In memory of John Lennon…" and a nuclear-war passage.
4. Only then call it a solve.

## 6. If you want an LLM to run the loop for you

Paste this, attaching your clean text file:

> You are running a book-cipher search. The repository you are in contains
> solver/sweep.py, which tests a book text against four unsolved 1980s ciphers under
> 21 extraction rule families, every numbering start, both directions. If a
> .chapters.json file sits beside the text, also test the chapter-title chain.
> Run:
> `uv run python solver/sweep.py <file> --cipher all --top 10`. Then report, for each
> cipher: the best score, the rule family and start offset, and the decoded string.
> State plainly whether any score exceeds -8.2 (the genuine-English threshold is
> -7.9 to -8.0; noise is -8.6 and below). If one does, quote the decode and the rule,
> and list the checks from docs/check-your-own-book.md section 5 that still need a
> human with the physical book. Do not claim a solve from a score alone.

And for a candidate that needs checking:

> Here is a candidate decode and its rule/start offset: <paste>. Here is the cipher:
> <paste from data/ciphers.json>. Re-derive the decode step by step from the rule
> description in docs/methodology.md and confirm or refute it. Point out any literal
> letter in the cipher that the decode places incorrectly.

## 7. Tell someone

- Open an issue or pull request on this repository with your text-file hash, the
  scores, and your verdict. Negative results are worth posting.
- Karen has asked that finished solutions go to the contact at the end of her
  videos: final text, key-text source and start point, rules applied, and author.
  The three videos are listed in `docs/sources.md`. This repository does not
  republish that address.
