"""
kaggle_music_gen.py
Generates full AI songs with REAL VOCALS by running ACE-Step on
Kaggle's FREE T4 GPU (16GB VRAM, 30 hours/week).

Flow:
  1. Upload lyrics/style params as a Kaggle dataset
  2. Trigger the ACE-Step kernel via Kaggle API
  3. Poll until complete (usually 3-8 minutes)
  4. Download the generated MP3

Requirements:
  KAGGLE_USERNAME: your Kaggle username (GitHub Secret)
  KAGGLE_KEY: your Kaggle API key (GitHub Secret)
"""
import json, os, time, subprocess, requests, tempfile
from pathlib import Path


def _setup_kaggle_credentials(username: str, key: str):
    """Write Kaggle API credentials to the expected location."""
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(exist_ok=True)
    creds_file = kaggle_dir / "kaggle.json"
    creds_file.write_text(json.dumps({"username": username, "key": key}))
    creds_file.chmod(0o600)
    print(f"  [kaggle] Credentials set for user: {username}")


def _run(cmd: list, **kwargs) -> subprocess.CompletedProcess:
    """Run a shell command."""
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr[:500]}")
    return result


def upload_params_dataset(username: str, lyrics: str, style: str,
                          title: str, duration: int = 180) -> str:
    """
    Upload song parameters as a Kaggle dataset so the kernel can read them.
    Returns the dataset slug (username/song-params).
    """
    params = {"lyrics": lyrics, "style": style, "title": title, "duration": duration}
    dataset_slug = f"{username}/song-params"

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        # Write params JSON
        (tmp / "params.json").write_text(json.dumps(params, indent=2))

        # Write dataset metadata
        meta = {
            "title": "Song Parameters",
            "id": dataset_slug,
            "licenses": [{"name": "CC0-1.0"}]
        }
        (tmp / "dataset-metadata.json").write_text(json.dumps(meta))

        print(f"  [kaggle] Uploading params dataset: {dataset_slug} ...")
        try:
            _run(["kaggle", "datasets", "create", "-p", str(tmp), "--quiet"])
        except RuntimeError:
            # Dataset exists — update it instead
            _run(["kaggle", "datasets", "version", "-p", str(tmp),
                  "-m", "updated params", "--quiet"])

    print(f"  [kaggle] Params uploaded ✓")
    return dataset_slug


def trigger_kernel(username: str, kernel_slug: str = "acestep-music-generator"):
    """Push and trigger the ACE-Step kernel."""
    kaggle_dir = Path(__file__).parent.parent / "kaggle"
    full_slug = f"{username}/{kernel_slug}"

    print(f"  [kaggle] Triggering kernel: {full_slug} ...")
    _run(["kaggle", "kernels", "push", "-p", str(kaggle_dir)])
    print(f"  [kaggle] Kernel triggered ✓")
    return full_slug


def wait_for_kernel(kernel_slug: str, timeout_min: int = 20) -> bool:
    """Poll kernel status until complete or failed."""
    print(f"  [kaggle] Waiting for kernel to complete ...")
    max_polls = timeout_min * 4   # every 15 seconds
    for attempt in range(max_polls):
        time.sleep(15)
        result = subprocess.run(
            ["kaggle", "kernels", "status", kernel_slug],
            capture_output=True, text=True
        )
        output = result.stdout.lower() + result.stderr.lower()
        print(f"  [kaggle] attempt {attempt+1}: {result.stdout.strip()[:80]}")

        if "complete" in output:
            print(f"  [kaggle] Kernel completed ✓")
            return True
        if "error" in output or "failed" in output:
            raise RuntimeError(f"Kernel failed: {result.stdout}")

    raise RuntimeError(f"Kernel timed out after {timeout_min} minutes")


def download_output(kernel_slug: str) -> bytes:
    """Download the generated MP3 from kernel output."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        print(f"  [kaggle] Downloading kernel output ...")
        _run(["kaggle", "kernels", "output", kernel_slug, "-p", str(tmp)])

        # Find the MP3 file
        mp3_files = list(tmp.glob("*.mp3"))
        wav_files = list(tmp.glob("*.wav"))

        if mp3_files:
            data = mp3_files[0].read_bytes()
            print(f"  [kaggle] Downloaded MP3: {len(data)//1024} KB ✓")
            return data
        elif wav_files:
            # Convert WAV to MP3
            wav_path = str(wav_files[0])
            mp3_path = str(tmp / "output.mp3")
            subprocess.run(["ffmpeg", "-y", "-i", wav_path,
                           "-codec:a", "libmp3lame", "-qscale:a", "2", mp3_path],
                          check=True, capture_output=True)
            data = Path(mp3_path).read_bytes()
            print(f"  [kaggle] Downloaded + converted: {len(data)//1024} KB ✓")
            return data
        else:
            files = list(tmp.glob("*"))
            raise RuntimeError(f"No audio file in output. Files found: {files}")


def generate_song_kaggle(lyrics: str, style: str, title: str,
                         kaggle_username: str, kaggle_key: str,
                         duration: int = 180) -> bytes:
    """
    Full end-to-end: upload params → trigger kernel → wait → download.
    Returns MP3 bytes of the generated song.
    """
    _setup_kaggle_credentials(kaggle_username, kaggle_key)

    kernel_slug = f"{kaggle_username}/acestep-music-generator"

    # Step 1: Upload params
    upload_params_dataset(kaggle_username, lyrics, style, title, duration)

    # Step 2: Trigger kernel
    trigger_kernel(kaggle_username)

    # Step 3: Wait for completion
    wait_for_kernel(kernel_slug, timeout_min=20)

    # Step 4: Download output
    return download_output(kernel_slug)
