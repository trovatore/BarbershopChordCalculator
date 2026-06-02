import unittest
import sys
import os
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.analyzer import ChordAnalyzer


class TestBarbershopVocab(unittest.TestCase):
    def test_major_triad_closed_root(self) -> None:
        res: Dict[str, Any] = ChordAnalyzer(["C4", "E4", "G4"]).analyze()
        self.assertIn("major triad", res["common_name"].lower())
        self.assertEqual(res["voicing"], "Closed")
        self.assertEqual(res["inversion"], "Root Position")
        self.assertEqual(res["notes"][0]["role"], "Root")

    def test_minor_triad_open_first_inversion(self) -> None:
        res: Dict[str, Any] = ChordAnalyzer(["C3", "E4", "A4"]).analyze()
        self.assertIn("minor triad", res["common_name"].lower())
        self.assertEqual(res["inversion"], "1st Inversion")

    def test_dominant_seventh_closed_root(self) -> None:
        res: Dict[str, Any] = ChordAnalyzer(["G3", "B3", "D4", "F4"]).analyze()
        self.assertIn("dominant seventh", res["common_name"].lower())
        self.assertEqual(res["notes"][3]["role"], "Flat 7th")

    def test_dominant_seventh_open_second_inversion(self) -> None:
        res: Dict[str, Any] = ChordAnalyzer(["F3", "Bb3", "D4", "Ab4"]).analyze()
        self.assertEqual(res["voicing"], "Open")
        self.assertEqual(res["inversion"], "2nd Inversion")

    def test_half_diminished_seventh_closed_third_inversion(self) -> None:
        res: Dict[str, Any] = ChordAnalyzer(["C4", "D4", "F4", "Ab4"]).analyze()
        self.assertIn("half-diminished seventh", res["common_name"].lower())
        self.assertEqual(res["notes"][1]["role"], "Root")

    def test_major_seventh_closed_root(self) -> None:
        res: Dict[str, Any] = ChordAnalyzer(["Ab3", "C4", "Eb4", "G4"]).analyze()
        self.assertIn("major seventh", res["common_name"].lower())

    def test_minor_seventh_open_first_inversion(self) -> None:
        res: Dict[str, Any] = ChordAnalyzer(["A2", "E3", "F#3", "C#4"]).analyze()
        self.assertIn("minor seventh", res["common_name"].lower())
        self.assertEqual(res["inversion"], "1st Inversion")

    def test_diminished_seventh_closed_second_inversion(self) -> None:
        res: Dict[str, Any] = ChordAnalyzer(["F3", "Ab3", "B3", "D4"]).analyze()
        self.assertIn("diminished seventh", res["common_name"].lower())
        self.assertEqual(res["notes"][1]["role"], "Dim 7th")

    def test_ninth_omitted_fifth_open(self) -> None:
        res: Dict[str, Any] = ChordAnalyzer(["C3", "E4", "Bb4", "D5"]).analyze()
        self.assertIn("dominant 9th", res["common_name"].lower())
        self.assertEqual(res["notes"][0]["role"], "Root")
        self.assertEqual(res["notes"][3]["role"], "Ninth")

    def test_double_accidental_logic(self) -> None:
        res: Dict[str, Any] = ChordAnalyzer(["F#3", "A#3", "Cx4"]).analyze()
        self.assertIn("augmented", res["common_name"].lower())
        self.assertEqual(res["notes"][2]["note"], "Cx4")
        self.assertEqual(res["notes"][2]["role"], "Aug 5th")

    def test_enharmonic_equivalence(self) -> None:
        analyzer1 = ChordAnalyzer(["G3", "B3", "D4", "F4"])
        analyzer2 = ChordAnalyzer(["G3", "Cb4", "D4", "F4"])

        if analyzer1.chord_obj and analyzer2.chord_obj:
            name1: str = analyzer1.chord_obj.simplifyEnharmonics().pitchedCommonName
            name2: str = analyzer2.chord_obj.simplifyEnharmonics().pitchedCommonName
            self.assertEqual(name1, name2)
        else:
            self.fail("Chord objects could not be initialized")

    def test_e_half_diminished_roles(self) -> None:
        res: Dict[str, Any] = ChordAnalyzer(["G3", "Bb3", "D4", "E4"]).analyze()
        self.assertEqual(res["notes"][3]["role"], "Root")
        self.assertEqual(res["notes"][2]["role"], "Flat 7th")
        self.assertEqual(res["notes"][1]["role"], "Dim 5th")
        self.assertEqual(res["notes"][0]["role"], "Minor 3rd")

    def test_dominant_seventh_open_voicing_span(self) -> None:
        """Explicitly tests the 'Open' voicing detection via span."""
        res: Dict[str, Any] = ChordAnalyzer(["G2", "D3", "B3", "F4"]).analyze()
        self.assertEqual(res["voicing"], "Open")

    def test_barbershop_ninth_special_naming(self) -> None:
        """Tests the custom logic for incomplete dominant 9th chords."""
        res: Dict[str, Any] = ChordAnalyzer(["G3", "B3", "F4", "A4"]).analyze()
        self.assertEqual(res["common_name"], "G dominant 9th chord")

    def test_invalid_notes_handling(self) -> None:
        """Tests behavior with invalid musical input."""
        res: Dict[str, Any] = ChordAnalyzer(["NotANote", "X", "???"]).analyze()
        self.assertEqual(res["common_name"], "Unknown Chord")
        self.assertEqual(res["notes"], [])

    def test_rootless_ninth_logic(self) -> None:
        """Tests that E half-dim is treated as C9 rootless when enabled."""
        notes = ["E3", "G3", "Bb3", "D4"]

        # Disabled
        res_off = ChordAnalyzer(notes, allow_rootless_ninths=False).analyze()
        self.assertIn("half-diminished", res_off["common_name"].lower())
        self.assertEqual(res_off["notes"][0]["role"], "Root")

        # Enabled
        res_on = ChordAnalyzer(notes, allow_rootless_ninths=True).analyze()
        self.assertIn("C dominant 9th chord (rootless)", res_on["common_name"])
        self.assertEqual(res_on["inversion"], "1st Inversion")
        self.assertEqual(res_on["notes"][0]["role"], "Major 3rd")
        self.assertEqual(res_on["notes"][3]["role"], "Ninth")

    def test_dominant_ninth_omitted_fifth_role(self) -> None:
        """Confirms Ninth role labeling in dominant 9th context."""
        res: Dict[str, Any] = ChordAnalyzer(["G3", "B3", "F4", "A4"]).analyze()
        self.assertIn("dominant 9th", res["common_name"].lower())
        roles = [n["role"] for n in res["notes"]]
        self.assertIn("Ninth", roles)

    def test_ji_tuning_major_triad(self) -> None:
        """Major triad: Root (0), M3 (-13.7), P5 (+2.0)."""
        res = ChordAnalyzer(["C3", "E4", "G4"]).analyze()
        tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(tunings, [0.0, -13.7, 2.0])

    def test_ji_tuning_minor_triad(self) -> None:
        """Minor triad: Root (0), m3 (+15.6), P5 (+2.0)."""
        res = ChordAnalyzer(["C3", "Eb4", "G4"]).analyze()
        tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(tunings, [0.0, 15.6, 2.0])

    def test_ji_tuning_dominant_seventh(self) -> None:
        """Dom 7th: Root (0), M3 (-13.7), P5 (2.0), Flat 7 (-31.2)."""
        res = ChordAnalyzer(["G2", "G3", "B3", "F4"]).analyze()
        tunings = [n["tuning"] for n in res["notes"]]
        # Two Gs are both roots
        self.assertEqual(tunings, [0.0, 0.0, -13.7, -31.2])

    def test_ji_tuning_dominant_ninth_no_fifth(self) -> None:
        """Dom 9th (no 5th): Root (0), M3 (-13.7), Flat 7 (-31.2), Ninth (+3.9)."""
        res = ChordAnalyzer(["C3", "E4", "Bb4", "D5"]).analyze()
        tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(tunings, [0.0, -13.7, -31.2, 3.9])

    def test_ji_tuning_half_dim_as_rootless_ninth(self) -> None:
        """
        E-G-Bb-D treated as C9 (rootless).
        Virtual offsets (vs C): E:-13.7, G:2.0, Bb:-31.2, D:3.9.
        Physical Root E must be 0: All offsets +13.7.
        E:0, G:15.7, Bb:-17.5, D:17.6.
        """
        res = ChordAnalyzer(["E3", "G3", "Bb3", "D4"]).analyze()
        tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(tunings, [0.0, 15.7, -17.5, 17.6])

    def test_ji_tuning_major_seventh(self) -> None:
        """Major 7th: Root (0), M3 (-13.7), P5 (2.0), M7 (-11.7)."""
        res = ChordAnalyzer(["C3", "E4", "G4", "B4"]).analyze()
        tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(tunings, [0.0, -13.7, 2.0, -11.7])

    def test_ji_tuning_minor_seventh(self) -> None:
        """Minor 7th (harmonic): Root (0), m3 (+15.6), P5 (2.0), Flat 7 (-31.2)."""
        res = ChordAnalyzer(["C3", "Eb4", "G4", "Bb4"]).analyze()
        tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(tunings, [0.0, 15.6, 2.0, -31.2])

    def test_ji_tuning_inversion_root_remains_zero(self) -> None:
        """In G7 1st inversion (B in bass), G is still the 0 reference."""
        res = ChordAnalyzer(["B2", "D3", "F3", "G3"]).analyze()
        # Order: B, D, F, G
        # Roles: M3, P5, m7, Root
        # Offsets: -13.7, 2.0, -31.2, 0.0
        tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(tunings, [-13.7, 2.0, -31.2, 0.0])


if __name__ == "__main__":
    unittest.main()
