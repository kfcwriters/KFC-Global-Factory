#!/usr/bin/env python3
"""
lyrics_pipeline.py — Romantic Lyric Video with AI Vocals
Vocal priority: Edge TTS (Microsoft neural) → gTTS → espeak-ng
"""
import os, random, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from lyrics_gen     import generate_lyrics
from lyrics_overlay import add_lyrics
from vocals_gen     import generate_vocals, mix_vocals_music
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
    "soft romantic piano with gentle strings, slow love ballad",
    "acoustic guitar warm romantic evening, slow and melodic",
    "smooth violin with piano, passionate love theme, cinematic",
    "gentle piano ballad with cello, emotional and tender",
]


def run():
    HF_TOKEN            = os.environ.get("HF_TOKEN", "")
    ANTHROPIC_API_KEY   = os.environ.get("ANTHROPIC_API_KEY")
    YOUTUBE_CREDENTIALS = os.environ.get("YOUTUBE_CREDENTIALS")

    if not HF_TOKEN:            raise EnvironmentError("HF_TOKEN not set")
    if not YOUTUBE_CREDENTIALS: raise EnvironmentError("YOUTUBE_CREDENTIALS not set")

    print(f"\n{'='*60}")
    print(f"  Pipeline : Romantic Lyric Video with AI Vocals")
    print(f"  Duration : {DURATION_SEC}s")
    print(f"{'='*60}\n")

    # Step 1: Lyrics
    print("📝  Step 1/6 — Generating lyrics ...")
    song     = generate_lyrics(ANTHROPIC_API_KEY)
    sections = song["sections"]
    print(f"  → {song['title']} ({len(sections)} sections)")

    with tempfile.TemporaryDirectory(prefix="lyrics_") as tmp:
        tmp = Path(tmp)

        # Step 2: Vocals (Edge TTS → gTTS → espeak)
        print("\n🎤  Step 2/6 — Generating AI vocals ...")
        vocal_bytes, vocal_ext = generate_vocals(sections)

        # Step 3: Instrumental
        print("\n🎵  Step 3/6 — Composing instrumental music ...")
        music_prompt = random.choice(MUSIC_PROMPTS)
        audio_bytes  = generate_music(music_prompt, HF_TOKEN,
                                      duration_sec=DURATION_SEC)
        music_raw = tmp / "music_raw.audio"
        music_raw.write_bytes(audio_bytes)
        music_mp3 = str(tmp / "music.mp3")
        subprocess.run(
            ["ffmpeg","-y","-i",str(music_raw),
             "-codec:a","libmp3lame","-qscale:a","2", music_mp3],
            check=True, capture_output=True)
        print(f"  → {os.path.getsize(music_mp3)//1024} KB ✓")

        # Step 4: Mix vocals + music
        print("\n🎚️   Step 4/6 — Mixing vocals + music ...")
        mixed_mp3 = str(tmp / "mixed.mp3")
        mix_vocals_music(vocal_bytes, vocal_ext, music_mp3,
                         mixed_mp3, DURATION_SEC)

        # Step 5: Lyric frames
        print(f"\n🖼️   Step 5/6 — Generating {len(sections)} lyric frames ...")
        bg_list  = [random.choice(BG_PROMPTS) for _ in range(len(sections))]
        raw_imgs = generate_images(bg_list, HF_TOKEN, vertical=False)
        image_paths = []
        for i, (sec, img) in enumerate(zip(sections, raw_imgs)):
            frame = add_lyrics(img, sec["lines"][:4],
                               sec.get("type","verse"), song["title"])
            p = tmp / f"frame_{i:02d}.jpg"
            p.write_bytes(frame)
            image_paths.append(str(p))

        # Step 6: Metadata + video + upload
        print("\n📤  Step 6/6 — Build video + upload ...")
        meta = generate_metadata(
            f"romantic English love song — {song['title']}",
            "romantic songs", ANTHROPIC_API_KEY)
        meta["title"] = f"🎵 {song['title']} | Romantic Song 🌹"[:100]
        meta["tags"]  = (["romantic song","love song","english romantic",
                          "ballad","lyric video","romantic music",
                          "love ballad"] + meta.get("tags",[]))[:15]
        print(f"  → {meta['title']}")

        thumb = str(tmp / "thumbnail.jpg")
        create_thumbnail(raw_imgs[0], meta["title"], thumb)

        video_path = str(tmp / "lyrics_output.mp4")
        create_video(mixed_mp3, image_paths, video_path, vertical=False)

        print("\n📤  Uploading to YouTube ...")
        vid = upload_to_youtube(
            video_path=video_path, thumbnail_path=thumb,
            title=meta["title"], description=meta["description"],
            tags=meta["tags"], credentials_json=YOUTUBE_CREDENTIALS)
        print(f"\n🎉  Live! https://youtu.be/{vid}")
        return vid


if __name__ == "__main__":
    run()
