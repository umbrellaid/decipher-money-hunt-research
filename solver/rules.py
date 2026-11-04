"""Key-stream rule families for the Decipher book-cipher attack.

Every builder returns a contiguous A-Z stream, which is what engine.search_stream
consumes (it slides the numbering start across the stream and also tests the
reversed stream). Families mirror the rules Warren Holland actually used on the
solved puzzles, plus the variants the Decipher III clues point at ("10", "End")
and the null-tolerance question raised by the rulebook.

Two search shapes are needed, not one. The 21 families below are *sliding*: the
numbering start is unknown, so engine.search_stream tries every offset. Puzzle 2-1
turned out to use a different shape (Eckman 2026,
doi:10.5281/zenodo.23844582): a single passage doubled with its own reversal,
`S || reverse(S)`, which is *anchored* — the passage boundary fixes both the start
and the turnaround, so sliding cannot express it. `palindromic_candidates` emits
each of the 21 families in that doubled form, anchored on paragraph boundaries and
gated to the passage lengths a given cipher can actually address. Without it the
sweep would return a noise-band negative on the correct book, passage and offset:
153 of 2-1's 314 integers exceed the 492-letter source. See docs/methodology.md
gap 3.

Validated provenance for each family is recorded in validate.py.
"""
import re

from engine import ASCII, first_letters, last_letters, letters_only

SENTENCE_END = re.compile(r"[.!?][\"')\]]?\s+")


def line_first_letters(text):
    out = []
    for ln in text.split("\n"):
        s = ln.strip()
        if not s:
            continue
        for c in s:
            if c in ASCII:
                out.append(c.upper())
                break
    return "".join(out)


def line_last_letters(text):
    out = []
    for ln in text.split("\n"):
        s = ln.strip()
        last = ""
        for c in s:
            if c in ASCII:
                last = c.upper()
        if last:
            out.append(last)
    return "".join(out)


def every_nth_letter(text, n):
    """The '10' clue read as: every Nth letter of the continuous letter stream."""
    return letters_only(text)[n - 1::n]


def every_nth_word_first(text, n):
    return first_letters(text)[n - 1::n]


def every_nth_word_last(text, n):
    return last_letters(text)[n - 1::n]


def words(text):
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text)


def word_nth_letter(text, k):
    """k-th letter of every word that has at least k letters (1-based)."""
    out = []
    for w in words(text):
        letters = [c for c in w if c.isalpha()]
        if len(letters) >= k:
            out.append(letters[k - 1].upper())
    return "".join(out)


def sentence_first_letters(text):
    out = []
    start = True
    for c in text:
        if c in ASCII:
            if start:
                out.append(c.upper())
                start = False
        elif c in ".!?" :
            start = True
    return "".join(out)


def paragraph_first_letters(text):
    out = []
    for para in re.split(r"\n\s*\n", text):
        for c in para:
            if c in ASCII:
                out.append(c.upper())
                break
    return "".join(out)


def base_rules(text):
    """The five families used by the original sweeps (kept byte-identical)."""
    return {
        "letters": letters_only(text),
        "first-letters": first_letters(text),
        "last-letters": last_letters(text),
        "line-first": line_first_letters(text),
        "line-last": line_last_letters(text),
    }


def extended_rules(text, steps=(2, 3, 5, 10)):
    """New families added 2026-10-05. '10' is the printed Message #1 clue."""
    rules = {}
    for n in steps:
        rules[f"every{n}-letter"] = every_nth_letter(text, n)
        rules[f"every{n}-wordfirst"] = every_nth_word_first(text, n)
        rules[f"every{n}-wordlast"] = every_nth_word_last(text, n)
    for k in (2, 3):
        rules[f"word{k}th-letter"] = word_nth_letter(text, k)
    rules["sentence-first"] = sentence_first_letters(text)
    rules["paragraph-first"] = paragraph_first_letters(text)
    return rules


def chapter_title_chain(titles):
    """Letters of chapter titles in order, concatenated.

    Puzzle 2-2 uses this chain reversed. The decoded letters are then read
    backwards. Apostrophes, digits, and other non-letters are dropped.
    """
    return "".join(letters_only(t) for t in titles)


def all_rules(text, steps=(2, 3, 5, 10)):
    rules = base_rules(text)
    rules.update(extended_rules(text, steps))
    return rules


def sentence_boundary_starts(text):
    """(letter_index, word_index) for the start of every sentence in `text`.

    Both coordinates are returned because engine.search_anchored works in STREAM
    coordinates and the families differ: the continuous-letter family indexes by
    letter, the word-initial families index by word.

    Sentence starts are the anchoring granularity for the palindromic scan. 2-1's
    passage opens "Those to whom the king had entrusted me", a sentence start.
    Paragraph runs were tried first and are far too coarse: the Gutenberg prose
    corpus averages about 48 letters per paragraph (Austen and Melville are both
    dialogue-heavy), so reaching the 490-letter lower bound of the 2-1 gate needs
    runs of roughly fifteen paragraphs, and measured candidate counts came out at
    ZERO for the 2-1 and 2-4 gates across three different texts.
    """
    out = [(0, 0)]
    letters = words = 0
    in_word = False
    pending = False
    for ch in text:
        if ch in ASCII:
            if not in_word:
                if pending:
                    out.append((letters, words))
                    pending = False
                words += 1
                in_word = True
            letters += 1
        else:
            in_word = False
            if ch in ".!?":
                pending = True
    return out


def palindromic_length_gate(max_n):
    """Passage lengths worth testing for a cipher whose largest integer is max_n.

    A key of S || reverse(S) has 2*len(S) positions and indexing is 1-based, so it
    must satisfy 2*len(S) >= max_n, giving the lower bound ceil(max_n/2). At
    len(S) == max_n every observation maps into the forward half and the reversal is
    never reached, so the construction degenerates to a plain forward stream that the
    sliding sweep in sweep.py already covers; hence the upper bound max_n - 1.

    For 2-1 (max_n 980) this is [490, 979], which admits the true 492-letter source
    and also admits the 490-letter Wikisource variant - deliberately, since that
    variant is the near-miss the window score exists to surface.

    This replaces body_scan.py's fixed `len(words) >= 240` gate, which was a
    window-level word count and could never select a 492-letter passage.
    """
    return -(-max_n // 2), max_n - 1


def anchored_scan_families():
    """The families whose stream coordinates map exactly onto a passage start.

    Deliberately narrow. `letters` indexes by letter and `first-letters` /
    `last-letters` index by word, so a sentence start converts to a stream index
    with no ambiguity. The every-Nth and word-Nth-letter families stride through
    the text, so a sentence start does not land on a stream index without a
    separate mapping, and guessing that mapping would silently produce an empty or
    misaligned search that still printed a confident negative. They are NOT covered
    by the anchored palindromic scan, and a negative from it does not speak to them.

    `letters` is also the family 2-1 actually used, so the highest-value case is
    the one that is covered.
    """
    return ("letters", "first-letters", "last-letters")
