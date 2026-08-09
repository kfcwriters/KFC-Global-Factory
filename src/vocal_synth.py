"""
vocal_synth.py
Our own formant-based singing voice synthesizer — 100% Python, no GPU,
no external API, no cookies, no credits. Runs entirely on GitHub Actions.

This simulates human vocal production:
  - Glottal pulse train (vocal cord vibration) at melody pitch
  - Formant filters (vocal tract resonances) shape vowel sounds
  - Syllables mapped to lyrics, sung on a chord-following melody

Honest expectation: this sounds synthetic/robotic-singing (like early
vocaloid/speak & spell), NOT like a human singer. But it genuinely SINGS
pitched notes following the melody — a real step up from silence or
spoken narration, and something we fully own and control forever.
"""
import numpy as np
import scipy.io.wavfile as wavfile
import io, re, random

SR = 44100

# ── Vowel formant frequencies (F1, F2, F3) — classic speech synthesis data ────
VOWEL_FORMANTS = {
    "a": (730, 1090, 2440),   # "ah"
    "e": (530, 1840, 2480),   # "eh"
    "i": (270, 2290, 3010),   # "ee"
    "o": (570, 840, 2410),    # "oh"
    "u": (300, 870, 2240),    # "oo"
}

# Simple grapheme-to-vowel mapping (rough, good enough for singing synthesis)
VOWEL_MAP = [
    (re.compile(r"oo|u"), "u"),
    (re.compile(r"ee|ea|i"), "i"),
    (re.compile(r"oh|o|ow"), "o"),
    (re.compile(r"ay|a|e"), "e"),
    (re.compile(r"ah|a"), "a"),
]


def _guess_vowel(syllable: str) -> str:
    s = syllable.lower()
    for pattern, vowel in VOWEL_MAP:
        if pattern.search(s):
            return vowel
    return "a"


def _syllabify(word: str) -> list:
    """Very rough syllable splitter based on vowel groups."""
    word = re.sub(r"[^a-zA-Z]", "", word).lower()
    if not word:
        return []
    syllables = re.findall(r"[^aeiou]*[aeiou]+[^aeiou]*", word)
    return syllables if syllables else [word]


def _formant_note(freq: float, dur: float, vowel: str, amp: float = 0.3) -> np.ndarray:
    """
    Synthesize one sung note using glottal pulses + formant filtering.

    Args:
        freq  : Fundamental pitch (Hz) — the note being sung.
        dur   : Duration in seconds.
        vowel : Which vowel shape ("a","e","i","o","u").
        amp   : Amplitude.
    """
    n = int(SR * dur)
    if n <= 0:
        return np.array([], dtype=np.float32)

    t = np.linspace(0, dur, n, dtype=np.float32)

    # 1. Glottal pulse train — vocal cord vibration (sawtooth-like buzz)
    glottal = np.zeros(n, dtype=np.float32)
    for harmonic in range(1, 12):
        h_amp = 1.0 / harmonic   # natural harmonic rolloff
        glottal += h_amp * np.sin(2 * np.pi * freq * harmonic * t)
    glottal /= np.max(np.abs(glottal) + 1e-9)

    # Add subtle vibrato (natural singing wobble)
    vibrato = 1.0 + 0.015 * np.sin(2 * np.pi * 5.5 * t)
    glottal *= vibrato

    # 2. Formant filtering — shape the buzz into a vowel sound
    f1, f2, f3 = VOWEL_FORMANTS.get(vowel, VOWEL_FORMANTS["a"])
    signal = _apply_formant_filter(glottal, [f1, f2, f3])

    # 3. Envelope — soft attack/release so notes don't click
    attack = min(int(SR * 0.03), n // 4)
    release = min(int(SR * 0.08), n // 4)
    env = np.ones(n, dtype=np.float32)
    if attack > 0:
        env[:attack] = np.linspace(0, 1, attack)
    if release > 0:
        env[-release:] = np.linspace(1, 0, release)

    return (signal * env * amp).astype(np.float32)


def _apply_formant_filter(signal: np.ndarray, formants: list) -> np.ndarray:
    """Apply resonant band-pass filters at formant frequencies (simple IIR)."""
    out = np.zeros_like(signal)
    for f in formants:
        out += _resonant_filter(signal, f, bandwidth=80)
    peak = np.max(np.abs(out)) + 1e-9
    return out / peak


def _resonant_filter(signal: np.ndarray, freq: float, bandwidth: float) -> np.ndarray:
    """Simple 2nd-order resonant filter (formant peak) via biquad."""
    n = len(signal)
    if n == 0:
        return signal

    r = np.exp(-np.pi * bandwidth / SR)
    theta = 2 * np.pi * freq / SR
    a1 = -2 * r * np.cos(theta)
    a2 = r * r

    out = np.zeros(n, dtype=np.float32)
    x1 = x2 = y1 = y2 = 0.0
    for i in range(n):
        x0 = signal[i]
        y0 = x0 - a1 * y1 - a2 * y2
        out[i] = y0
        x2, x1 = x1, x0
        y2, y1 = y1, y0
    return out


# ── Melody note pool (pentatonic — always sounds pleasant) ────────────────────
MELODY_NOTES_BY_MOOD = {
    "romantic":  [220, 246, 261, 293, 329, 349, 392],
    "happy":     [261, 293, 329, 392, 440, 493],
    "sad":       [196, 220, 233, 261, 293, 311],
    "default":   [220, 246, 261, 293, 329, 349, 392],
}


def sing_lyrics(sections: list, mood: str = "romantic",
                tempo_bpm: int = 76) -> bytes:
    """
    Generate a full sung vocal track from lyrics sections.

    Args:
        sections  : List of {"type": str, "lines": [str, ...]}
        mood      : "romantic" / "happy" / "sad" — picks melody pool.
        tempo_bpm : Singing tempo.

    Returns:
        WAV audio bytes of the synthesized singing.
    """
    print(f"  [vocal-synth] Synthesizing singing voice (mood={mood}, {tempo_bpm} BPM) ...")

    notes = MELODY_NOTES_BY_MOOD.get(mood, MELODY_NOTES_BY_MOOD["default"])
    beat_dur = 60.0 / tempo_bpm
    syllable_dur = beat_dur / 2   # 2 syllables per beat, roughly

    chunks = []
    rng = random.Random(42)

    for sec_idx, section in enumerate(sections):
        is_chorus = section.get("type") == "chorus"
        note_pool = notes[3:] if is_chorus else notes[:5]   # chorus = higher notes

        for line in section.get("lines", []):
            words = line.split()
            for word in words:
                syllables = _syllabify(word)
                if not syllables:
                    syllables = [word]
                for syl in syllables:
                    vowel = _guess_vowel(syl)
                    freq = rng.choice(note_pool)
                    dur = syllable_dur * rng.uniform(0.85, 1.3)
                    amp = 0.45 if is_chorus else 0.35
                    note = _formant_note(freq, dur, vowel, amp)
                    chunks.append(note)
                # tiny gap between words
                chunks.append(np.zeros(int(SR * 0.03), dtype=np.float32))
            # gap between lines
            chunks.append(np.zeros(int(SR * beat_dur * 0.5), dtype=np.float32))
        # gap between sections
        chunks.append(np.zeros(int(SR * beat_dur), dtype=np.float32))

    if not chunks:
        chunks = [np.zeros(SR, dtype=np.float32)]

    full = np.concatenate(chunks)

    # Final normalize + fade
    peak = np.max(np.abs(full)) + 1e-9
    full = full / peak * 0.75
    fade = min(int(SR * 1.5), len(full) // 6)
    if fade > 0:
        full[:fade] *= np.linspace(0, 1, fade)
        full[-fade:] *= np.linspace(1, 0, fade)

    buf = io.BytesIO()
    wavfile.write(buf, SR, (full * 32767).astype(np.int16))
    data = buf.getvalue()
    dur_sec = len(full) / SR
    print(f"  [vocal-synth] Generated {dur_sec:.1f}s of singing ({len(data)//1024} KB) ✓")
    return data


def detect_mood(style_text: str) -> str:
    """Guess mood category from a style/tags string."""
    s = style_text.lower()
    if any(w in s for w in ["sad", "melancholic", "longing", "missing"]):
        return "sad"
    if any(w in s for w in ["upbeat", "happy", "joyful", "cheerful"]):
        return "happy"
    return "romantic"
