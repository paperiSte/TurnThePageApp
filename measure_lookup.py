"""
Translation layer v2: beat → measure lookup function,
calibrated to Matchmaker's beat numbering convention.

Music21 offsets the pickup at beat 0.
Matchmaker reports the pickup as negative (e.g. -1.5),
so we shift its output by +PICKUP_LENGTH before lookup.
"""
from pathlib import Path
from music21 import converter

SCRIPT_DIR = Path(__file__).parent
SCORE_FILE = SCRIPT_DIR / "idea-n10-gibran-alcocer-8bars.mxl"


from score_model import build_lookup, beat_to_measure


# --- Test with the actual beat positions from today's chroma run ---
if __name__ == "__main__":
    lookup, pickup_offset = build_lookup(SCORE_FILE)
    print(f"Pickup offset: {pickup_offset} beats\n")

    # The frame-by-frame positions Matchmaker reported today
    test_positions = [
        (-1.50, "first position (pickup)"),
        (4.83,  "frame 20"),
        (9.83,  "frame 40"),
        (10.50, "frame 60"),
        (14.50, "frame 80 — held chord"),
        (15.50, "frame 140"),
        (17.37, "frame 160 — sustain pedal"),
        (18.50, "frame 320"),
        (20.03, "frame 340 — last position"),
    ]

    print(f"{'Beat':>8} {'Measure':>10}   Description")
    print("-" * 55)
    for beat, desc in test_positions:
        measure = beat_to_measure(beat, lookup, pickup_offset)
        print(f"{beat:>8.2f} {str(measure):>10}   {desc}")