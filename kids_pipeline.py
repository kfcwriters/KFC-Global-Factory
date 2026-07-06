#!/usr/bin/env python3
"""
kids_pipeline.py
================
Fully automated kids cartoon channel pipeline.
Generates: story/rhyme/educational/fairy tale content
Narrates with Microsoft neural voice (Edge TTS)
Creates cartoon-style images via Pollinations.ai
Mixes narration over happy kids background music
Uploads to YouTube 3x per week

Schedule:
  Monday    9:00 AM UTC = 2:30 PM IST
  Wednesday 9:00 AM UTC = 2:30 PM IST
  Friday    9:00 AM UTC = 2:30 PM IST
"""
import os, random, subprocess, sys, tempfile, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from kids_story_gen import get_content_for_week
from kids_voice_gen import generate_narration
from image_gen      import generate_images
from video_assembly import create_video
from thumbnail_gen  import create_thumbnail
from youtube_upload import upload_to_youtube

import numpy as np
import scipy.io.wavfile as wf
import io, math

SR = 44100

# Upload slot: 0=Monday, 1=Wednesday, 2=Friday
UPLOAD_SLOTS = {0: 0, 2: 1, 4: 2}   # weekday → slot number


def get_upload_slot() -> int:
    from datetime import datetime
    return UPLOAD_SLOTS.get(datetime.utcnow().weekday(), 0)


def make_kids_music(style: str, duration: int, tmp: Path) -> str:
    """Generate happy background music for kids content."""
    print(f"  [music] Generating kids background music ({duration}s) ...")
    n     = int(SR * duration)
    t_arr = np.linspace(0, duration, n, dtype=np.float32)
    audio = np.zeros(n, np.float32)

    # Detect style
    p = style.lower()
    if "lullaby" in p or "bedtime" in p or "peaceful" in p:
        # Soft lullaby — gentle sine waves
        for freq, amp in [(261,0.12),(330,0.09),(392,0.07),(523,0.05)]:
            mod    = 0.6 + 0.4*np.sin(2*math.pi*0.05*t_arr)
            audio += amp * mod * np.sin(2*math.pi*freq*t_arr)
    elif "magical" in p or "fairy" in p or "enchanted" in p:
        # Magical — sparkling high notes
        for freq, amp in [(523,0.10),(659,0.08),(784,0.07),(1047,0.05)]:
            mod    = 0.5 + 0.5*np.sin(2*math.pi*0.08*t_arr)
            audio += amp * mod * np.sin(2*math.pi*freq*t_arr)
    else:
        # Upbeat happy — cheerful notes
        for freq, amp in [(392,0.12),(494,0.10),(523,0.09),(659,0.07)]:
            mod    = 0.7 + 0.3*np.sin(2*math.pi*0.12*t_arr)
            audio += amp * mod * np.sin(2*math.pi*freq*t_arr)

    # Soft noise
    noise = np.random.randn(n).astype(np.float32)*0.008
    for k in range(1,n): noise[k]=0.95*noise[k-1]+0.05*noise[k]
    audio += noise

    peak = np.max(np.abs(audio))
    if peak > 0: audio = audio/peak*0.70
    fade = min(int(SR*2), n//5)
    audio[:fade]  *= np.linspace(0,1,fade)
    audio[-fade:] *= np.linspace(1,0,fade)

    raw = tmp / "kids_music.wav"
    wf.write(str(raw), SR, (audio*32767).astype(np.int16))
    mp3 = str(tmp / "kids_music.mp3")
    subprocess.run(["ffmpeg","-y","-i",str(raw),
                   "-codec:a","libmp3lame","-qscale:a","2",mp3],
                  check=True, capture_output=True)
    print(f"  [music] Kids music ready ✓")
    return mp3


def mix_narration_music(narration_bytes: bytes, music_mp3: str,
                        out_mp3: str, duration: int):
    """Mix narration (loud) over background music (soft)."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        nar_tmp = f.name
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        looped  = f.name

    try:
        open(nar_tmp,"wb").write(narration_bytes)

        # Loop narration to fill duration
        subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i",nar_tmp,
                       "-t",str(duration), looped],
                      check=True, capture_output=True)

        # Mix: narration loud (3.0), music soft (0.25)
        subprocess.run([
            "ffmpeg","-y",
            "-i",looped, "-i",music_mp3,
            "-filter_complex",
            "[0:a]volume=3.0[v];"
            "[1:a]volume=0.25[m];"
            "[v][m]amix=inputs=2:duration=shortest",
            "-t",str(duration),
            "-c:a","libmp3lame","-q:a","2",
            out_mp3
        ], check=True, capture_output=True)
        print(f"  [mix] Audio mixed ✓")
    finally:
        for p in [nar_tmp, looped]:
            if os.path.exists(p): os.unlink(p)


def make_metadata(content: dict) -> dict:
    """Build YouTube metadata for kids content."""
    type_tags = {
        "bedtime_story" : ["bedtime story","kids story","children story",
                           "story for kids","moral story","animated story"],
        "nursery_rhyme" : ["nursery rhyme","kids songs","children songs",
                           "rhymes for kids","baby songs","toddler songs"],
        "educational"   : ["educational for kids","learn for kids",
                           "kids learning","preschool learning","kids education"],
        "fairy_tale"    : ["fairy tale","kids fairy tale","children fairy tale",
                           "magical story","bedtime fairy tale","animated fairy tale"],
    }

    emoji = {"bedtime_story":"🌙","nursery_rhyme":"🎵",
             "educational":"📚","fairy_tale":"✨"}[content["type"]]

    title = f"{emoji} {content['title']} | Kids Cartoon Story"[:100]

    tags = (type_tags.get(content["type"], []) +
            ["kids cartoon","children video","kids youtube",
             "cartoon for kids","kids stories","bedtime stories",
             "nursery rhymes","educational kids"])[:15]

    desc = (
        f"{title}\n\n"
        f"🎬 {content['type'].replace('_',' ').title()} for Children\n\n"
        f"Perfect for:\n"
        f"  • Bedtime routine\n"
        f"  • Learning and education\n"
        f"  • Fun entertainment for kids aged 2-8\n\n"
        f"🔔 Subscribe for new kids videos 3 times every week!\n\n"
        f"#kidscartoon #kidsstories #kidslearning #childrenstories "
        f"#kidssongs #bedtimestories #nurseryryhmes"
    )

    return {"title": title, "tags": tags, "description": desc}


def run():
    HF_TOKEN            = os.environ.get("HF_TOKEN","")
    YOUTUBE_CREDENTIALS = os.environ.get("YOUTUBE_CREDENTIALS")
    UPLOAD_NUM          = int(os.environ.get("UPLOAD_NUM","0"))

    if not HF_TOKEN:            raise EnvironmentError("HF_TOKEN not set")
    if not YOUTUBE_CREDENTIALS: raise EnvironmentError("YOUTUBE_CREDENTIALS not set")

    print(f"\n{'='*60}")
    print(f"  Pipeline  : Kids Cartoon Channel")
    print(f"  Upload    : #{UPLOAD_NUM+1} of week")
    print(f"{'='*60}\n")

    # Step 1: Generate content
    print("📖  Step 1/6 — Generating kids content ...")
    content = get_content_for_week(UPLOAD_NUM)
    print(f"  → Type : {content['type']}")
    print(f"  → Title: {content['title']}")
    print(f"  → Lines: {len(content['script'])}")

    with tempfile.TemporaryDirectory(prefix="kids_") as tmp:
        tmp = Path(tmp)

        # Step 2: Narration voice
        print("\n🗣️   Step 2/6 — Generating narration voice ...")
        nar_bytes = generate_narration(content["script"], content["type"])

        # Step 3: Background music
        print("\n🎵  Step 3/6 — Generating background music ...")
        # Estimate duration from script length
        words    = sum(len(l.split()) for l in content["script"])
        duration = max(60, min(300, words * 2 + 30))  # 1-5 minutes
        music_mp3 = make_kids_music(content["music"], duration, tmp)

        # Step 4: Mix audio
        print("\n🎚️   Step 4/6 — Mixing narration + music ...")
        mixed_mp3 = str(tmp / "mixed.mp3")
        mix_narration_music(nar_bytes, music_mp3, mixed_mp3, duration)

        # Step 5: Generate cartoon images
        print(f"\n🎨  Step 5/6 — Generating {len(content['prompts'])} cartoon images ...")
        # Add cartoon style to all prompts
        cartoon_prompts = [
            f"{p}, bright vivid colors, safe for children, no scary elements"
            for p in content["prompts"]
        ]
        raw_imgs     = generate_images(cartoon_prompts, HF_TOKEN, vertical=False)
        image_paths  = []
        for i, img in enumerate(raw_imgs):
            p = tmp / f"frame_{i:02d}.jpg"
            p.write_bytes(img)
            image_paths.append(str(p))

        # Step 6: Metadata + thumbnail + video + upload
        print("\n📤  Step 6/6 — Assembling video + uploading ...")
        meta  = make_metadata(content)
        thumb = str(tmp / "thumbnail.jpg")
        create_thumbnail(raw_imgs[0], meta["title"], thumb)

        video = str(tmp / "kids_output.mp4")
        create_video(mixed_mp3, image_paths, video, vertical=False)

        vid = upload_to_youtube(
            video_path=video, thumbnail_path=thumb,
            title=meta["title"], description=meta["description"],
            tags=meta["tags"], credentials_json=YOUTUBE_CREDENTIALS
        )
        print(f"\n🎉  Live! https://youtu.be/{vid}")
        return vid


if __name__ == "__main__":
    run()
