"""
kaggle_music_gen.py
Generates full AI songs with REAL VOCALS by running ACE-Step on
Kaggle's FREE T4 GPU (16GB VRAM, 30 hours/week).

FIXED: Explicit UTF-8 encoding throughout — without this, Devanagari
Hindi text (or any non-ASCII script) can get mangled when written to
disk/JSON, causing ACE-Step to receive corrupted or fallback-to-English
text even though the Python string itself was correct.
"""
import json, os, time, subprocess, tempfile
from pathlib import Path


def _setup_kaggle_credentials(username: str, key: str):
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(exist_ok=True)

    if key.startswith("KGAT_") or (not username and key):
        token_file = kaggle_dir / "access_token"
        token_file.write_text(key.strip(), encoding="utf-8")
        token_file.chmod(0o600)
        os.environ["KAGGLE_API_TOKEN"] = key.strip()
        print(f"  [kaggle] New-format API token set ✓")
    else:
        creds_file = kaggle_dir / "kaggle.json"
        creds_file.write_text(
            json.dumps({"username": username, "key": key}),
            encoding="utf-8"
        )
        creds_file.chmod(0o600)
        print(f"  [kaggle] Legacy credentials set for: {username}")


def _run(cmd: list, check=True) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if check and result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\n"
            f"stdout: {result.stdout[:400]}\nstderr: {result.stderr[:400]}"
        )
    return result


def upload_params_dataset(username: str, lyrics: str, style: str,
                          title: str, duration: int = 180) -> str:
    """
    Upload song parameters as a Kaggle dataset.

    CRITICAL FIX: Both json.dumps(..., ensure_ascii=False) AND
    write_text(..., encoding="utf-8") are required together.
    - ensure_ascii=False keeps Devanagari/non-Latin chars as real UTF-8
      bytes in the file (readable, not \\uXXXX escapes)
    - encoding="utf-8" ensures Path.write_text() doesn't fall back to
      a platform-default encoding (which can differ on some runners)
    """
    params = {"lyrics": lyrics, "style": style, "title": title, "duration": duration}
    dataset_slug = f"{username}/song-params"

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        params_json = json.dumps(params, indent=2, ensure_ascii=False)
        (tmp / "params.json").write_text(params_json, encoding="utf-8")

        # Debug: confirm what's actually being written
        print(f"  [kaggle] Lyrics preview (first 100 chars): {lyrics[:100]}")

        meta = {
            "title": "Song Parameters",
            "id": dataset_slug,
            "licenses": [{"name": "CC0-1.0"}]
        }
        (tmp / "dataset-metadata.json").write_text(
            json.dumps(meta, ensure_ascii=False), encoding="utf-8"
        )

        print(f"  [kaggle] Uploading params dataset ...")

        create_result = _run(
            ["kaggle", "datasets", "create", "-p", str(tmp), "--quiet"],
            check=False
        )

        if create_result.returncode != 0:
            err = (create_result.stdout + create_result.stderr).lower()
            if any(w in err for w in ["already exists", "already have", "409", "exists"]):
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
    """Push kernel with T4 GPU explicitly requested."""
    kernel_slug = f"{username}/ace-step-music-generator"
    print(f"  [kaggle] Triggering kernel: {kernel_slug} (T4 GPU) ...")

    result = _run(
        ["kaggle", "kernels", "push", "-p", str(kaggle_dir),
         "--accelerator", "NvidiaTeslaT4"],
        check=False
    )

    if result.returncode != 0:
        err = (result.stdout + result.stderr).lower()
        if "unrecognized" in err or "no such option" in err or "unexpected" in err:
            print(f"  [kaggle] --accelerator flag not supported, pushing without it ...")
            _run(["kaggle", "kernels", "push", "-p", str(kaggle_dir)])
        else:
            raise RuntimeError(f"Kernel push failed:\n{result.stdout}\n{result.stderr}")

    print(f"  [kaggle] Kernel triggered ✓")
    return kernel_slug


def wait_for_kernel(kernel_slug: str, timeout_min: int = 25) -> bool:
    print(f"  [kaggle] Waiting for kernel (up to {timeout_min} min) ...")
    max_polls = timeout_min * 4
    for attempt in range(max_polls):
        time.sleep(15)
        result = subprocess.run(
            ["kaggle", "kernels", "status", kernel_slug],
            capture_output=True, text=True, encoding="utf-8"
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
    kernel_slug = f"{kaggle_username}/ace-step-music-generator"

    upload_params_dataset(kaggle_username, lyrics, style, title, duration)
    trigger_kernel(kaggle_username, kaggle_dir)
    wait_for_kernel(kernel_slug, timeout_min=25)
    return download_output(kernel_slug)
