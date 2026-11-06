# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow"]
# ///
"""
blind_read.py — prepare a genuinely blind reading of a contested region of a scan.

Why this exists. When two candidate readings of one glyph are already written down
somewhere (a paper, a corrections file, a chat log), every reader who has seen that
document is contaminated and cannot be blind. The 2026-11-05 reading of Decipher II
observation 169 (`330` vs `830`) was settled this way: four fresh model contexts,
given only a neutrally-named crop and a plain transcription instruction, returned
`830` unanimously while correctly reading the genuine `330` two rows away. See
results/blind-reading-protocol-2026-11-05.md.

Blindness is engineered by this tool, not assumed:

  1. The crop is written to a NEUTRAL filename. The real source name says what the
     document is, and a reader who sees it can look the answer up.
  2. The printed prompt names no project, no candidate values and no observation
     numbers. It asks for every number in the image, so the reader cannot tell which
     one is under test.
  3. The crop is built to contain CONTROLS as well as the target: other glyphs that
     exercise the same confusion (a genuine `330` beside the contested `830`).
     Agreement on the target alone proves little; getting the controls right in the
     same image is what makes the result mean something.
  4. Nothing about the target position is written into the artifact.

The crop derives from a copyrighted scan and MUST NOT be committed or published.
Default output is the system temp directory for that reason.

Usage:
    uv run solver/blind_read.py --source PATH --box X0,Y0,X1,Y1 [--scale 2]
                                [--out PATH] [--emit-prompt]

To regenerate the exact observation-169 crop used on 2026-11-05:
    --source ".../Decipher-II-puzzle-front.jpg" --box 300,1650,2600,2200 --scale 2
"""
from __future__ import annotations

import argparse
import secrets
import sys
from pathlib import Path

from PIL import Image

PROMPT = """You are doing a pure optical transcription task. There is no puzzle, no project, \
no context, and nothing to investigate or look up. Do not search the filesystem, do not open \
any other file, do not run any command, do not use any tool except reading the single image \
named below.

Read the image at this exact path:
{path}

It shows several rows of printed comma-separated integers (mostly three digits, a few two \
digits) on a jigsaw-puzzle surface.

Transcribe EVERY number visible, row by row, left to right, top to bottom. Output exactly one \
line per row, numbers separated by ", ". Transcribe only what the glyphs show; do not infer \
from patterns or from neighbouring rows. If a digit is genuinely ambiguous, still give your \
best reading, and after all rows add a final line beginning with "AMBIGUOUS:" listing which \
numbers you were unsure about and what the alternatives were. If none, write "AMBIGUOUS: none".
"""

# Variants that decorrelate the readers' errors. Agreement across differently-biased
# readers is evidence; agreement across identical readers is repetition.
VARIANTS = {
    "plain": "",
    "primed": (
        "For EACH number, look carefully at every digit individually before writing it, and "
        "pay particular attention to distinguishing 3 from 8 and 3 from 9: a 3 is open on its "
        "left side, an 8 is closed at top and bottom, a 9 has a closed loop only at the top. "
    ),
    "rtl": (
        "Work row by row, top to bottom. Within each row read the numbers right to left, then "
        "reverse your list for that row before writing it out (this is a deliberate check on "
        "reading order). "
    ),
}


def parse_box(s: str) -> tuple[int, int, int, int]:
    try:
        x0, y0, x1, y1 = (int(v) for v in s.split(","))
    except ValueError:
        sys.exit(f"--box must be X0,Y0,X1,Y1 integers, got {s!r}")
    if not (x1 > x0 and y1 > y0):
        sys.exit(f"--box corners are not ordered: {s}")
    return x0, y0, x1, y1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True, help="path to the scan (typically under private/)")
    ap.add_argument("--box", required=True, help="crop box X0,Y0,X1,Y1 in source pixels")
    ap.add_argument("--scale", type=int, default=2, help="upscale factor (default 2)")
    ap.add_argument("--quality", type=int, default=95)
    ap.add_argument("--out", default=None,
                    help="output path; defaults to a random name in the system temp dir")
    ap.add_argument("--variant", choices=sorted(VARIANTS), default="plain",
                    help="which reader prompt to emit")
    ap.add_argument("--emit-prompt", action="store_true", help="print the reader prompt")
    args = ap.parse_args()

    src = Path(args.source)
    if not src.is_file():
        sys.exit(f"source not found: {src}")
    x0, y0, x1, y1 = parse_box(args.box)

    im = Image.open(src)
    W, H = im.size
    if x1 > W or y1 > H:
        sys.exit(f"--box exceeds the source image ({W}x{H})")

    if args.out:
        out = Path(args.out)
    else:
        import tempfile
        out = Path(tempfile.gettempdir()) / f"blind_{secrets.token_hex(6)}.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)

    crop = im.crop((x0, y0, x1, y1))
    if args.scale != 1:
        crop = crop.resize((crop.width * args.scale, crop.height * args.scale), Image.LANCZOS)
    crop.save(out, quality=args.quality)

    print(f"source : {src}")
    print(f"box    : {x0},{y0},{x1},{y1}  scale={args.scale}")
    print(f"crop   : {out}  ({crop.width}x{crop.height})")
    print()
    print("REMINDER: this crop derives from a copyrighted scan. Do not commit it,")
    print("publish it, or attach it to a public issue. The reader receives only the")
    print("neutral filename and the prompt below.")
    print()
    print(f"--- reader prompt ({args.variant}) ---")
    prompt = PROMPT.format(path=out)
    extra = VARIANTS[args.variant]
    if extra:
        prompt = prompt.replace("Transcribe EVERY number visible,", extra + "Transcribe EVERY number visible,")
    print(prompt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
