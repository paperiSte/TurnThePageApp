# Turn The Page

A local rehearsal player for the bundled **Idea No. 10** recording and its eight-measure MusicXML excerpt (pickup 0, measures 1–7).

One Start button plays the recording and drives highlighting from its audio clock. The score has two real rendered pages. Two beats before the boundary, the next page appears underneath; the main page advances at the boundary so current notes remain visible. Pause, Restart, Previous/Next and Auto-turn provide recovery controls.

## Run locally

Use Python **3.12**. Install FluidSynth's native library first:

- macOS: `brew install fluidsynth`
- Ubuntu/Debian: `sudo apt-get install libfluidsynth3`

Then, from this directory:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python setup_soundfont.py
python -m streamlit run app.py
```

Open the local URL Streamlit prints. The first preparation synthesizes reference audio and calculates alignment; playback starts only after preparation finishes. `setup_soundfont.py` downloads and verifies Partitura’s default MuseScore soundfont over HTTPS (about 40 MB), avoiding its FTP fallback. Run it once before launching. Subsequent sessions use Streamlit's content-keyed preparation cache. Nothing is sent to an external inference service.

On Windows, FluidSynth must be installed and its DLL discoverable by Python; the commands above are verified for the Python code path on Linux, not a Windows installation.

## Controls

- **Start / Resume** and **Pause** share one audio transport.
- **Restart** pauses, returns to the pickup and clears all turn state.
- **Previous/Next page** enters manual mode. Enable **Auto-turn** to rejoin the recording.
- A two-beat next-page preview retains the current page. The main page advances only once at each boundary; small backward alignment movements do not flip it back.

## Implementation

- `score_model.py`: shared pickup-aware timing map; encodes four measures per page / two per system in MEI, then maps actual SVG IDs to pages. Boundaries come from those rendered pages, not the old fake measure-4 boundary.
- `alignment.py`: explicit Matchmaker Arzt/chroma configuration, timestamped using the configured sample rate and hop length. Preparation runs before playback, with no CPU-time pacing loop.
- `player_state.mjs`: consumes every alignment event crossed by browser audio time, including after a delayed animation frame.
- `player.html`: local embedded audio, SVG reader and transport controls. No external JavaScript CDN.
- `app.py`: Streamlit preparation, error reporting and component host.

The earlier experiment scripts remain for historical comparison. `match_test_mm_live.py` uses a file, despite its name. Their printed thresholds are experimental and do not configure the reader.

## Checks

```sh
python -m unittest discover -s tests
node --test tests/player_state.test.mjs
```

The Python tests check actual excerpt timing, pickup mapping, rendered page membership and threshold suppression. Node tests exercise preview, jitter, delayed updates, manual recovery, pause-time stability and restart. CI runs both suites.

For a real recording check (requires FluidSynth and the soundfont):

```sh
python -m unittest discover -s tests_integration
```

Optional browser smoke check (starts and stops its own local server):

```sh
python -m pip install playwright==1.51.0
python -m playwright install chromium --only-shell
python scripts/browser_smoke.py
```

Before using this for a performance, listen through the recording while watching the highlights, especially pickup → measure 1 and measure 3 → 4. Automated checks verify event delivery and score mapping; musical alignment accuracy still needs listening calibration against manually labelled audible measure starts. No claim of measured beat-level accuracy is made.

## Scope

This is a **recorded rehearsal MVP**, not live piano following. It supports only the bundled excerpt, linear playback, and this fixed two-page layout. The full MusicXML/PDF are preserved as future material but are not loaded. Arbitrary uploads, PDF recognition, repeats/jumps and microphone input are outside this increment. Pedal import warnings from the score are expected; timing and page-membership tests cover the extracted excerpt structure.
