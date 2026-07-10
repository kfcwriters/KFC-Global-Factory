#!/usr/bin/env python3
"""
kids_pipeline.py — Professional Kids Cartoon Channel
Uses pawpatrol_engine.py for Paw Patrol style animation.
Uploads Mon/Wed/Fri at 2:30 PM IST.
"""
import os, random, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from kids_story_gen   import get_content_for_week
from kids_voice_gen   import generate_narration
from pawpatrol_engine import create_cartoon_video, get_thumbnail_frame
from youtube_upload   import upload_to_youtube

import numpy as np
import scipy.io.wavfile as wf
import io, math

W, H = 1280, 720
SR   = 44100


def make_kids_music(style: str, duration: int, tmp: Path) -> str:
    print(f"  [music] Generating background music ({duration}s) ...")
    n     = int(SR * duration)
    t_arr = np.linspace(0, duration, n, dtype=np.float32)
    audio = np.zeros(n, np.float32)
    p     = style.lower()

    if "lullaby" in p or "bedtime" in p:
        freqs = [(261,.10),(330,.08),(392,.06),(523,.04)]
        mf    = 0.05
    elif "magical" in p or "fairy" in p:
        freqs = [(523,.09),(659,.07),(784,.06),(1047,.04)]
        mf    = 0.08
    else:
        freqs = [(392,.10),(494,.09),(523,.08),(659,.06)]
        mf    = 0.12

    for freq, amp in freqs:
        mod    = 0.6 + 0.4*np.sin(2*math.pi*mf*t_arr)
        audio += amp * mod * np.sin(2*math.pi*freq*t_arr)

    noise = np.random.randn(n).astype(np.float32)*0.006
    for k in range(1,n): noise[k]=0.95*noise[k-1]+0.05*noise[k]
    audio += noise

    peak = np.max(np.abs(audio))
    if peak > 0: audio = audio/peak*0.55
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


def mix_narration_music(narration_bytes, music_mp3, out_mp3, duration):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        nt = f.name
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        lp = f.name
    try:
        open(nt,"wb").write(narration_bytes)
        subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i",nt,
                       "-t",str(duration),lp],
                      check=True, capture_output=True)
        subprocess.run([
            "ffmpeg","-y","-i",lp,"-i",music_mp3,
            "-filter_complex",
            "[0:a]volume=4.0[v];[1:a]volume=0.20[m];"
            "[v][m]amix=inputs=2:duration=shortest",
            "-t",str(duration),"-c:a","libmp3lame","-q:a","2",out_mp3
        ], check=True, capture_output=True)
        print("  [mix] Audio ready ✓")
    finally:
        for p2 in [nt,lp]:
            if os.path.exists(p2): os.unlink(p2)


def make_thumbnail(content_type, title, tmp):
    from PIL import ImageDraw, ImageFont
    img  = get_thumbnail_frame(content_type)
    draw = ImageDraw.Draw(img)

    # Title banner
    draw.rectangle([0, H*3//4, W, H], fill=(255,220,0))
    draw.rectangle([0, H*3//4, W, H*3//4+6], fill=(255,100,0))

    fnt   = None
    for fp in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        if Path(fp).exists():
            try:
                from PIL import ImageFont
                fnt = ImageFont.truetype(fp, 52)
                break
            except: pass
    if fnt is None:
        from PIL import ImageFont
        fnt = ImageFont.load_default()

    clean = title[:40]
    bb    = draw.textbbox((0,0), clean, font=fnt)
    tx    = (W - (bb[2]-bb[0])) // 2
    ty    = H*3//4 + 15
    draw.text((tx+2,ty+2), clean, font=fnt, fill=(200,0,0))
    draw.text((tx, ty),    clean, font=fnt, fill=(50,50,50))

    thumb = str(tmp/"thumbnail.jpg")
    img.save(thumb, quality=95)
    return thumb


def make_metadata(content):
    type_tags = {
        "bedtime_story" : ["bedtime story","kids story","moral story",
                           "animated story","children bedtime","kids cartoon"],
        "nursery_rhyme" : ["nursery rhyme","kids songs","rhymes for kids",
                           "baby songs","toddler songs","kids rhymes"],
        "educational"   : ["educational kids","learn for kids","kids learning",
                           "preschool","kids education","learn with cartoons"],
        "fairy_tale"    : ["fairy tale kids","animated fairy tale",
                           "magical story","kids fairy tale","cartoon story"],
    }
    emoji = {"bedtime_story":"🌙","nursery_rhyme":"🎵",
             "educational":"📚","fairy_tale":"✨"}[content["type"]]
    title = f"{emoji} {content['title']} | Cartoon for Kids"[:100]
    tags  = (type_tags.get(content["type"],[]) +
             ["kids cartoon","cartoon for kids","children cartoon",
              "animated cartoon","kids youtube"])[:15]
    desc  = (
        f"{title}\n\n"
        f"🎬 Fun animated cartoon for children!\n\n"
        f"Perfect for kids aged 2-8 years.\n"
        f"Educational, fun and entertaining!\n\n"
        f"🔔 Subscribe for new cartoons 3x every week!\n\n"
        f"#kidscartoon #cartoon #kidslearning #childrenstories #animated"
    )
    return {"title":title,"tags":tags,"description":desc}


def run():
    HF_TOKEN            = os.environ.get("HF_TOKEN","")
    YOUTUBE_CREDENTIALS = os.environ.get("YOUTUBE_CREDENTIALS")
    UPLOAD_NUM          = int(os.environ.get("UPLOAD_NUM","0"))

    if not YOUTUBE_CREDENTIALS:
        raise EnvironmentError("YOUTUBE_CREDENTIALS not set")

    print(f"\n{'='*60}")
    print(f"  Pipeline  : Kids Cartoon (Paw Patrol Style)")
    print(f"  Upload    : #{UPLOAD_NUM+1} of week")
    print(f"{'='*60}\n")

    print("📖  Step 1/5 — Generating content ...")
    content = get_content_for_week(UPLOAD_NUM)
    print(f"  → Type : {content['type']}")
    print(f"  → Title: {content['title']}")

    with tempfile.TemporaryDirectory(prefix="kids_") as tmp:
        tmp = Path(tmp)

        print("\n🗣️   Step 2/5 — Narration voice ...")
        nar_bytes = generate_narration(content["script"], content["type"])

        print("\n🎵  Step 3/5 — Background music + mix ...")
        words    = sum(len(l.split()) for l in content["script"])
        duration = max(60, min(300, words*2+30))
        music    = make_kids_music(content["music"], duration, tmp)
        mixed    = str(tmp/"mixed.mp3")
        mix_narration_music(nar_bytes, music, mixed, duration)

        print("\n🎨  Step 4/5 — Rendering Paw Patrol style cartoon ...")
        video = str(tmp/"cartoon.mp4")
        create_cartoon_video(
            script       = content["script"],
            audio_path   = mixed,
            output_path  = video,
            content_type = content["type"],
        )

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
