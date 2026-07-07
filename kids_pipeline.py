#!/usr/bin/env python3
"""
kids_pipeline.py
================
Fully automated kids cartoon channel pipeline.
Uses Python-drawn animated cartoon characters (bunny/bear/cat)
with bouncing motion, speech bubbles, lip-sync effect.
Uploads 3x per week — Mon/Wed/Fri at 2:30 PM IST.
"""
import os, random, subprocess, sys, tempfile, math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from kids_story_gen import get_content_for_week
from kids_voice_gen import generate_narration
from cartoon_gen    import create_cartoon_video
from thumbnail_gen  import create_thumbnail
from youtube_upload import upload_to_youtube

import numpy as np
import scipy.io.wavfile as wf
import io

SR = 44100


def make_kids_music(style: str, duration: int, tmp: Path) -> str:
    """Generate happy background music for kids content."""
    print(f"  [music] Generating background music ({duration}s) ...")
    n     = int(SR * duration)
    t_arr = np.linspace(0, duration, n, dtype=np.float32)
    audio = np.zeros(n, np.float32)
    import math as m

    p = style.lower()
    if "lullaby" in p or "bedtime" in p or "peaceful" in p:
        freqs = [(261,0.10),(330,0.08),(392,0.06),(523,0.04)]
        mod_f = 0.05
    elif "magical" in p or "fairy" in p:
        freqs = [(523,0.09),(659,0.07),(784,0.06),(1047,0.04)]
        mod_f = 0.08
    else:
        freqs = [(392,0.10),(494,0.09),(523,0.08),(659,0.06)]
        mod_f = 0.12

    for freq, amp in freqs:
        mod    = 0.6 + 0.4*np.sin(2*m.pi*mod_f*t_arr)
        audio += amp * mod * np.sin(2*m.pi*freq*t_arr)

    noise = np.random.randn(n).astype(np.float32)*0.006
    for k in range(1,n): noise[k]=0.95*noise[k-1]+0.05*noise[k]
    audio += noise

    peak = np.max(np.abs(audio))
    if peak > 0: audio = audio/peak*0.55   # keep music soft
    fade = min(int(SR*2), n//5)
    audio[:fade]  *= np.linspace(0,1,fade)
    audio[-fade:] *= np.linspace(1,0,fade)

    raw = tmp/"kids_music.wav"
    wf.write(str(raw), SR, (audio*32767).astype(np.int16))
    mp3 = str(tmp/"kids_music.mp3")
    subprocess.run(["ffmpeg","-y","-i",str(raw),
                   "-codec:a","libmp3lame","-qscale:a","2",mp3],
                  check=True, capture_output=True)
    return mp3


def mix_narration_music(narration_bytes: bytes, music_mp3: str,
                        out_mp3: str, duration: int):
    """Mix narration (very loud) over background music (very soft)."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        nar_tmp = f.name
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        looped  = f.name
    try:
        open(nar_tmp,"wb").write(narration_bytes)
        subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i",nar_tmp,
                       "-t",str(duration),looped],
                      check=True, capture_output=True)
        subprocess.run([
            "ffmpeg","-y",
            "-i",looped,"-i",music_mp3,
            "-filter_complex",
            "[0:a]volume=4.0[v];"
            "[1:a]volume=0.20[m];"
            "[v][m]amix=inputs=2:duration=shortest",
            "-t",str(duration),
            "-c:a","libmp3lame","-q:a","2",
            out_mp3
        ], check=True, capture_output=True)
        print(f"  [mix] Audio ready ✓")
    finally:
        for p in [nar_tmp, looped]:
            if os.path.exists(p): os.unlink(p)


def make_thumbnail(content_type: str, title: str, tmp: Path) -> str:
    """Create a colorful thumbnail for the kids video."""
    from PIL import Image, ImageDraw, ImageFont
    from src.cartoon_gen import PALETTES, draw_cartoon_scene
    import random

    palette = random.choice(PALETTES)
    img     = draw_cartoon_scene(palette,
                                 random.choice(["bunny","bear","cat"]),
                                 False, 0, "")

    draw     = ImageDraw.Draw(img)
    font_big = None
    for fp in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        if Path(fp).exists():
            try:
                font_big = ImageFont.truetype(fp, 52)
                break
            except Exception:
                pass
    if not font_big:
        font_big = ImageFont.load_default()

    # Title banner at bottom
    draw.rectangle([0, H*3//4, W, H], fill=(255,220,0))
    draw.rectangle([0, H*3//4, W, H*3//4+6], fill=(255,100,0))

    clean = title[:40]
    bbox  = draw.textbbox((0,0), clean, font=font_big)
    tx    = (W - (bbox[2]-bbox[0])) // 2
    ty    = H*3//4 + 15
    draw.text((tx+2, ty+2), clean, font=font_big, fill=(200,0,0))
    draw.text((tx,   ty),   clean, font=font_big, fill=(50,50,50))

    thumb = str(tmp / "thumbnail.jpg")
    img.save(thumb, quality=95)
    return thumb


def make_metadata(content: dict) -> dict:
    type_tags = {
        "bedtime_story" : ["bedtime story","kids story","moral story",
                           "animated story for kids","children bedtime"],
        "nursery_rhyme" : ["nursery rhyme","kids songs","rhymes for kids",
                           "baby songs","toddler songs","kids rhymes"],
        "educational"   : ["educational for kids","learn for kids",
                           "kids learning","preschool","kids education"],
        "fairy_tale"    : ["fairy tale kids","animated fairy tale",
                           "magical story","kids fairy tale","bedtime fairy tale"],
    }
    emoji = {"bedtime_story":"🌙","nursery_rhyme":"🎵",
             "educational":"📚","fairy_tale":"✨"}[content["type"]]
    title = f"{emoji} {content['title']} | Cartoon for Kids"[:100]
    tags  = (type_tags.get(content["type"],[]) +
             ["kids cartoon","cartoon for kids","children cartoon",
              "animated cartoon","kids youtube","cartoon story"])[:15]
    desc  = (
        f"{title}\n\n"
        f"🎬 Fun cartoon {content['type'].replace('_',' ')} for children!\n\n"
        f"Perfect for kids aged 2-8 years.\n"
        f"Educational, fun and entertaining!\n\n"
        f"🔔 Subscribe for new cartoons 3 times every week!\n\n"
        f"#kidscartoon #cartoon #kidslearning #childrenstories"
    )
    return {"title":title, "tags":tags, "description":desc}


H = 720   # module-level for thumbnail function


def run():
    HF_TOKEN            = os.environ.get("HF_TOKEN","")
    YOUTUBE_CREDENTIALS = os.environ.get("YOUTUBE_CREDENTIALS")
    UPLOAD_NUM          = int(os.environ.get("UPLOAD_NUM","0"))

    if not YOUTUBE_CREDENTIALS:
        raise EnvironmentError("YOUTUBE_CREDENTIALS not set")

    print(f"\n{'='*60}")
    print(f"  Pipeline  : Kids Cartoon Channel (Animated)")
    print(f"  Upload    : #{UPLOAD_NUM+1} of week")
    print(f"{'='*60}\n")

    # Step 1: Generate content
    print("📖  Step 1/5 — Generating kids content ...")
    content = get_content_for_week(UPLOAD_NUM)
    print(f"  → Type : {content['type']}")
    print(f"  → Title: {content['title']}")

    with tempfile.TemporaryDirectory(prefix="kids_") as tmp:
        tmp = Path(tmp)

        # Step 2: Narration voice
        print("\n🗣️   Step 2/5 — Generating narration voice ...")
        nar_bytes = generate_narration(content["script"], content["type"])

        # Step 3: Background music + mix
        print("\n🎵  Step 3/5 — Background music + mix ...")
        words    = sum(len(l.split()) for l in content["script"])
        duration = max(60, min(300, words * 2 + 30))
        music    = make_kids_music(content["music"], duration, tmp)
        mixed    = str(tmp/"mixed.mp3")
        mix_narration_music(nar_bytes, music, mixed, duration)

        # Step 4: Animated cartoon video
        print("\n🎨  Step 4/5 — Rendering animated cartoon ...")
        video = str(tmp/"cartoon.mp4")
        create_cartoon_video(
            script       = content["script"],
            audio_path   = mixed,
            output_path  = video,
            content_type = content["type"],
        )

        # Step 5: Thumbnail + upload
        print("\n📤  Step 5/5 — Thumbnail + upload ...")
        thumb = make_thumbnail(content["type"], content["title"], tmp)
        meta  = make_metadata(content)

        vid = upload_to_youtube(
            video_path       = video,
            thumbnail_path   = thumb,
            title            = meta["title"],
            description      = meta["description"],
            tags             = meta["tags"],
            credentials_json = YOUTUBE_CREDENTIALS,
        )
        print(f"\n🎉  Live! https://youtu.be/{vid}")
        return vid


if __name__ == "__main__":
    run()
