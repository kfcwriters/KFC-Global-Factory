"""
acestep_music_gen.py
Generates full songs WITH REAL VOCALS using ACE-Step's official HF Space.

Based on the actual live UI, the text2music Gradio app has these fields
(in this order): audio_duration, enable_audio2audio, lora_name_or_path,
ref_audio_input, ref_audio_strength, tags(prompt), lyrics, infer_step,
guidance_scale, guidance_scale_text, guidance_scale_lyric, manual_seeds,
scheduler_type, cfg_type, use_erg_tag, use_erg_lyric, use_erg_diffusion,
oss_steps, guidance_interval, guidance_interval_decay, min_guidance_scale,
granularity_scale.

Since gradio_client version/space differences can change exact api_name,
this module first tries the documented call, and if that fails, DUMPS the
live API schema to the log so we can read the ground truth and fix it
in one more iteration — no more blind guessing.
"""
import time

ACESTEP_SPACES = [
    "ACE-Step/ACE-Step",         # official v1 — confirmed alive & responding
    "ACE-Step/Ace-Step-v1.5",    # official v1.5 — newer
]


def _connect(space_id: str, hf_token: str):
    from gradio_client import Client
    try:
        return Client(space_id, token=hf_token)
    except TypeError:
        return Client(space_id, hf_token=hf_token)


def _dump_api_schema(client, space_id: str):
    """Print the real API schema so we can see exact endpoint/param names."""
    try:
        print(f"  [acestep] --- API schema for {space_id} ---")
        api_info = client.view_api(print_info=False, return_format="dict")
        import json
        print(json.dumps(api_info, indent=2)[:3000])   # cap output size
        print(f"  [acestep] --- end schema ---")
    except Exception as e:
        print(f"  [acestep] Could not dump schema: {e}")


def generate_song_acestep(lyrics: str, style_tags: str, hf_token: str,
                          duration_sec: int = 210) -> bytes:
    """Generate a full song with real vocals using ACE-Step."""
    last_error = None

    for space_id in ACESTEP_SPACES:
        try:
            print(f"  [acestep] Connecting to {space_id} ...")
            client = _connect(space_id, hf_token)

            print(f"  [acestep] Generating song ({duration_sec}s target) ...")
            print(f"  [acestep] Style: {style_tags[:60]}")

            # Try the documented positional order for the text2music tab.
            # Using positional args (not kwargs) avoids api_name/kwarg mismatches
            # across Space versions — matches the visible UI field order.
            try:
                result = client.predict(
                    float(duration_sec),   # audio_duration
                    False,                  # enable_audio2audio
                    "",                     # lora_name_or_path
                    None,                   # ref_audio_input
                    0.5,                    # ref_audio_strength
                    style_tags,             # tags
                    lyrics,                 # lyrics
                    27,                     # infer_step
                    15,                     # guidance_scale
                    0,                      # guidance_scale_text
                    0,                      # guidance_scale_lyric
                    "",                     # manual_seeds
                    "euler",                # scheduler_type
                    "apg",                  # cfg_type
                    True,                   # use_erg_tag
                    True,                   # use_erg_lyric
                    True,                   # use_erg_diffusion
                    "",                     # oss_steps
                    0.5,                    # guidance_interval
                    0.0,                    # guidance_interval_decay
                    3,                      # min_guidance_scale
                    10,                     # granularity_scale
                    api_name="/text2music_stage_1"
                )
            except Exception as e1:
                print(f"  [acestep] Named endpoint failed ({str(e1)[:100]}), "
                      f"trying default fn_index=0 ...")
                # Fallback: let gradio_client use the first/default API function
                result = client.predict(
                    float(duration_sec), False, "", None, 0.5,
                    style_tags, lyrics, 27, 15, 0, 0, "",
                    "euler", "apg", True, True, True, "",
                    0.5, 0.0, 3, 10,
                    fn_index=0
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
            # Dump the real schema so we know exactly what to fix next time
            try:
                client = _connect(space_id, hf_token)
                _dump_api_schema(client, space_id)
            except Exception:
                pass
            time.sleep(5)

    raise RuntimeError(f"All ACE-Step spaces failed. Last error: {last_error}")


def build_acestep_lyrics(sections: list) -> str:
    """Format section list into ACE-Step's [verse]/[chorus]/[bridge] format."""
    parts = []
    for sec in sections:
        tag = sec.get("type", "verse")
        lines = sec.get("lines", [])
        parts.append(f"[{tag}]")
        parts.extend(lines)
        parts.append("")
    return "\n".join(parts)
