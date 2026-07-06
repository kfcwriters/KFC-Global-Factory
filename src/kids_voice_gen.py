"""
kids_voice_gen.py
Generates narration voice for kids content using Edge TTS.
Microsoft neural voices — free, natural, kid-friendly.
Falls back to espeak-ng (offline, always works).
"""
import io, os, asyncio, subprocess, tempfile


# Best kid-friendly voices from Microsoft Edge TTS
NARRATOR_VOICES = [
    "en-US-JennyNeural",      # warm, friendly female — great for stories
    "en-US-AriaNeural",       # expressive female — good for fairy tales
    "en-GB-SoniaNeural",      # British, clear — good for educational
    "en-US-MichelleNeural",   # friendly — good for nursery rhymes
]


async def _edge_speak(text: str, voice: str, out_path: str, rate: str = "-10%"):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch="+5Hz")
    await communicate.save(out_path)


def generate_narration(script: list, content_type: str) -> bytes:
    """
    Generate narration for kids content.
    Returns WAV/MP3 bytes.
    """
    # Build full narration text with pauses
    if content_type == "nursery_rhyme":
        # Slower, sing-song pace for rhymes
        full_text = " ... ".join(script)
        rate      = "-20%"
    elif content_type == "educational":
        # Clear, enthusiastic for learning
        full_text = " ... ".join(script)
        rate      = "-15%"
    else:
        # Natural storytelling pace
        parts = []
        for i, line in enumerate(script):
            parts.append(line)
            if i % 2 == 1:
                parts.append("...")  # pause every 2 lines
        full_text = " ".join(parts)
        rate      = "-10%"

    print(f"  [voice] Narrating {len(script)} lines ({len(full_text)} chars) ...")

    # Try Edge TTS voices
    for voice in NARRATOR_VOICES:
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                out = f.name
            asyncio.run(_edge_speak(full_text, voice, out, rate))
            if os.path.getsize(out) > 1000:
                with open(out, "rb") as f:
                    data = f.read()
                os.unlink(out)
                print(f"  [voice] Edge TTS OK ({voice}, {len(data)//1024} KB) ✓")
                return data
        except Exception as e:
            print(f"  [voice] {voice}: {str(e)[:60]}")
            if os.path.exists(out):
                os.unlink(out)

    # Fallback: espeak-ng offline
    print("  [voice] Using espeak-ng fallback ...")
    return _espeak_narrate(full_text, content_type)


def _espeak_narrate(text: str, content_type: str) -> bytes:
    """espeak-ng — always works on Ubuntu."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        raw = f.name
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        out = f.name
    try:
        # Female voice, slower pace, higher pitch for kids
        subprocess.run(
            ["espeak-ng", "-v", "en+f3",
             "-s", "130" if content_type == "educational" else "120",
             "-p", "65", "-g", "10",
             text, "-w", raw],
            check=True, capture_output=True
        )
        # Add warmth with reverb
        subprocess.run([
            "ffmpeg", "-y", "-i", raw,
            "-af", "aecho=0.8:0.9:40:0.3", out
        ], check=True, capture_output=True)
        with open(out, "rb") as f:
            data = f.read()
        print(f"  [voice] espeak OK ({len(data)//1024} KB) ✓")
        return data
    finally:
        for p in [raw, out]:
            if os.path.exists(p): os.unlink(p)
