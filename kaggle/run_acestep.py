#!/usr/bin/env python3
"""
run_acestep.py — Runs on Kaggle GPU notebook
Generates a full romantic song with real vocals using ACE-Step.

UPDATED: Reads params.json from the SAME folder as this script
(pushed together as kernel files) instead of a separate Kaggle
dataset attachment — the dataset mechanism proved unreliable.
"""
import os

os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import json, subprocess, sys
from pathlib import Path

# Look for params.json in the same directory as this script first
script_dir       = Path(__file__).parent
local_params_path = script_dir / "params.json"
# Fallback: old dataset location, in case it's ever reattached
dataset_params_path = Path("/kaggle/input/song-params/params.json")

if local_params_path.exists():
    print(f"Reading params from local file: {local_params_path}")
    with open(local_params_path, encoding="utf-8") as f:
        params = json.load(f)
elif dataset_params_path.exists():
    print(f"Reading params from dataset: {dataset_params_path}")
    with open(dataset_params_path, encoding="utf-8") as f:
        params = json.load(f)
else:
    print("WARNING: No params.json found anywhere — using hardcoded test fallback")
    params = {
        "lyrics": "[verse]\nIn the quiet of the night\nI reach out for your hand\nEvery star above us shines\n\n[chorus]\nI will never let you go\nYou are the only love I know",
        "style": "romantic ballad, soft piano, emotional female vocals, slow tempo",
        "title": "Never Let You Go",
        "duration": 180
    }

print(f"Generating: {params['title']}")
print(f"Style: {params['style'][:60]}")
print(f"Duration: {params.get('duration', 180)}s")
print(f"Lyrics preview: {params['lyrics'][:100]}")

# ── Install ACE-Step from GitHub ──────────────────────────────────────────────
print("\nInstalling ACE-Step from GitHub source...")
subprocess.run([
    sys.executable, "-m", "pip", "install",
    "git+https://github.com/ace-step/ACE-Step.git",
    "--quiet"
], check=True)

subprocess.run([
    sys.executable, "-m", "pip", "install",
    "torchaudio", "--quiet"
], check=False)

# ── Generate song ─────────────────────────────────────────────────────────────
print("\nGenerating song with ACE-Step on GPU...")

from acestep.pipeline_ace_step import ACEStepPipeline
import torch
torch.cuda.empty_cache()

pipe = ACEStepPipeline(
    checkpoint_dir=None,
    dtype="float16",
    torch_compile=False,
    cpu_offload=True,
)

duration = float(params.get("duration", 180))

output_paths = pipe(
    audio_duration=duration,
    prompt=params["style"],
    lyrics=params["lyrics"],
    infer_step=27,
    guidance_scale=15.0,
    scheduler_type="euler",
    cfg_type="apg",
    omega_scale=10.0,
    guidance_interval=0.5,
    guidance_interval_decay=0.0,
    min_guidance_scale=3.0,
    use_erg_tag=True,
    use_erg_lyric=True,
    use_erg_diffusion=True,
    save_path="/kaggle/working/",
)

print(f"\nOutput paths: {output_paths}")

import glob
audio_files = glob.glob("/kaggle/working/*.wav") + glob.glob("/kaggle/working/*.mp3")

if not audio_files:
    raise RuntimeError(f"No audio file found. Contents: {os.listdir('/kaggle/working/')}")

source_file = audio_files[0]
print(f"Found generated file: {source_file}")

final_mp3 = "/kaggle/working/generated_song.mp3"
if source_file.endswith(".wav"):
    subprocess.run([
        "ffmpeg", "-y", "-i", source_file,
        "-codec:a", "libmp3lame", "-qscale:a", "2",
        final_mp3
    ], check=True)
else:
    import shutil
    if source_file != final_mp3:
        shutil.copy(source_file, final_mp3)

size = os.path.getsize(final_mp3) // 1024
print(f"\n✅ Song generated: {final_mp3} ({size} KB)")
print(f"Title: {params['title']}")
