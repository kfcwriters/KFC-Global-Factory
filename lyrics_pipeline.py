#!/usr/bin/env python3
"""
lyrics_pipeline.py — Hindi+English Lyric Video with AI Vocals
All vocal logic is INLINE here — no external vocals_gen.py dependency.
"""
import io, os, random, subprocess, sys, tempfile, time, requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from lyrics_gen     import generate_lyrics
from lyrics_overlay import add_lyrics
from image_gen      import generate_images
from music_gen      import generate_music
from video_assembly import create_video
from metadata_gen   import generate_metadata
from thumbnail_gen  import create_thumbnail
from youtube_upload import upload_to_youtube

DURATION_SEC = 210

BG_PROMPTS = [
    "romantic couple holding hands at golden sunset on beach, cinematic warm glow",
    "couple slow dancing in candlelit room with rose petals, soft bokeh lights",
    "two lovers on rooftop under stars, city lights below, romantic night",
    "couple under cherry blossom tree, pink petals falling, dreamy spring light",
    "man surprising woman with roses in garden, romantic golden evening",
    "couple sharing umbrella in gentle rain, warm street lights reflection",
    "silhouette of couple embracing at sunset on hill, dramatic orange sky",
    "couple sitting by lake at twilight, fairy lights on water reflection",
    "woman in red dress and man dancing at outdoor wedding, fairy lights",
    "couple on boat in misty river at dawn, mountains behind them",
    "close up of two hands intertwined, soft bokeh golden background",
    "couple watching stars lying on grass, milky way above, peaceful romantic",
]

MUSIC_PROMPTS = [
    "soft romantic piano with gentle strings, slow love ballad, Bollywood style",
    "acoustic guitar with sitar, warm romantic evening, Hindi film music style",
    "smooth violin with piano, passionate love theme, cinematic and slow",
    "soft bansuri flute with tabla, romantic Indian classical fusion, soulful",
]


# ── Step A: Generate vocals using espeak-ng (OFFLINE, always works) ──────────

def make_vocals(sections: list, out_wav: str):
    """
    Generates vocal WAV using espeak-ng directly.
    espeak-ng is offline — no internet, no API key, always works on Ubuntu.
    """
    parts = []
    for sec in sections:
        for line in sec.get("lines", []):
            if line.strip():
                parts.append(line)
        parts.append(".")          # short pause between sections

    full_text = " . ".join(parts)
    print(f"  [vocals] espeak-ng generating {len(full_text)} chars of lyrics ...")

    result = subprocess.run(
        ["espeak-ng",
         "-v", "en+f3",    # female voice (more melodic)
         "-s", "105",      # slow speed (dramatic, song-like)
         "-p", "68",       # higher pitch (more musical)
         "-g", "6",        # gap between words (ms)
         full_text,
         "-w", out_wav],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"espeak-ng failed: {result.stderr}")

    size = os.path.getsize(out_wav)
    print(f"  [vocals] espeak-ng WAV: {size//1024} KB ✓")
    return size


# ── Step B: Loop + mix vocals with instrumental ───────────────────────────────

def mix_audio(vocal_wav: str, music_mp3: str, out_mp3: str):
    """
    Step 1: Loop vocals to fill full DURATION_SEC
    Step 2: Simple mix — vocals loud (5.0), music soft (0.20)
    """
    # Step 1: Loop vocals → fill 210 seconds
    looped = out_mp3 + "_looped.wav"
    print(f"  [vocals] looping vocals to {DURATION_SEC}s ...")
    r1 = subprocess.run([
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", vocal_wav,
        "-t", str(DURATION_SEC),
        looped
    ], capture_output=True, text=True)

    if r1.returncode != 0:
        raise RuntimeError(f"Loop failed: {r1.stderr[-300:]}")

    looped_size = os.path.getsize(looped) // 1024
    print(f"  [vocals] looped vocals: {looped_size} KB ✓")

    # Step 2: Mix looped vocals + instrumental
    print(f"  [vocals] mixing vocals (vol 5.0) + music (vol 0.20) ...")
    r2 = subprocess.run([
        "ffmpeg", "-y",
        "-i", looped,        # vocals (already 210s)
        "-i", music_mp3,     # instrumental
        "-filter_complex",
        "[0:a]volume=5.0[v];"
        "[1:a]volume=0.20[m];"
        "[v][m]amix=inputs=2:duration=shortest",
        "-t", str(DURATION_SEC),
        "-c:a", "libmp3lame", "-q:a", "2",
        out_mp3
    ], capture_output=True, text=True)

    if r2.returncode != 0:
        raise RuntimeError(f"Mix failed: {r2.stderr[-300:]}")

    # Cleanup looped file
    if os.path.exists(looped):
        os.unlink(looped)

    mixed_size = os.path.getsize(out_mp3) // 1024
    print(f"  [vocals] final mixed audio: {mixed_size} KB ✓")

    # Verify mixed duration
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", out_mp3],
        capture_output=True, text=True
    )
    dur = float(probe.stdout.strip() or 0)
    print(f"  [vocals] mixed duration: {dur:.1f}s ✓")


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run():
    HF_TOKEN            = os.environ.get("HF_TOKEN", "")
    ANTHROPIC_API_KEY   = os.environ.get("ANTHROPIC_API_KEY")
    YOUTUBE_CREDENTIALS = os.environ.get("YOUTUBE_CREDENTIALS")

    if not HF_TOKEN:        raise EnvironmentError("HF_TOKEN not set")
    if not YOUTUBE_CREDENTIALS: raise EnvironmentError("YOUTUBE_CREDENTIALS not set")

    print(f"\n{'='*60}")
    print(f"  Pipeline : Hindi+English Lyric Video with AI Vocals")
    print(f"  Duration : {DURATION_SEC}s")
    print(f"{'='*60}\n")

    # Step 1: Lyrics
    print("📝  Step 1/6 — Generating bilingual lyrics ...")
    song     = generate_lyrics(ANTHROPIC_API_KEY)
    sections = song["sections"]
    print(f"  → Song: {song['title']} ({len(sections)} sections)")

    with tempfile.TemporaryDirectory(prefix="lyrics_") as tmp:
        tmp = Path(tmp)

        # Step 2: AI Vocals (espeak-ng — offline, guaranteed)
        print("\n🎤  Step 2/6 — Generating AI vocals (espeak-ng) ...")
        vocal_wav = str(tmp / "vocals.wav")
        make_vocals(sections, vocal_wav)

        # Step 3: Instrumental music
        print("\n🎵  Step 3/6 — Composing instrumental music ...")
        music_prompt = random.choice(MUSIC_PROMPTS)
        audio_bytes  = generate_music(music_prompt, HF_TOKEN, duration_sec=DURATION_SEC)
        music_raw    = tmp / "music_raw.audio"
        music_raw.write_bytes(audio_bytes)

        music_mp3 = str(tmp / "music.mp3")
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(music_raw),
             "-codec:a", "libmp3lame", "-qscale:a", "2", music_mp3],
            check=True, capture_output=True
        )
        print(f"  → Music: {os.path.getsize(music_mp3)//1024} KB ✓")

        # Step 4: Mix vocals + music
        print("\n🎚️   Step 4/6 — Mixing vocals + instrumental ...")
        mixed_mp3 = str(tmp / "mixed.mp3")
        mix_audio(vocal_wav, music_mp3, mixed_mp3)

        # Step 5: Lyric frames (romantic images + lyrics text)
        print(f"\n🖼️   Step 5/6 — Generating {len(sections)} lyric frames ...")
        n       = len(sections)
        bg_list = [random.choice(BG_PROMPTS) for _ in range(n)]
        raw_imgs = generate_images(bg_list, HF_TOKEN, vertical=False)

        image_paths = []
        for i, (sec, img) in enumerate(zip(sections, raw_imgs)):
            frame = add_lyrics(img, sec["lines"][:4],
                               sec.get("type", "verse"), song["title"])
            p = tmp / f"frame_{i:02d}.jpg"
            p.write_bytes(frame)
            image_paths.append(str(p))

        # Step 6: Metadata + thumbnail + video + upload
        print("\n📝  Step 6/6 — Metadata, video, upload ...")
        meta = generate_metadata(
            f"romantic bilingual Hindi English love song — {song['title']}",
            "romantic hindi english songs", ANTHROPIC_API_KEY
        )
        meta["title"] = f"🎵 {song['title']} | Hindi English Song 🌹"[:100]
        meta["tags"]  = (["hindi songs","romantic hindi song","hindi english song",
                          "bollywood romantic","lyric video","ai singer"] +
                          meta.get("tags", []))[:15]
        print(f"  → {meta['title']}")

        thumb = str(tmp / "thumbnail.jpg")
        create_thumbnail(raw_imgs[0], meta["title"], thumb)

        video_path = str(tmp / "lyrics_output.mp4")
        create_video(mixed_mp3, image_paths, video_path, vertical=False)

        print("\n📤  Uploading to YouTube ...")
        vid = upload_to_youtube(
            video_path=video_path, thumbnail_path=thumb,
            title=meta["title"], description=meta["description"],
            tags=meta["tags"], credentials_json=YOUTUBE_CREDENTIALS,
        )
        print(f"\n🎉  Live! https://youtu.be/{vid}")
        return vid


if __name__ == "__main__":
    run()
