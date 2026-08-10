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

            # ── Extract ALL audio-like paths from result (there may be several) ──
            print(f"  [acestep] Raw result type: {type(result)}")
            if isinstance(result, (list, tuple)):
                print(f"  [acestep] Result has {len(result)} items:")
                for i, item in enumerate(result):
                    print(f"    [{i}] {type(item).__name__}: {str(item)[:150]}")

            candidate_paths = []
            items = result if isinstance(result, (list, tuple)) else [result]
            for item in items:
                if isinstance(item, str) and (item.endswith(".wav") or item.endswith(".mp3") or item.endswith(".flac")):
                    candidate_paths.append(item)
                elif isinstance(item, dict):
                    p = item.get("path") or item.get("audio") or item.get("value")
                    if isinstance(p, str) and (p.endswith(".wav") or p.endswith(".mp3") or p.endswith(".flac")):
                        candidate_paths.append(p)

            if not candidate_paths:
                raise RuntimeError(f"No audio file paths found in result: {result}")

            print(f"  [acestep] Found {len(candidate_paths)} audio candidate(s): {candidate_paths}")

            # ── Validate each candidate: must exist, be non-trivial size, and NOT silent ──
            import subprocess as _sp
            for audio_path in candidate_paths:
                try:
                    with open(audio_path, "rb") as f:
                        data = f.read()

                    if len(data) < 50_000:   # smaller than ~50KB is suspicious for a song
                        print(f"  [acestep] {audio_path}: too small ({len(data)} bytes) — skipping")
                        continue

                    # Check for actual audio content (not silence) using ffmpeg volumedetect
                    probe = _sp.run(
                        ["ffmpeg", "-i", audio_path, "-af", "volumedetect",
                         "-f", "null", "-"],
                        capture_output=True, text=True, timeout=30
                    )
                    stderr = probe.stderr
                    mean_vol_line = [l for l in stderr.split("\n") if "mean_volume" in l]
                    if mean_vol_line:
                        mean_db = float(mean_vol_line[0].split(":")[1].strip().replace(" dB",""))
                        print(f"  [acestep] {audio_path}: mean_volume={mean_db:.1f}dB, size={len(data)//1024}KB")
                        if mean_db < -50:   # essentially silent
                            print(f"  [acestep] {audio_path}: SILENT — skipping")
                            continue
                    else:
                        print(f"  [acestep] {audio_path}: could not detect volume, accepting cautiously")

                    print(f"  [acestep] Validated real audio: {audio_path} ({len(data)//1024} KB) ✓")
                    return data

                except Exception as val_err:
                    print(f"  [acestep] {audio_path}: validation error ({val_err}) — skipping")
                    continue

            raise RuntimeError("All candidate audio files were invalid, too small, or silent")

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
