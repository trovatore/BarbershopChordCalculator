import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.analyzer import ChordAnalyzer


class TestBarbershopVocab(unittest.TestCase):
    def test_major_triad_closed_root(self):
        res = ChordAnalyzer(["C4", "E4", "G4"]).analyze()
        self.assertIn("major triad", res["common_name"].lower())
        self.assertEqual(res["voicing"], "Closed")
        self.assertEqual(res["inversion"], "Root Position")
        self.assertEqual(res["notes"][0]["role"], "Root")

    def test_minor_triad_open_first_inversion(self):
        res = ChordAnalyzer(["C3", "E4", "A4"]).analyze()
        self.assertIn("minor triad", res["common_name"].lower())
        self.assertEqual(res["inversion"], "1st Inversion")

    def test_dominant_seventh_closed_root(self):
        res = ChordAnalyzer(["G3", "B3", "D4", "F4"]).analyze()
        self.assertIn("dominant seventh", res["common_name"].lower())
        self.assertEqual(res["notes"][3]["role"], "Flat 7th")

    def test_dominant_seventh_open_second_inversion(self):
        res = ChordAnalyzer(["F3", "Bb3", "D4", "Ab4"]).analyze()
        self.assertEqual(res["voicing"], "Open")
        self.assertEqual(res["inversion"], "2nd Inversion")

    def test_half_diminished_seventh_closed_third_inversion(self):
        res = ChordAnalyzer(["C4", "D4", "F4", "Ab4"]).analyze()
        self.assertIn("half-diminished seventh", res["common_name"].lower())
        self.assertEqual(res["notes"][1]["role"], "Root")

    def test_major_seventh_closed_root(self):
        res = ChordAnalyzer(["Ab3", "C4", "Eb4", "G4"]).analyze()
        self.assertIn("major seventh", res["common_name"].lower())

    def test_minor_seventh_open_first_inversion(self):
        res = ChordAnalyzer(["A2", "E3", "F#3", "C#4"]).analyze()
        self.assertIn("minor seventh", res["common_name"].lower())
        self.assertEqual(res["inversion"], "1st Inversion")

    def test_diminished_seventh_closed_second_inversion(self):
        res = ChordAnalyzer(["F3", "Ab3", "B3", "D4"]).analyze()
        self.assertIn("diminished seventh", res["common_name"].lower())
        self.assertEqual(res["notes"][1]["role"], "Dim 7th")

    def test_ninth_omitted_fifth_open(self):
        res = ChordAnalyzer(["C3", "E4", "Bb4", "D5"]).analyze()
        self.assertIn("dominant 9th", res["common_name"].lower())
        self.assertEqual(res["notes"][0]["role"], "Root")
        self.assertEqual(res["notes"][3]["role"], "Major 2nd")

    def test_double_accidental_logic(self):
        res = ChordAnalyzer(["F#3", "A#3", "Cx4"]).analyze()
        self.assertIn("augmented", res["common_name"].lower())
        self.assertEqual(res["notes"][2]["note"], "Cx4")
        self.assertEqual(res["notes"][2]["role"], "Aug 5th")

    def test_enharmonic_equivalence(self):
        obj1 = ChordAnalyzer(["G3", "B3", "D4", "F4"]).chord_obj
        obj2 = ChordAnalyzer(["G3", "Cb4", "D4", "F4"]).chord_obj
        name1 = obj1.simplifyEnharmonics().pitchedCommonName
        name2 = obj2.simplifyEnharmonics().pitchedCommonName
        self.assertEqual(name1, name2)

    def test_e_half_diminished_roles(self):
        res = ChordAnalyzer(["G3", "Bb3", "D4", "E4"]).analyze()
        self.assertEqual(res["notes"][3]["role"], "Root")
        self.assertEqual(res["notes"][2]["role"], "Flat 7th")
        self.assertEqual(res["notes"][1]["role"], "Dim 5th")
        self.assertEqual(res["notes"][0]["role"], "Minor 3rd")


if __name__ == "__main__":
    unittest.main()
