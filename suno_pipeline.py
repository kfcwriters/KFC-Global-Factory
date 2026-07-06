#!/usr/bin/env python3
"""
suno_pipeline.py — Fully Automatic Romantic Song Video
Music priority:
  1. apiframe.ai (300 free credits/month recurring — BEST FREE OPTION)
  2. SunoAI Python library + your cookie (free, keep-alive built in)
  3. songs/ folder (manual uploads)
  4. Local synthesis (always works)
"""
import os, random, subprocess, sys, tempfile, json, time, requests
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "src"))
from image_gen      import generate_images
from lyrics_overlay import add_lyrics
from video_assembly import create_video
from metadata_gen   import generate_metadata
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
    "couple on swing at sunrise, soft morning mist, peaceful love",
    "man holding woman from behind watching sunset over ocean together",
]

# Song styles — music feel changes each week even with fresh lyrics
SONG_STYLES = [
    {"style": "romantic ballad, soft piano, emotional female vocals, slow tempo, heartfelt", "mood": "eternal love"},
    {"style": "sad romantic ballad, piano and violin, emotional female vocals, melancholic", "mood": "longing and missing"},
    {"style": "upbeat romantic pop, acoustic guitar, happy female vocals, feel good love", "mood": "joyful love"},
    {"style": "bollywood fusion romantic, sitar and piano, Hindi English female vocals", "mood": "passionate love"},
    {"style": "orchestral romantic, strings and piano, powerful female vocals, cinematic", "mood": "epic forever love"},
    {"style": "soft intimate ballad, acoustic guitar, whispery female vocals, tender", "mood": "quiet love"},
    {"style": "monsoon romantic, piano and rain sounds, dreamy female vocals, nostalgic", "mood": "rainy day love"},
    {"style": "wedding romantic, orchestral, uplifting female vocals, ceremonial beautiful", "mood": "forever commitment"},
    {"style": "first love ballad, sweet acoustic guitar, young innocent female vocals", "mood": "first love innocence"},
    {"style": "soulful romantic RnB, piano and cello, deep emotional female vocals", "mood": "soulmate love"},
]

# Fallback lyrics when Claude API is not available
FALLBACK_LYRICS = [
    {"title": "Never Let You Go", "prompt": "[Verse]\nIn the quiet of the night\nI reach out for your hand\nEvery star above us shines\nJust the way I had planned\n\n[Chorus]\nI will never let you go\nYou are the only love I know\nIn this world of highs and lows\nYou are my reason you are my soul\n\n[Verse]\nThrough every storm and every rain\nThrough every joy and every pain\nYour love is all I ever need\nYou are my heart you are my creed\n\n[Chorus]\nI will never let you go\nYou are the only love I know\nIn this world of highs and lows\nYou are my reason you are my soul"},
    {"title": "Missing You Tonight", "prompt": "[Verse]\nThe rain falls on an empty street\nI walk alone without your heartbeat\nEvery corner holds your memory\nEvery shadow is what you used to be\n\n[Chorus]\nMissing you like the stars miss the sun\nMissing you now that you are gone\nEvery night I close my eyes and pray\nThat you will come back to me someday\n\n[Bridge]\nSomewhere out there under the same sky\nI know you think of me sometimes\nAnd that is all I need to get by\nUntil we meet again in better times"},
    {"title": "You Are My World", "prompt": "[Verse]\nBefore you came into my life\nEverything was black and white\nNow the colors fill my days\nYou have set my heart ablaze\n\n[Chorus]\nYou are my world you are my sky\nThe reason that I laugh and cry\nWithout you here I am not complete\nYou are the rhythm of my heartbeat\n\n[Verse]\nYour gentle touch your tender kiss\nA feeling I would always miss\nIf you were ever far from me\nYou are my heart you are my peace"},
    {"title": "Tere Bina My Love", "prompt": "[Verse]\nTere bina yeh dil mera\nKhoya khoya rehta hai\nTeri yaad mein har pal\nDard ka asar rehta hai\n\n[Chorus]\nCome back to me my love\nI cannot breathe without you near\nEvery moment without you\nIs a moment full of fear\n\n[Verse]\nIshq mera sachcha hai\nYeh dil tera deewana hai\nHar pal har ghadi bas tu hi\nMeri duniya meri jaana hai"},
    {"title": "Forever Is You", "prompt": "[Verse]\nI used to think that love was just a word\nA pretty song that no one ever heard\nBut then you came and changed everything\nMade my heart open up and want to sing\n\n[Chorus]\nForever is you forever is this\nThe warmth of your hug the touch of your kiss\nNo matter how far the journey may go\nForever is you I want you to know\n\n[Bridge]\nWrite your name across my heart\nPromise me we will never part\nIn a world that changes every day\nMy love for you will always stay"},
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


# ── apiframe.ai (300 free credits/month) ──────────────────────────────────────

def generate_apiframe(api_key: str, anthropic_api_key=None) -> tuple:
    """Generate fresh unique song every week using pure Python lyrics — no API needed."""
    # Fresh unique lyrics — different every week, free forever
    song = generate_weekly_lyrics()

    print(f"  [apiframe] Generating: '{song['title']}' ...")
    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    resp = requests.post(
        "https://api.apiframe.ai/v2/music/generate",
        headers=headers,
        json={
            "model" : "suno",
            "prompt": song["prompt"],
            "sunoParams": {
                "custom_mode"  : True,
                "style"        : song["style"],
                "instrumental" : False,
                "model_version": "V5_5",
            }
        },
        timeout=30
    )
    if not resp.ok:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")

    job_id = resp.json().get("jobId")
    print(f"  [apiframe] jobId: {job_id} — polling ...")

    for i in range(40):
        time.sleep(8)
        poll   = requests.get(f"https://api.apiframe.ai/v2/jobs/{job_id}",
                              headers=headers, timeout=30)
        data   = poll.json()
        status = data.get("status", "")
        print(f"  [apiframe] {i+1}: {status}")

        if status == "COMPLETED":
            tracks = data.get("result", {}).get("tracks", [])
            url    = tracks[0].get("audioUrl") if tracks else None
            if not url:
                raise RuntimeError(f"No audioUrl in result")
            mp3 = requests.get(url, timeout=120)
            mp3.raise_for_status()
            print(f"  [apiframe] {len(mp3.content)//1024} KB ✓")
            return mp3.content, song["title"]

        if status == "FAILED":
            raise RuntimeError(f"Job failed: {data}")

    raise RuntimeError("Timeout after 5 min")


def generate_sunoai_lib(cookie: str) -> tuple[bytes, str]:
    raw = cookie.strip()
    if raw.startswith("["):
        items = json.loads(raw)
        cookie = "; ".join(f"{c['name']}={c['value']}" for c in items
                           if c.get("name") and c.get("value"))
    else:
        cookie = " ".join(raw.split())

    from suno import Suno, ModelVersions
    from datetime import datetime
    week_num = datetime.utcnow().isocalendar()[1]
    song     = ROMANTIC_SONGS[week_num % len(ROMANTIC_SONGS)]
    print(f"  [sunolib] Week {week_num} → {song['title']} ...")
    client = Suno(cookie=cookie, model_version=ModelVersions.CHIRP_V3_5)
    clips  = client.generate(prompt=song["prompt"], tags=song["tags"],
                              title=song["title"], is_custom=True,
                              make_instrumental=False, wait_audio=True)
    if not clips: raise RuntimeError("No clips returned")
    mp3 = requests.get(clips[0].audio_url, timeout=120)
    mp3.raise_for_status()
    print(f"  [sunolib] {len(mp3.content)//1024} KB ✓")
    return mp3.content, song["title"]


# ── Local synthesis (always works, no singing) ────────────────────────────────

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
    ANTHROPIC_API_KEY   = os.environ.get("ANTHROPIC_API_KEY")
    APIFRAME_KEY        = os.environ.get("APIFRAME_KEY")
    SUNO_COOKIE         = os.environ.get("SUNO_COOKIE")
    YOUTUBE_CREDENTIALS = os.environ.get("YOUTUBE_CREDENTIALS")

    if not HF_TOKEN:            raise EnvironmentError("HF_TOKEN not set")
    if not YOUTUBE_CREDENTIALS: raise EnvironmentError("YOUTUBE_CREDENTIALS not set")

    print(f"\n{'='*60}")
    print(f"  Pipeline : Romantic Song Video (Fully Automated)")
    if APIFRAME_KEY: print(f"  Music    : apiframe.ai (300 free/month) ★★★★★")
    elif SUNO_COOKIE: print(f"  Music    : SunoAI Python lib + cookie ★★★★★")
    else: print(f"  Music    : songs/ folder or local synthesis")
    print(f"{'='*60}\n")

    with tempfile.TemporaryDirectory(prefix="romantic_") as tmp:
        tmp=Path(tmp); song_mp3=None; title="Beautiful Love Song"

        # 1. apiframe.ai (300 free/month recurring)
        if APIFRAME_KEY and not song_mp3:
            try:
                print("🎵  Generating via apiframe.ai (300 free/month) ...")
                data, title = generate_apiframe(APIFRAME_KEY, ANTHROPIC_API_KEY)
                p=tmp/"apiframe.mp3"; p.write_bytes(data); song_mp3=str(p)
            except Exception as e: print(f"  ⚠️  apiframe: {e}")

        # 2. SunoAI Python library
        if SUNO_COOKIE and not song_mp3:
            try:
                print("🎵  Generating via SunoAI library ...")
                data, title = generate_sunoai_lib(SUNO_COOKIE)
                p=tmp/"suno.mp3"; p.write_bytes(data); song_mp3=str(p)
            except Exception as e: print(f"  ⚠️  SunoAI lib: {e}")

        # 3. Saved songs folder
        if not song_mp3:
            saved, saved_title = get_saved_song()
            if saved: song_mp3=saved; title=saved_title; print(f"🎵  Using saved: {title}")

        # 4. Local synthesis
        if not song_mp3:
            print("🎵  Synthesising locally ...")
            song_mp3=make_local(tmp,DURATION)

        # Loop short songs
        dur = probe_duration(song_mp3)
        if dur < DURATION-10:
            looped=str(tmp/"looped.mp3")
            subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i",song_mp3,
                           "-t",str(DURATION),"-c","copy",looped],
                          check=True,capture_output=True)
            song_mp3=looped
        dur=min(dur,DURATION); n_images=min(16,max(8,int(dur/15)))

        print(f"\n🖼️   Generating {n_images} romantic images ...")
        prompts=[random.choice(BG_PROMPTS) for _ in range(n_images)]
        raw_imgs=generate_images(prompts,HF_TOKEN,vertical=False)

        image_paths=[]
        for i,img in enumerate(raw_imgs):
            frame=add_lyrics(img,[title],"verse","")
            p=tmp/f"frame_{i:02d}.jpg"; p.write_bytes(frame)
            image_paths.append(str(p))

        print("\n📝  Generating metadata ...")
        meta=generate_metadata(f"romantic love song — {title}","romantic songs",ANTHROPIC_API_KEY)
        meta["title"]=f"🎵 {title} | Romantic Song 🌹"[:100]
        meta["tags"]=(["romantic song","love song","ai music","romantic music",
                       "love ballad","romantic video"]+meta.get("tags",[]))[:15]
        print(f"  → {meta['title']}")

        thumb=str(tmp/"thumbnail.jpg")
        create_thumbnail(raw_imgs[0],meta["title"],thumb)
        video=str(tmp/"output.mp4")
        create_video(song_mp3,image_paths,video,vertical=False)

        print("\n📤  Uploading ...")
        vid=upload_to_youtube(video_path=video,thumbnail_path=thumb,
            title=meta["title"],description=meta["description"],
            tags=meta["tags"],credentials_json=YOUTUBE_CREDENTIALS)
        print(f"\n🎉  Live! https://youtu.be/{vid}")
        return vid

if __name__=="__main__":
    run()
