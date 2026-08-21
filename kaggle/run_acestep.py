#!/usr/bin/env python3
"""
run_acestep.py — Runs on Kaggle GPU notebook
Generates a full romantic song with real vocals using ACE-Step.
Called automatically via Kaggle API from GitHub Actions.

Input: /kaggle/input/song-params/params.json
Output: /kaggle/working/generated_song.mp3
"""
import json, os, subprocess, sys

# ── Read parameters from input dataset ────────────────────────────────────────
params_path = "/kaggle/input/song-params/params.json"
if os.path.exists(params_path):
    with open(params_path) as f:
        params = json.load(f)
else:
    params = {
        "lyrics": "[verse]\nIn the quiet of the night\nI reach out for your hand\nEvery star above us shines\n\n[chorus]\nI will never let you go\nYou are the only love I know",
        "style": "romantic ballad, soft piano, emotional female vocals, slow tempo",
        "title": "Never Let You Go",
        "duration": 180
    }

print(f"Generating: {params['title']}")
print(f"Style: {params['style'][:60]}")
print(f"Duration: {params.get('duration', 180)}s")

# ── Install ACE-Step ──────────────────────────────────────────────────────────
print("\nInstalling ACE-Step...")
subprocess.run([
    sys.executable, "-m", "pip", "install",
    "acestep", "--quiet"
], check=True)

# ── Generate song ─────────────────────────────────────────────────────────────
print("\nGenerating song with ACE-Step on GPU...")

from acestep.pipeline import ACEStepPipeline

pipe = ACEStepPipeline.from_pretrained(
    "ACE-Step/ACE-Step-v1",
    torch_dtype="float16"
)
pipe = pipe.to("cuda")

duration = float(params.get("duration", 180))
result = pipe(
    audio_duration=duration,
    prompt=params["style"],
    lyrics=params["lyrics"],
    infer_step=27,
    guidance_scale=15.0,
    scheduler_type="euler",
    cfg_type="apg",
    use_erg_tag=True,
    use_erg_lyric=True,
    use_erg_diffusion=True,
    guidance_interval=0.5,
    guidance_interval_decay=0.0,
    min_guidance_scale=3.0,
    granularity_scale=10.0,
)

# Save output
out_wav = "/kaggle/working/generated_song.wav"
out_mp3 = "/kaggle/working/generated_song.mp3"

import torchaudio
torchaudio.save(out_wav, result["waveform"].squeeze(0).cpu(), result["sample_rate"])
print(f"WAV saved: {out_wav}")

# Convert to MP3
subprocess.run([
    "ffmpeg", "-y", "-i", out_wav,
    "-codec:a", "libmp3lame", "-qscale:a", "2",
    out_mp3
], check=True)

size = os.path.getsize(out_mp3) // 1024
print(f"\n✅ Song generated: {out_mp3} ({size} KB)")
print(f"Title: {params['title']}")
