"""
acestep_music_gen.py
Generates full songs WITH REAL VOCALS using ACE-Step — a legitimate,
actively-maintained open-source music foundation model (Apache 2.0/MIT).

Unlike the YuE community mirrors (which were abandoned/broken), these are
the OFFICIAL Spaces run by the ACE-Step team itself:
  - ACE-Step/Ace-Step-v1.5  (newer, better quality, faster)
  - ACE-Step/ACE-Step       (v1, fallback)

Free via HuggingFace ZeroGPU using your existing HF_TOKEN.
Generates full songs (4 min in ~20s on real GPU) with lyric-guided vocals.
"""
import time

ACESTEP_SPACES = [
    "ACE-Step/Ace-Step-v1.5",   # official, newest, best quality
    "ACE-Step/ACE-Step",         # official, v1 fallback
]


def generate_song_acestep(lyrics: str, style_tags: str, hf_token: str,
                          duration_sec: int = 210) -> bytes:
    """
    Generate a full song with real vocals using ACE-Step.

    Args:
        lyrics       : Full lyrics text (with [verse]/[chorus] structure).
        style_tags   : Style/genre description e.g. "pop, female vocals, romantic, piano".
        hf_token     : HuggingFace access token.
        duration_sec : Target song length in seconds.

    Returns:
        Raw audio bytes (WAV/MP3) of the generated song.
    """
    from gradio_client import Client

    last_error = None
    for space_id in ACESTEP_SPACES:
        try:
            print(f"  [acestep] Connecting to {space_id} ...")
            try:
                client = Client(space_id, token=hf_token)
            except TypeError:
                client = Client(space_id, hf_token=hf_token)

            print(f"  [acestep] Generating song ({duration_sec}s target) ...")
            print(f"  [acestep] Style: {style_tags[:60]}")

            # ACE-Step Gradio API — text2music endpoint
            # Standard params based on ACE-Step's app.py interface
            result = client.predict(
                format="wav",
                audio_duration=float(duration_sec),
                prompt=style_tags,
                lyrics=lyrics,
                infer_step=27,
                guidance_scale=15,
                scheduler_type="euler",
                cfg_type="apg",
                omega_scale=10,
                manual_seeds="",
                guidance_interval=0.5,
                guidance_interval_decay=0,
                min_guidance_scale=3,
                use_erg_tag=True,
                use_erg_lyric=True,
                use_erg_diffusion=True,
                oss_steps="",
                guidance_scale_text=0,
                guidance_scale_lyric=0,
                api_name="/__call__"
            )

            audio_path = result[0] if isinstance(result, (list, tuple)) else result
            if isinstance(audio_path, dict):
                audio_path = audio_path.get("path") or audio_path.get("audio") or audio_path.get("value")

            with open(audio_path, "rb") as f:
                data = f.read()

            print(f"  [acestep] Generated {len(data)//1024} KB ✓")
            return data

        except Exception as e:
            last_error = e
            print(f"  [acestep] {space_id} failed: {str(e)[:200]}")
            time.sleep(5)

    raise RuntimeError(f"All ACE-Step spaces failed. Last error: {last_error}")


def build_acestep_lyrics(sections: list) -> str:
    """
    Format section list into ACE-Step's expected lyrics format:
    [verse], [chorus], [bridge] tags with lines below each.
    """
    parts = []
    for sec in sections:
        tag = sec.get("type", "verse")
        lines = sec.get("lines", [])
        parts.append(f"[{tag}]")
        parts.extend(lines)
        parts.append("")
    return "\n".join(parts)
