import unittest
from pathlib import Path
from score_model import SCORE_FILE, build_lookup, beat_to_measure, render_score
from page_turn_logic import PageTurner

class ScoreTests(unittest.TestCase):
    def test_pickup_boundaries(self):
        lookup, pickup = build_lookup(SCORE_FILE)
        self.assertEqual(pickup, 1.5)
        for beat, expected in [(-2,None),(-1.5,0),(-0.01,0),(0,1),(3,2),(18,7),(30,7)]:
            self.assertEqual(beat_to_measure(beat,lookup,pickup),expected)

    def test_real_pages_and_explicit_ids(self):
        model=render_score()
        self.assertEqual(len(model.pages),2)
        self.assertEqual([m['number'] for m in model.measures],list(range(8)))
        self.assertEqual(model.boundaries,[9.0])
        for m in model.measures:
            self.assertIn(f'id="{m["id"]}"',model.pages[m['page']])
            self.assertNotIn(f'id="{m["id"]}"',model.pages[1-m['page']])

    def test_turn_threshold_and_jitter(self):
        t=PageTurner([9.0],2)
        self.assertIsNone(t.update(6.9))
        self.assertEqual(t.update(7),0)
        self.assertIsNone(t.update(6))
        self.assertIsNone(t.update(12))
        self.assertEqual(PageTurner([9],2).update(7),0)

if __name__=='__main__':unittest.main()
