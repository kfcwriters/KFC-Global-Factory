"""
kaggle_music_gen.py
Generates full AI songs with REAL VOCALS by running ACE-Step on
Kaggle's FREE T4 GPU (16GB VRAM, 30 hours/week).
"""
import json, os, time, subprocess, tempfile
from pathlib import Path


def _setup_kaggle_credentials(username: str, key: str):
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(exist_ok=True)
    creds_file = kaggle_dir / "kaggle.json"
    creds_file.write_text(json.dumps({"username": username, "key": key}))
    creds_file.chmod(0o600)
    print(f"  [kaggle] Credentials set for user: {username}")


def _run(cmd: list, check=True) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\n"
            f"stdout: {result.stdout[:300]}\n"
            f"stderr: {result.stderr[:300]}"
        )
    return result


def upload_params_dataset(username: str, lyrics: str, style: str,
                          title: str, duration: int = 180) -> str:
    """Upload song parameters as a Kaggle dataset."""
    params = {"lyrics": lyrics, "style": style, "title": title, "duration": duration}
    dataset_slug = f"{username}/song-params"

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "params.json").write_text(json.dumps(params, indent=2))
        meta = {
            "title": "Song Parameters",
            "id": dataset_slug,
            "licenses": [{"name": "CC0-1.0"}]
        }
        (tmp / "dataset-metadata.json").write_text(json.dumps(meta))

        print(f"  [kaggle] Uploading params dataset ...")

        # Try create first, fall back to version if it already exists
        create_result = _run(
            ["kaggle", "datasets", "create", "-p", str(tmp), "--quiet"],
            check=False
        )

        if create_result.returncode != 0:
            err = (create_result.stdout + create_result.stderr).lower()
            if "already exists" in err or "already have" in err or "409" in err or "exists" in err:
                print(f"  [kaggle] Dataset exists — updating ...")
                _run(["kaggle", "datasets", "version", "-p", str(tmp),
                      "-m", "updated", "--quiet"])
            else:
                raise RuntimeError(
                    f"Dataset create failed:\n"
                    f"{create_result.stdout}\n{create_result.stderr}"
                )

    print(f"  [kaggle] Params uploaded: {dataset_slug} ✓")
    return dataset_slug


def trigger_kernel(username: str, kaggle_dir: Path):
    """Push and trigger the ACE-Step kernel."""
    kernel_slug = f"{username}/acestep-music-generator"
    print(f"  [kaggle] Triggering kernel: {kernel_slug} ...")
    _run(["kaggle", "kernels", "push", "-p", str(kaggle_dir)])
    print(f"  [kaggle] Kernel triggered ✓")
    return kernel_slug


def wait_for_kernel(kernel_slug: str, timeout_min: int = 20) -> bool:
    """Poll kernel status until complete or failed."""
    print(f"  [kaggle] Waiting for kernel (up to {timeout_min} min) ...")
    max_polls = timeout_min * 4
    for attempt in range(max_polls):
        time.sleep(15)
        result = subprocess.run(
            ["kaggle", "kernels", "status", kernel_slug],
            capture_output=True, text=True
        )
        output = (result.stdout + result.stderr).lower()
        status_line = result.stdout.strip()
        print(f"  [kaggle] attempt {attempt+1}: {status_line[:100]}")

        if "complete" in output:
            print(f"  [kaggle] Kernel completed ✓")
            return True
        if any(w in output for w in ["error", "failed", "cancel"]):
            raise RuntimeError(f"Kernel failed: {result.stdout}")

    raise RuntimeError(f"Kernel timed out after {timeout_min} minutes")


def download_output(kernel_slug: str) -> bytes:
    """Download the generated MP3/WAV from kernel output."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        print(f"  [kaggle] Downloading kernel output ...")
        _run(["kaggle", "kernels", "output", kernel_slug, "-p", str(tmp)])

        mp3_files = list(tmp.glob("*.mp3"))
        wav_files = list(tmp.glob("*.wav"))

        if mp3_files:
            data = mp3_files[0].read_bytes()
            print(f"  [kaggle] Downloaded MP3: {len(data)//1024} KB ✓")
            return data

        if wav_files:
            wav_path = str(wav_files[0])
            mp3_path = str(tmp / "output.mp3")
            subprocess.run(
                ["ffmpeg", "-y", "-i", wav_path,
                 "-codec:a", "libmp3lame", "-qscale:a", "2", mp3_path],
                check=True, capture_output=True
            )
            data = Path(mp3_path).read_bytes()
            print(f"  [kaggle] Downloaded + converted: {len(data)//1024} KB ✓")
            return data

        all_files = list(tmp.glob("*"))
        raise RuntimeError(f"No audio file in output. Files: {[f.name for f in all_files]}")


def generate_song_kaggle(lyrics: str, style: str, title: str,
                         kaggle_username: str, kaggle_key: str,
                         duration: int = 180) -> bytes:
    """Full pipeline: upload params → trigger kernel → wait → download."""
    _setup_kaggle_credentials(kaggle_username, kaggle_key)

    kaggle_dir = Path(__file__).parent.parent / "kaggle"
    kernel_slug = f"{kaggle_username}/acestep-music-generator"

    upload_params_dataset(kaggle_username, lyrics, style, title, duration)
    trigger_kernel(kaggle_username, kaggle_dir)
    wait_for_kernel(kernel_slug, timeout_min=20)
    return download_output(kernel_slug)
