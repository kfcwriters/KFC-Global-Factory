"""
kaggle_video_gen.py
Generates real animated cartoon clips using AnimateDiff on a SEPARATE
Kaggle account's free T4 GPU — independent quota from the music pipeline.

Requires GitHub Secrets:
  KAGGLE_USERNAME_2 : second Kaggle account username
  KAGGLE_KEY_2       : second Kaggle account API token (KGAT_... format)
"""
import json, os, time, subprocess, tempfile
from pathlib import Path


def _setup_kaggle_credentials(username: str, key: str):
    """Supports both new (KGAT_) and legacy token formats."""
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(exist_ok=True)

    if key.startswith("KGAT_") or (not username and key):
        token_file = kaggle_dir / "access_token"
        token_file.write_text(key.strip())
        token_file.chmod(0o600)
        os.environ["KAGGLE_API_TOKEN"] = key.strip()
        print(f"  [kaggle-video] New-format API token set ✓")
    else:
        creds_file = kaggle_dir / "kaggle.json"
        creds_file.write_text(json.dumps({"username": username, "key": key}))
        creds_file.chmod(0o600)
        print(f"  [kaggle-video] Legacy credentials set for: {username}")


def _run(cmd: list, check=True) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\n"
            f"stdout: {result.stdout[:400]}\nstderr: {result.stderr[:400]}"
        )
    return result


def upload_params_dataset(username: str, prompts: list, title: str,
                          num_frames: int = 16, fps: int = 8) -> str:
    """Upload scene prompts as a Kaggle dataset."""
    params = {"prompts": prompts, "title": title,
              "num_frames": num_frames, "fps": fps}
    dataset_slug = f"{username}/cartoon-params"

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "params.json").write_text(json.dumps(params, indent=2))
        meta = {"title": "Cartoon Parameters", "id": dataset_slug,
                "licenses": [{"name": "CC0-1.0"}]}
        (tmp / "dataset-metadata.json").write_text(json.dumps(meta))

        print(f"  [kaggle-video] Uploading params ({len(prompts)} scenes) ...")
        create_result = _run(
            ["kaggle", "datasets", "create", "-p", str(tmp), "--quiet"],
            check=False
        )
        if create_result.returncode != 0:
            err = (create_result.stdout + create_result.stderr).lower()
            if any(w in err for w in ["already exists", "already have", "409", "exists"]):
                print(f"  [kaggle-video] Dataset exists — updating ...")
                _run(["kaggle", "datasets", "version", "-p", str(tmp),
                      "-m", "updated", "--quiet"])
            else:
                raise RuntimeError(
                    f"Dataset create failed:\n{create_result.stdout}\n{create_result.stderr}"
                )

    print(f"  [kaggle-video] Params uploaded ✓")
    return dataset_slug


def trigger_kernel(username: str, kaggle_dir: Path):
    """Push kernel with T4 GPU explicitly requested."""
    kernel_slug = f"{username}/animatediff-cartoon-generator"
    print(f"  [kaggle-video] Triggering kernel (T4 GPU) ...")

    result = _run(
        ["kaggle", "kernels", "push", "-p", str(kaggle_dir),
         "--accelerator", "NvidiaTeslaT4"],
        check=False
    )
    if result.returncode != 0:
        err = (result.stdout + result.stderr).lower()
        if "unrecognized" in err or "no such option" in err:
            print(f"  [kaggle-video] --accelerator flag unsupported, pushing without it ...")
            _run(["kaggle", "kernels", "push", "-p", str(kaggle_dir)])
        else:
            raise RuntimeError(f"Kernel push failed:\n{result.stdout}\n{result.stderr}")

    print(f"  [kaggle-video] Kernel triggered ✓")
    return kernel_slug


def wait_for_kernel(kernel_slug: str, timeout_min: int = 30) -> bool:
    """Video generation takes longer than music — allow more time."""
    print(f"  [kaggle-video] Waiting (up to {timeout_min} min) ...")
    max_polls = timeout_min * 4
    for attempt in range(max_polls):
        time.sleep(15)
        result = subprocess.run(
            ["kaggle", "kernels", "status", kernel_slug],
            capture_output=True, text=True
        )
        output = (result.stdout + result.stderr).lower()
        print(f"  [kaggle-video] attempt {attempt+1}: {result.stdout.strip()[:100]}")

        if "complete" in output:
            print(f"  [kaggle-video] Kernel completed ✓")
            return True
        if any(w in output for w in ["error", "failed", "cancel"]):
            raise RuntimeError(f"Kernel failed: {result.stdout}")

    raise RuntimeError(f"Kernel timed out after {timeout_min} minutes")


def download_clips(kernel_slug: str) -> list:
    """Download all generated video clips."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        print(f"  [kaggle-video] Downloading clips ...")
        _run(["kaggle", "kernels", "output", kernel_slug, "-p", str(tmp)])

        clip_files = sorted((tmp / "clips").glob("*.mp4")) if (tmp/"clips").exists() \
                     else sorted(tmp.glob("**/*.mp4"))

        if not clip_files:
            all_files = list(tmp.glob("**/*"))
            raise RuntimeError(f"No clips found. Files: {[f.name for f in all_files]}")

        clips_bytes = [f.read_bytes() for f in clip_files]
        total_kb = sum(len(c) for c in clips_bytes) // 1024
        print(f"  [kaggle-video] Downloaded {len(clips_bytes)} clips ({total_kb} KB total) ✓")
        return clips_bytes


def generate_clips_kaggle(prompts: list, title: str,
                          kaggle_username: str, kaggle_key: str,
                          num_frames: int = 16, fps: int = 8) -> list:
    """Full pipeline: upload params → trigger kernel → wait → download clips."""
    _setup_kaggle_credentials(kaggle_username, kaggle_key)

    kaggle_dir = Path(__file__).parent.parent / "kaggle_video"
    kernel_slug = f"{kaggle_username}/animatediff-cartoon-generator"

    upload_params_dataset(kaggle_username, prompts, title, num_frames, fps)
    trigger_kernel(kaggle_username, kaggle_dir)
    wait_for_kernel(kernel_slug, timeout_min=30)
    return download_clips(kernel_slug)
