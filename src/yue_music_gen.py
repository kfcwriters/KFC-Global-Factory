"""
yue_music_gen.py
Generates full songs with REAL vocals using YuE — a genuinely open-source
model (not a paid wrapper around Suno). "Something similar to Suno.ai but open."

Calls the official public HuggingFace Space for free via ZeroGPU.
Uses your existing HF_TOKEN (same one used for Pollinations images).

No cookies, no monthly credit limits from a third party —
this is YuE's own model, hosted for free by HuggingFace/the YuE team.

Space: https://huggingface.co/spaces/multimodal-art-projection/YuE
"""
import os, time

YUE_SPACES = [
    "multimodal-art-projection/YuE",
    "innova-ai/YuE-music-generator-space",  # community mirror, fallback
]


def generate_song_yue(lyrics: str, genre_tags: str, hf_token: str,
                      duration_sec: int = 210) -> bytes:
    """
    Generate a full song with real vocals using YuE.

    Args:
        lyrics       : Full lyrics with [verse]/[chorus] structure tags.
        genre_tags   : Style description e.g. "pop, female vocal, emotional, piano".
        hf_token     : HuggingFace access token.
        duration_sec : Approximate target length (YuE generates in segments).

    Returns:
        Raw audio bytes (MP3/WAV) of the generated song.
    """
    from gradio_client import Client

    last_error = None
    for space_id in YUE_SPACES:
        try:
            print(f"  [yue] Connecting to {space_id} ...")
            # Newer gradio_client versions use token=, older used hf_token=
            try:
                client = Client(space_id, token=hf_token)
            except TypeError:
                client = Client(space_id, hf_token=hf_token)

            print(f"  [yue] Generating song ({len(lyrics)} chars lyrics) ...")
            print(f"  [yue] Genre: {genre_tags[:60]}")

            # YuE gradio interface typically takes: genre text, lyrics text,
            # num_segments (song sections), max_new_tokens (length control)
            result = client.predict(
                genre_txt=genre_tags,
                lyrics_txt=lyrics,
                num_segments=max(2, min(6, duration_sec // 40)),
                max_new_tokens=3000,
                api_name="/predict"
            )

            audio_path = result[0] if isinstance(result, (list, tuple)) else result
            if isinstance(audio_path, dict):
                audio_path = audio_path.get("path") or audio_path.get("audio")

            with open(audio_path, "rb") as f:
                data = f.read()

            print(f"  [yue] Generated {len(data)//1024} KB ✓")
            return data

        except Exception as e:
            last_error = e
            print(f"  [yue] {space_id} failed: {str(e)[:150]}")
            time.sleep(5)

    raise RuntimeError(f"All YuE spaces failed. Last error: {last_error}")


def build_yue_lyrics(sections: list) -> str:
    """
    Format section list into YuE's expected lyrics format.

    Args:
        sections : List of {"type": "verse"/"chorus", "lines": [...]}

    Returns:
        Formatted lyrics string with [verse]/[chorus] tags.
    """
    parts = []
    for sec in sections:
        tag = sec.get("type", "verse")
        lines = sec.get("lines", [])
        parts.append(f"[{tag}]")
        parts.extend(lines)
        parts.append("")   # blank line between sections
    return "\n".join(parts)
