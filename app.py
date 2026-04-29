"""
Turn The Page — Phase 3: Matchmaker + translation layer in the browser.
 
Now with audio playback so the page-turn timing can actually be
evaluated against the music it's synchronized to.
 
HOW TO RUN:
    python -m streamlit run app.py
"""
 
from pathlib import Path
from queue import Empty
import re
import time
 
import streamlit as st
from matchmaker import Matchmaker
import verovio
 
from page_turn_logic import (
    build_lookup,
    page_end_beats,
    PageTurner,
    LOOKAHEAD_BEATS,
    PAGE_BREAKS_AFTER_MEASURE,
)
 
# ── Config ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR       = Path(__file__).parent
SCORE_FILE       = SCRIPT_DIR / "idea-n10-gibran-alcocer-8bars.mxl"
PERFORMANCE_FILE = SCRIPT_DIR / "Idea10.wav"
 
st.set_page_config(page_title="Turn The Page", page_icon="🎵", layout="centered")
 
# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f0f1a; }
    .measure-display {
        font-size: 96px;
        font-weight: bold;
        color: #a78bfa;
        text-align: center;
        font-family: Georgia, serif;
        padding: 20px;
        min-height: 140px;
    }
    .measure-label {
        font-size: 14px;
        color: #6b7280;
        text-align: center;
        font-family: monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .beat-display {
        font-size: 14px;
        color: #6b7280;
        text-align: center;
        font-family: monospace;
    }
    .page-indicator {
        font-size: 24px;
        color: #c4b5fd;
        text-align: center;
        font-family: Georgia, serif;
        padding: 30px;
        border: 2px solid #534AB7;
        border-radius: 12px;
        margin: 16px 0;
    }
    .page-flipped {
        background-color: #534AB7;
        color: white;
        transition: background-color 0.6s ease;
    }
    .bell-fired {
        font-size: 48px;
        text-align: center;
        color: #E24B4A;
        animation: flash 0.8s ease-out;
    }
    .measure-active {
    fill: #E24B4A !important;
    stroke: #E24B4A !important;
    }      
    @keyframes flash {
        0%   { transform: scale(0.5); opacity: 0; }
        50%  { transform: scale(1.2); opacity: 1; }
        100% { transform: scale(1.0); opacity: 1; }
    }
    div[data-testid="stButton"] button {
        width: 100%;
        background-color: #534AB7;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px;
        font-size: 16px;
    }
    div[data-testid="stButton"] button:hover { background-color: #3C3489; }
</style>
""", unsafe_allow_html=True)
 
# ── Helpers ────────────────────────────────────────────────────────────────────
def beat_to_measure(beat, lookup, pickup_offset):
    shifted = beat + pickup_offset
    for start, end, num in lookup:
        if start <= shifted < end:
            return num
    if shifted >= lookup[-1][1]:
        return lookup[-1][2]
    return None
 
 
def _render_score():
    tk = verovio.toolkit()
    tk.loadFile(str(SCORE_FILE))
    tk.setOptions({
        "pageWidth": 2100,
        "scale": 35,
        "adjustPageHeight": True,
    })
    svg = tk.renderToSVG(1)
    ids = re.findall(
        r'<g[^>]*id="([^"]+)"[^>]*class="measure"',
        svg,
    )
    return svg, ids
 
 
# ── Session state ──────────────────────────────────────────────────────────────
if "running" not in st.session_state:
    st.session_state.running = False
 
if (
    "score_svg" not in st.session_state
    or not st.session_state.score_svg
    or not st.session_state.measure_ids
):
    st.session_state.score_svg, st.session_state.measure_ids = _render_score()
 
# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("## 🎵 Turn The Page")
st.markdown("*Score-following demo · Idea No. 10 · Gibran Alcocer*")
st.divider()
score_ph = st.empty()
 
# ── Setup ──────────────────────────────────────────────────────────────────────
lookup, pickup_offset = build_lookup(SCORE_FILE)
page_ends = page_end_beats(lookup, pickup_offset, PAGE_BREAKS_AFTER_MEASURE)
total_beats = lookup[-1][1] - pickup_offset
trigger_beat = page_ends[0] - LOOKAHEAD_BEATS
 
st.markdown(
    f"<p class='measure-label'>Page 1 ends after measure "
    f"{PAGE_BREAKS_AFTER_MEASURE[0]} · "
    f"Turn fires at beat {trigger_beat:.1f} "
    f"({LOOKAHEAD_BEATS}-beat lookahead)</p>",
    unsafe_allow_html=True,
)
 
# ── Audio player ──────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<p class='measure-label'>Performance audio</p>", unsafe_allow_html=True
)
with open(PERFORMANCE_FILE, "rb") as f:
    audio_bytes = f.read()
st.audio(audio_bytes, format="audio/wav")
st.markdown(
    "<p class='beat-display'>▲ Press play above, then click Start "
    "Alignment below — try to start them together.</p>",
    unsafe_allow_html=True,
)
 
st.markdown("<br>", unsafe_allow_html=True)
 
# ── Start button ───────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if not st.session_state.running:
        if st.button("▶  Start Alignment"):
            st.session_state.running = True
            st.rerun()
 
# ── UI placeholders ────────────────────────────────────────────────────────────
measure_label_ph = st.empty()
measure_ph       = st.empty()
beat_ph          = st.empty()
progress_ph      = st.empty()
bell_ph          = st.empty()
page_ph          = st.empty()
 
def render_page(current_page):
    page_class = "page-indicator page-flipped" if current_page == 2 else "page-indicator"
    page_ph.markdown(
        f"<div class='{page_class}'>📄 Showing page {current_page} of 2</div>",
        unsafe_allow_html=True,
    )
 
# Initial render
score_ph.markdown(st.session_state.score_svg, unsafe_allow_html=True)
measure_label_ph.markdown(
    "<p class='measure-label'>Current measure</p>", unsafe_allow_html=True
)
measure_ph.markdown(
    "<div class='measure-display'>—</div>", unsafe_allow_html=True
)
beat_ph.markdown(
    "<div class='beat-display'>Waiting to start…</div>", unsafe_allow_html=True
)
progress_ph.progress(0.0)
render_page(1)
 
# ── Main pipeline ──────────────────────────────────────────────────────────────
if st.session_state.running:
    turner = PageTurner(page_ends, LOOKAHEAD_BEATS)
    current_page = 1
 
    mm = Matchmaker(
        score_file       = str(SCORE_FILE),
        performance_file = str(PERFORMANCE_FILE),
        input_type       = "audio",
    )
 
    HOP_DURATION = 2048 / 44100  # ≈ 46ms per frame
    loop_start = time.time()
    frames = []
    last_measure = None
    current_beat = 0.0
 
    try:
        for current_beat in mm.run():
            frames.append(current_beat)
            frame_count = len(frames)
 
            measure = beat_to_measure(current_beat, lookup, pickup_offset)
 
            # Update score highlight when the measure changes
            if measure != last_measure:
                if measure and 1 <= measure <= len(st.session_state.measure_ids):
                    mid = st.session_state.measure_ids[measure - 1]
                    highlight_css = (
                    f"<style>"
                    f"#{mid} {{ fill: #E24B4A !important; }}"
                    f"#{mid} * {{ fill: #E24B4A !important; }}"
                    f"</style>"
                    )
                    score_ph.markdown(
                        highlight_css + st.session_state.score_svg,
                        unsafe_allow_html=True,
                    )
                last_measure = measure
 
                turn_fired = turner.update(current_beat)
    
                progress = max(0.0, min(1.0, current_beat / total_beats))
    
                measure_ph.markdown(
                    f"<div class='measure-display'>"
                    f"{measure if measure is not None else '—'}</div>",
                    unsafe_allow_html=True,
                )
                beat_ph.markdown(
                    f"<div class='beat-display'>Beat {current_beat:.2f} / "
                    f"{total_beats:.2f}</div>",
                    unsafe_allow_html=True,
                )
                progress_ph.progress(progress)
    
                if turn_fired is not None:
                    current_page = turn_fired + 2
                    bell_ph.markdown(
                        "<div class='bell-fired'>🔔 PAGE TURN</div>",
                        unsafe_allow_html=True,
                    )
                    render_page(current_page)
    
                # Pace to real-time using the hop duration of the analysis frames.
                target_elapsed = frame_count * HOP_DURATION
                actual_elapsed = time.time() - loop_start
                sleep_needed = target_elapsed - actual_elapsed
                if sleep_needed > 0:
                    time.sleep(sleep_needed)
 
    except Empty:
        pass
 
    beat_ph.markdown(
        f"<div class='beat-display'>Performance complete · "
        f"final beat {current_beat:.2f}</div>",
        unsafe_allow_html=True,
    )
    st.session_state.running = False
 
    if st.button("↻  Run again"):
        st.rerun()
 