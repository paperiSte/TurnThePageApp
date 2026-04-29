"""
Translation layer v3: page-turn trigger.

Given the current beat position (from Matchmaker) and a set of
page boundaries, decide whether to fire a page turn.

Trigger rule: fire when we are within LOOKAHEAD_BEATS of the end
of the current page, and haven't fired for this page yet.
"""
from pathlib import Path
from music21 import converter

SCRIPT_DIR = Path(__file__).parent
SCORE_FILE = SCRIPT_DIR / "idea-n10-gibran-alcocer-8bars.mxl"

# --- Tunable UX parameter ---
LOOKAHEAD_BEATS = 2.0   # turn this many beats before the page ends

# --- Fake page layout for testing ---
# "Page 1 ends after measure 4" → the first page contains measures 0-4
PAGE_BREAKS_AFTER_MEASURE = [4]   # list, so we can extend to multi-page later


def build_lookup(score_path):
    score = converter.parse(str(score_path))
    measures = list(score.parts[0].getElementsByClass("Measure"))
    lookup = [
        (float(m.offset),
         float(m.offset) + float(m.duration.quarterLength),
         m.number)
        for m in measures
    ]
    pickup_offset = next(start for start, _, num in lookup if num == 1)
    return lookup, pickup_offset


def page_end_beats(lookup, pickup_offset, breaks_after):
    """
    For each page break, return the music21-beat where that page ends.
    Expressed in Matchmaker's convention (subtract pickup_offset).
    """
    ends = []
    for measure_num in breaks_after:
        # find the end beat of that measure in music21's convention
        end_music21 = next(end for _, end, num in lookup if num == measure_num)
        # convert to Matchmaker convention
        ends.append(end_music21 - pickup_offset)
    return ends


class PageTurner:
    """Stateful page-turn decider. Remembers which pages have fired."""

    def __init__(self, page_end_beats_mm, lookahead_beats):
        self.page_ends = page_end_beats_mm
        self.lookahead = lookahead_beats
        self.fired = set()   # indices of pages already turned

    def update(self, current_beat):
        """
        Call on every Matchmaker frame.
        Returns page index (0, 1, ...) if a turn should fire now,
        otherwise None.
        """
        for i, page_end in enumerate(self.page_ends):
            if i in self.fired:
                continue
            if current_beat >= page_end - self.lookahead:
                self.fired.add(i)
                return i
        return None


# --- Simulate with today's captured Matchmaker frames ---
if __name__ == "__main__":
    lookup, pickup_offset = build_lookup(SCORE_FILE)
    page_ends = page_end_beats(lookup, pickup_offset, PAGE_BREAKS_AFTER_MEASURE)

    print(f"Pickup offset: {pickup_offset} beats")
    print(f"Page-end beats (Matchmaker convention): {page_ends}")
    print(f"Lookahead: {LOOKAHEAD_BEATS} beats")
    print(f"→ Page 1 turn should fire at beat "
          f"{page_ends[0] - LOOKAHEAD_BEATS:.2f}\n")

    turner = PageTurner(page_ends, LOOKAHEAD_BEATS)

    # Replay today's chroma-run beat positions frame by frame
    frames = [
        (20,  -1.50), (40,  4.83), (60,  9.83), (80, 10.50),
        (100, 14.50), (140, 15.50), (160, 17.37), (200, 17.37),
        (260, 17.37), (300, 17.77), (320, 18.50), (340, 20.03),
    ]

    print(f"{'Frame':>6} {'Beat':>8}   Event")
    print("-" * 50)
    for frame, beat in frames:
        result = turner.update(beat)
        event = f"🔔 FIRE page turn {result + 1}" if result is not None else ""
        print(f"{frame:>6} {beat:>8.2f}   {event}")