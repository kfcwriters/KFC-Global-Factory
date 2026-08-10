"""
acestep_music_gen.py
Generates full songs WITH REAL VOCALS using ACE-Step's official HF Space.

v3: Smarter schema discovery — automatically finds the actual generation
endpoint (searching for "generate"/"text2music" in the name) instead of
guessing, and calls it with the exact discovered parameter names.
"""
import time, json

ACESTEP_SPACES = [
    "ACE-Step/ACE-Step",         # official v1 — confirmed alive, generation demo
]

# Keywords that indicate the "real" generation endpoint vs training/admin endpoints
GENERATE_KEYWORDS = ["text2music", "generate", "__call__", "predict", "run"]
SKIP_KEYWORDS = ["dataset", "checkpoint", "toggle", "visibility", "lambda",
                 "update_model", "import", "training", "lora"]


def _connect(space_id: str, hf_token: str):
    from gradio_client import Client
    try:
        return Client(space_id, token=hf_token)
    except TypeError:
        return Client(space_id, hf_token=hf_token)


def _find_generate_endpoint(client) -> tuple:
    """
    Inspect the full API schema and find the actual generation endpoint.
    Returns (endpoint_name, list_of_param_names) or (None, None).
    """
    api_info = client.view_api(print_info=False, return_format="dict")
    endpoints = api_info.get("named_endpoints", {})

    print(f"  [acestep] Found {len(endpoints)} total endpoints")

    candidates = []
    for name, info in endpoints.items():
        lname = name.lower()
        if any(skip in lname for skip in SKIP_KEYWORDS):
            continue
        params = info.get("parameters", [])
        # A real generation endpoint takes several parameters (duration, tags, lyrics etc)
        # and returns audio
        returns = info.get("returns", [])
        returns_audio = any(
            "audio" in str(r.get("component","")).lower() or
            "audio" in str(r.get("label","")).lower()
            for r in returns
        )
        score = len(params)
        if any(kw in lname for kw in GENERATE_KEYWORDS):
            score += 100
        if returns_audio:
            score += 50
        candidates.append((score, name, params))

    if not candidates:
        return None, None

    candidates.sort(key=lambda x: -x[0])
    best_score, best_name, best_params = candidates[0]

    print(f"  [acestep] Best candidate endpoint: {best_name} (score={best_score})")
    param_names = [p.get("parameter_name", p.get("label","?")) for p in best_params]
    print(f"  [acestep] Parameters ({len(param_names)}): {param_names}")

    return best_name, best_params


def generate_song_acestep(lyrics: str, style_tags: str, hf_token: str,
                          duration_sec: int = 210) -> bytes:
    """Generate a full song with real vocals using ACE-Step, auto-discovering the API."""
    last_error = None

    for space_id in ACESTEP_SPACES:
        try:
            print(f"  [acestep] Connecting to {space_id} ...")
            client = _connect(space_id, hf_token)

            print(f"  [acestep] Discovering real generation endpoint ...")
            endpoint_name, params = _find_generate_endpoint(client)

            if not endpoint_name:
                raise RuntimeError("No suitable generation endpoint found")

            # Build kwargs by matching discovered parameter names to our values
            kwargs = {}
            for p in params:
                pname = p.get("parameter_name", "")
                default = p.get("parameter_default")
                pl = pname.lower()

                if "duration" in pl:
                    kwargs[pname] = float(duration_sec)
                elif "tag" in pl or "prompt" in pl:
                    kwargs[pname] = style_tags
                elif "lyric" in pl:
                    kwargs[pname] = lyrics
                elif "infer_step" in pl or "steps" in pl:
                    kwargs[pname] = 27
                elif "guidance_scale" in pl and "text" not in pl and "lyric" not in pl:
                    kwargs[pname] = 15.0
                elif pname and p.get("parameter_has_default"):
                    kwargs[pname] = default   # use documented default

            print(f"  [acestep] Calling {endpoint_name} with {len(kwargs)} matched params ...")
            result = client.predict(**kwargs, api_name=endpoint_name)

            # Result may be a single value, tuple, or nested audio dict
            audio_path = None
            if isinstance(result, (list, tuple)):
                for item in result:
                    if isinstance(item, str) and (item.endswith(".wav") or item.endswith(".mp3")):
                        audio_path = item
                        break
                    if isinstance(item, dict) and ("path" in item or "audio" in item):
                        audio_path = item.get("path") or item.get("audio")
                        break
                if not audio_path:
                    audio_path = result[0]
            elif isinstance(result, dict):
                audio_path = result.get("path") or result.get("audio")
            else:
                audio_path = result

            if not audio_path:
                raise RuntimeError(f"Could not extract audio path from result: {result}")

            with open(audio_path, "rb") as f:
                data = f.read()

            print(f"  [acestep] Generated {len(data)//1024} KB ✓")
            return data

        except Exception as e:
            last_error = e
            print(f"  [acestep] {space_id} failed: {str(e)[:300]}")
            time.sleep(5)

    raise RuntimeError(f"All ACE-Step spaces failed. Last error: {last_error}")


def build_acestep_lyrics(sections: list) -> str:
    parts = []
    for sec in sections:
        tag = sec.get("type", "verse")
        lines = sec.get("lines", [])
        parts.append(f"[{tag}]")
        parts.extend(lines)
        parts.append("")
    return "\n".join(parts)
