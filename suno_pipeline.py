#!/usr/bin/env python3
"""
suno_pipeline.py — Weekly Romantic Song Video + Short
Music priority:
  1. YuE (open-source, free HuggingFace Space) — REAL vocals, no cost ever
  2. songs/ folder (manual Suno uploads, backup)
  3. Local synthesis (instrumental, always works)
"""
import os, random, subprocess, sys, tempfile
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "src"))
from image_gen      import generate_images
from lyrics_overlay import add_lyrics
from lyrics_writer  import generate_weekly_lyrics
from seo_gen        import generate_seo
from shorts_maker   import make_short_from_video, make_shorts_metadata
from yue_music_gen  import generate_song_yue, build_yue_lyrics
from video_assembly import create_video
from thumbnail_gen  import create_thumbnail
from youtube_upload import upload_to_youtube

SONGS_DIR = Path(__file__).parent / "songs"
DURATION  = 210

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
    "couple in flower field at sunset, golden hour, romantic and joyful",
    "first dance at wedding with sparklers and fairy lights around them",
]


def probe_duration(path):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","default=noprint_wrappers=1:nokey=1",path],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 180)


def get_saved_song():
    songs = sorted(SONGS_DIR.glob("*.mp3"))
    if not songs: return None, None
    idx = datetime.utcnow().timetuple().tm_yday % len(songs)
    s   = songs[idx]
    return str(s), s.stem.replace("_"," ").replace("-"," ").title()


def make_local(tmp, duration):
    import numpy as np, scipy.io.wavfile as wf, io, math
    SR = 44100; n = int(SR*duration)
    audio = np.zeros(n, np.float32)
    t_arr = np.linspace(0, duration, n, dtype=np.float32)
    for freq, amp in [(130,.15),(196,.12),(261,.10),(330,.08)]:
        mod = .7+.3*np.sin(2*math.pi*.06*t_arr)
        audio += amp*mod*np.sin(2*math.pi*freq*t_arr)
    noise = np.random.randn(n).astype(np.float32)*.015
    for k in range(1,n): noise[k]=.94*noise[k-1]+.06*noise[k]
    audio += noise
    peak = np.max(np.abs(audio))
    if peak>0: audio=audio/peak*.80
    fade = min(int(SR*3),n//5)
    audio[:fade]*=np.linspace(0,1,fade); audio[-fade:]*=np.linspace(1,0,fade)
    buf=io.BytesIO(); wf.write(buf,SR,(audio*32767).astype(np.int16))
    raw=tmp/"local.wav"; raw.write_bytes(buf.getvalue())
    mp3=str(tmp/"music.mp3")
    subprocess.run(["ffmpeg","-y","-i",str(raw),"-codec:a","libmp3lame","-qscale:a","2",mp3],
                   check=True,capture_output=True)
    return mp3


def run():
    HF_TOKEN            = os.environ.get("HF_TOKEN","")
    YOUTUBE_CREDENTIALS = os.environ.get("YOUTUBE_CREDENTIALS")

    if not HF_TOKEN:            raise EnvironmentError("HF_TOKEN not set")
    if not YOUTUBE_CREDENTIALS: raise EnvironmentError("YOUTUBE_CREDENTIALS not set")

    print(f"\n{'='*60}")
    print(f"  Pipeline : Romantic Song Video + Short (Weekly)")
    print(f"  Music    : YuE (open-source, free) ★★★★★")
    print(f"{'='*60}\n")

    with tempfile.TemporaryDirectory(prefix="romantic_") as tmp:
        tmp=Path(tmp); song_mp3=None; title="Beautiful Love Song"; style_used=""

        # ── 1. YuE — open-source, genuinely free ─────────────────────────────
        print("🎵  Generating via YuE (open-source, free) ...")
        try:
            song = generate_weekly_lyrics()
            title = song["title"]
            style_used = song.get("style", "romantic pop, female vocal, emotional")
            yue_lyrics = build_yue_lyrics(song.get("sections", [
                {"type":"verse", "lines": song["prompt"].split("\n")[:4]},
                {"type":"chorus","lines": song["prompt"].split("\n")[4:8]},
            ])) if "sections" in song else song["prompt"]

            data = generate_song_yue(yue_lyrics, style_used, HF_TOKEN, DURATION)
            p = tmp/"yue_song.mp3"
            p.write_bytes(data)
            song_mp3 = str(p)
            print(f"  → YuE generated: '{title}' ✓")
        except Exception as e:
            print(f"  ⚠️  YuE failed: {str(e)[:200]}")

        # ── 2. Saved songs folder ─────────────────────────────────────────────
        if not song_mp3:
            saved, saved_title = get_saved_song()
            if saved:
                song_mp3 = saved; title = saved_title
                print(f"🎵  Using saved song: {title}")

        # ── 3. Local synthesis ────────────────────────────────────────────────
        if not song_mp3:
            print("🎵  Synthesising locally ...")
            song_mp3 = make_local(tmp, DURATION)

        # ── Loop short songs to fill duration ───────────────────────────────
        dur = probe_duration(song_mp3)
        if dur < DURATION-10:
            looped=str(tmp/"looped.mp3")
            subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i",song_mp3,
                           "-t",str(DURATION),"-c","copy",looped],
                          check=True,capture_output=True)
            song_mp3=looped
        dur=min(dur,DURATION); n_images=min(16,max(8,int(dur/15)))

        # ── Images ───────────────────────────────────────────────────────────
        print(f"\n🖼️   Generating {n_images} romantic images ...")
        prompts=[random.choice(BG_PROMPTS) for _ in range(n_images)]
        raw_imgs=generate_images(prompts,HF_TOKEN,vertical=False)

        image_paths=[]
        for i,img in enumerate(raw_imgs):
            frame=add_lyrics(img,[title],"verse","")
            p=tmp/f"frame_{i:02d}.jpg"; p.write_bytes(frame)
            image_paths.append(str(p))

        # ── SEO metadata ─────────────────────────────────────────────────────
        print("\n📝  Generating SEO-optimized metadata ...")
        meta = generate_seo(title, "romantic songs", style_used)
        print(f"  → {meta['title']}")

        # ── Thumbnail + video ────────────────────────────────────────────────
        thumb=str(tmp/"thumbnail.jpg")
        create_thumbnail(raw_imgs[0],meta["title"],thumb)
        video=str(tmp/"output.mp4")
        create_video(song_mp3,image_paths,video,vertical=False)

        # ── Shorts ────────────────────────────────────────────────────────────
        print("\n📱  Creating Shorts version ...")
        short_video = str(tmp/"short.mp4")
        make_short_from_video(video, short_video, duration=55, start_offset=15)
        short_meta  = make_shorts_metadata(meta["title"], meta["tags"])

        # ── Upload both ───────────────────────────────────────────────────────
        print("\n📤  Uploading main video ...")
        vid=upload_to_youtube(video_path=video,thumbnail_path=thumb,
            title=meta["title"],description=meta["description"],
            tags=meta["tags"],credentials_json=YOUTUBE_CREDENTIALS)
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
