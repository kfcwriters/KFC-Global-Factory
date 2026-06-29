"""
vocals_gen.py
Vocal engines in priority order:
  1. Bark (suno/bark) — genuine AI singing with melody and tone ★★★★★
  2. Edge TTS          — natural human voice, free ★★★☆☆
  3. espeak-ng         — offline fallback ★☆☆☆☆
"""
import io, os, subprocess, tempfile, time, asyncio
import numpy as np


# ── ENGINE 1: Bark AI Singing ─────────────────────────────────────────────────

def vocals_bark(sections: list) -> tuple[bytes, str]:
    """
    Bark by Suno — generates ACTUAL singing audio with melody and tone.
    Uses small models (~870MB, cached after first run).
    Speaker v2/en_speaker_9 is known for singing quality.
    """
    # Force small models (faster download, still good quality)
    os.environ["SUNO_USE_SMALL_MODELS"] = "True"
    os.environ["SUNO_OFFLOAD_CPU"]      = "True"
    os.environ["CUDA_VISIBLE_DEVICES"]  = ""  # force CPU

    from bark import SAMPLE_RATE, generate_audio, preload_models
    from scipy.io.wavfile import write as write_wav

    print("  [vocals] Loading Bark models (cached after 1st run) ...")
    preload_models()
    print("  [vocals] Bark ready ✓")

    sr          = SAMPLE_RATE          # 24000 Hz
    silence     = np.zeros(int(sr * 0.8), dtype=np.float32)
    audio_parts = []

    for i, sec in enumerate(sections):
        sec_type = sec.get("type", "verse")
        lines    = sec.get("lines", [])[:3]   # max 3 lines (Bark token limit)
        text     = ". ".join(lines)

        # ♪ notation = Bark generates singing, not speech
        if sec_type == "chorus":
            prompt = f"[singing loudly] ♪ {text} ♪"
        else:
            prompt = f"♪ {text} ♪"

        print(f"  [vocals] Bark singing section {i+1}/{len(sections)} ...")
        try:
            # en_speaker_9 is the best Bark voice for singing
            audio = generate_audio(prompt, history_prompt="v2/en_speaker_9")
            audio_parts.append(audio.astype(np.float32))
            audio_parts.append(silence)
            print(f"  [vocals] section {i+1} done ✓")
        except Exception as e:
            print(f"  [vocals] section {i+1} failed ({e}) — silence placeholder")
            audio_parts.append(np.zeros(int(sr * 5), dtype=np.float32))

    full_audio = np.concatenate(audio_parts)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav_path = f.name

    try:
        write_wav(wav_path, sr, full_audio)
        with open(wav_path, "rb") as f:
            data = f.read()
        print(f"  [vocals] Bark complete: {len(data)//1024} KB ✓")
        return data, ".wav"
    finally:
        if os.path.exists(wav_path):
            os.unlink(wav_path)


# ── ENGINE 2: Edge TTS (Microsoft neural voices) ─────────────────────────────

async def _edge_async(text: str, voice: str, out: str):
    import edge_tts
    await edge_tts.Communicate(text, voice, rate="-15%").save(out)


def vocals_edge(sections: list) -> tuple[bytes, str]:
    parts = []
    for sec in sections:
        for line in sec.get("lines", []):
            if line.strip(): parts.append(line)
        parts.append("...")
    text = " ... ".join(parts)
    print(f"  [vocals] Edge TTS: {len(text)} chars ...")

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        out = f.name

    for voice in ["en-US-JennyNeural","en-US-AriaNeural","en-GB-SoniaNeural"]:
        try:
            asyncio.run(_edge_async(text, voice, out))
            if os.path.getsize(out) > 1000:
                with open(out,"rb") as f: data = f.read()
                print(f"  [vocals] Edge TTS OK ({len(data)//1024} KB) ✓")
                return data, ".mp3"
        except Exception as e:
            print(f"  [vocals] Edge {voice}: {str(e)[:60]}")
    raise RuntimeError("Edge TTS failed")


# ── ENGINE 3: espeak-ng (offline, always works) ───────────────────────────────

def vocals_espeak(sections: list) -> tuple[bytes, str]:
    parts = []
    for sec in sections:
        for line in sec.get("lines",[]): 
            if line.strip(): parts.append(line)
        parts.append(".")
    text = " . ".join(parts)
    print(f"  [vocals] espeak-ng: {len(text)} chars ...")

    with tempfile.NamedTemporaryFile(suffix=".wav",delete=False) as f: r=f.name
    with tempfile.NamedTemporaryFile(suffix=".wav",delete=False) as f: p=f.name
    try:
        subprocess.run(["espeak-ng","-v","en+f3","-s","100","-p","72",
                        "-g","8",text,"-w",r], check=True, capture_output=True)
        subprocess.run(["ffmpeg","-y","-i",r,"-af",
                        "vibrato=f=5.5:d=0.6,aecho=0.85:0.92:60:0.45,"
                        "chorus=0.7:0.9:55:0.4:0.25:2", p],
                       check=True, capture_output=True)
        with open(p,"rb") as f: data=f.read()
        print(f"  [vocals] espeak OK ({len(data)//1024} KB) ✓")
        return data, ".wav"
    finally:
        for x in [r,p]:
            if os.path.exists(x): os.unlink(x)


# ── MAIN: try engines in order ────────────────────────────────────────────────

def generate_vocals(sections: list, hf_token: str = "") -> tuple[bytes, str]:
    """Returns (audio_bytes, extension)."""

    # 1. Bark (actual singing)
    try:
        return vocals_bark(sections)
    except Exception as e:
        print(f"  [vocals] Bark failed: {str(e)[:100]}")

    # 2. Edge TTS
    try:
        return vocals_edge(sections)
    except Exception as e:
        print(f"  [vocals] Edge TTS failed: {str(e)[:80]}")

    # 3. espeak fallback
    return vocals_espeak(sections)


# ── MIXING ────────────────────────────────────────────────────────────────────

def mix_vocals_music(vocal_bytes: bytes, vocal_ext: str,
                     music_mp3: str, out_mp3: str, duration_sec: int = 210):
    with tempfile.NamedTemporaryFile(suffix=vocal_ext,delete=False) as f: vt=f.name
    with tempfile.NamedTemporaryFile(suffix=".wav",   delete=False) as f: lp=f.name
    try:
        open(vt,"wb").write(vocal_bytes)

        pr = subprocess.run(
            ["ffprobe","-v","error","-show_entries","format=duration",
             "-of","default=noprint_wrappers=1:nokey=1",vt],
            capture_output=True,text=True)
        dur = float(pr.stdout.strip() or 0)
        print(f"  [vocals] source: {dur:.1f}s → looping to {duration_sec}s")

        subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i",vt,
                        "-t",str(duration_sec),lp],
                       check=True,capture_output=True)

        subprocess.run([
            "ffmpeg","-y","-i",lp,"-i",music_mp3,
            "-filter_complex",
            "[0:a]volume=5.0[v];[1:a]volume=0.18[m];"
            "[v][m]amix=inputs=2:duration=shortest",
            "-t",str(duration_sec),"-c:a","libmp3lame","-q:a","2",out_mp3
        ], check=True, capture_output=True)

        print(f"  [vocals] mixed: {os.path.getsize(out_mp3)//1024} KB ✓")
    finally:
        for x in [vt,lp]:
            if os.path.exists(x): os.unlink(x)
