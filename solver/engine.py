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

def palindromic_key(source: str) -> str:
    """K = S || reverse(S), the construction Puzzle 2-1 actually uses.

    Eckman (2026, doi:10.5281/zenodo.23844582) established that 2-1's key is a
    492-letter Gulliver's Travels passage concatenated with its own reversal,
    giving 984 positions in which slots n and 985-n address the same letter.
    The printed clue "One way gets you half way there" says exactly this.

    Decoding needs no special index mapping: K is an ordinary string and
    decode_stream(K, cipher, offset=1) resolves every observation. The doubling
    is what makes indices above len(S) reachable at all.
    """
    return source + source[::-1]

def decode_palindromic(source: str, cipher, offset=1) -> str:
    """Decode against S || reverse(S). See palindromic_key."""
    return decode_stream(palindromic_key(source), cipher, offset)

def _cipher_layout(cipher):
    """Numeric tokens and literal letters, laid out for vectorized decoding.

    Literal letters embedded in the cipher (E, Y, Z...) map to themselves, proven
    by the solved 2-3; they occupy fixed output columns whatever the key is. Shared
    by search_stream (sliding) and score_keys (anchored) so the two cannot drift.
    """
    num_pos = [i for i, t in enumerate(cipher) if isinstance(t, int)]
    lits = {i: ord(str(t).upper()) - 65 for i, t in enumerate(cipher) if isinstance(t, str)}
    all_pos = sorted(num_pos + list(lits.keys()))
    pos_index = {p: k for k, p in enumerate(all_pos)}
    lit_row = np.full(len(all_pos), -1, dtype=np.int64)
    for p, v in lits.items():
        lit_row[pos_index[p]] = v
    lit_mask = lit_row >= 0
    return {
        'nums': np.array([t for t in cipher if isinstance(t, int)]),
        'num_cols': np.array([pos_index[p] for p in num_pos]),
        'lit_mask': lit_mask,
        'lit_vals': np.where(lit_mask, lit_row, 0),
        'W': len(all_pos),
    }

def _trigram_means(rows: np.ndarray, scorer) -> np.ndarray:
    """Mean per-trigram log-probability for each row of a (B, W) letter-index matrix."""
    ids = rows[:, :-2] * 676 + rows[:, 1:-1] * 26 + rows[:, 2:]
    return scorer.logp[ids].sum(axis=1) / (rows.shape[1] - 2)

def best_window_matrix(rows: np.ndarray, scorer, frac: float = 0.6,
                       min_len: int = 24) -> np.ndarray:
    """Vectorized TrigramScorer.score_best_window over a batch of decodes.

    Same statistic, same defaults, computed for every row at once. Needed because
    the null-tolerant window score is what surfaces a near-miss whose mean has been
    dragged into the noise band by a textual variant or a wrong construction; a
    per-row Python call is far too slow to run over every candidate.

    Mirrors score_best_window exactly, including both of its fallbacks: rows
    shorter than min_len fall back to the plain mean, and rows shorter than 10
    letters score -1e9, which is what TrigramScorer.score returns for them.
    """
    n = rows.shape[1]
    if n < 10:
        return np.full(rows.shape[0], -1e9)
    ids = rows[:, :-2] * 676 + rows[:, 1:-1] * 26 + rows[:, 2:]
    mean = scorer.logp[ids].sum(axis=1) / ids.shape[1]
    if n < min_len:
        return mean
    w = max(min_len, int(n * frac))
    k = w - 2
    if k < 1 or k > ids.shape[1]:
        return mean
    cum = np.zeros((rows.shape[0], ids.shape[1] + 1), dtype=np.float64)
    np.cumsum(scorer.logp[ids], axis=1, out=cum[:, 1:])
    wins = (cum[:, k:] - cum[:, :cum.shape[1] - k]) / k
    return wins.max(axis=1)

def score_keys(keys, cipher, scorer, chunk: int = 20000):
    """Score complete candidate keys in one batch, without sliding an offset.

    This is the anchored counterpart to search_stream. Sliding is the wrong shape
    for a palindromic key: the passage boundary fixes both the start and the
    turnaround, so each candidate is used as-is from position 1. Indexing is
    1-based, so a key needs at least max_n positions; callers enforce that with the
    `ceil(max_n/2) <= len(S) <= max_n - 1` gate in rules.palindromic_length_gate.

    Returns a list of dicts in input order, carrying BOTH the mean score and the
    null-tolerant window score, plus which plaintext direction won. Ranking on the
    mean alone is what let sweep.py discard edition-drift near-misses unseen.
    """
    lay = _cipher_layout(cipher)
    nums, num_cols = lay['nums'], lay['num_cols']
    lit_mask, lit_vals, W = lay['lit_mask'], lay['lit_vals'], lay['W']
    max_n = int(nums.max()) if len(nums) else 0
    idx = nums - 1
    out = []
    for start in range(0, len(keys), chunk):
        batch = keys[start:start + chunk]
        rows = np.zeros((len(batch), W), dtype=np.int64)
        for r, k in enumerate(batch):
            if len(k) < max_n:
                raise ValueError(
                    f'key {r} has {len(k)} positions but the cipher indexes to '
                    f'{max_n}; apply the length gate before scoring')
            arr = np.frombuffer(k.encode(), dtype=np.uint8).astype(np.int64) - 65
            if ((arr < 0) | (arr > 25)).any():
                raise ValueError('key must be A-Z only')
            rows[r, num_cols] = arr[idx]
        rows[:, lit_mask] = lit_vals[lit_mask]
        mean_f = _trigram_means(rows, scorer)
        mean_r = _trigram_means(rows[:, ::-1], scorer)
        win_f = best_window_matrix(rows, scorer)
        win_r = best_window_matrix(rows[:, ::-1], scorer)
        fwd = mean_f >= mean_r
        for r in range(len(batch)):
            out.append({
                'mean': float(mean_f[r] if fwd[r] else mean_r[r]),
                'windowed': float(win_f[r] if fwd[r] else win_r[r]),
                'plaintext_direction': 'fwd' if fwd[r] else 'rev',
            })
    return out

def search_anchored(stream: str, cipher, scorer, starts, lengths,
                    chunk: int = 10000, top_k: int = 50):
    """Score every (start, L) palindromic key over one stream, vectorized.

    The construction is K = S || reverse(S) with S = stream[start:start+L], so a
    cipher value c resolves to stream[start + sigma(c, L) - 1] where
    sigma(c, L) = c if c <= L else 2L + 1 - c. No key string is ever materialized:
    the (batch, N) index matrix is built directly, which is what makes an exact scan
    over every L affordable.

    `starts` and `lengths` are in STREAM coordinates, so the caller decides what
    counts as a passage boundary - sentence starts for the continuous-letter
    families, word starts for the word-initial families.

    L cannot be subsampled. The 492 / 491 / 490 witness variants recorded in
    docs/methodology.md gap 1 show that a single letter's difference destroys
    alignment, so every integer length in the gate has to be tried.

    Returns (by_mean, by_window): two lists of at most top_k dicts, each with
    score, windowed, start, length and plaintext_direction. Both lists are needed
    because the two statistics have different noise floors; ranking on the mean
    alone is what let edition-drift near-misses go unseen.
    """
    lay = _cipher_layout(cipher)
    nums, num_cols = lay['nums'], lay['num_cols']
    lit_mask, lit_vals, W = lay['lit_mask'], lay['lit_vals'], lay['W']
    max_n = int(nums.max()) if len(nums) else 0

    arr = np.frombuffer(stream.encode(), dtype=np.uint8).astype(np.int64) - 65
    if ((arr < 0) | (arr > 25)).any():
        raise ValueError('stream must be A-Z only')
    n = len(arr)

    starts = np.asarray(starts, dtype=np.int64)
    lengths = np.asarray(lengths, dtype=np.int64)
    if starts.size == 0 or lengths.size == 0:
        return [], []

    # 2L >= max_n so the doubled key reaches the largest observation; start+L <= n
    # so the passage exists inside the stream.
    ok = (2 * lengths[None, :] >= max_n) & (starts[:, None] + lengths[None, :] <= n) \
        & (lengths[None, :] > 0)
    si, li = np.nonzero(ok)
    st_all, len_all = starts[si], lengths[li]
    n_pairs = len(st_all)
    if n_pairs == 0:
        return [], []

    by_mean, by_window = [], []
    for c0 in range(0, n_pairs, chunk):
        b_st = st_all[c0:c0 + chunk][:, None]
        b_len = len_all[c0:c0 + chunk][:, None]
        sigma = np.where(nums[None, :] <= b_len, nums[None, :],
                         2 * b_len + 1 - nums[None, :])
        idx = b_st + sigma - 1
        rows = np.zeros((idx.shape[0], W), dtype=np.int64)
        rows[:, num_cols] = arr[idx]
        rows[:, lit_mask] = lit_vals[lit_mask]

        mean_f = _trigram_means(rows, scorer)
        mean_r = _trigram_means(rows[:, ::-1], scorer)
        win_f = best_window_matrix(rows, scorer)
        win_r = best_window_matrix(rows[:, ::-1], scorer)
        fwd = mean_f >= mean_r
        mean = np.where(fwd, mean_f, mean_r)
        win = np.where(fwd, win_f, win_r)

        k = min(top_k, len(mean))
        for pick, order in ((np.argpartition(-mean, k - 1)[:k], by_mean),
                            (np.argpartition(-win, k - 1)[:k], by_window)):
            for j in pick:
                order.append({
                    'score': float(mean[j]), 'windowed': float(win[j]),
                    'start': int(b_st[j, 0]), 'length': int(b_len[j, 0]),
                    'plaintext_direction': 'fwd' if fwd[j] else 'rev',
                    'pairs': n_pairs,
                })
    by_mean.sort(key=lambda d: -d['score'])
    by_window.sort(key=lambda d: -d['windowed'])
    return by_mean[:top_k], by_window[:top_k]


def search_stream(stream: str, cipher, scorer: TrigramScorer, max_n: int,
                  step: int = 1, label: str = '', results: list = None, top_k=25):
    """Slide a numbering start position across the stream; also test reversed stream.
    Literal letters embedded in the cipher are kept at their positions (they map to
    themselves, as proven by the solved 2-3). Accumulates (score, label, offset,
    direction, plain-direction) into `results`."""
    need = max_n
    L = np.frombuffer(stream.encode(), dtype=np.uint8).astype(np.int64) - 65
    if ((L < 0) | (L > 25)).any():
        raise ValueError('stream must be A-Z only')
    lay = _cipher_layout(cipher)
    nums, num_cols = lay['nums'], lay['num_cols']
    lit_mask, lit_vals, W = lay['lit_mask'], lay['lit_vals'], lay['W']

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
