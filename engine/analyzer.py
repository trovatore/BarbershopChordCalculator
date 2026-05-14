import copy
from music21 import chord, interval


class ChordAnalyzer:
    def __init__(self, notes):
        sanitized = [n.replace("x", "##") for n in notes]
        self.chord_obj = chord.Chord(sanitized)
        self.parts = ["Bass", "Bari", "Lead", "Tenor"]

    def _get_barbershop_name(self):
        """
        Refines the music21 chord name for Barbershop vocabulary.
        Specifically handles incomplete Ninth chords.
        """
        c = self.chord_obj
        root = c.root()
        intervals = {interval.Interval(root, p).directedSimpleName for p in c.pitches}

        # Ninth Chord Fingerprint: Root, M3, m7, M9 (M2)
        ninth_set = {"P1", "M3", "m7", "M2"}
        if ninth_set.issubset(intervals):
            return f"{root.name} dominant 9th chord"

        name = c.pitchedCommonName
        if "tetramirror" in name or "forte" in name.lower():
            return c.commonName
        return name

    def get_interval_role(self, p):
        """
        Calculates the musical role of pitch 'p' relative to the chord root.
        Normalizes to the octave at or above the root to preserve spelling.
        """
        root = self.chord_obj.root()
        if not root:
            return "Unknown"

        p_target = copy.deepcopy(p)
        while p_target.ps < root.ps:
            p_target.octave += 1
        while p_target.ps >= root.ps + 12:
            p_target.octave -= 1

        i = interval.Interval(root, p_target)
        name = i.directedSimpleName

        role_map = {
            "P1": "Root",
            "m2": "Minor 2nd",
            "M2": "Major 2nd",
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

    def analyze(self):
        c = self.chord_obj
        inv_names = {
            0: "Root Position",
            1: "1st Inversion",
            2: "2nd Inversion",
            3: "3rd Inversion",
        }
        pitches = c.pitches
        span = max(p.ps for p in pitches) - min(p.ps for p in pitches) if pitches else 0

        return {
            "common_name": self._get_barbershop_name(),
            "inversion": inv_names.get(c.inversion(), f"{c.inversion()} Inversion"),
            "voicing": "Closed" if span <= 12 else "Open",
            "notes": [
                {
                    "part": self.parts[i],
                    "note": p.nameWithOctave.replace("##", "x"),
                    "role": self.get_interval_role(p),
                }
                for i, p in enumerate(c.pitches)
            ],
        }
