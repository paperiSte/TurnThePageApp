"""Opt-in check with the real audio; requires native FluidSynth."""
import math
import unittest
import wave
from pathlib import Path
from alignment import prepare_alignment
from score_model import SCORE_FILE, render_score

class RecordingTests(unittest.TestCase):
    def test_bundled_audio_reaches_real_page_boundary(self):
        audio=Path(__file__).resolve().parents[1]/'Idea10.wav'
        with wave.open(str(audio)) as f:
            duration=f.getnframes()/f.getframerate()
        events=prepare_alignment(SCORE_FILE,audio)
        model=render_score()
        self.assertGreater(len(events),10)
        self.assertTrue(all(math.isfinite(e['beat']) for e in events))
        self.assertTrue(all(a['time']<b['time'] for a,b in zip(events,events[1:])))
        self.assertLessEqual(events[-1]['time'],duration+2048/44100)
        self.assertGreaterEqual(max(e['beat'] for e in events),model.boundaries[0])
        self.assertLessEqual(events[0]['beat'],0)

if __name__=='__main__':unittest.main()
