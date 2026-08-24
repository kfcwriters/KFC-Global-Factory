#!/usr/bin/env python3
"""
run_animatediff.py — Runs on Kaggle GPU notebook (SEPARATE Kaggle account)
Generates real animated video clips using AnimateDiff.
"""
import os

# Must be set before importing torch
os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import json, subprocess, sys

params_path = "/kaggle/input/cartoon-params/params.json"
if os.path.exists(params_path):
    with open(params_path) as f:
        params = json.load(f)
else:
    params = {
        "prompts": [
            "cute cartoon bunny hopping in a colorful meadow, children's animation style",
            "happy cartoon bear waving hello, bright colors, kids cartoon style",
        ],
        "title": "Test Cartoon",
        "num_frames": 16,
        "fps": 8,
    }

print(f"Generating cartoon: {params['title']}")
print(f"Number of scene prompts: {len(params['prompts'])}")

print("\nInstalling dependencies...")
subprocess.run([
    sys.executable, "-m", "pip", "install",
    "diffusers", "transformers", "accelerate", "imageio", "imageio-ffmpeg",
    "--quiet", "--upgrade"
], check=True)

import torch
from diffusers import AnimateDiffPipeline, MotionAdapter, EulerDiscreteScheduler
from diffusers.utils import export_to_video

torch.cuda.empty_cache()

print("\nLoading AnimateDiff motion adapter...")
adapter = MotionAdapter.from_pretrained(
    "guoyww/animatediff-motion-adapter-v1-5-2",
    torch_dtype=torch.float16
)

print("Loading base pipeline (Realistic Vision / SD 1.5 backbone)...")
pipe = AnimateDiffPipeline.from_pretrained(
    "SG161222/Realistic_Vision_V5.1_noVAE",
    motion_adapter=adapter,
    torch_dtype=torch.float16
)

pipe.scheduler = EulerDiscreteScheduler.from_config(
    pipe.scheduler.config,
    timestep_spacing="linspace",
    beta_schedule="linear"
)

pipe.enable_model_cpu_offload()
pipe.enable_vae_slicing()

print("Pipeline loaded ✓\n")

os.makedirs("/kaggle/working/clips", exist_ok=True)
num_frames = params.get("num_frames", 16)
fps        = params.get("fps", 8)

clip_paths = []
for i, prompt in enumerate(params["prompts"]):
    print(f"\n[{i+1}/{len(params['prompts'])}] Generating: {prompt[:60]}...")

    output = pipe(
        prompt=prompt,
        negative_prompt="blurry, low quality, distorted, scary, dark, violent",
        num_frames=num_frames,
        guidance_scale=7.5,
        num_inference_steps=25,
    )

    frames = output.frames[0]
    clip_path = f"/kaggle/working/clips/clip_{i:02d}.mp4"
    export_to_video(frames, clip_path, fps=fps)
    clip_paths.append(clip_path)
    print(f"  Saved: {clip_path} ✓")

    torch.cuda.empty_cache()

print(f"\n✅ Generated {len(clip_paths)} clips")
for p in clip_paths:
    size = os.path.getsize(p) // 1024
    print(f"  {p} ({size} KB)")
