"""
music_gen.py
Primary  : HuggingFace MusicGen API
Fallback : Full song synthesiser — chord progressions + melody + bass
           Each run picks a different key/tempo/style so songs sound unique.
"""
import io, time, random, math
import numpy as np
import scipy.io.wavfile as wavfile
import requests

HF_ENDPOINTS = [
    "https://router.huggingface.co/hf-inference/models/facebook/musicgen-small",
    "https://api-inference.huggingface.co/models/facebook/musicgen-small",
]
SR = 44100


# ── Note frequencies ──────────────────────────────────────────────────────────
def hz(note, octave):
    """Return frequency of a note (C=0, D=2, E=4, F=5, G=7, A=9, B=11)."""
    semitones = {
        'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,
        'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11
    }
    return 440.0 * (2 ** ((semitones[note] + (octave - 4) * 12 - 9) / 12))


# ── Song style presets ────────────────────────────────────────────────────────
# Each style = (tempo_bpm, chord_roots, mode, melody_shape)
STYLES = [
    # Romantic minor — Am F C E — emotional Bollywood feel
    {
        "name"   : "romantic_minor",
        "tempo"  : random.choice([68, 72, 76]),
        "chords" : [
            [hz('A',3), hz('C',4), hz('E',4)],   # Am
            [hz('F',3), hz('A',3), hz('C',4)],   # F
            [hz('C',4), hz('E',4), hz('G',4)],   # C
            [hz('E',3), hz('G#',3), hz('B',3)],  # E
        ],
        "bass"   : [hz('A',2), hz('F',2), hz('C',3), hz('E',2)],
        "melody" : [hz('A',4), hz('G',4), hz('E',4), hz('D',4),
                    hz('C',4), hz('B',3), hz('A',3), hz('C',4)],
        "decay"  : 0.9988,
    },
    # Romantic major — C G Am F — warm uplifting love song
    {
        "name"   : "romantic_major",
        "tempo"  : random.choice([76, 80, 84]),
        "chords" : [
            [hz('C',4), hz('E',4), hz('G',4)],   # C
            [hz('G',3), hz('B',3), hz('D',4)],   # G
            [hz('A',3), hz('C',4), hz('E',4)],   # Am
            [hz('F',3), hz('A',3), hz('C',4)],   # F
        ],
        "bass"   : [hz('C',3), hz('G',2), hz('A',2), hz('F',2)],
        "melody" : [hz('E',5), hz('D',5), hz('C',5), hz('B',4),
                    hz('A',4), hz('G',4), hz('A',4), hz('C',5)],
        "decay"  : 0.9982,
    },
    # Bollywood — Dm G C Am — Hindi film music feel
    {
        "name"   : "bollywood",
        "tempo"  : random.choice([72, 78, 82]),
        "chords" : [
            [hz('D',3), hz('F',3), hz('A',3)],   # Dm
            [hz('G',3), hz('B',3), hz('D',4)],   # G
            [hz('C',4), hz('E',4), hz('G',4)],   # C
            [hz('A',3), hz('C',4), hz('E',4)],   # Am
        ],
        "bass"   : [hz('D',2), hz('G',2), hz('C',3), hz('A',2)],
        "melody" : [hz('D',4), hz('F',4), hz('A',4), hz('G',4),
                    hz('F',4), hz('E',4), hz('D',4), hz('F',4)],
        "decay"  : 0.9985,
    },
    # Sad romantic — Em C G D — longing/nostalgia
    {
        "name"   : "sad_romantic",
        "tempo"  : random.choice([60, 64, 68]),
        "chords" : [
            [hz('E',3), hz('G',3), hz('B',3)],   # Em
            [hz('C',4), hz('E',4), hz('G',4)],   # C
            [hz('G',3), hz('B',3), hz('D',4)],   # G
            [hz('D',3), hz('F#',3), hz('A',3)],  # D
        ],
        "bass"   : [hz('E',2), hz('C',3), hz('G',2), hz('D',2)],
        "melody" : [hz('B',4), hz('A',4), hz('G',4), hz('F#',4),
                    hz('E',4), hz('G',4), hz('A',4), hz('B',4)],
        "decay"  : 0.9990,
    },
    # Lofi chill — Fmaj7 Am Dm G — relaxed cafe feel
    {
        "name"   : "lofi_chill",
        "tempo"  : random.choice([80, 85, 90]),
        "chords" : [
            [hz('F',3), hz('A',3), hz('C',4), hz('E',4)],   # Fmaj7
            [hz('A',3), hz('C',4), hz('E',4)],               # Am
            [hz('D',3), hz('F',3), hz('A',3)],               # Dm
            [hz('G',3), hz('B',3), hz('D',4)],               # G
        ],
        "bass"   : [hz('F',2), hz('A',2), hz('D',3), hz('G',2)],
        "melody" : [hz('C',5), hz('A',4), hz('F',4), hz('G',4),
                    hz('E',4), hz('F',4), hz('A',4), hz('C',5)],
        "decay"  : 0.9975,
    },
]


# ── Karplus-Strong plucked string ─────────────────────────────────────────────
def _ks(freq: float, dur: float, decay: float = 0.998) -> np.ndarray:
    n   = int(SR * dur)
    p   = max(int(SR / freq), 2)
    buf = (np.random.randn(p) * 0.9).astype(np.float32)
    out = np.zeros(n, np.float32)
    for i in range(n):
        out[i]         = buf[i % p]
        buf[i % p]     = decay * 0.5 * (buf[i % p] + buf[(i+1) % p])
    attack = min(int(SR * 0.008), n)
    out[:attack] *= np.linspace(0, 1, attack)
    return out


def _place(audio: np.ndarray, note: np.ndarray, start_sec: float, amp: float = 1.0):
    s   = int(start_sec * SR)
    end = min(s + len(note), len(audio))
    if s < len(audio):
        audio[s:end] += note[:end - s] * amp


# ── Song generator ────────────────────────────────────────────────────────────
def _synthesise(prompt: str, duration_sec: int = 45) -> bytes:
    # Pick style — use prompt to bias toward romantic minor for romantic songs
    p = prompt.lower()
    if "romantic" in p or "love" in p or "bollywood" in p:
        style = random.choice(STYLES[:3])   # romantic styles
    elif "lofi" in p or "chill" in p:
        style = STYLES[4]
    elif "sad" in p or "emotional" in p:
        style = STYLES[3]
    else:
        style = random.choice(STYLES)

    print(f"  [music] style={style['name']}  tempo={style['tempo']} BPM")

    tempo     = style["tempo"]
    beat      = 60.0 / tempo          # seconds per beat
    bar       = beat * 4              # seconds per 4-beat bar
    chords    = style["chords"]
    bass_f    = style["bass"]
    melody_f  = style["melody"]
    decay     = style["decay"]

    n     = int(SR * duration_sec)
    audio = np.zeros(n, np.float32)

    # ── Section lengths (bars) ──────────────────
    # Intro:4 | Verse:8 | Chorus:8 | Verse:8 | Chorus:8 | Outro:4
    sections = []
    t = beat * 2        # start after 2-beat silence (intro space)

    for section_bars, section_type in [
        (4,  "intro"),
        (8,  "verse"),
        (8,  "chorus"),
        (8,  "verse"),
        (8,  "chorus"),
        (4,  "outro"),
    ]:
        for bar_i in range(section_bars):
            if t >= duration_sec - bar: break
            chord_idx = (bar_i // 2) % len(chords)
            chord     = chords[chord_idx]
            bass      = bass_f[chord_idx]

            # ── Bass note (beat 1 and 3) ──────────
            _place(audio, _ks(bass, beat*2.2, decay+0.001), t,         amp=0.50)
            _place(audio, _ks(bass, beat*2.2, decay+0.001), t+beat*2,  amp=0.40)

            # ── Chord arpeggio (all 4 beats) ──────
            for b, note_f in enumerate(chord[:4]):
                _place(audio, _ks(note_f, beat*1.8, decay), t + b*beat, amp=0.28)

            # ── Melody (chorus louder, verse softer) ─
            is_chorus  = section_type == "chorus"
            m_amp      = 0.65 if is_chorus else 0.45
            m_pattern  = [0, 2, 4, 3, 1, 5, 3, 2] if is_chorus else [0, 1, 3, 2, 4, 2, 1, 0]
            notes_per_bar = 4 if not is_chorus else 8
            step_dur   = bar / notes_per_bar

            for step in range(notes_per_bar):
                m_idx  = m_pattern[step % len(m_pattern)] % len(melody_f)
                m_freq = melody_f[m_idx]
                # Occasional octave variation for interest
                if random.random() < 0.15:
                    m_freq *= 0.5
                _place(audio, _ks(m_freq, step_dur*1.6, decay-0.001),
                       t + step * step_dur, amp=m_amp)

            t += bar

    # ── Soft room ambience ─────────────────────────────────────────────────
    noise = np.random.randn(n).astype(np.float32) * 0.012
    for k in range(1, n):
        noise[k] = 0.95 * noise[k-1] + 0.05 * noise[k]
    audio += noise

    # ── Normalise ──────────────────────────────────────────────────────────
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.82

    # ── Fade in / out ──────────────────────────────────────────────────────
    fade = min(int(SR * 2.5), n // 5)
    audio[:fade]  *= np.linspace(0, 1, fade)
    audio[-fade:] *= np.linspace(1, 0, fade)

    buf = io.BytesIO()
    wavfile.write(buf, SR, (audio * 32767).astype(np.int16))
    data = buf.getvalue()
    print(f"  [music] synthesised ({len(data)//1024} KB) ✓")
    return data


# ── Public function ────────────────────────────────────────────────────────────
def generate_music(prompt: str, hf_token: str, duration_sec: int = 45) -> bytes:
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": prompt,
               "parameters": {"max_new_tokens": min(256 * duration_sec, 1500)}}

    for url in HF_ENDPOINTS:
        print(f"  [music] trying {url.split('/')[2]} …")
        for attempt in range(1, 4):
            try:
                r = requests.post(url, headers=headers, json=payload, timeout=120)
                if r.status_code == 200:
                    print(f"  [music] HuggingFace OK ({len(r.content)//1024} KB) ✓")
                    return r.content
                elif r.status_code == 503:
                    try:    wait = float(r.json().get("estimated_time", 40))
                    except: wait = 40
                    time.sleep(min(wait, 60))
                else:
                    print(f"  [music] HTTP {r.status_code} — next")
                    break
            except Exception as e:
                print(f"  [music] attempt {attempt}: {str(e)[:80]}")
                time.sleep(15)

    print("  [music] falling back to song synthesiser …")
    return _synthesise(prompt, duration_sec)
