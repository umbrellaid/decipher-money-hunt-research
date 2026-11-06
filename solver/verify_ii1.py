# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
verify_ii1.py — independent verification of the published Decipher II-1 reconstruction.

Reimplements the construction from the *specification* in Eckman (2026),
"An Independent Reconstruction of Decipher II, Message 1 (1985-86)",
https://doi.org/10.5281/zenodo.23844582, and compares the results against that
paper's published SHA-256 values. **No third-party code is imported or executed.**
A match is therefore two independent implementations agreeing, which is stronger
evidence than running the author's own decoder.

Construction under test (paper section 3.1):

    N(P) = retain_ASCII_A_to_Z(uppercase(NFKD(P)))
    S    = N(P)                       |S| = 492
    K    = S || reverse(S)            |K| = 984
    sigma(n) = n          for 1 <= n <= 492
    sigma(n) = 985 - n    for 493 <= n <= 984
    p_i = K[c_i] = S[sigma(c_i)]      for 1 <= i <= 314

Two working corrections are applied to the historical transcription (paper
Table 2). This repository's `data/ciphers.json` already carries the 388 reading
at observation 306, corrected here on 2026-10-05 and independently re-derived by
Eckman; observation 169 still carries the original 330.

What this script does NOT do: it never prints, writes or stores the decoded
message. The plaintext is third-party expression that the author deliberately
does not redistribute (see his RIGHTS_AND_LICENSING.md); only its length and
SHA-256 are reported. The Swift passage in `data/gulliver_ii1_passage.txt` is a
public-domain transcription of the Alden (1911) witness and is safe to hold.

Run from the repository root:

    uv run solver/verify_ii1.py

Exits 0 only if every published value reproduces.
"""
from __future__ import annotations

import hashlib
import json
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

PASSAGE = ROOT / "data" / "gulliver_ii1_passage.txt"
CORRECTIONS = ROOT / "data" / "ii1_corrections.json"
CIPHERS = ROOT / "data" / "ciphers.json"

# Published values, transcribed from the reconstruction's README and paper.
EXPECT_SOURCE_LEN = 492
EXPECT_KEY_LEN = 984
EXPECT_PLAIN_LEN = 314
EXPECT_SOURCE_SHA = "9eeff566fe707e39486c1bb119d5c82f19566772706342c44803d6079faef29d"
EXPECT_KEY_SHA = "571b2327a0ef55d6fc74394b228ffc59e24a00f2ef6f670beb1fa08879eb5466"
EXPECT_PLAIN_SHA = "859f2c3458025e03ad8a425b8e9b9e16f152927b8b34e33300ad1d49d065ee1f"
# Fingerprint of the ORIGINAL (uncorrected) 314-value transcription: 1,530
# canonical ASCII bytes, decimal integers separated by comma-space, then "." and LF.
EXPECT_INPUT_SHA = "1e60d5d63422148b385abfd0569edb1c709308eb79d51e4195b6c8a781be2edc"
EXPECT_INPUT_BYTES = 1530
# Distinct-value counts stated in the paper's section 2.
EXPECT_DISTINCT_ORIGINAL = 259
EXPECT_DISTINCT_CORRECTED = 261

failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(name)


def sha(text: str) -> str:
    """SHA-256 over uppercase ASCII letters, no trailing newline."""
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def normalize(passage: str) -> str:
    """NFKD, uppercase, retain ASCII A-Z only (paper section 3.1)."""
    decomposed = unicodedata.normalize("NFKD", passage).upper()
    return "".join(c for c in decomposed if "A" <= c <= "Z")


def sigma(n: int, half: int) -> int:
    """One-based position within S for key slot n of K = S || reverse(S)."""
    return n if n <= half else 2 * half + 1 - n


def main() -> int:
    if not PASSAGE.is_file():
        sys.exit(f"Missing {PASSAGE}. See docs/decipher-ii.md for provenance.")
    passage = PASSAGE.read_text(encoding="utf-8")

    # --- 1. The source sequence -------------------------------------------
    source = normalize(passage)
    check("source: passage normalizes to 492 letters",
          len(source) == EXPECT_SOURCE_LEN, f"got {len(source)}")
    check("source: SHA-256 matches the published value",
          sha(source) == EXPECT_SOURCE_SHA, f"got {sha(source)}")

    # --- 2. The 984-position palindromic key -------------------------------
    key = source + source[::-1]
    check("key: length is 984", len(key) == EXPECT_KEY_LEN, f"got {len(key)}")
    check("key: SHA-256 matches the published value",
          sha(key) == EXPECT_KEY_SHA, f"got {sha(key)}")
    half = EXPECT_SOURCE_LEN
    check("key: slot n and slot 985-n address the same letter",
          all(key[n - 1] == key[2 * half + 1 - n - 1] for n in range(1, half + 1)))
    check("key: the turnaround duplicates the last source letter at slots 492/493",
          key[half - 1] == key[half] == source[-1])

    # --- 3. The historical transcription and its corrections ---------------
    cipher = json.loads(CIPHERS.read_text(encoding="utf-8"))["2-1"]
    spec = json.loads(CORRECTIONS.read_text(encoding="utf-8"))["corrections"]
    check("transcription: 314 tokens, all integers (no literal letters in 2-1)",
          len(cipher) == EXPECT_PLAIN_LEN and all(isinstance(t, int) for t in cipher),
          f"n={len(cipher)}")

    original = list(cipher)
    working = list(cipher)
    for c in spec:
        idx = c["position"] - 1
        transcribed, corrected = c["transcribed"], c["corrected"]
        stored = working[idx]
        original[idx] = transcribed
        if stored == transcribed:
            state, ok = "applied here", True
        elif stored == corrected:
            state, ok = "already applied in this repository", True
        else:
            state, ok = f"UNEXPECTED stored value {stored}", False
        working[idx] = corrected
        check(f"correction: observation {c['position']} {transcribed}->{corrected}",
              ok, state)

    check(f"transcription: {EXPECT_DISTINCT_ORIGINAL} distinct original values",
          len(set(original)) == EXPECT_DISTINCT_ORIGINAL,
          f"got {len(set(original))}")
    check(f"transcription: {EXPECT_DISTINCT_CORRECTED} distinct corrected values",
          len(set(working)) == EXPECT_DISTINCT_CORRECTED,
          f"got {len(set(working))}")

    # --- 4. Cross-check against the author's input fingerprint -------------
    # Our 2-1 was transcribed from the printed puzzle surface at 3x on 2026-10-05;
    # his came via Kavett's public compilation. The fingerprint is over the
    # PRE-correction sequence, so observation 306 is reverted from our 388 to the
    # compilation's 338 before hashing. A shared fingerprint therefore means the two
    # records agree on 313 of 314 observations, and differ at 306 only because this
    # repository applies the photograph-supported correction there. Do not describe
    # this as "all 314 agree" - see Addendum 1,
    # doi:10.5281/zenodo.23963541, and results/eckman-ii1-verification-2026-11-03.md
    # for the three qualifications on calling our reading independent at all.
    canonical = ", ".join(str(n) for n in original) + ".\n"
    check(f"fingerprint: canonical form is {EXPECT_INPUT_BYTES} ASCII bytes",
          len(canonical.encode("ascii")) == EXPECT_INPUT_BYTES,
          f"got {len(canonical.encode('ascii'))}")
    fp = hashlib.sha256(canonical.encode("ascii")).hexdigest()
    check("fingerprint: our original transcription matches the published input hash",
          fp == EXPECT_INPUT_SHA, f"got {fp}")

    # --- 5. Decode ---------------------------------------------------------
    # The 169 correction moves an observation across the halfway point: 330 sits
    # in the forward half, 830 in the reversal half. Both counts are asserted so
    # the effect of that single correction is explicit rather than incidental.
    orig_over = sum(1 for n in original if n > half)
    over_half = [n for n in working if n > half]
    check("decode: every observation resolves inside the 984-position key",
          all(1 <= n <= len(key) for n in working),
          f"max={max(working)} keylen={len(key)}")
    check("reachability: 152 of 314 original observations exceed the 492-letter source",
          orig_over == 152, f"got {orig_over}")
    check("reachability: 153 of 314 working observations need the reversal half "
          "(obs 169 crosses the halfway point, 330->830)",
          len(over_half) == 153, f"got {len(over_half)}")

    plain = "".join(key[sigma(n, half) - 1] for n in working)
    check("decode: plaintext is 314 letters", len(plain) == EXPECT_PLAIN_LEN,
          f"got {len(plain)}")
    check("decode: plaintext SHA-256 matches the published value",
          sha(plain) == EXPECT_PLAIN_SHA, f"got {sha(plain)}")
    positions: dict[int, list[int]] = {}
    for i, v in enumerate(working):
        positions.setdefault(v, []).append(i)
    repeated = {v: idxs for v, idxs in positions.items() if len(idxs) > 1}
    check("decode: repeated integers decode identically (sanity, not proof)",
          all(len({plain[i] for i in idxs}) == 1 for idxs in repeated.values()),
          f"{len(repeated)} values repeat")

    # Deliberately reported as a hash only. See the module docstring.
    print(f"\nplaintext withheld: {len(plain)} letters, sha256={sha(plain)}")

    print()
    if failures:
        print(f"{len(failures)} FAILURES: {failures}")
        return 1
    print("ALL 2-1 VERIFICATION CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
