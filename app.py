"""Bundled recording rehearsal player. Run: python -m streamlit run app.py"""
import base64
from dataclasses import asdict
import json
from pathlib import Path
import streamlit as st
from alignment import prepare_alignment
from score_model import SCORE_FILE, render_score

ROOT = Path(__file__).parent
AUDIO_FILE = ROOT / 'Idea10.wav'
st.set_page_config(page_title='Turn The Page', page_icon='🎵', layout='wide')
st.title('Turn The Page')
st.caption('Idea No. 10 · Gibran Alcocer · Recorded rehearsal')

@st.cache_data(show_spinner=False)
def prepare(score_bytes, audio_bytes):
    # File contents are cache keys, so replacing an asset invalidates the session.
    return asdict(render_score(SCORE_FILE)), prepare_alignment(SCORE_FILE, AUDIO_FILE)

try:
    with st.spinner('Preparing score and following timeline… You can play when this finishes.'):
        model, events = prepare(SCORE_FILE.read_bytes(), AUDIO_FILE.read_bytes())
except Exception as error:
    st.error(f'Could not prepare this rehearsal: {error}')
    st.info('Check the installation steps in README.md, then reload.')
    st.stop()

payload = dict(model=model, events=events,
               audio=base64.b64encode(AUDIO_FILE.read_bytes()).decode('ascii'))
# Escape HTML script terminators while preserving JSON string values.
data = json.dumps(payload).replace('<', '\\u003c')
html = (ROOT / 'player.html').read_text().replace('__REHEARSAL_DATA__', data)
html = html.replace('__STATE_MODULE__', base64.b64encode((ROOT / 'player_state.mjs').read_bytes()).decode('ascii'))
st.iframe(html, height=1100, alt="Interactive music score rehearsal player")
st.caption('This version follows the bundled recording. Microphone input and arbitrary scores are not supported yet.')
