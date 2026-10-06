"""Key-stream rule families for the Decipher book-cipher attack.

Every builder returns a contiguous A-Z stream, which is what engine.search_stream
consumes (it slides the numbering start across the stream and also tests the
reversed stream). Families mirror the rules Warren Holland actually used on the
solved puzzles, plus the variants the Decipher III clues point at ("10", "End")
and the null-tolerance question raised by the rulebook.

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
