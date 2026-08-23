#!/usr/bin/env python3
"""
run_acestep.py — Runs on Kaggle GPU notebook
Generates a full romantic song with real vocals using ACE-Step.

FIXED: "acestep" is NOT on PyPI under that name for pip install.
Correct install is directly from GitHub:
  pip install git+https://github.com/ace-step/ACE-Step.git
"""
import json, os, subprocess, sys

# Reduce CUDA memory fragmentation (T4 has limited VRAM ~15GB usable)
os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

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

# ── Install ACE-Step from GitHub (correct method — not on PyPI as 'acestep') ──
print("\nInstalling ACE-Step from GitHub source...")
subprocess.run([
    sys.executable, "-m", "pip", "install",
    "git+https://github.com/ace-step/ACE-Step.git",
    "--quiet"
], check=True)

print("Installing ffmpeg-python and torchaudio (if missing)...")
subprocess.run([
    sys.executable, "-m", "pip", "install",
    "torchaudio", "--quiet"
], check=False)   # may already be present in Kaggle image

# ── Generate song ─────────────────────────────────────────────────────────────
print("\nGenerating song with ACE-Step on GPU...")

import torch
from acestep.pipeline_ace_step import ACEStepPipeline

# Free any cached memory before loading
torch.cuda.empty_cache()

pipe = ACEStepPipeline(
    checkpoint_dir=None,       # auto-downloads to ~/.cache/ace-step/checkpoints
    dtype="float16",
    torch_compile=False,
    cpu_offload=True,          # offload unused layers to CPU RAM — fixes OOM on 16GB GPUs
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

# Find the generated audio file
import glob
audio_files = glob.glob("/kaggle/working/*.wav") + glob.glob("/kaggle/working/*.mp3")

if not audio_files:
    raise RuntimeError(f"No audio file found in /kaggle/working/. Contents: {os.listdir('/kaggle/working/')}")

source_file = audio_files[0]
print(f"Found generated file: {source_file}")

# Ensure final output is named generated_song.mp3
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
