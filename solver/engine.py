"""
Decipher III search engine.

Mechanic (validated on solved Puzzle 2-2):
  - A "key stream" is a string of letters extracted from a published work under some rule.
  - Cipher number n -> letter at position n (1-based) of the stream (0-based index n-1).
  - Some variants number from the END (reversed stream), and the plaintext itself may
    read backwards relative to the decode order (2-2 needed a final reversal).
  - Literal letters embedded in the cipher (E, Y, Z...) map to themselves (proven by 2-3).

Scoring: trigram log-likelihood of the decoded 170-char string under an English model
built from public-domain reference books. We score both the decode and its reverse.
"""
import json
import numpy as np

def letters_only(s):
    return ''.join(c for c in s.upper() if 'A' <= c <= 'Z')

ASCII = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

def first_letters(s):
    out = []
    prev_nonword = True
    for c in s:
        is_word_char = c in ASCII
        if is_word_char and prev_nonword:
            out.append(c.upper())
        prev_nonword = not is_word_char
    return ''.join(out)

def last_letters(s):
    out = []
    in_word = False
    last = ''
    for c in s:
        if c in ASCII:
            in_word = True
            last = c.upper()
        else:
            if in_word:
                out.append(last)
            in_word = False
    if in_word:
        out.append(last)
    return ''.join(out)

class TrigramScorer:
    def __init__(self, texts):
        cnt = np.ones((26*26*26,), dtype=np.float64) * 0.1
        for t in texts:
            L = np.frombuffer(letters_only(t).encode(), dtype=np.uint8).astype(np.int64) - 65
            L = L[(L >= 0) & (L < 26)]
            if len(L) < 10:
                continue
            ids = L[:-2]*676 + L[1:-1]*26 + L[2:]
            np.add.at(cnt, ids, 1.0)
        self.logp = np.log(cnt / cnt.sum())

    def score(self, decoded: str) -> float:
        L = np.frombuffer(decoded.encode(), dtype=np.uint8).astype(np.int64) - 65
        L = L[(L >= 0) & (L < 26)]
        if len(L) < 10:
            return -1e9
        ids = L[:-2]*676 + L[1:-1]*26 + L[2:]
        return float(self.logp[ids].sum() / len(ids))  # per-trigram average

    def score_best_window(self, decoded: str, frac: float = 0.6, min_len: int = 24) -> float:
        """Null-tolerant score: best contiguous window covering `frac` of the decode.

        The Decipher III rulebook warns that plaintexts may contain inserted
        'nulls' (meaningless letters). A whole-decode average is dragged down by
        them; the cleanest window of a partly-nulled English decode still sits in
        the genuine-English band, so this score can surface keys that `score`
        would rank as noise.
        """
        L = np.frombuffer(decoded.encode(), dtype=np.uint8).astype(np.int64) - 65
        L = L[(L >= 0) & (L < 26)]
        n = len(L)
        if n < min_len:
            return self.score(decoded)
        w = max(min_len, int(n * frac))
        ids = L[:-2]*676 + L[1:-1]*26 + L[2:]
        cum = np.concatenate(([0.0], np.cumsum(self.logp[ids])))
        k = w - 2
        wins = (cum[k:] - cum[:len(cum) - k]) / k
        return float(wins.max())

def decode_stream(stream: str, cipher, offset=1) -> str:
    """offset=1 -> 1-based numbering (index n-1); offset=0 -> 0-based."""
    out = []
    for t in cipher:
        if isinstance(t, str):
            out.append(t)
            continue
        i = t - offset
        out.append(stream[i] if 0 <= i < len(stream) else '?')
    return ''.join(out)

def search_stream(stream: str, cipher, scorer: TrigramScorer, max_n: int,
                  step: int = 1, label: str = '', results: list = None, top_k=25):
    """Slide a numbering start position across the stream; also test reversed stream.
    Literal letters embedded in the cipher are kept at their positions (they map to
    themselves, as proven by the solved 2-3). Accumulates (score, label, offset,
    direction, plain-direction) into `results`."""
    need = max_n + 1
    L = np.frombuffer(stream.encode(), dtype=np.uint8).astype(np.int64) - 65
    if ((L < 0) | (L > 25)).any():
        raise ValueError('stream must be A-Z only')
    # numeric-token layout: positions in the cipher of numeric tokens + literal letters
    num_pos = [i for i, t in enumerate(cipher) if isinstance(t, int)]
    nums = np.array([t for t in cipher if isinstance(t, int)])
    lits = {i: ord(str(t).upper()) - 65 for i, t in enumerate(cipher) if isinstance(t, str)}
    all_pos = sorted(num_pos + list(lits.keys()))
    pos_index = {p: k for k, p in enumerate(all_pos)}
    lit_row = np.full(len(all_pos), -1, dtype=np.int64)
    for p, v in lits.items():
        lit_row[pos_index[p]] = v
    num_cols = np.array([pos_index[p] for p in num_pos])
    lit_mask = lit_row >= 0
    lit_vals = np.where(lit_mask, lit_row, 0)
    W = len(all_pos)

    def build_decode(arr, starts):
        n = len(arr)
        idx = starts[:, None] + (nums[None, :] - 1)
        ok = np.all(idx < n, axis=1) & np.all(idx >= 0, axis=1)
        starts = starts[ok]
        idx = idx[ok]
        rows = np.zeros((len(starts), W), dtype=np.int64)
        rows[:, num_cols] = arr[idx]
        rows[:, lit_mask] = lit_vals[lit_mask]
        return starts, rows

    def scan(arr, direction):
        n = len(arr)
        if n < need:
            return
        starts = np.arange(0, n - need + 1, step)
        for chunk_start in range(0, len(starts), 50000):
            st = starts[chunk_start:chunk_start+50000]
            st, mat = build_decode(arr, st)
            if len(st) == 0:
                continue
            def trigram_scores(m):
                a, b, c = m[:, :-2], m[:, 1:-1], m[:, 2:]
                ids = a*676 + b*26 + c
                return scorer.logp[ids].sum(axis=1) / (W - 2)
            scores = trigram_scores(mat)
            rmat = mat[:, ::-1]
            rscores = trigram_scores(rmat)
            for j in range(len(st)):
                if scores[j] >= rscores[j]:
                    results.append((float(scores[j]), label, int(st[j]), direction, 'fwd'))
                else:
                    results.append((float(rscores[j]), label, int(st[j]), direction, 'rev'))

    scan(L, 'fwd')
    scan(L[::-1], 'from-end')
    if results is not None:
        results.sort(key=lambda r: -r[0])
    return results[:top_k] if results else results

def best_decode(stream: str, cipher, offset: int, reverse_plain: bool) -> str:
    d = decode_stream(stream, cipher, offset)
    return d[::-1] if reverse_plain else d
