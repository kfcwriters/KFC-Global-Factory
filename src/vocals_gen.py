"""
vocals_gen.py
Vocal engines in priority order:
  1. Edge TTS  — Microsoft neural voices, free, no API key, very human
  2. gTTS      — Google TTS, free, no API key
  3. espeak-ng — offline fallback, always works
"""
import io, os, subprocess, tempfile, asyncio, requests, time


# ── ENGINE 1: Edge TTS (Microsoft neural voices) ─────────────────────────────

async def _edge_tts_async(text: str, voice: str, out_path: str):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, rate="-15%", pitch="+2Hz")
    await communicate.save(out_path)


def vocals_edge_tts(sections: list) -> bytes:
    """
    Microsoft Edge TTS — neural voices, sounds very human.
    Uses en-US-JennyNeural (warm, emotional female voice).
    Free, no API key, no signup needed.
    """
    import edge_tts

    # Build lyrics with pauses
    parts = []
    for sec in sections:
        sec_type = sec.get("type", "verse")
        for line in sec.get("lines", []):
            if line.strip():
                parts.append(line)
        parts.append("..." if sec_type != "chorus" else "... ...")
    full_text = " ... ".join(parts)

    print(f"  [vocals] Edge TTS: {len(full_text)} chars ...")

    # Romantic female voices — try in order
    voices = [
        "en-US-JennyNeural",     # warm, emotional
        "en-US-AriaNeural",      # expressive
        "en-GB-SoniaNeural",     # British, elegant
        "en-US-MichelleNeural",  # clear, friendly
    ]

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        out_path = f.name

    for voice in voices:
        try:
            asyncio.run(_edge_tts_async(full_text, voice, out_path))
            size = os.path.getsize(out_path)
            if size > 1000:
                print(f"  [vocals] Edge TTS OK — voice={voice} ({size//1024} KB) ✓")
                with open(out_path, "rb") as f:
                    return f.read()
        except Exception as e:
            print(f"  [vocals] Edge TTS {voice}: {str(e)[:60]}")

    raise RuntimeError("All Edge TTS voices failed")


# ── ENGINE 2: gTTS (Google TTS) ──────────────────────────────────────────────

def vocals_gtts(sections: list) -> bytes:
    """Google TTS — simple, reliable, free."""
    from gtts import gTTS

    parts = []
    for sec in sections:
        for line in sec.get("lines", []):
            if line.strip():
                parts.append(line)
        parts.append("...")
    full_text = " ... ".join(parts)

    print(f"  [vocals] gTTS: {len(full_text)} chars ...")
    tts = gTTS(text=full_text, lang="en", slow=True)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    data = buf.getvalue()
    print(f"  [vocals] gTTS OK ({len(data)//1024} KB) ✓")
    return data


# ── ENGINE 3: espeak-ng (offline, always works) ───────────────────────────────

def vocals_espeak(sections: list) -> bytes:
    """espeak-ng — offline fallback, always available on Ubuntu."""
    parts = []
    for sec in sections:
        for line in sec.get("lines", []):
            if line.strip():
                parts.append(line)
        parts.append(".")
    full_text = " . ".join(parts)

    print(f"  [vocals] espeak-ng: {len(full_text)} chars ...")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        raw_wav = f.name
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        fx_wav = f.name

    try:
        subprocess.run(
            ["espeak-ng", "-v", "en+f3", "-s", "100",
             "-p", "72", "-g", "8", full_text, "-w", raw_wav],
            check=True, capture_output=True
        )
        # Apply musical effects
        subprocess.run([
            "ffmpeg", "-y", "-i", raw_wav,
            "-af", "vibrato=f=5.5:d=0.6,"
                   "aecho=0.85:0.92:60:0.45,"
                   "chorus=0.7:0.9:55:0.4:0.25:2",
            fx_wav
        ], check=True, capture_output=True)

        with open(fx_wav, "rb") as f:
            data = f.read()
        print(f"  [vocals] espeak OK ({len(data)//1024} KB) ✓")
        return data
    finally:
        for p in [raw_wav, fx_wav]:
            if os.path.exists(p): os.unlink(p)


# ── MAIN: try engines in order ────────────────────────────────────────────────

def generate_vocals(sections: list, hf_token: str = "") -> tuple[bytes, str]:
    """
    Returns (audio_bytes, ext) where ext is '.mp3' or '.wav'.
    Tries Edge TTS → gTTS → espeak in order.
    """
    # 1. Edge TTS
    try:
        data = vocals_edge_tts(sections)
        return data, ".mp3"
    except Exception as e:
        print(f"  [vocals] Edge TTS failed: {str(e)[:80]}")

    # 2. gTTS
    try:
        data = vocals_gtts(sections)
        return data, ".mp3"
    except Exception as e:
        print(f"  [vocals] gTTS failed: {str(e)[:80]}")

    # 3. espeak-ng (guaranteed)
    data = vocals_espeak(sections)
    return data, ".wav"


# ── MIXING ────────────────────────────────────────────────────────────────────

def mix_vocals_music(vocal_bytes: bytes, vocal_ext: str,
                     music_mp3: str, out_mp3: str, duration_sec: int = 210):
    """Loop vocals to fill duration, mix loudly over soft instrumental."""
    with tempfile.NamedTemporaryFile(suffix=vocal_ext, delete=False) as f:
        voc_tmp = f.name
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        looped  = f.name

    try:
        open(voc_tmp, "wb").write(vocal_bytes)

        # Probe duration
        pr = subprocess.run(
            ["ffprobe","-v","error","-show_entries","format=duration",
             "-of","default=noprint_wrappers=1:nokey=1", voc_tmp],
            capture_output=True, text=True)
        dur = float(pr.stdout.strip() or 0)
        print(f"  [vocals] source duration: {dur:.1f}s → looping to {duration_sec}s")

        # Loop to fill duration
        subprocess.run([
            "ffmpeg","-y","-stream_loop","-1","-i", voc_tmp,
            "-t", str(duration_sec), looped
        ], check=True, capture_output=True)

        # Mix: vocals loud (5.0), music soft (0.18)
        subprocess.run([
            "ffmpeg","-y",
            "-i", looped,
            "-i", music_mp3,
            "-filter_complex",
            "[0:a]volume=5.0[v];"
            "[1:a]volume=0.18[m];"
            "[v][m]amix=inputs=2:duration=shortest",
            "-t", str(duration_sec),
            "-c:a","libmp3lame","-q:a","2",
            out_mp3
        ], check=True, capture_output=True)

        size = os.path.getsize(out_mp3)//1024
        print(f"  [vocals] mixed audio: {size} KB ✓")

    finally:
        for p in [voc_tmp, looped]:
            if os.path.exists(p): os.unlink(p)
