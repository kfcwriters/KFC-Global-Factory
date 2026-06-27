"""
lyrics_gen.py
Generates original Hindi+English romantic song lyrics.
Primary  : Claude API
Fallback : 8 hand-crafted bilingual template songs (no API needed)
"""
import random, json, re, requests

CLAUDE_API = "https://api.anthropic.com/v1/messages"
CLAUDE_MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-6",
    "claude-3-5-haiku-20241022",
    "claude-3-haiku-20240307",
]

# ── 8 complete bilingual romantic songs (fallback) ────────────────────────────
TEMPLATE_SONGS = [
    {
        "title": "Tere Bina — Without You",
        "sections": [
            {"type":"verse",   "lines":["In the silence of the night", "I still search for your light", "Every moment, every day", "You never seem too far away"]},
            {"type":"prechorus","lines":["Kuch keh nahi sakta", "Par feel hota hai yeh dil mera"]},
            {"type":"chorus",  "lines":["Tere bina zindagi hai adhoori", "You complete me, that's my whole story", "Dil mera bas teri talash mein", "Lost in you, in your warm embrace"]},
            {"type":"verse",   "lines":["Aankhon mein teri kho jaata hoon", "Har pal teri yaad satati hai", "Teri muskaan meri duniya hai", "Tere bina sab kuch khaali hai"]},
            {"type":"chorus",  "lines":["Tere bina zindagi hai adhoori", "You complete me, that's my whole story", "Dil mera bas teri talash mein", "Lost in you, in your warm embrace"]},
            {"type":"bridge",  "lines":["Maybe words can never say enough", "All I know is I need your love", "In this lifetime and the next", "You're the one I won't forget"]},
            {"type":"chorus",  "lines":["Tere bina zindagi hai adhoori", "You complete me, that's my whole story", "Dil mera bas teri talash mein", "Lost in you, in your warm embrace"]},
            {"type":"outro",   "lines":["Tere bina... tere bina...", "Without you... I'm not me"]},
        ]
    },
    {
        "title": "Dil Mera Tumhara — My Heart is Yours",
        "sections": [
            {"type":"verse",   "lines":["When I first saw you smile", "Time just stood still for a while", "In that moment I just knew", "My whole world would change with you"]},
            {"type":"prechorus","lines":["Dil dhadakta hai tere liye", "Aur koi wajah nahi chahiye"]},
            {"type":"chorus",  "lines":["Dil mera tumhara, you're my everything", "Jaan meri tu hi, you make my heart sing", "Har khushi mein tu, har gham mein bhi tu", "My heart is yours, always and forever true"]},
            {"type":"verse",   "lines":["Tere haathon ka sparsh", "Mujhe sab bhula deta hai", "Teri aawaaz ki goonj", "Dil ko chain aata hai"]},
            {"type":"chorus",  "lines":["Dil mera tumhara, you're my everything", "Jaan meri tu hi, you make my heart sing", "Har khushi mein tu, har gham mein bhi tu", "My heart is yours, always and forever true"]},
            {"type":"bridge",  "lines":["Saathon janam ka yeh bandhan hai", "This love is written in the stars above", "Teri baahon mein meri duniya hai", "I found my heaven in your love"]},
            {"type":"outro",   "lines":["Dil mera tumhara... tumhara...", "My heart is yours... only yours..."]},
        ]
    },
    {
        "title": "Mohabbat — True Love",
        "sections": [
            {"type":"verse",   "lines":["Every morning your face I see", "In the sunlight, you're my dream", "Every heartbeat calls your name", "Nothing will ever be the same"]},
            {"type":"prechorus","lines":["Tujhse hai meri mohabbat", "Yeh dil kehta hai baar baar"]},
            {"type":"chorus",  "lines":["Mohabbat hai yeh, this is real love", "Sent from the heavens, from God above", "Tu meri khushiyon ka raaz hai", "You are the answer to my every prayer"]},
            {"type":"verse",   "lines":["Kabhi na socha tha yeh hoga", "Teri nazar ne kar diya jaadoo", "Ab toh bas ek arzoo hai", "Har janam mein tu mile mujhko"]},
            {"type":"chorus",  "lines":["Mohabbat hai yeh, this is real love", "Sent from the heavens, from God above", "Tu meri khushiyon ka raaz hai", "You are the answer to my every prayer"]},
            {"type":"bridge",  "lines":["Distance means nothing when you're near my heart", "Time stands still when I'm lost in your eyes", "Koi door nahi, koi faasla nahi", "You and I, together till the end"]},
            {"type":"outro",   "lines":["Mohabbat... mohabbat...", "Real love... only love..."]},
        ]
    },
    {
        "title": "Pyaar Ka Rang — Color of Love",
        "sections": [
            {"type":"verse",   "lines":["Like the colors of sunrise", "Like the stars in your eyes", "Like the rain after summer heat", "You make everything complete"]},
            {"type":"prechorus","lines":["Rang bhare hain tere pyaar ke", "Zindagi rang gayi hai teri"]},
            {"type":"chorus",  "lines":["Pyaar ka rang hai anokha", "This love colours my whole world", "Tu mere dil ka hai rajah", "You're my king, you're my lord", "Har rang mein tu hi nazar aata", "In every colour I see you"]},
            {"type":"verse",   "lines":["Gulaabi hain teri yaadon ke rang", "Neela hai tera aasmaan", "Peela hai tera pyaar ka ujala", "Laal hai mera dil tera"]},
            {"type":"chorus",  "lines":["Pyaar ka rang hai anokha", "This love colours my whole world", "Tu mere dil ka hai rajah", "You're my king, you're my lord"]},
            {"type":"bridge",  "lines":["Paint my world in shades of you", "Every colour feels brand new", "Bin tere sab rang hain pheeke", "With you every moment is true"]},
            {"type":"outro",   "lines":["Rang... pyaar ka rang...", "Colours... of our love..."]},
        ]
    },
    {
        "title": "Saath Hain Hum — We Are Together",
        "sections": [
            {"type":"verse",   "lines":["Through the storms and sunny days", "Through the nights and morning haze", "Hand in hand we walk this road", "Together we can bear any load"]},
            {"type":"prechorus","lines":["Saath hain hum, saath rahenge", "Yeh waada hai hamara"]},
            {"type":"chorus",  "lines":["Saath hain hum, we walk together", "Through every storm and changing weather", "Teri raahon mein meri raahein", "Our paths are one, in love forever"]},
            {"type":"verse",   "lines":["Jab bhi gira, tune thaama", "Jab bhi roya, tune muskuraya", "Har mushkil mein mera saaya", "Ban ke tu mere paas aaya"]},
            {"type":"chorus",  "lines":["Saath hain hum, we walk together", "Through every storm and changing weather", "Teri raahon mein meri raahein", "Our paths are one, in love forever"]},
            {"type":"bridge",  "lines":["You're not just my love, you're my best friend", "Yaar bhi hai tu, pyaar bhi tu", "This beautiful journey has no end", "Main hoon tere saath, tu hai mere saath"]},
            {"type":"outro",   "lines":["Saath hain hum... hamesha...", "Together we are... always..."]},
        ]
    },
    {
        "title": "Teri Aankhein — Your Eyes",
        "sections": [
            {"type":"verse",   "lines":["I could get lost in your eyes", "Like stars scattered across midnight skies", "Every glance, every look you give", "Makes me feel so alive, so alive"]},
            {"type":"prechorus","lines":["Teri aankhein baat karti hain", "Dil ki gehraiyon se milti hain"]},
            {"type":"chorus",  "lines":["Teri aankhein, your beautiful eyes", "Mujhe bulaati hain, pulling me inside", "In their depths I found my paradise", "Teri aankhein, I'm lost in your eyes"]},
            {"type":"verse",   "lines":["Kaali kaali aankhein teri", "Jo mujhe chain nahi deti", "Din raat tera hi khayal hai", "Neend bhi mujhse rooth gayi"]},
            {"type":"chorus",  "lines":["Teri aankhein, your beautiful eyes", "Mujhe bulaati hain, pulling me inside", "In their depths I found my paradise", "Teri aankhein, I'm lost in your eyes"]},
            {"type":"bridge",  "lines":["Never look away, never look away", "Mujhe dekh tu is tarah", "In your gaze I want to stay", "Hamesha, hamesha, always"]},
            {"type":"outro",   "lines":["Teri aankhein... teri aankhein...", "Your eyes... your beautiful eyes..."]},
        ]
    },
    {
        "title": "Humsafar — My Fellow Traveller",
        "sections": [
            {"type":"verse",   "lines":["On this journey called life", "Through the joy and through the strife", "I searched for a guiding star", "Never knew you'd come this far"]},
            {"type":"prechorus","lines":["Tu hai mera humsafar", "Zindagi ka yeh safar"]},
            {"type":"chorus",  "lines":["Humsafar hai tu mera, you're my companion", "Raah meri teri meri, walking in tandem", "Jahan bhi jaayein hum, wherever we go", "Saath hain hum dono, our love will grow"]},
            {"type":"verse",   "lines":["Lamba hai yeh raasta", "Par tere saath aashan hai", "Thak bhi jaata hoon kabhi", "Teri haansi mera armaan hai"]},
            {"type":"chorus",  "lines":["Humsafar hai tu mera, you're my companion", "Raah meri teri meri, walking in tandem", "Jahan bhi jaayein hum, wherever we go", "Saath hain hum dono, our love will grow"]},
            {"type":"bridge",  "lines":["Every road leads back to you", "Har raah pe tu hi milta hai", "No matter where this journey goes", "Main tujhse hi juda nahi"]},
            {"type":"outro",   "lines":["Humsafar... mera humsafar...", "My companion... always..."]},
        ]
    },
    {
        "title": "Ishq Wala Love — True Love",
        "sections": [
            {"type":"verse",   "lines":["They say love is complicated", "But with you it's so clear", "Every doubt has been erased", "When you're near, nothing to fear"]},
            {"type":"prechorus","lines":["Yeh ishq hai sachcha mera", "Koi dhoka nahi koi fareb nahi"]},
            {"type":"chorus",  "lines":["Ishq wala love hai yeh mera", "This is real, no illusion", "Tu hi meri khushiyon ka gehera", "You're my solution, my conclusion", "Dil se dil ka yeh milan hai", "Heart to heart, a true connection"]},
            {"type":"verse",   "lines":["Pehle pyaar nahi maanta tha main", "Ab tujhse mil ke maanta hoon", "Woh pehli mulaqaat ki yaad", "Dil mein aaj bhi sajata hoon"]},
            {"type":"chorus",  "lines":["Ishq wala love hai yeh mera", "This is real, no illusion", "Tu hi meri khushiyon ka gehera", "You're my solution, my conclusion"]},
            {"type":"bridge",  "lines":["First love, true love, only love", "Pehla pyaar, sachcha pyaar, akhri pyaar", "You are all the love I've ever known", "Tu hi sab kuch, tu hi mera ghar"]},
            {"type":"outro",   "lines":["Ishq wala love... yeh love...", "Real love... only you..."]},
        ]
    },
]


def generate_lyrics(anthropic_api_key: str | None = None) -> dict:
    """
    Returns a song dict:
    {
      "title": str,
      "sections": [{"type": str, "lines": [str, ...]}]
    }
    """
    if anthropic_api_key:
        try:
            return _claude_lyrics(anthropic_api_key)
        except Exception as e:
            print(f"  [lyrics] Claude failed ({str(e)[:80]}) — using template")
    return _template_lyrics()


def _claude_lyrics(api_key: str) -> dict:
    system = (
        "You are a bilingual Bollywood lyricist. Write original romantic song lyrics "
        "mixing Hindi (romanized, not Devanagari script) and English. "
        "Return ONLY valid JSON, no markdown. "
        'Format: {"title": "Song Title", "sections": ['
        '{"type": "verse|chorus|prechorus|bridge|outro", "lines": ["line1", "line2", "line3", "line4"]}'
        ']}. Include: verse, prechorus, chorus, verse, chorus, bridge, chorus, outro. '
        "Each section has 3-4 lines. Mix Hindi and English naturally."
    )

    themes = [
        "eternal love and longing", "first meeting and falling in love",
        "missing someone deeply", "celebrating togetherness",
        "love that transcends distance", "the beauty of a lover's eyes",
    ]
    theme = random.choice(themes)
    user  = f"Write a complete romantic song about: {theme}"

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    for model in CLAUDE_MODELS:
        try:
            resp = requests.post(
                CLAUDE_API, headers=headers,
                json={"model": model, "max_tokens": 1500,
                      "system": system,
                      "messages": [{"role": "user", "content": user}]},
                timeout=40,
            )
            if resp.status_code == 200:
                raw  = resp.json()["content"][0]["text"].strip()
                raw  = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()
                data = json.loads(raw)
                print(f"  [lyrics] Claude OK (model={model}) ✓")
                return data
            print(f"  [lyrics] {model} HTTP {resp.status_code}")
        except Exception as e:
            print(f"  [lyrics] {model}: {str(e)[:80]}")

    raise RuntimeError("All Claude models failed")


def _template_lyrics() -> dict:
    song = random.choice(TEMPLATE_SONGS)
    print(f"  [lyrics] template: {song['title']} ✓")
    return song
