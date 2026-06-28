"""
vocals_gen.py
AI Vocals for lyric videos.
Priority order:
  1. Bark (suno/bark) — HuggingFace AI singing
  2. gTTS            — Google TTS (needs internet)
  3. espeak-ng       — Offline TTS, ALWAYS works on Ubuntu GitHub Actions
"""
import io, os, time, subprocess, tempfile, requests


HF_ENDPOINTS = [
    "https://router.huggingface.co/hf-inference/models/suno/bark",
    "https://api-inference.huggingface.co/models/suno/bark",
]


def generate_vocals(sections: list, hf_token: str) -> bytes:
    """Try multiple vocal engines in order. Returns audio bytes."""

    # 1. Try Bark (AI singing)
    print("  [vocals] trying Bark AI singing ...")
    result = _bark(sections, hf_token)
    if result and len(result) > 5000:
        print(f"  [vocals] Bark OK ({len(result)//1024} KB) ✓")
        return result

    # 2. Try gTTS
    print("  [vocals] trying Google TTS ...")
    try:
        result = _gtts(sections)
        if result and len(result) > 1000:
            print(f"  [vocals] gTTS OK ({len(result)//1024} KB) ✓")
            return result
    except Exception as e:
        print(f"  [vocals] gTTS failed: {str(e)[:80]}")

    # 3. espeak-ng — OFFLINE, always works on GitHub Actions Ubuntu
    print("  [vocals] using espeak-ng (offline, guaranteed) ...")
    result = _espeak(sections)
    print(f"  [vocals] espeak-ng OK ({len(result)//1024} KB) ✓")
    return result


def mix_vocals_music(vocal_path: str, music_path: str,
                     output_path: str, duration_sec: int = 210):
    """
    Mix vocals + instrumental.
    - Loops vocals to fill full duration
    - Vocals at high volume so clearly heard
    - Music soft in background
    """
    # First: probe vocal file to confirm it has audio
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", vocal_path],
        capture_output=True, text=True
    )
    vocal_dur = float(probe.stdout.strip() or 0)
    print(f"  [vocals] vocal track duration: {vocal_dur:.1f}s")

    if vocal_dur < 1.0:
        print("  [vocals] ⚠️  vocal file is empty — regenerating with espeak-ng")
        # Force espeak fallback and save to vocal_path
        from pathlib import Path
        sections_dummy = [{"lines":["Hello, this is a romantic song", "Please enjoy the music"]}]
        data = _espeak(sections_dummy)
        Path(vocal_path).write_bytes(data)

    print("  [vocals] mixing vocals + music ...")
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", vocal_path,   # loop vocals
        "-i", music_path,
        "-filter_complex",
        # Apply musical chorus effect + high volume to vocals
        "[0:a]volume=4.0,"
        "chorus=0.7:0.9:55:0.4:0.25:2,"          # chorus = richer voice
        "aecho=0.8:0.7:40:0.3"                    # slight echo = room feel
        "[v];"
        "[1:a]volume=0.18[m];"                    # music soft background
        "[v][m]amix=inputs=2:duration=longest",
        "-t", str(duration_sec),
        "-c:a", "libmp3lame", "-q:a", "2",
        output_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"Mix failed:\n{r.stderr[-400:]}")

    size = os.path.getsize(output_path) // 1024
    print(f"  [vocals] mixed audio: {size} KB ✓")


# ── Engine 1: Bark AI singing ─────────────────────────────────────────────────

def _bark(sections: list, hf_token: str) -> bytes | None:
    lines = []
    for sec in sections:
        for line in sec.get("lines", []):
            if line.strip():
                lines.append(f"♪ {line} ♪")
        lines.append("")
    text    = "\n".join(lines[:20])
    headers = {"Authorization": f"Bearer {hf_token}"}

    for url in HF_ENDPOINTS:
        for attempt in range(2):
            try:
                r = requests.post(url, headers=headers,
                                  json={"inputs": text}, timeout=90)
                if r.status_code == 200:
                    return r.content
                elif r.status_code == 503:
                    time.sleep(40)
                else:
                    break
            except Exception:
                time.sleep(10)
    return None


# ── Engine 2: Google TTS ──────────────────────────────────────────────────────

def _gtts(sections: list) -> bytes:
    from gtts import gTTS
    parts = []
    for sec in sections:
        for line in sec.get("lines", []):
            if line.strip():
                parts.append(line)
        parts.append("...")
    tts = gTTS(text=" ... ".join(parts), lang="en", slow=True)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()


# ── Engine 3: espeak-ng (OFFLINE) ─────────────────────────────────────────────

def _espeak(sections: list) -> bytes:
    """
    Uses espeak-ng — available on Ubuntu, completely offline.
    en+f3 = female voice (more melodic for romantic songs)
    -s 105 = slow (dramatic, song-like pace)
    -p 68  = higher pitch (more musical)
    """
    parts = []
    for sec in sections:
        sec_type = sec.get("type", "verse")
        for line in sec.get("lines", []):
            if line.strip():
                parts.append(line)
        # Longer pause after chorus
        parts.append("..." if sec_type != "chorus" else ". . .")

    full_text = ". ".join(parts)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav_path = f.name

    try:
        subprocess.run(
            ["espeak-ng",
             "-v", "en+f3",   # female voice
             "-s", "105",     # slow speed
             "-p", "68",      # higher pitch
             "-g", "8",       # word gap (ms) = slight pauses
             full_text,
             "-w", wav_path],
            check=True, capture_output=True
        )
        with open(wav_path, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(wav_path):
            os.unlink(wav_path)
