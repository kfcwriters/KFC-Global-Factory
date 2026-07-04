"""
suno_gen.py
Generates songs using SunoAI Python library.
The library has built-in keep-alive so cookie stays fresh automatically.
Install: pip install SunoAI
"""
import random, time, requests, json

ROMANTIC_SONGS = [
    {
        "prompt": "[Verse]\nIn the quiet of the night\nI reach out for your hand\nEvery star above us shines\nJust the way I had planned\n\n[Chorus]\nI will never let you go\nYou're the only love I know\nIn this world of highs and lows\nYou're my reason you're my soul",
        "tags": "romantic ballad, soft piano, emotional female vocals, slow tempo",
        "title": "Never Let You Go"
    },
    {
        "prompt": "[Verse]\nThe way you smile at morning light\nThe way you hold me through the night\nEvery little thing you do\nMakes me fall in love with you\n\n[Chorus]\nI want all of you\nEvery flaw and every truth\nIn the good and in the bad\nYou're the best I've ever had",
        "tags": "romantic love song, acoustic guitar, warm female vocals, heartfelt",
        "title": "All Of You"
    },
    {
        "prompt": "[Verse]\nThe moon is hanging in the sky\nThe stars are scattered way up high\nAll I want is you right here\nTo whisper softly in your ear\n\n[Chorus]\nStay with me tonight\nHold me till the morning light\nLet the world just fade away\nBaby please I need you to stay",
        "tags": "slow romantic ballad, piano and strings, emotional vocals, cinematic",
        "title": "Stay With Me Tonight"
    },
    {
        "prompt": "[Verse]\nBefore you came into my life\nEverything was black and white\nNow the colors fill my days\nYou have set my heart ablaze\n\n[Chorus]\nYou are my world you are my sky\nThe reason that I laugh and cry\nWithout you here I'm not complete\nYou are the rhythm of my heartbeat",
        "tags": "romantic pop ballad, orchestra and piano, powerful female vocals",
        "title": "You Are My World"
    },
    {
        "prompt": "[Verse]\nI used to think that love was just a word\nA pretty song that no one ever heard\nBut then you came and changed everything\nMade my heart open up and want to sing\n\n[Chorus]\nForever is you forever is this\nThe warmth of your hug the touch of your kiss\nNo matter how far the journey may go\nForever is you I want you to know",
        "tags": "romantic love ballad, soft guitar and strings, emotional singer",
        "title": "Forever Is You"
    },
    {
        "prompt": "[Verse]\nEvery morning when I wake\nThe first thought is of you I take\nEvery evening when I sleep\nYour memory is mine to keep\n\n[Chorus]\nI just want to be close to you\nFeel your heartbeat hear you breathe\nEvery moment that I'm with you\nIs the only place I need to be",
        "tags": "soft romantic ballad, violin and piano, tender female vocals, slow",
        "title": "Close To You"
    },
    {
        "prompt": "[Verse]\nI see you in the morning sun\nI hear you when the day is done\nYour laughter echoes in my mind\nThe sweetest sound I'll ever find\n\n[Chorus]\nEvery breath I take is yours\nEvery dream that I explore\nEvery wish upon a star\nI'm so grateful that you are\nThe one who holds my hand tonight",
        "tags": "emotional romantic ballad, piano and cello, heartfelt female vocals",
        "title": "Every Breath"
    },
]


def generate_with_sunoai_lib(cookie: str) -> tuple[bytes, str]:
    """
    Uses SunoAI Python library — has built-in keep-alive so cookie stays fresh.
    pip install SunoAI
    """
    from suno import Suno, ModelVersions

    song_data = random.choice(ROMANTIC_SONGS)
    print(f"  [suno] Generating: {song_data['title']} ...")

    client = Suno(
        cookie=cookie,
        model_version=ModelVersions.CHIRP_V3_5
    )

    clips = client.generate(
        prompt      = song_data["prompt"],
        tags        = song_data["tags"],
        title       = song_data["title"],
        is_custom   = True,
        make_instrumental = False,
        wait_audio  = True,
    )

    if not clips:
        raise RuntimeError("SunoAI returned no clips")

    clip = clips[0]
    print(f"  [suno] Generated clip ID: {clip.id}")

    # Download the audio
    audio_url = clip.audio_url
    if not audio_url:
        raise RuntimeError("No audio URL in clip")

    mp3 = requests.get(audio_url, timeout=120)
    mp3.raise_for_status()
    print(f"  [suno] Downloaded: {len(mp3.content)//1024} KB ✓")
    return mp3.content, song_data["title"]


def generate_with_apiframe(api_key: str) -> tuple[bytes, str]:
    """
    apiframe.ai — 300 free credits/month recurring, no credit card.
    Get free API key at: https://apiframe.pro
    Add as GitHub Secret: APIFRAME_KEY
    """
    song_data = random.choice(ROMANTIC_SONGS)
    print(f"  [apiframe] Generating: {song_data['title']} ...")

    headers = {
        "Authorization": api_key,
        "Content-Type" : "application/json"
    }

    # Start generation
    resp = requests.post(
        "https://api.apiframe.pro/suno-create",
        headers=headers,
        json={
            "custom_mode"  : True,
            "prompt"       : song_data["prompt"],
            "tags"         : song_data["tags"],
            "title"        : song_data["title"],
            "make_instrumental": False,
        },
        timeout=30
    )
    resp.raise_for_status()
    task_id = resp.json().get("task_id")
    print(f"  [apiframe] task_id: {task_id} — polling ...")

    # Poll until done (usually 30-90s)
    for attempt in range(40):
        time.sleep(8)
        poll = requests.post(
            "https://api.apiframe.pro/fetch",
            headers=headers,
            json={"task_id": task_id},
            timeout=30
        )
        poll.raise_for_status()
        data   = poll.json()
        status = data.get("status", "")
        print(f"  [apiframe] attempt {attempt+1}: {status}")

        if status in ("done", "completed", "success"):
            clips     = data.get("clips") or data.get("data", {}).get("clips", [])
            audio_url = clips[0].get("audio_url") if clips else data.get("audio_url")
            if not audio_url:
                raise RuntimeError(f"No audio URL: {data.keys()}")
            mp3 = requests.get(audio_url, timeout=120)
            mp3.raise_for_status()
            print(f"  [apiframe] Downloaded: {len(mp3.content)//1024} KB ✓")
            return mp3.content, song_data["title"]

        if status in ("failed", "error"):
            raise RuntimeError(f"apiframe failed: {data}")

    raise RuntimeError("apiframe timed out")


def _parse_cookie(raw: str) -> str:
    """Handle both JSON (EditThisCookie) and plain string cookie formats."""
    raw = raw.strip()
    if raw.startswith("["):
        items = json.loads(raw)
        parts = [f"{c['name']}={c['value']}" for c in items
                 if c.get("name") and c.get("value")]
        return "; ".join(parts)
    return " ".join(raw.split())


def generate_suno_song(cookie: str) -> tuple[bytes, str]:
    """Try SunoAI lib first, then cookie-based approach."""
    cookie = _parse_cookie(cookie)

    # Try SunoAI Python library (has keep-alive built in)
    try:
        return generate_with_sunoai_lib(cookie)
    except Exception as e:
        print(f"  [suno] SunoAI lib failed: {str(e)[:80]}")

    # Fallback: direct API call
    from src.suno_gen_direct import generate_direct
    return generate_direct(cookie)
