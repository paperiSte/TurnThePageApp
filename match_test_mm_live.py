"""
End-to-end pipeline test:
audio → Matchmaker → beat → measure → page turn decision

Reuses the logic from page_turn_logic.py, wired into the live
Matchmaker frame loop instead of replaying captured frames.
"""
from pathlib import Path
from queue import Empty
from matchmaker import Matchmaker

from page_turn_logic import (
    build_lookup,
    page_end_beats,
    PageTurner,
    LOOKAHEAD_BEATS,
    PAGE_BREAKS_AFTER_MEASURE,
)

SCRIPT_DIR       = Path(__file__).parent
SCORE_FILE       = SCRIPT_DIR / "idea-n10-gibran-alcocer-8bars.mxl"
PERFORMANCE_FILE = SCRIPT_DIR / "Idea10.wav"


from score_model import beat_to_measure


# --- Setup: parse score, build lookup, configure page turner ---
print(f"Score file:       {SCORE_FILE.name}")
print(f"Performance file: {PERFORMANCE_FILE.name}")
print("-" * 60)

lookup, pickup_offset = build_lookup(SCORE_FILE)
page_ends = page_end_beats(lookup, pickup_offset, PAGE_BREAKS_AFTER_MEASURE)
turner = PageTurner(page_ends, LOOKAHEAD_BEATS)

print(f"Pages: {len(PAGE_BREAKS_AFTER_MEASURE) + 1}")
print(f"Page 1 ends after measure {PAGE_BREAKS_AFTER_MEASURE[0]} "
      f"(Matchmaker beat {page_ends[0]:.2f})")
print(f"Lookahead: {LOOKAHEAD_BEATS} beats → trigger at beat "
      f"{page_ends[0] - LOOKAHEAD_BEATS:.2f}\n")

# --- Run Matchmaker and feed every frame through the pipeline ---
mm = Matchmaker(
    score_file       = str(SCORE_FILE),
    performance_file = str(PERFORMANCE_FILE),
    input_type       = "audio",
)

print("Running alignment...\n")
print(f"{'Frame':>6} {'Beat':>8} {'Measure':>9}   Event")
print("-" * 60)

frame_count = 0
try:
    for current_beat in mm.run():
        frame_count += 1
        measure = beat_to_measure(current_beat, lookup, pickup_offset)
        turn_fired = turner.update(current_beat)

        # Print every 20th frame, plus any frame where a turn fires
        if frame_count % 20 == 0 or turn_fired is not None:
            event = (f"🔔 FIRE page turn {turn_fired + 1}"
                     if turn_fired is not None else "")
            print(f"{frame_count:>6} {current_beat:>8.2f} "
                  f"{str(measure):>9}   {event}")

except Empty:
    print("\n(End of audio reached.)")

print(f"\n{'-' * 60}")
print(f"Total frames processed: {frame_count}")
print(f"Pages turned: {len(turner.fired)} of {len(page_ends)}")