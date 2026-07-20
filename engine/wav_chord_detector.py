import math
from typing import Any, BinaryIO, Dict, List

import numpy as np
from scipy.io import wavfile
from scipy.signal import find_peaks

# Vocal fundamentals live here (covers bass low E2 up through tenor's higher notes);
# candidates outside this range are almost always harmonics, not sung pitches.
MIN_FUNDAMENTAL_HZ = 70
MAX_FUNDAMENTAL_HZ = 1000

# How many of a candidate's own harmonics to credit it for -- see detect_chord's docstring.
N_HARMONICS = 6

# Tuning drift/vibrato tolerance when looking for energy at a harmonic, and when deciding
# two candidates are really the same note (one an octave/multiple of the other).
MATCH_TOLERANCE_CENTS = 25
DEDUPE_TOLERANCE_CENTS = 30

MAX_VOICES = 4
PARTS_LOW_TO_HIGH = ["Bass", "Bari", "Lead", "Tenor"]


def _read_mono(file_stream: BinaryIO):
    sample_rate, data = wavfile.read(file_stream)
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float32) / 2147483648.0
    else:
        data = data.astype(np.float32)
    if data.ndim > 1:
        data = data.mean(axis=1)
    return sample_rate, data


def _mag_near(freqs: np.ndarray, mag: np.ndarray, f: float, tol_cents: float = MATCH_TOLERANCE_CENTS) -> float:
    """Local max magnitude within +/- tol_cents of f -- tolerant of real-world tuning
    drift/vibrato, since a harmonic rarely lands exactly on n * f0."""
    if f <= 0:
        return -200.0
    lo = f * 2 ** (-tol_cents / 1200)
    hi = f * 2 ** (tol_cents / 1200)
    idx = np.where((freqs >= lo) & (freqs <= hi))[0]
    return float(np.max(mag[idx])) if len(idx) else -200.0


def _harmonic_salience(freqs: np.ndarray, mag: np.ndarray, f0: float, n_harmonics: int = N_HARMONICS) -> float:
    """Sum of the magnitude at f0 and its first few integer harmonics. A sung note's energy
    is shaped by the singer's vocal-tract formants, which routinely boost an upper harmonic
    well above the fundamental's own amplitude -- especially for low notes, whose fundamental
    often sits far from any formant peak. Raw single-bin peak height conflates fundamentals
    with harmonics and can rank a real note's own overtone above the note itself; summing
    across the harmonic series gives the fundamental credit for all of its own energy instead
    of just whatever a single bin happens to show. (Proven out interactively against a real
    recording before this was built -- see plan.md/memory for that investigation.)"""
    return sum(_mag_near(freqs, mag, f0 * k) for k in range(1, n_harmonics + 1))


def _has_peak_near(peak_freqs: List[float], f: float, tol_cents: float = MATCH_TOLERANCE_CENTS) -> bool:
    return any(abs(1200 * math.log2(pf / f)) < tol_cents for pf in peak_freqs)


def _correct_octave_errors(peak_freqs: List[float], chosen: List[float]) -> List[float]:
    """Harmonic salience has a structural bias toward picking the octave *below* the true
    note: every even harmonic of the true fundamental (2f0, 4f0, 6f0...) is exactly a
    harmonic of f0/2 too, so a candidate at f0/2 gets partial credit for the real note's
    energy "for free," even with zero energy of its own. Restricting candidates to genuine
    detected peaks (see detect_chord's docstring) only rules out a *hallucinated* f0/2 with
    no energy there at all -- it does nothing when something else (very commonly,
    instrumental accompaniment doubling the vocal an octave down) provides real energy
    at that position too.

    A false subharmonic's *odd* harmonics (3f0, 5f0...) don't coincide with the true note's
    harmonic series, so they're the tell: if a candidate has a real peak at exactly double
    its frequency but no independent evidence at its own odd harmonics, it's almost
    certainly that higher note's octave-error ghost, not a real fundamental of its own.

    Confirmed empirically 2026-07-19 against a real two-voice-plus-instrumental recording:
    correctly promoted a false subharmonic to the octave above, matching a manual pitch ID.
    Known limitation, not attempted here: this only corrects octave errors *within* the
    already-chosen candidates -- it can't tell a real low voice from unrelated instrumental
    content that isn't an octave-error of anything (a bass note with no relation to either
    singer just looks like a fifth, uncorrected "voice").
    """
    corrected = []
    for f in chosen:
        doubled = f * 2
        has_octave_above = _has_peak_near(peak_freqs, doubled)
        has_own_odd_harmonic = _has_peak_near(peak_freqs, f * 3) or _has_peak_near(peak_freqs, f * 5)
        corrected.append(doubled if (has_octave_above and not has_own_odd_harmonic) else f)
    return sorted(set(corrected))


def detect_chord(file_stream: BinaryIO, max_voices: int = MAX_VOICES) -> Dict[str, Any]:
    """Detects up to `max_voices` sung fundamentals in a single-chord WAV recording, sorted
    low to high and labeled Bass..Tenor by pitch order -- no attempt at identifying which
    singer's voice is which beyond that (unreliable from audio alone; pitch order is the
    practical proxy).

    Candidates are restricted to genuine detected spectral peaks (never a frequency
    invented from nothing -- that's how naive harmonic-product methods hallucinate
    false subharmonics/octave errors), then re-ranked by harmonic salience instead of
    raw peak loudness, then greedily deduplicated against integer multiples/divisors of
    an already-chosen, higher-salience candidate (those are that note's own harmonics,
    not a separate voice), then passed through an octave-error correction pass (see
    _correct_octave_errors's docstring).

    Known limitation, not attempted here: works best on close-to-a-cappella recordings.
    Instrumental accompaniment can still get mistaken for an extra voice -- the octave-error
    correction only fixes a candidate that's a false subharmonic of another chosen note, not
    a genuinely separate (but unwanted) pitch from an instrument.
    """
    sample_rate, data = _read_mono(file_stream)
    n = len(data)
    if n == 0:
        return {"notes": [], "warnings": ["Empty audio."]}

    window = np.hanning(n)
    freqs = np.fft.rfftfreq(n, 1 / sample_rate)
    mag = 20 * np.log10(np.abs(np.fft.rfft(data * window)) + 1e-12)

    global_max = float(np.max(mag))
    cutoff_db = global_max - 90
    mag = np.maximum(mag, cutoff_db)

    df = sample_rate / n
    min_peak_dist = max(1, int(20 / df))
    peak_idx, _ = find_peaks(mag, height=global_max - 50, prominence=10, distance=min_peak_dist)
    peak_freqs = [f for f in freqs[peak_idx] if f > 20]

    candidates = sorted(
        (f for f in peak_freqs if MIN_FUNDAMENTAL_HZ <= f <= MAX_FUNDAMENTAL_HZ),
        key=lambda f: -_harmonic_salience(freqs, mag, f),
    )

    chosen: List[float] = []
    for f in candidates:
        related_to_existing = False
        for c in chosen:
            ratio = f / c
            nearest = round(ratio)
            if nearest >= 1 and abs(1200 * math.log2(ratio / nearest)) < DEDUPE_TOLERANCE_CENTS:
                related_to_existing = True
                break
        if not related_to_existing:
            chosen.append(f)
        if len(chosen) >= max_voices:
            break

    chosen = _correct_octave_errors(peak_freqs, chosen)

    notes = []
    for f in chosen:
        standard_midi = 12 * math.log2(f / 440.0) + 69
        nearest_midi = round(standard_midi)
        cents = round((standard_midi - nearest_midi) * 100)
        # This app's own semitone convention (oct*12 + step-within-octave + acc, per
        # spelling.js's getAbsSemitone) is standard MIDI minus 12 -- see state.js/main.js.
        app_semitone = nearest_midi - 12
        notes.append({"hz": round(f, 1), "app_semitone": app_semitone, "cents": cents})

    warnings = []
    if len(notes) < max_voices:
        warnings.append(
            f"Only found {len(notes)} distinct voice(s) -- some may be unison/octave doublings, "
            "or the recording may be quiet/noisy."
        )

    for note, part in zip(notes, PARTS_LOW_TO_HIGH[: len(notes)]):
        note["part"] = part

    return {"notes": notes, "warnings": warnings}
