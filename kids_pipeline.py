#!/usr/bin/env python3
"""
kids_pipeline.py — Kids Cartoon Channel with REAL Animation
Uses AnimateDiff on a SEPARATE Kaggle account's free T4 GPU.
Falls back to Ken Burns image storybook if Kaggle fails.

Uploads Mon/Wed/Fri at 2:30 PM IST.
"""
import os, random, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from kids_story_gen         import get_content_for_week
from kids_voice_gen         import generate_narration
from kaggle_video_gen       import generate_clips_kaggle
from clip_stitcher          import stitch_clips
from image_gen               import generate_images
from lyrics_overlay          import add_lyrics
from video_assembly_kenburns import create_video as create_video_kenburns
from thumbnail_gen           import create_thumbnail
from youtube_upload          import upload_to_youtube

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
        freqs = [(261,.10),(330,.08),(392,.06),(523,.04)]; mf=0.05
    elif "magical" in p or "fairy" in p:
        freqs = [(523,.09),(659,.07),(784,.06),(1047,.04)]; mf=0.08
    else:
        freqs = [(392,.10),(494,.09),(523,.08),(659,.06)]; mf=0.12

    for freq, amp in freqs:
        mod = 0.6 + 0.4*np.sin(2*math.pi*mf*t_arr)
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
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f: nt = f.name
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f: lp = f.name
    try:
        open(nt,"wb").write(narration_bytes)
        subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i",nt,
                       "-t",str(duration),lp], check=True, capture_output=True)
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
        "bedtime_story" : ["bedtime story","kids story","moral story","animated story"],
        "nursery_rhyme" : ["nursery rhyme","kids songs","rhymes for kids","toddler songs"],
        "educational"   : ["educational kids","learn for kids","kids learning","preschool"],
        "fairy_tale"    : ["fairy tale kids","animated fairy tale","magical story"],
    }
    emoji = {"bedtime_story":"🌙","nursery_rhyme":"🎵","educational":"📚","fairy_tale":"✨"}[content["type"]]
    title = f"{emoji} {content['title']} | Animated Cartoon"[:100]
    tags  = (type_tags.get(content["type"],[]) +
             ["kids cartoon","animated cartoon","cartoon for kids","kids youtube"])[:15]
    desc  = (f"{title}\n\n🎬 Fun animated {content['type'].replace('_',' ')} for children!\n\n"
             f"Perfect for kids aged 2-8 years.\n\n🔔 Subscribe for new cartoons 3x weekly!\n\n"
             f"#kidscartoon #animatedcartoon #kidslearning")
    return {"title":title,"tags":tags,"description":desc}


def run():
    HF_TOKEN             = os.environ.get("HF_TOKEN","")
    YOUTUBE_CREDENTIALS  = os.environ.get("YOUTUBE_CREDENTIALS")
    KAGGLE_USERNAME_2    = os.environ.get("KAGGLE_USERNAME_2","")
    KAGGLE_KEY_2         = os.environ.get("KAGGLE_KEY_2","")
    UPLOAD_NUM           = int(os.environ.get("UPLOAD_NUM","0"))

    if not YOUTUBE_CREDENTIALS: raise EnvironmentError("YOUTUBE_CREDENTIALS not set")

    print(f"\n{'='*60}")
    print(f"  Pipeline  : Kids Cartoon — REAL AnimateDiff Animation")
    print(f"  Upload    : #{UPLOAD_NUM+1} of week")
    if KAGGLE_USERNAME_2 and KAGGLE_KEY_2:
        print(f"  Animation : Kaggle GPU (2nd account) → AnimateDiff ★★★★★")
    else:
        print(f"  Animation : KAGGLE_USERNAME_2/KAGGLE_KEY_2 not set → Ken Burns fallback")
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
        duration = max(60, min(180, words*2+30))
        music    = make_kids_music(content["music"], duration, tmp)
        mixed    = str(tmp/"mixed.mp3")
        mix_narration_music(nar_bytes, music, mixed, duration)

        # ── Step 4: Try real animation via Kaggle GPU ─────────────────────────
        print(f"\n🎬  Step 4/6 — Attempting AnimateDiff animation (Kaggle GPU) ...")
        video = str(tmp/"cartoon.mp4")
        used_animation = False

        if KAGGLE_USERNAME_2 and KAGGLE_KEY_2:
            try:
                animation_prompts = [
                    f"{p}, cartoon animation style, smooth motion, colorful, cute, children's animation"
                    for p in content["prompts"][:6]
                ]
                clips = generate_clips_kaggle(
                    prompts=animation_prompts, title=content["title"],
                    kaggle_username=KAGGLE_USERNAME_2, kaggle_key=KAGGLE_KEY_2,
                    num_frames=16, fps=8
                )
                if len(clips) >= 3:
                    print(f"  → Got {len(clips)} real animated clips ✓")
                    stitch_clips(clips, mixed, video, target_duration=duration, vertical=False)
                    used_animation = True
                else:
                    print(f"  → Only {len(clips)} clips — not enough, falling back")
            except Exception as e:
                print(f"  → AnimateDiff failed: {str(e)[:200]}")

        # ── Fallback: Ken Burns storybook ─────────────────────────────────────
        if not used_animation:
            print(f"\n🖼️   Fallback — Ken Burns image storybook ...")
            cartoon_prompts = [f"{p}, bright vivid colors, safe for children, storybook illustration"
                              for p in content["prompts"]]
            raw_imgs = generate_images(cartoon_prompts, HF_TOKEN, vertical=False)
            image_paths = []
            for i, img in enumerate(raw_imgs):
                line_idx = min(i, len(content["script"])-1)
                frame = add_lyrics(img, [content["script"][line_idx]], "verse", "")
                p = tmp / f"frame_{i:02d}.jpg"; p.write_bytes(frame)
                image_paths.append(str(p))
            create_video_kenburns(mixed, image_paths, video, vertical=False)
            thumb_source_img = raw_imgs[0]
        else:
            thumb_source_img = None

        # ── Step 5: Thumbnail ─────────────────────────────────────────────────
        print("\n📤  Step 5/6 — Thumbnail ...")
        meta  = make_metadata(content)
        thumb = str(tmp/"thumbnail.jpg")
        if thumb_source_img:
            create_thumbnail(thumb_source_img, meta["title"], thumb)
        else:
            frame_path = str(tmp/"thumb_frame.jpg")
            subprocess.run(["ffmpeg","-y","-i",video,"-ss","1","-vframes","1",
                           frame_path], capture_output=True)
            with open(frame_path, "rb") as f:
                create_thumbnail(f.read(), meta["title"], thumb)

        # ── Step 6: Upload ────────────────────────────────────────────────────
        print("\n📤  Step 6/6 — Uploading ...")
        print(f"  → Mode: {'REAL ANIMATION 🎬' if used_animation else 'Ken Burns storybook 🖼️'}")
        vid = upload_to_youtube(
            video_path=video, thumbnail_path=thumb,
            title=meta["title"], description=meta["description"],
            tags=meta["tags"], credentials_json=YOUTUBE_CREDENTIALS,
        )
        print(f"\n🎉  Live! https://youtu.be/{vid}")
        return vid


if __name__ == "__main__":
    run()
