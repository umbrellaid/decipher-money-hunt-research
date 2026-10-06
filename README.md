# decipher-money-hunt-research

**Unofficial fan research.** Not affiliated with, endorsed by, or produced by
Karen Kavett or the Karen Puzzles channel. Her videos and the folders she shared
are the primary material. These notes and this solver are an independent attempt
to organize what is already public and to test candidate books. The person who
compiled this repository asks for no personal credit.

**The unsolved 1980s prize puzzles from the Karen Puzzles YouTube channel — and a
solver for the ones that are still open.**

In the 1980s a Norfolk, Virginia company called Decipher, Inc. sold jigsaw puzzles with
secret messages printed on them and paid out six figures in prize money. One contest
was solved by MIT students in a weekend. One was solved and then **lost**. Two were
never solved at all, and a separate 1986 armchair treasure hunt worth **$1,000,000**
died in court with its answer still secret. This repository organizes published
material on those puzzles, includes a solver checked against the rulebook's worked
example, puzzle 2-2, and round trips of each implemented rule, and records which
candidate key texts have been ruled out.

If you found this page by searching for *Decipher III*, *the Decipher puzzle*, *Warren
Holland*, *The Money Hunt*, *John Poser*, *the unsolved $100,000 jigsaw*, or *Karen
Puzzles' unsolved videos*: you are in the right place, and here is the whole picture.

## Status at a glance

| Puzzle | Year | Prize | Status |
|---|---|---|---|
| Decipher I | 1983 | $100,000 | **Solved** 1985 by Baldwin & Sherman (MIT); key = Sagan, *Cosmos* ch. 6 |
| Decipher II 2-1 / 2-2 / 2-3 | 1985 | $25,000 each | **Solved** in contest (Novak, Chirpich, Brown) |
| Decipher II 2-4 | 1985 | $25,000 | **Solved then LOST** — winner unknown, solution never recovered |
| Decipher III 3-1 / 3-2 / 3-3 | 1987 | $100,000 | **UNSOLVED** — no winner ever came forward |
| The Money Hunt | 1986 | $1,000,000 | **UNSOLVED** — prize expired 1988; answer never published |

## Start here

| Document | What it gives you |
|---|---|
| [`docs/decipher-i.md`](docs/decipher-i.md) | The solved 1983 puzzle, and why it is the Rosetta stone for the rest |
| [`docs/decipher-ii.md`](docs/decipher-ii.md) | Three solved messages, the lost fourth, and what has been eliminated for it |
| [`docs/decipher-iii.md`](docs/decipher-iii.md) | The three open ciphers, the recovered author groups A/B/C, the ranked suspect list |
| [`docs/money-hunt.md`](docs/money-hunt.md) | The million-dollar treasure hunt: what is established, what was added in 2026, what is open |
| [`docs/methodology.md`](docs/methodology.md) | How the book-cipher attack works, how the scoring is calibrated, what a "no hit" proves |
| [`docs/check-your-own-book.md`](docs/check-your-own-book.md) | How to photograph a paperback, OCR it, sweep it, and read a hit |
| [`docs/sources.md`](docs/sources.md) | Every video, document, archive and article, with links |
| [`results/RUN_LOG.md`](results/RUN_LOG.md) | Sweeps run for this repository, with scores, durations and verdicts |

## The primary material — Karen Puzzles

Nearly all of the source material here was gathered and freely shared by **Karen
Kavett / Karen Puzzles**. Watch the videos first; they are the reason this repository
exists.

- Channel: https://www.youtube.com/@KarenPuzzles · site: https://www.karenkavett.com
- [*The $100,000 Puzzle That Took Two Years to Solve*](https://www.youtube.com/watch?v=meaUE2b5whI) — Decipher I
- [*The $100,000 Puzzles That Were NEVER SOLVED*](https://www.youtube.com/watch?v=-XnCfS3ee8c) — Decipher II & III
- [*The Little-Known $1,000,000 Puzzle That's Never Been Solved*](https://www.youtube.com/watch?v=lYuS2rja2nI) — The Money Hunt

Her shared research — the master document with every cipher and author list, the scan
folders, the solving notes — is linked (not rehosted) in [`docs/sources.md`](docs/sources.md).
This repository deliberately ships **no scans, no photographs and no copyrighted book
text**; it links to her folders and lets you supply your own books.

## What this repository adds

1. **A solver with a regression suite.** `solver/validate.py` runs 93 checks: the
   Decipher III rulebook's worked example (three ciphers that must decode to CODES),
   puzzle 2-2 against the 42 *Catch-22* chapter titles, an encode→search→decode round
   trip for each of 21 rule families in all four direction combinations, and 3
   null-tolerance checks. `solver/sweep.py` also tests a chapter-title chain when a
   `.chapters.json` file is present beside the book.
2. **Eliminations that can be rerun.** About 15 million candidate key-stream positions
   across 61 public-domain texts and 21 rule families. The 61 are 49 Project Gutenberg
   texts, 9 Poe texts, and 3 Standard Ebooks Faulkner editions. Five further Gutenberg
   books are the scoring model only; they are not elimination targets. Edgar Allan Poe
   is ruled out for message 3-1; the public-domain members of all three author groups
   are ruled out for 3-2/3-3; six of eleven authors are ruled out for the lost 2-4.
   The logs and top scores are in `results/`.
3. **Author groups and cipher sequences.** The three Decipher III author groups (A/B/C)
   are printed in the rulebook and copied here. They had been described as lost with
   the 1987 hotline. All seven cipher sequences were re-transcribed from the printed
   puzzle surfaces and compared token by token. One stored number was wrong and is
   corrected here.
4. **Money Hunt notes and an errata.** A page-by-page image read of all 24 clue
   pages, and an errata listing fourteen defects in the earlier transcriptions.
   Three of those notes describe the wrong page. The affected page files are stubs.
5. **A path for anyone with a bookshelf.** The remaining suspects are all in-copyright
   and DRM-locked as ebooks, so the only lawful machine-readable route is your own
   physical copy. [`docs/check-your-own-book.md`](docs/check-your-own-book.md) is the
   complete loop, including copy-paste prompts for driving your own LLM through it.

## Quick start

Needs [uv](https://docs.astral.sh/uv/). From this directory:

```
uv run python solver/fetch_texts.py     # public-domain corpus + scoring model
uv run python solver/validate.py        # 93 checks; all must pass
uv run python solver/sweep.py BOOK.txt --cipher all --top 10
```

If `uv` is not found: install it first (`winget install astral-sh.uv`, or
`pip install uv`), then restart the terminal so the PATH change takes effect
— that restart step is the usual snag on Windows. If `uv run` instead
complains that no scoring model is found, run the `fetch_texts.py` line
above first; it downloads the five public-domain model books and the sweep
corpus.

Genuine English decodes score ≈ −7.9…−8.0 per trigram; noise sits at −8.6 and below.
Anything above −8.2 is flagged for a human with the physical book.

## How this was made

The analysis, transcriptions, eliminations and code were produced with AI coding
assistants — primarily **Qwen Code** (Alibaba), with earlier exploration by
**GLM** (Zhipu AI), further research, review and auditing by **Grok** (xAI),
and this pre-publication audit by **Kimi** (Moonshot AI).
Multimodal models read the puzzle scans, rulebook pages and clue-book artwork;
coding models wrote and tested the solver. What 1987 needed a Symbolics Lisp
machine and a month of hotline clues to attempt, 2026 needs a laptop, a used
paperback and an afternoon. The text of the remaining in-copyright books is still
required, and that is a legal and logistical limit.

No personal prompts, private correspondence or identifying details are included.
The compiler asks for no personal credit. Write-ups are CC-BY-4.0
([LICENSE-DOCS.md](LICENSE-DOCS.md)); code is MIT ([LICENSE](LICENSE)). Please
credit Karen Puzzles for the source material, and Project Gutenberg and Standard
Ebooks for the public-domain texts. Attribution to the compiler is not requested.
