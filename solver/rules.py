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
import bisect
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
    """The three core families run by default in the anchored palindromic scan.

    `letters` indexes by letter and `first-letters` / `last-letters` index by word,
    so `sentence_boundary_starts` converts directly to stream coordinates (`letters`
    is also the family 2-1 actually used). The remaining 18 strided and structural
    families require modulo-N phase splitting (`(s0 + n - 1) % n`) or character-offset
    alignment so a mid-text sentence start maps onto the exact extracted stream of
    `text[start:]`; `anchored_palindromic_substreams(text, include_extended=True)`
    provides that exact mapping for all 21 families (`sweep.py --all-palindromic`).
    """
    return ("letters", "first-letters", "last-letters")


def sentence_char_offsets(text):
    """0-based character offsets in `text` where each sentence opens."""
    out = []
    in_word = False
    pending = True
    for idx, ch in enumerate(text):
        if ch in ASCII:
            if not in_word:
                if pending:
                    out.append(idx)
                    pending = False
                in_word = True
        else:
            in_word = False
            if ch in ".!?":
                pending = True
    return out


def paragraph_char_offsets(text):
    """0-based character offsets in `text` of the first ASCII letter of each paragraph."""
    out = []
    pos = 0
    for m in re.finditer(r"\n\s*\n", text):
        chunk = text[pos:m.start()]
        for i, ch in enumerate(chunk):
            if ch in ASCII:
                out.append(pos + i)
                break
        pos = m.end()
    chunk = text[pos:]
    for i, ch in enumerate(chunk):
        if ch in ASCII:
            out.append(pos + i)
            break
    return out


def anchored_palindromic_substreams(text, include_extended=False):
    """Yield `(family, phase, substream, starts)` for anchored `S || reverse(S)` scans.

    `phase` is `None` for single-stream families and `0..n-1` (`base[phase::n]`) for
    strided `every{n}-*` families.

    When `include_extended=False`, yields the 3 default families (`letters`,
    `first-letters`, `last-letters`) with identical coordinates to
    `sentence_boundary_starts(text)`.

    When `include_extended=True`, yields exact phase-resolved substreams for all 21
    families in `all_rules(text)`. For 1-based every-Nth extraction (`base[n-1::n]`)
    starting at coordinate `s0`, item `j` lands at `base[s0 + n - 1 + j*n]`, which is
    index `q0 + j` of phase substream `base[p::n]` where `p = (s0 + n - 1) % n` and
    `q0 = (s0 + n - 1) // n`. Splitting into `n` phase substreams preserves exactness
    at every sentence or paragraph start without multiplying total start anchors.
    """
    starts_lw = sentence_boundary_starts(text)
    let_str = letters_only(text)
    wf_str = first_letters(text)
    wl_str = last_letters(text)

    l_starts = [s[0] for s in starts_lw]
    w_starts = [s[1] for s in starts_lw]

    yield ("letters", None, let_str, l_starts)
    yield ("first-letters", None, wf_str, w_starts)
    yield ("last-letters", None, wl_str, w_starts)

    if not include_extended:
        return

    sent_chars = sentence_char_offsets(text)
    para_chars = paragraph_char_offsets(text)
    anchor_chars = sorted(set(sent_chars) | set(para_chars))
    anchor_set = set(anchor_chars)

    # Compute (letter_idx, word_idx) at all sentence OR paragraph openings
    ext_l_starts, ext_w_starts = [], []
    letters_ct = words_ct = 0
    in_word = False
    for idx, ch in enumerate(text):
        if ch in ASCII:
            if not in_word:
                if idx in anchor_set:
                    ext_l_starts.append(letters_ct)
                    ext_w_starts.append(words_ct)
                words_ct += 1
                in_word = True
            letters_ct += 1
        else:
            in_word = False

    for n in (2, 3, 5, 10):
        for fam, base, base_starts in (
            (f"every{n}-letter", let_str, ext_l_starts),
            (f"every{n}-wordfirst", wf_str, ext_w_starts),
            (f"every{n}-wordlast", wl_str, ext_w_starts),
        ):
            buckets = [[] for _ in range(n)]
            for s0 in base_starts:
                p = (s0 + n - 1) % n
                q = (s0 + n - 1) // n
                buckets[p].append(q)
            for p, qs in enumerate(buckets):
                sub = base[p::n]
                if sub and qs:
                    yield (fam, p, sub, sorted(set(qs)))

    word_matches = list(re.finditer(r"[A-Za-z]+(?:'[A-Za-z]+)?", text))
    for k in (2, 3):
        fam = f"word{k}th-letter"
        kept_char_starts = []
        out_chars = []
        for m in word_matches:
            w_alpha = [c for c in m.group(0) if c.isalpha()]
            if len(w_alpha) >= k:
                kept_char_starts.append(m.start())
                out_chars.append(w_alpha[k - 1].upper())
        stream_k = "".join(out_chars)
        if stream_k and anchor_chars:
            idxs = [bisect.bisect_left(kept_char_starts, c) for c in anchor_chars]
            valid_idxs = sorted(set(x for x in idxs if x < len(stream_k)))
            if valid_idxs:
                yield (fam, None, stream_k, valid_idxs)

    lf_chars, ll_chars = [], []
    line_first_char_pos = []
    pos = 0
    for ln in text.split("\n"):
        s = ln.strip()
        if s:
            first_c = ""
            first_off = None
            last_c = ""
            for i_c, c in enumerate(ln):
                if c in ASCII:
                    if not first_c:
                        first_c = c.upper()
                        first_off = pos + i_c
                    last_c = c.upper()
            if first_c:
                lf_chars.append(first_c)
                ll_chars.append(last_c)
                line_first_char_pos.append(first_off)
        pos += len(ln) + 1
    if lf_chars and anchor_chars:
        lf_str = "".join(lf_chars)
        ll_str = "".join(ll_chars)
        lf_starts = [i for i, cp in enumerate(line_first_char_pos) if cp in anchor_set]
        if 0 not in lf_starts:
            lf_starts.insert(0, 0)
        ll_starts = sorted(
            set(
                x
                for x in (bisect.bisect_right(line_first_char_pos, c) - 1 for c in anchor_chars)
                if 0 <= x < len(ll_str)
            )
        )
        yield ("line-first", None, lf_str, sorted(set(lf_starts)))
        if ll_starts:
            yield ("line-last", None, ll_str, ll_starts)

    sf_str = sentence_first_letters(text)
    if sf_str:
        yield ("sentence-first", None, sf_str, list(range(len(sf_str))))

    pf_str = paragraph_first_letters(text)
    if pf_str:
        yield ("paragraph-first", None, pf_str, list(range(len(pf_str))))
