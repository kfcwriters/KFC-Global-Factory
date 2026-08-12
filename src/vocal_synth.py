"""
vocal_synth.py — v3, Formant Singing Synthesizer with RMS Loudness Fix
=========================================================================
Our own singing voice synthesizer, no GPU/API/external dependency.

v3 fix: Uses RMS (average loudness) normalization instead of peak-only
normalization. Formant-filtered signals are often "peaky" (loud transients,
quiet sustain) — peak normalization alone leaves them perceptually quiet
even when mixed at high volume. RMS normalization ensures the vocal track
has genuine audible presence when layered under instrumental music.
"""
import numpy as np
import scipy.io.wavfile as wavfile
from scipy.signal import lfilter
import io, re, random

SR = 44100

VOWEL_FORMANTS = {
    "a": (730, 1090, 2440),
    "e": (530, 1840, 2480),
    "i": (270, 2290, 3010),
    "o": (570, 840, 2410),
    "u": (300, 870, 2240),
}

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
    word = re.sub(r"[^a-zA-Z]", "", word).lower()
    if not word:
        return []
    syllables = re.findall(r"[^aeiou]*[aeiou]+[^aeiou]*", word)
    return syllables if syllables else [word]


def _plan_events(sections: list, notes: dict, tempo_bpm: int) -> list:
    beat_dur = 60.0 / tempo_bpm
    events = []
    rng = random.Random(42)

    for section in sections:
        is_chorus = section.get("type") == "chorus"
        pool = notes["chorus"] if is_chorus else notes["verse"]

        for line in section.get("lines", []):
            words = line.split()
            for word in words:
                syllables = _syllabify(word) or [word]
                for si, syl in enumerate(syllables):
                    vowel = _guess_vowel(syl)
                    freq = rng.choice(pool)
                    stressed = (si == 0)
                    dur = beat_dur * (0.55 if not stressed else 0.75)
                    dur *= rng.uniform(0.9, 1.15)
                    amp = (0.55 if is_chorus else 0.42) * (1.15 if stressed else 1.0)
                    events.append({
                        "freq": freq, "dur": dur, "vowel": vowel,
                        "amp": amp, "stressed": stressed
                    })
                events.append({"freq": 0, "dur": beat_dur*0.12, "vowel": "a", "amp": 0})
            events.append({"freq": 0, "dur": beat_dur*0.6, "vowel": "a", "amp": 0})
        events.append({"freq": 0, "dur": beat_dur*1.2, "vowel": "a", "amp": 0})

    return events


def _synthesize_continuous(events: list) -> np.ndarray:
    total_dur = sum(e["dur"] for e in events)
    n = int(SR * total_dur)
    if n <= 0:
        return np.zeros(SR, dtype=np.float32)

    pitch_contour = np.zeros(n, dtype=np.float32)
    amp_contour   = np.zeros(n, dtype=np.float32)
    vowel_idx     = np.zeros(n, dtype=np.int32)
    vowels_list   = list(VOWEL_FORMANTS.keys())

    pos = 0
    prev_freq = 220.0
    for e in events:
        dur_samples = max(1, int(SR * e["dur"]))
        end = min(pos + dur_samples, n)
        seg_len = end - pos
        if seg_len <= 0:
            break

        target_freq = e["freq"] if e["freq"] > 0 else prev_freq
        glide_len = min(seg_len, max(1, int(seg_len * 0.4)))
        glide = np.linspace(prev_freq, target_freq, glide_len)
        hold  = np.full(seg_len - glide_len, target_freq)
        pitch_contour[pos:end] = np.concatenate([glide, hold])[:seg_len]

        amp_val = e["amp"]
        att = min(seg_len // 4, int(SR * 0.02))
        rel = min(seg_len // 4, int(SR * 0.03))
        env = np.full(seg_len, amp_val, dtype=np.float32)
        if att > 0:
            env[:att] = np.linspace(0, amp_val, att)
        if rel > 0:
            env[-rel:] = np.linspace(amp_val, amp_val*0.3, rel)
        amp_contour[pos:end] = env

        v_idx = vowels_list.index(e["vowel"]) if e["vowel"] in vowels_list else 0
        vowel_idx[pos:end] = v_idx

        prev_freq = target_freq
        pos = end

    t = np.arange(n, dtype=np.float32) / SR

    vibrato = 1.0 + 0.012 * np.sin(2*np.pi*5.5*t)
    inst_freq = pitch_contour * vibrato
    phase = np.cumsum(2*np.pi*inst_freq/SR)

    glottal = np.zeros(n, dtype=np.float32)
    for harmonic in range(1, 10):
        glottal += (1.0/harmonic) * np.sin(harmonic * phase)
    peak = np.max(np.abs(glottal)) + 1e-9
    glottal /= peak

    breath = np.random.randn(n).astype(np.float32) * 0.04
    for k in range(1, n):
        breath[k] = 0.9*breath[k-1] + 0.1*breath[k]
    glottal_with_breath = glottal * 0.92 + breath

    signal = _apply_smooth_formants(glottal_with_breath, vowel_idx, vowels_list)
    signal *= amp_contour
    signal = _add_chorus(signal)

    # ── RMS loudness normalization — fixes "vocals too quiet" issue ────────
    rms = np.sqrt(np.mean(signal**2)) + 1e-9
    target_rms = 0.28
    signal = signal * (target_rms / rms)
    signal = np.clip(signal, -0.95, 0.95)

    return signal.astype(np.float32)


def _apply_smooth_formants(signal: np.ndarray, vowel_idx: np.ndarray,
                           vowels_list: list) -> np.ndarray:
    n = len(signal)
    block = max(1, int(SR * 0.03))
    out = np.zeros(n, dtype=np.float32)

    filtered_per_vowel = {}
    for vi, vowel in enumerate(vowels_list):
        f1, f2, f3 = VOWEL_FORMANTS[vowel]
        filtered_per_vowel[vi] = (
            _resonant_filter(signal, f1, 90) +
            _resonant_filter(signal, f2, 110) +
            _resonant_filter(signal, f3, 130)
        )

    for start in range(0, n, block):
        end = min(start+block, n)
        block_vowels = vowel_idx[start:end]
        if len(block_vowels) == 0:
            continue
        vi = int(np.bincount(block_vowels).argmax())
        out[start:end] = filtered_per_vowel[vi][start:end]

    peak = np.max(np.abs(out)) + 1e-9
    return out / peak


def _resonant_filter(signal: np.ndarray, freq: float, bandwidth: float) -> np.ndarray:
    r = np.exp(-np.pi * bandwidth / SR)
    theta = 2 * np.pi * freq / SR
    a1 = -2 * r * np.cos(theta)
    a2 = r * r
    b0 = (1 - r*r) * 0.5
    return lfilter([b0], [1, a1, a2], signal).astype(np.float32)


def _add_chorus(signal: np.ndarray, voices: int = 3) -> np.ndarray:
    n = len(signal)
    out = signal.copy()
    rng = random.Random(7)
    for v in range(voices - 1):
        detune = rng.uniform(-0.008, 0.008)
        delay_samples = rng.randint(int(SR*0.01), int(SR*0.03))
        idx = np.arange(n) * (1 + detune)
        idx = np.clip(idx, 0, n-1).astype(np.int32)
        detuned = signal[idx]
        delayed = np.zeros(n, dtype=np.float32)
        if delay_samples < n:
            delayed[delay_samples:] = detuned[:n-delay_samples]
        out += delayed * 0.35
    peak = np.max(np.abs(out)) + 1e-9
    return out / peak * 0.85


MELODY_NOTES_BY_MOOD = {
    "romantic": {"verse":[220,246,261,293],  "chorus":[293,329,349,392]},
    "happy":    {"verse":[261,293,329,349],  "chorus":[349,392,440,493]},
    "sad":      {"verse":[196,220,233,261],  "chorus":[233,261,277,311]},
}


def sing_lyrics(sections: list, mood: str = "romantic",
                tempo_bpm: int = 76) -> bytes:
    print(f"  [vocal-synth-v3] Synthesizing (mood={mood}, {tempo_bpm} BPM) ...")

    notes = MELODY_NOTES_BY_MOOD.get(mood, MELODY_NOTES_BY_MOOD["romantic"])
    events = _plan_events(sections, notes, tempo_bpm)

    if not events:
        events = [{"freq":220,"dur":2.0,"vowel":"a","amp":0.4,"stressed":False}]

    print(f"  [vocal-synth-v3] {len(events)} note events planned ...")
    signal = _synthesize_continuous(events)

    rms = np.sqrt(np.mean(signal**2))
    peak = np.max(np.abs(signal))
    print(f"  [vocal-synth-v3] RMS={rms:.3f}, Peak={peak:.3f}")

    dur_sec = len(signal) / SR
    buf = io.BytesIO()
    wavfile.write(buf, SR, (signal * 32767).astype(np.int16))
    data = buf.getvalue()
    print(f"  [vocal-synth-v3] Generated {dur_sec:.1f}s ({len(data)//1024} KB) ✓")
    return data


def detect_mood(style_text: str) -> str:
    s = style_text.lower()
    if any(w in s for w in ["sad", "melancholic", "longing", "missing"]):
        return "sad"
    if any(w in s for w in ["upbeat", "happy", "joyful", "cheerful"]):
        return "happy"
    return "romantic"
