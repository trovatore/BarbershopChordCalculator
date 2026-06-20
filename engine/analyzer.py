import copy
from typing import List, Dict, Any, Optional
from music21 import chord, interval, pitch


class ChordAnalyzer:
    def __init__(self, notes: List[str], allow_rootless_ninths: bool = False) -> None:
        sanitized: List[str] = [n.replace("x", "##") for n in notes]
        try:
            self.chord_obj: Optional[chord.Chord] = chord.Chord(sanitized)
        except Exception:
            self.chord_obj = None
        self.parts: List[str] = ["Bass", "Bari", "Lead", "Tenor"]
        self.allow_rootless_ninths: bool = allow_rootless_ninths

    def _is_ninth(self) -> bool:
        if not self.chord_obj:
            return False
        c = self.chord_obj
        root = c.root()
        intervals = {interval.Interval(root, p).directedSimpleName for p in c.pitches}
        ninth_shell = {"P1", "M3", "m7", "M2"}
        if ninth_shell.issubset(intervals):
            return True
        if self.allow_rootless_ninths and "half-diminished seventh" in c.commonName:
            return True
        return False

    def _get_barbershop_name(self) -> str:
        c = self.chord_obj
        if not c:
            return "Unknown Chord"
        root = c.root()
        if self.allow_rootless_ninths and "half-diminished seventh" in c.commonName:
            virtual_root = root.transpose("-M3")
            return f"{virtual_root.name} dominant 9th chord (rootless)"
        if self._is_ninth():
            return f"{root.name} dominant 9th chord"
        name: str = c.pitchedCommonName
        if "tetramirror" in name or "forte" in name.lower():
            return c.commonName
        return name

    def get_interval_role(
        self, p: pitch.Pitch, root_override: Optional[pitch.Pitch] = None
    ) -> str:
        if not self.chord_obj:
            return "Unknown"
        root = root_override or self.chord_obj.root()
        if not root:
            return "Unknown"
        p_target = copy.deepcopy(p)
        while p_target.ps < root.ps:
            p_target.octave += 1
        while p_target.ps >= root.ps + 12:
            p_target.octave -= 1
        i = interval.Interval(root, p_target)
        name = i.directedSimpleName
        is_ninth_context = self._is_ninth()
        role_map: Dict[str, str] = {
            "P1": "Root",
            "m2": "Minor 2nd",
            "M2": "Ninth" if is_ninth_context else "Major 2nd",
            "m3": "Minor 3rd",
            "M3": "Major 3rd",
            "P4": "Perfect 4th",
            "A4": "Aug 4th",
            "d5": "Dim 5th",
            "P5": "Fifth",
            "A5": "Aug 5th",
            "m6": "Minor 6th",
            "M6": "Major 6th",
            "d7": "Dim 7th",
            "m7": "Flat 7th",
            "M7": "Major 7th",
            "P8": "Root",
        }
        return role_map.get(name, i.niceName)

    def get_tuning_adjustments(self, style: str = "just") -> List[float]:
        if not self.chord_obj or not self.chord_obj.pitches or style == "equal":
            return [0.0] * len(self.chord_obj.pitches) if self.chord_obj else []

        c = self.chord_obj
        actual_root = c.root()
        tuning_root = actual_root
        if "half-diminished seventh" in c.commonName:
            tuning_root = actual_root.transpose("-M3")

        just_offsets: Dict[str, float] = {
            "Root": 0.0,
            "Ninth": 3.9,
            "Major 2nd": 3.9,
            "Minor 3rd": 15.6,
            "Major 3rd": -13.7,
            "Perfect 4th": -2.0,
            "Dim 5th": -17.5,
            "Fifth": 2.0,
            "Aug 5th": -13.7,
            "Minor 6th": 13.7,
            "Major 6th": -15.6,
            "Dim 7th": -33.1,
            "Flat 7th": -31.2,
            "Major 7th": -11.7,
        }

        pyth_offsets: Dict[str, float] = {
            "Root": 0.0,
            "Ninth": 3.9,
            "Major 2nd": 3.9,
            "Minor 3rd": -5.9,
            "Major 3rd": 7.8,
            "Perfect 4th": -2.0,
            "Dim 5th": -13.7,
            "Fifth": 2.0,
            "Aug 5th": 9.8,
            "Minor 6th": -7.8,
            "Major 6th": 5.9,
            "Dim 7th": -17.6,
            "Flat 7th": -3.9,
            "Major 7th": 9.8,
        }

        # For custom or unknown styles, we provide just_offsets as a baseline
        # calculation, although the frontend typically manages 'custom' overrides.
        offsets = pyth_offsets if style == "pythagorean" else just_offsets
        raw_adjs: List[float] = []
        root_adj_value = 0.0

        for p in c.pitches:
            role = self.get_interval_role(p, root_override=tuning_root)
            adj = offsets.get(role, 0.0)
            raw_adjs.append(adj)
            if p.name == actual_root.name:
                root_adj_value = adj

        return [round(a - root_adj_value, 1) for a in raw_adjs]

    def analyze(self, tuning_style: str = "just") -> Dict[str, Any]:
        c = self.chord_obj
        if not c or not c.pitches:
            return {
                "common_name": "Unknown Chord",
                "inversion": "N/A",
                "voicing": "N/A",
                "notes": [],
            }
        root = c.root()
        virtual_root: Optional[pitch.Pitch] = None
        inversion_name = "N/A"
        if self.allow_rootless_ninths and "half-diminished seventh" in c.commonName:
            virtual_root = root.transpose("-M3")
            inv_idx = c.inversion() + 1
            inv_map = {1: "1st Inversion", 2: "2nd Inversion", 3: "3rd Inversion"}
            inversion_name = inv_map.get(inv_idx, f"Inv {inv_idx}")
        else:
            inv_names: Dict[int, str] = {
                0: "Root Position",
                1: "1st Inversion",
                2: "2nd Inversion",
                3: "3rd Inversion",
            }
            inversion_name = inv_names.get(c.inversion(), f"{c.inversion()} Inversion")

        tunings = self.get_tuning_adjustments(style=tuning_style)
        pitches = c.pitches
        span: float = (
            max(p.ps for p in pitches) - min(p.ps for p in pitches) if pitches else 0
        )
        return {
            "common_name": self._get_barbershop_name(),
            "inversion": inversion_name,
            "voicing": "Closed" if span <= 12 else "Open",
            "notes": [
                {
                    "part": self.parts[i],
                    "note": p.nameWithOctave.replace("##", "x"),
                    "role": self.get_interval_role(p, root_override=virtual_root),
                    "tuning": tunings[i] if i < len(tunings) else 0.0,
                }
                for i, p in enumerate(c.pitches)
            ],
        }