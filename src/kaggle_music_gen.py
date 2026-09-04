"""
kaggle_music_gen.py
Generates full AI songs with REAL VOCALS by running ACE-Step on
Kaggle's FREE T4 GPU (16GB VRAM, 30 hours/week).

FINAL FIX: kaggle kernels push (kernel_type=script) only uploads the
SINGLE code_file — it does NOT bundle sibling files in the same folder,
and Kaggle "dataset" attachments proved unreliable (stale caching once
a kernel was manually edited via browser).

The reliable solution: bake params directly into the Python script's
SOURCE CODE as a JSON literal, generating run_acestep.py fresh from
run_acestep_template.py before every single push. What we write is
exactly what the kernel executes — no external file, no caching layer.
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


def bake_params_into_script(kaggle_dir: Path, lyrics: str, style: str,
                            title: str, duration: int = 180):
    """
    Fill run_acestep_template.py's __PARAMS_JSON__ placeholder with real
    data and write the result as run_acestep.py — the actual file that
    gets pushed and executed. Regenerated fresh every single run.
    """
    template_path = kaggle_dir / "run_acestep_template.py"
    output_path   = kaggle_dir / "run_acestep.py"

    if not template_path.exists():
        raise FileNotFoundError(
            f"Template not found: {template_path}. "
            f"Upload run_acestep_template.py to the kaggle/ folder first."
        )

    template = template_path.read_text(encoding="utf-8")

    params = {"lyrics": lyrics, "style": style, "title": title, "duration": duration}
    # Use a Python raw-string-safe JSON dump — escape any literal ''' sequences
    # that could break out of the r'''...''' block in the template.
    params_json = json.dumps(params, ensure_ascii=False)
    params_json_safe = params_json.replace("'''", "\\'\\'\\'")

    filled = template.replace("__PARAMS_JSON__", params_json_safe)
    output_path.write_text(filled, encoding="utf-8")

    print(f"  [kaggle] Baked params into run_acestep.py ✓")
    print(f"  [kaggle] Title: {title}")
    print(f"  [kaggle] Lyrics preview: {lyrics[:100]}")


def trigger_kernel(username: str, kaggle_dir: Path):
    """Push kernel (run_acestep.py now contains baked-in params) with T4 GPU."""
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
    """Full pipeline: bake params into script → push → wait → download."""
    _setup_kaggle_credentials(kaggle_username, kaggle_key)

    kaggle_dir = Path(__file__).parent.parent / "kaggle"
    kernel_slug = f"{kaggle_username}/ace-step-music-generator"

    bake_params_into_script(kaggle_dir, lyrics, style, title, duration)
    trigger_kernel(kaggle_username, kaggle_dir)
    wait_for_kernel(kernel_slug, timeout_min=25)
    return download_output(kernel_slug)
