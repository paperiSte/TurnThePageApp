"""
match_test_mm.py
----------------
Go/no-go experiment: can Matchmaker align Idea No. 10 out of the box?

This script is completely separate from match_test.py. Runs in its own
conda env (`matchmaker`, Python 3.12) -- NOT in the `turnthepage` env.

What "success" looks like:
    - The script prints a stream of beat positions.
    - Those numbers start near 0 and rise (roughly) monotonically until
      the end of the piece.
    - No backwards jumps of more than a beat or two.

Files expected in the same folder as this script:
    - idea-n10-gibran-alcocer-8bars.mxl   (the trimmed 8-bar score)
    - Idea10.wav                          (convert Idea10.m4a first)
"""

from pathlib import Path
from queue import Empty   # for a clean end-of-audio exit
from matchmaker import Matchmaker

# --- Configuration ------------------------------------------------------

SCRIPT_DIR = Path(__file__).parent
SCORE_FILE = SCRIPT_DIR / "idea-n10-gibran-alcocer-8bars.mxl"
PERFORMANCE_FILE = SCRIPT_DIR / "Idea10.wav"

# --- Sanity checks ------------------------------------------------------

assert SCORE_FILE.exists(), f"Missing score file: {SCORE_FILE}"
assert PERFORMANCE_FILE.exists(), f"Missing performance file: {PERFORMANCE_FILE}"

print(f"Score file:       {SCORE_FILE.name}")
print(f"Performance file: {PERFORMANCE_FILE.name}")
print("-" * 60)

# --- Run alignment ------------------------------------------------------
#
# Defaults used here:
#   method       = "arzt"    (OLTW variant; the Matchmaker paper found
#                             this performs best for piano audio)
#   feature_type = "chroma"  (the default)
#
# The paper reports "logspectral" outperforms chroma in both accuracy
# and latency. Once this first run succeeds, try changing feature_type
# below to "logspectral" and compare the output.

mm = Matchmaker(
    score_file=str(SCORE_FILE),
    performance_file=str(PERFORMANCE_FILE),
    input_type="audio",
    # method="arzt",
    # feature_type="chroma",     # try "logspectral" on your second run
)

print("Running alignment... (this may take a moment on first run)")
print("Each line below = current beat position in the score, one sample\n")

positions = []
try:
    for current_position in mm.run():
        positions.append(current_position)
        # Print every 20th frame so the terminal doesn't flood
        if len(positions) % 20 == 0:
            print(f"  frame {len(positions):4d}:  beat = {current_position:.2f}")
except Empty:
    # Matchmaker times out waiting for more audio once the file ends.
    # That's expected when feeding a pre-recorded file; treat as EOF.
    print("\n(End of audio reached.)")

# --- Summary ------------------------------------------------------------

print("-" * 60)
if not positions:
    print("No positions were produced. Something went wrong.")
else:
    print(f"Total frames processed: {len(positions)}")
    print(f"First position: {positions[0]:.2f} beats")
    print(f"Last position:  {positions[-1]:.2f} beats")
    print(f"Total range covered: {positions[-1] - positions[0]:.2f} beats")

    # Quick monotonicity check -- a healthy alignment should mostly
    # move forward.
    backward_jumps = sum(
        1 for a, b in zip(positions, positions[1:]) if b < a - 0.5
    )
    print(f"Backward jumps > 0.5 beats: {backward_jumps}")
    if backward_jumps > len(positions) * 0.05:
        print("  (High rate of backward jumps -- alignment may be struggling.)")
    else:
        print("  (Looks mostly forward-moving -- good sign.)")
