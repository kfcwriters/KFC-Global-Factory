#!/usr/bin/env python3
"""
kids_pipeline.py — Kids Content Test Pipeline (Ken Burns test bed)
Uses AI images (Pollinations) + NEW Ken Burns video_assembly.py
This is the safe place to test the Ken Burns/transitions upgrade
before rolling it into the main Suno pipeline.

Uploads Mon/Wed/Fri at 2:30 PM IST.
"""
import os, random, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from kids_story_gen  import get_content_for_week
from kids_voice_gen  import generate_narration
from image_gen       import generate_images
from lyrics_overlay  import add_lyrics
from video_assembly_kenburns import create_video   # ← EXPERIMENTAL, kids-only
from thumbnail_gen   import create_thumbnail
from youtube_upload  import upload_to_youtube

import numpy as np
import scipy.io.wavfile as wf
import math

SR = 44100


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


def make_metadata(content):
    type_tags = {
        "bedtime_story" : ["bedtime story","kids story","moral story",
                           "animated story","children bedtime"],
        "nursery_rhyme" : ["nursery rhyme","kids songs","rhymes for kids",
                           "baby songs","toddler songs"],
        "educational"   : ["educational kids","learn for kids","kids learning",
                           "preschool","kids education"],
        "fairy_tale"    : ["fairy tale kids","animated fairy tale",
                           "magical story","kids fairy tale"],
    }
    emoji = {"bedtime_story":"🌙","nursery_rhyme":"🎵",
             "educational":"📚","fairy_tale":"✨"}[content["type"]]
    title = f"{emoji} {content['title']} | Story for Kids"[:100]
    tags  = (type_tags.get(content["type"],[]) +
             ["kids story","story for kids","children video",
              "kids youtube","bedtime stories"])[:15]
    desc  = (
        f"{title}\n\n"
        f"🎬 Fun {content['type'].replace('_',' ')} for children!\n\n"
        f"Perfect for kids aged 2-8 years.\n"
        f"Educational, fun and entertaining!\n\n"
        f"🔔 Subscribe for new stories 3x every week!\n\n"
        f"#kidsstory #storyforkids #kidslearning #childrenstories"
    )
    return {"title":title,"tags":tags,"description":desc}


def run():
    HF_TOKEN            = os.environ.get("HF_TOKEN","")
    YOUTUBE_CREDENTIALS = os.environ.get("YOUTUBE_CREDENTIALS")
    UPLOAD_NUM          = int(os.environ.get("UPLOAD_NUM","0"))

    if not HF_TOKEN:            raise EnvironmentError("HF_TOKEN not set")
    if not YOUTUBE_CREDENTIALS: raise EnvironmentError("YOUTUBE_CREDENTIALS not set")

    print(f"\n{'='*60}")
    print(f"  Pipeline  : Kids Story (Ken Burns TEST)")
    print(f"  Upload    : #{UPLOAD_NUM+1} of week")
    print(f"{'='*60}\n")

    print("📖  Step 1/6 — Generating content ...")
    content = get_content_for_week(UPLOAD_NUM)
    print(f"  → Type : {content['type']}")
    print(f"  → Title: {content['title']}")

    with tempfile.TemporaryDirectory(prefix="kids_") as tmp:
        tmp = Path(tmp)

        print("\n🗣️   Step 2/6 — Narration voice ...")
        nar_bytes = generate_narration(content["script"], content["type"])

        print("\n🎵  Step 3/6 — Background music + mix ...")
        words    = sum(len(l.split()) for l in content["script"])
        duration = max(60, min(240, words*2+30))
        music    = make_kids_music(content["music"], duration, tmp)
        mixed    = str(tmp/"mixed.mp3")
        mix_narration_music(nar_bytes, music, mixed, duration)

        print(f"\n🖼️   Step 4/6 — Generating {len(content['prompts'])} images ...")
        cartoon_prompts = [
            f"{p}, bright vivid colors, safe for children, storybook illustration style"
            for p in content["prompts"]
        ]
        raw_imgs = generate_images(cartoon_prompts, HF_TOKEN, vertical=False)

        image_paths = []
        for i, img in enumerate(raw_imgs):
            # Show a line of the story as caption on each image
            line_idx = min(i, len(content["script"])-1)
            frame = add_lyrics(img, [content["script"][line_idx]], "verse", "")
            p = tmp / f"frame_{i:02d}.jpg"
            p.write_bytes(frame)
            image_paths.append(str(p))

        print("\n🎬  Step 5/6 — Rendering video (Ken Burns + transitions) ...")
        video = str(tmp/"story.mp4")
        create_video(mixed, image_paths, video, vertical=False)

        print("\n📤  Step 6/6 — Thumbnail + upload ...")
        meta  = make_metadata(content)
        thumb = str(tmp/"thumbnail.jpg")
        create_thumbnail(raw_imgs[0], meta["title"], thumb)

        vid = upload_to_youtube(
            video_path=video, thumbnail_path=thumb,
            title=meta["title"], description=meta["description"],
            tags=meta["tags"], credentials_json=YOUTUBE_CREDENTIALS,
        )
        print(f"\n🎉  Live! https://youtu.be/{vid}")
        return vid


if __name__ == "__main__":
    run()
