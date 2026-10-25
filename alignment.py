"""Prepare timestamped following events before browser playback starts."""
from queue import Empty
import math


def prepare_alignment(score_path, audio_path):
    from matchmaker import Matchmaker
    mm = Matchmaker(str(score_path), str(audio_path), input_type='audio',
                    method='arzt', processor='chroma', unfold_score=False,
                    kwargs={'sample_rate': 44100, 'hop_length': 2048})
    events = []
    try:
        for beat in mm.run(verbose=False):
            # Each yielded frame corresponds to one configured audio hop.
            # Timestamp the end of the observed frame, rather than CPU time.
            timestamp = (len(events) + 1) * mm.hop_length / mm.sample_rate
            if not math.isfinite(float(beat)):
                raise ValueError('Alignment produced a non-finite beat')
            events.append({'time': timestamp, 'beat': float(beat)})
    except Empty:
        pass  # File-stream EOF in Matchmaker.
    if not events:
        raise ValueError('Alignment produced no positions')
    return events
