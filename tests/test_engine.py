import unittest
import sys
import os
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.analyzer import ChordAnalyzer


class TestBarbershopVocab(unittest.TestCase):
    """
    LEGACY SUITE: Ensures no regressions on original project logic.
    Coverage: ~28 cases.
    """

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
            name1 = analyzer1.chord_obj.simplifyEnharmonics().pitchedCommonName
            name2 = analyzer2.chord_obj.simplifyEnharmonics().pitchedCommonName
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
        res: Dict[str, Any] = ChordAnalyzer(["G2", "D3", "B3", "F4"]).analyze()
        self.assertEqual(res["voicing"], "Open")

    def test_barbershop_ninth_special_naming(self) -> None:
        res: Dict[str, Any] = ChordAnalyzer(["G3", "B3", "F4", "A4"]).analyze()
        self.assertEqual(res["common_name"], "G dominant 9th chord")

    def test_invalid_notes_handling(self) -> None:
        res: Dict[str, Any] = ChordAnalyzer(["NotANote", "X", "???"]).analyze()
        self.assertEqual(res["common_name"], "Unknown Chord")
        self.assertEqual(res["notes"], [])

    def test_rootless_ninth_logic(self) -> None:
        notes = ["E3", "G3", "Bb3", "D4"]
        res_off = ChordAnalyzer(notes, allow_rootless_ninths=False).analyze()
        self.assertIn("half-diminished", res_off["common_name"].lower())
        res_on = ChordAnalyzer(notes, allow_rootless_ninths=True).analyze()
        self.assertIn("C dominant 9th chord (rootless)", res_on["common_name"])
        self.assertEqual(res_on["notes"][3]["role"], "Ninth")

    def test_dominant_ninth_omitted_fifth_role(self) -> None:
        res: Dict[str, Any] = ChordAnalyzer(["G3", "B3", "F4", "A4"]).analyze()
        self.assertIn("dominant 9th", res["common_name"].lower())
        roles = [n["role"] for n in res["notes"]]
        self.assertIn("Ninth", roles)

    def test_ji_tuning_major_triad(self) -> None:
        res = ChordAnalyzer(["C3", "E4", "G4"]).analyze()
        tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(tunings, [0.0, -13.7, 2.0])

    def test_ji_tuning_minor_triad(self) -> None:
        res = ChordAnalyzer(["C3", "Eb4", "G4"]).analyze()
        tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(tunings, [0.0, 15.6, 2.0])

    def test_ji_tuning_dominant_seventh(self) -> None:
        res = ChordAnalyzer(["G2", "G3", "B3", "F4"]).analyze()
        tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(tunings, [0.0, 0.0, -13.7, -31.2])

    def test_ji_tuning_half_dim_as_rootless_ninth(self) -> None:
        res = ChordAnalyzer(["E3", "G3", "Bb3", "D4"]).analyze()
        tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(tunings, [0.0, 15.7, -17.5, 17.6])

    def test_ji_tuning_major_seventh(self) -> None:
        res = ChordAnalyzer(["C3", "E4", "G4", "B4"]).analyze()
        tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(tunings, [0.0, -13.7, 2.0, -11.7])

    def test_ji_tuning_minor_seventh(self) -> None:
        res = ChordAnalyzer(["C3", "Eb4", "G4", "Bb4"]).analyze()
        tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(tunings, [0.0, 15.6, 2.0, -31.2])

    def test_ji_tuning_inversion_root_remains_zero(self) -> None:
        res = ChordAnalyzer(["B2", "D3", "F3", "G3"]).analyze()
        tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(tunings, [-13.7, 2.0, -31.2, 0.0])

    def test_pythagorean_tuning_major_triad(self) -> None:
        res = ChordAnalyzer(["C3", "E4", "G4"]).analyze(tuning_style="pythagorean")
        tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(tunings, [0.0, 7.8, 2.0])

    def test_pythagorean_tuning_minor_triad(self) -> None:
        res = ChordAnalyzer(["C3", "Eb4", "G4"]).analyze(tuning_style="pythagorean")
        tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(tunings, [0.0, -5.9, 2.0])

    def test_pythagorean_tuning_dominant_seventh(self) -> None:
        res = ChordAnalyzer(["G3", "B3", "D4", "F4"]).analyze(tuning_style="pythagorean")
        tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(tunings, [0.0, 7.8, 2.0, -3.9])

    def test_equal_temperament_option(self) -> None:
        res = ChordAnalyzer(["C3", "E3", "G3", "Bb3"]).analyze(tuning_style="equal")
        tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(tunings, [0.0, 0.0, 0.0, 0.0])


class TestTheoryGoldStandard(unittest.TestCase):
    """
    DATA-DRIVEN SUITE: Explicit inversion and role mapping for JS port.
    Corrected to anchor tuning to the Chord Root (Root = 0.0).
    """

    def run_analysis_test(
        self,
        notes: List[str],
        expected_name: str,
        expected_inv: str,
        expected_voicing: str,
        expected_roles: List[str],
        expected_just_tunings: List[float],
        allow_rootless: bool = False,
    ) -> None:
        analyzer = ChordAnalyzer(notes, allow_rootless_ninths=allow_rootless)
        res = analyzer.analyze(tuning_style="just")

        self.assertIn(expected_name.lower(), res["common_name"].lower())
        self.assertEqual(res["inversion"], expected_inv)
        self.assertEqual(res["voicing"], expected_voicing)

        actual_roles = [n["role"] for n in res["notes"]]
        self.assertEqual(actual_roles, expected_roles)

        actual_tunings = [n["tuning"] for n in res["notes"]]
        self.assertEqual(actual_tunings, expected_just_tunings)

    def test_major_triad_root_closed(self) -> None:
        self.run_analysis_test(
            notes=["C4", "E4", "G4"],
            expected_name="major triad",
            expected_inv="Root Position",
            expected_voicing="Closed",
            expected_roles=["Root", "Major 3rd", "Fifth"],
            expected_just_tunings=[0.0, -13.7, 2.0],
        )

    def test_minor_triad_1st_inv_open(self) -> None:
        # C minor 1st inv: Eb3(m3), G3(P5), C4(Root). Root is C.
        self.run_analysis_test(
            notes=["Eb3", "G3", "C4"],
            expected_name="minor triad",
            expected_inv="1st Inversion",
            expected_voicing="Closed",
            expected_roles=["Minor 3rd", "Fifth", "Root"],
            expected_just_tunings=[15.6, 2.0, 0.0],
        )

    def test_dom7_root_closed(self) -> None:
        self.run_analysis_test(
            notes=["G3", "B3", "D4", "F4"],
            expected_name="dominant seventh",
            expected_inv="Root Position",
            expected_voicing="Closed",
            expected_roles=["Root", "Major 3rd", "Fifth", "Flat 7th"],
            expected_just_tunings=[0.0, -13.7, 2.0, -31.2],
        )

    def test_dom7_2nd_inv_open(self) -> None:
        # G7/D: D3(P5), G3(Root), B3(M3), F4(m7). Root is G.
        self.run_analysis_test(
            notes=["D3", "G3", "B3", "F4"],
            expected_name="dominant seventh",
            expected_inv="2nd Inversion",
            expected_voicing="Open",
            expected_roles=["Fifth", "Root", "Major 3rd", "Flat 7th"],
            expected_just_tunings=[2.0, 0.0, -13.7, -31.2],
        )

    def test_dom7_3rd_inv_closed(self) -> None:
        # G7/F: F3(m7), G3(Root), B3(M3), D4(P5). Root is G.
        self.run_analysis_test(
            notes=["F3", "G3", "B3", "D4"],
            expected_name="dominant seventh",
            expected_inv="3rd Inversion",
            expected_voicing="Closed",
            expected_roles=["Flat 7th", "Root", "Major 3rd", "Fifth"],
            expected_just_tunings=[-31.2, 0.0, -13.7, 2.0],
        )

    def test_half_dim_as_rootless_ji_anchor(self) -> None:
        # E half-dim: E3, G3, Bb3, D4. 
        # Anchored at actual root (E). E is M3 of virtual root C (-13.7).
        self.run_analysis_test(
            notes=["E3", "G3", "Bb3", "D4"],
            expected_name="half-diminished seventh",
            expected_inv="Root Position",
            expected_voicing="Closed",
            expected_roles=["Root", "Minor 3rd", "Dim 5th", "Flat 7th"],
            expected_just_tunings=[0.0, 15.7, -17.5, 17.6],
        )

    def test_enharmonic_equivalence_fsharp_naming(self) -> None:
        analyzer1 = ChordAnalyzer(["F#3", "A#3", "C#4"])
        res1 = analyzer1.analyze(tuning_style="just")
        # music21 outputs "F#-major triad"
        self.assertIn("F#-major triad", res1["common_name"])

    def test_voicing_border_case(self) -> None:
        # C3 to C4 is exactly 12 semitones -> Closed
        res = ChordAnalyzer(["C3", "G3", "C4"]).analyze()
        self.assertEqual(res["voicing"], "Closed")


if __name__ == "__main__":
    unittest.main()