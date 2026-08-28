#!/usr/bin/env python3
"""
hindi_song_pipeline.py — Weekly Hindi Romantic Song Video + Short
Reuses the exact same working infrastructure as suno_pipeline.py:
  - Same Kaggle account (kaggle/ folder, run_acestep.py)
  - Same ACE-Step model on T4 GPU
  - Same YouTube channel
Only difference: Hindi (Romanized) lyrics instead of English.
"""
import os, random, subprocess, sys, tempfile
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "src"))
from image_gen         import generate_images
from lyrics_overlay    import add_lyrics
from lyrics_writer_hindi import generate_weekly_lyrics_hindi
from seo_gen            import generate_seo
from shorts_maker       import make_short_from_video, make_shorts_metadata
from music_gen          import generate_music
from kaggle_music_gen   import generate_song_kaggle
from video_assembly     import create_video
from thumbnail_gen      import create_thumbnail
from youtube_upload     import upload_to_youtube

SONGS_DIR = Path(__file__).parent / "songs_hindi"
DURATION  = 180

BG_PROMPTS = [
    "romantic indian couple holding hands at golden sunset, cinematic warm glow",
    "bollywood style couple dancing in traditional attire, colorful festive lights",
    "indian couple on rooftop under stars, city lights below, romantic night",
    "couple under blooming tree, petals falling, dreamy indian spring light",
    "man surprising woman with roses in indian garden, romantic golden evening",
    "indian couple sharing umbrella in monsoon rain, warm street lights",
    "silhouette of indian couple embracing at sunset, dramatic orange sky",
    "couple sitting by lake at twilight, diyas floating on water reflection",
    "woman in red lehenga and man dancing at indian wedding, fairy lights",
    "couple on boat in misty river at dawn, indian mountains behind them",
    "close up of two hands with mehendi intertwined, golden bokeh background",
    "indian couple watching stars lying on grass, peaceful romantic moment",
    "couple in mustard flower field at sunset, golden hour, joyful",
    "first dance at indian wedding with sparklers and fairy lights",
]

MUSIC_PROMPTS = [
    "bollywood romantic piano ballad slow emotional",
    "soft hindi violin and piano love theme",
    "gentle hindi acoustic guitar ballad sitar",
    "hindi orchestral love theme strings tabla",
    "slow hindi piano romantic ballad emotional",
]


def probe_duration(path):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","default=noprint_wrappers=1:nokey=1",path],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 180)


def get_saved_song():
    songs = sorted(SONGS_DIR.glob("*.mp3")) if SONGS_DIR.exists() else []
    if not songs: return None, None
    idx = datetime.utcnow().timetuple().tm_yday % len(songs)
    s   = songs[idx]
    return str(s), s.stem.replace("_"," ").replace("-"," ").title()


def run():
    HF_TOKEN            = os.environ.get("HF_TOKEN","")
    YOUTUBE_CREDENTIALS = os.environ.get("YOUTUBE_CREDENTIALS")
    KAGGLE_USERNAME     = os.environ.get("KAGGLE_USERNAME","")
    KAGGLE_KEY          = os.environ.get("KAGGLE_KEY","")

    if not HF_TOKEN:            raise EnvironmentError("HF_TOKEN not set")
    if not YOUTUBE_CREDENTIALS: raise EnvironmentError("YOUTUBE_CREDENTIALS not set")

    print(f"\n{'='*60}")
    print(f"  Pipeline : Hindi Romantic Song Video + Short (Weekly)")
    if KAGGLE_USERNAME and KAGGLE_KEY:
        print(f"  Music    : Kaggle GPU → ACE-Step real Hindi vocals ★★★★★")
    else:
        print(f"  Music    : music_gen.py instrumental (add KAGGLE creds for vocals)")
    print(f"{'='*60}\n")

    with tempfile.TemporaryDirectory(prefix="hindi_") as tmp:
        tmp = Path(tmp); song_mp3 = None

        song       = generate_weekly_lyrics_hindi()
        title      = song["title"]
        style_used = song.get("style", "bollywood romantic ballad, female vocals")
        lyrics_text = song["prompt"]

        # ── 1. Kaggle GPU → ACE-Step (real Hindi vocals) ──────────────────────
        if KAGGLE_USERNAME and KAGGLE_KEY and not song_mp3:
            print("🎵  Generating Hindi song via Kaggle GPU + ACE-Step ...")
            try:
                data = generate_song_kaggle(
                    lyrics=lyrics_text, style=style_used, title=title,
                    kaggle_username=KAGGLE_USERNAME, kaggle_key=KAGGLE_KEY,
                    duration=DURATION,
                )
                p = tmp/"kaggle_song.mp3"; p.write_bytes(data)
                song_mp3 = str(p)
                print(f"  → Real Hindi AI vocals generated ✓")
            except Exception as e:
                print(f"  ⚠️  Kaggle failed: {str(e)[:200]}")

        # ── 2. Saved Hindi songs folder ────────────────────────────────────────
        if not song_mp3:
            saved, saved_title = get_saved_song()
            if saved:
                song_mp3 = saved; title = saved_title
                print(f"🎵  Using saved Hindi song: {title}")

        # ── 3. music_gen.py instrumental fallback ──────────────────────────────
        if not song_mp3:
            print("🎵  Generating instrumental via music_gen.py ...")
            music_prompt = random.choice(MUSIC_PROMPTS)
            audio_bytes  = generate_music(music_prompt, HF_TOKEN, duration_sec=DURATION)
            raw = tmp/"music_raw.audio"; raw.write_bytes(audio_bytes)
            mp3 = str(tmp/"music.mp3")
            subprocess.run(["ffmpeg","-y","-i",str(raw),
                           "-codec:a","libmp3lame","-qscale:a","2",mp3],
                          check=True, capture_output=True)
            song_mp3 = mp3
            print(f"  → Instrumental generated ✓")

        # ── Loop if needed ───────────────────────────────────────────────────
        dur = probe_duration(song_mp3)
        if dur < DURATION-10:
            looped = str(tmp/"looped.mp3")
            subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i",song_mp3,
                           "-t",str(DURATION),"-c","copy",looped],
                          check=True, capture_output=True)
            song_mp3 = looped
        dur = min(dur, DURATION)
        n_images = min(16, max(8, int(dur/15)))

        # ── Images ───────────────────────────────────────────────────────────
        print(f"\n🖼️   Generating {n_images} romantic images ...")
        prompts  = [random.choice(BG_PROMPTS) for _ in range(n_images)]
        raw_imgs = generate_images(prompts, HF_TOKEN, vertical=False)

        image_paths = []
        for i, img in enumerate(raw_imgs):
            frame = add_lyrics(img, [title], "verse", "")
            p = tmp/f"frame_{i:02d}.jpg"; p.write_bytes(frame)
            image_paths.append(str(p))

        # ── SEO metadata (Hindi-specific tags) ────────────────────────────────
        print("\n📝  Generating SEO metadata ...")
        meta = generate_seo(title, "romantic songs", style_used)
        # Add Hindi-specific tags on top of the base SEO
        meta["tags"] = (["hindi song","bollywood song","hindi love song",
                         "romantic hindi song","hinglish song"] + meta["tags"])[:15]
        meta["title"] = f"{title} 🎵 Hindi Romantic Song 🌹"[:100]
        print(f"  → {meta['title']}")

        # ── Thumbnail + video ─────────────────────────────────────────────────
        thumb = str(tmp/"thumbnail.jpg")
        create_thumbnail(raw_imgs[0], meta["title"], thumb)
        video = str(tmp/"output.mp4")
        create_video(song_mp3, image_paths, video, vertical=False)

        # ── Short ────────────────────────────────────────────────────────────
        print("\n📱  Creating Short ...")
        short_video = str(tmp/"short.mp4")
        make_short_from_video(video, short_video, duration=55, start_offset=15)
        short_meta  = make_shorts_metadata(meta["title"], meta["tags"])

        # ── Upload ────────────────────────────────────────────────────────────
        print("\n📤  Uploading main video ...")
        vid = upload_to_youtube(video_path=video, thumbnail_path=thumb,
            title=meta["title"], description=meta["description"],
            tags=meta["tags"], credentials_json=YOUTUBE_CREDENTIALS)
        print(f"  → https://youtu.be/{vid}")

        print("\n📱  Uploading Short ...")
        short_id = upload_to_youtube(video_path=short_video, thumbnail_path=thumb,
            title=short_meta["title"], description=short_meta["description"],
            tags=short_meta["tags"], credentials_json=YOUTUBE_CREDENTIALS)
        print(f"  → https://youtu.be/{short_id}")

        print(f"\n🎉  Both live! Main: https://youtu.be/{vid} | Short: https://youtu.be/{short_id}")
        return vid


if __name__=="__main__":
    run()
