"""
Translation layer v1: build beat → measure lookup from the score.
Standalone script — no Matchmaker yet, just verifying we can
extract the right structure from the MusicXML file.
"""
from pathlib import Path
from music21 import converter

SCRIPT_DIR = Path(__file__).parent
SCORE_FILE = SCRIPT_DIR / "idea-n10-gibran-alcocer-8bars.mxl"

from score_model import build_lookup
lookup, _ = build_lookup(SCORE_FILE)

# Print it so we can eyeball it
print(f"{'Measure':>8} {'Start beat':>12} {'End beat':>12} {'Length':>8}")
print("-" * 45)
for start, end, num in lookup:
    print(f"{num:>8} {start:>12.2f} {end:>12.2f} {end - start:>8.2f}")

print(f"\nTotal measures: {len(lookup)}")
print(f"Score spans beat {lookup[0][0]:.2f} to beat {lookup[-1][1]:.2f}")
