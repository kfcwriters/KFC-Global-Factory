"""
vocals_gen.py
Generates AI singing/vocals for song lyrics.
Primary  : Bark model via HuggingFace — actual AI singing with ♪ notation
Fallback : Google TTS (gTTS) — clear voice reading lyrics over music
"""
import io, time, subprocess, requests
from pathlib import Path

HF_ENDPOINTS = [
    "https://router.huggingface.co/hf-inference/models/suno/bark",
    "https://api-inference.huggingface.co/models/suno/bark",
]


def generate_vocals(sections: list, hf_token: str) -> bytes:
    """
    Generate vocal audio for all lyric sections.
    Returns audio bytes (MP3/FLAC/WAV).
    """
    # Try Bark (AI singing)
    result = _bark_singing(sections, hf_token)
    if result:
        return result

    # Fallback: Google TTS (spoken voice over music)
    print("  [vocals] Bark unavailable — using Google TTS voice")
    return _gtts_voice(sections)


def mix_vocals_music(vocal_path: str, music_path: str,
                     output_path: str, duration_sec: int = 210):
    """
    Mix vocal track with instrumental music using ffmpeg.
    Vocals: primary (boosted + reverb for warmth)
    Music : soft background layer
    """
    print("  [vocals] mixing vocals + instrumental …")
    cmd = [
        "ffmpeg", "-y",
        "-i", vocal_path,
        "-i", music_path,
        "-filter_complex",
        # Vocals — boost + reverb echo for a sung feel
        "[0:a]volume=1.4,"
        "aecho=0.85:0.90:50:0.40,"
        "aecho=0.70:0.80:100:0.25"
        "[v];"
        # Instrumental — background at 35%
        "[1:a]volume=0.35[m];"
        # Merge both tracks
        "[v][m]amix=inputs=2:duration=longest",
        "-t", str(duration_sec),
        "-c:a", "libmp3lame", "-q:a", "2",
        output_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg mix failed:\n{r.stderr[-500:]}")
    print("  [vocals] mixed audio saved ✓")


# ── Bark (AI singing) ─────────────────────────────────────────────────────────

def _bark_singing(sections: list, hf_token: str) -> bytes | None:
    """Submit lyrics to Bark model — generates actual singing."""
    # Format all lyrics with ♪ notation (tells Bark to sing)
    lines = []
    for sec in sections:
        for line in sec.get("lines", []):
            if line.strip():
                lines.append(f"♪ {line} ♪")
        lines.append("")   # blank line = natural pause
    singing_text = "\n".join(lines[:25])  # Bark token limit

    headers = {"Authorization": f"Bearer {hf_token}"}
    payload  = {"inputs": singing_text}

    for url in HF_ENDPOINTS:
        print(f"  [vocals] Bark via {url.split('/')[2]} …")
        for attempt in range(3):
            try:
                resp = requests.post(url, headers=headers,
                                     json=payload, timeout=120)
                if resp.status_code == 200 and len(resp.content) > 5000:
                    print(f"  [vocals] Bark OK ({len(resp.content)//1024} KB) ✓")
                    return resp.content
                elif resp.status_code == 503:
                    try:    wait = float(resp.json().get("estimated_time", 45))
                    except: wait = 45
                    print(f"  [vocals] model loading, wait {wait:.0f}s …")
                    time.sleep(min(wait, 60))
                else:
                    print(f"  [vocals] HTTP {resp.status_code} — next")
                    break
            except Exception as e:
                print(f"  [vocals] attempt {attempt+1}: {str(e)[:80]}")
                time.sleep(15)
    return None


# ── Google TTS fallback ───────────────────────────────────────────────────────

def _gtts_voice(sections: list) -> bytes:
    """
    Use Google TTS to read lyrics as a voice.
    English lines: read in English.
    Hindi/mixed lines: read phonetically in English (close enough for music).
    Adds pauses between sections for natural flow.
    """
    from gtts import gTTS

    all_text_parts = []
    for section in sections:
        sec_type = section.get("type", "verse")
        lines    = section.get("lines", [])

        # Chorus gets emphasis markers
        if sec_type == "chorus":
            all_text_parts.append("...")
        for line in lines:
            if line.strip():
                all_text_parts.append(line)
        all_text_parts.append("...")   # pause between sections

    full_text = " ... ".join(all_text_parts)
    print(f"  [vocals] gTTS generating ({len(full_text)} chars) …")

    # slow=True gives a more dramatic, song-like pace
    tts = gTTS(text=full_text, lang="en", slow=True)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    data = buf.getvalue()
    print(f"  [vocals] gTTS OK ({len(data)//1024} KB) ✓")
    return data
