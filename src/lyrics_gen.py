"""
lyrics_gen.py — Pure English romantic lyrics.
Primary : Claude API
Fallback: 8 hand-crafted English romantic songs (no Hindi — cleaner vocals)
"""
import random, json, re, requests

CLAUDE_API    = "https://api.anthropic.com/v1/messages"
CLAUDE_MODELS = ["claude-haiku-4-5-20251001","claude-sonnet-4-6",
                 "claude-3-5-haiku-20241022","claude-3-haiku-20240307"]

TEMPLATE_SONGS = [
    {
        "title": "Never Let You Go",
        "sections": [
            {"type":"verse",    "lines":["In the quiet of the night","I reach out for your hand","Every star above us shines","Just the way I had planned"]},
            {"type":"prechorus","lines":["How did I get so lucky","To find someone like you","You walked into my world","And made everything brand new"]},
            {"type":"chorus",   "lines":["I will never let you go","You're the only love I know","In this world of highs and lows","You're my reason, you're my soul"]},
            {"type":"verse",    "lines":["Through the storms and through the rain","Through the joy and through the pain","Every moment with you here","Makes this life so crystal clear"]},
            {"type":"chorus",   "lines":["I will never let you go","You're the only love I know","In this world of highs and lows","You're my reason, you're my soul"]},
            {"type":"bridge",   "lines":["Distance cannot keep us apart","You live inside my beating heart","Time may pass and seasons change","But my love will still remain"]},
            {"type":"chorus",   "lines":["I will never let you go","You're the only love I know","In this world of highs and lows","You're my reason, you're my soul"]},
            {"type":"outro",    "lines":["Never let you go","Never let you go","You are all I need","My love, my everything"]},
        ]
    },
    {
        "title": "All Of You",
        "sections": [
            {"type":"verse",    "lines":["The way you smile at morning light","The way you hold me through the night","Every little thing you do","Makes me fall in love with you"]},
            {"type":"prechorus","lines":["I never thought that I would find","A love so pure, a love so kind","But here you are, right by my side","My greatest joy, my greatest pride"]},
            {"type":"chorus",   "lines":["I want all of you","Every flaw and every truth","In the good and in the bad","You're the best I've ever had"]},
            {"type":"verse",    "lines":["Your laughter fills the empty rooms","Your presence lifts away the gloom","I'd travel to the end of time","Just knowing that you're mine"]},
            {"type":"chorus",   "lines":["I want all of you","Every flaw and every truth","In the good and in the bad","You're the best I've ever had"]},
            {"type":"bridge",   "lines":["Forever is a word I used to fear","But now forever sounds so clear","As long as you are standing near","My love, my life, you're always here"]},
            {"type":"chorus",   "lines":["I want all of you","Every flaw and every truth","In the good and in the bad","You're the best I've ever had"]},
            {"type":"outro",    "lines":["All of you","I want all of you","My heart, my soul","You make me whole"]},
        ]
    },
    {
        "title": "Stay With Me Tonight",
        "sections": [
            {"type":"verse",    "lines":["The moon is hanging in the sky","The stars are scattered way up high","And all I want is you right here","To whisper softly in your ear"]},
            {"type":"prechorus","lines":["Don't you walk away from me","You are all that I can see","In this moment, in this light","Everything just feels so right"]},
            {"type":"chorus",   "lines":["Stay with me tonight","Hold me till the morning light","Let the world just fade away","Baby please, I need you to stay"]},
            {"type":"verse",    "lines":["I've been waiting all my life","To find a love that cuts like a knife","In the best and sweetest way","Every single night and day"]},
            {"type":"chorus",   "lines":["Stay with me tonight","Hold me till the morning light","Let the world just fade away","Baby please, I need you to stay"]},
            {"type":"bridge",   "lines":["I don't want tomorrow to come","As long as we are together as one","Right here in your arms I belong","This is where my heart calls home"]},
            {"type":"chorus",   "lines":["Stay with me tonight","Hold me till the morning light","Let the world just fade away","Baby please, I need you to stay"]},
            {"type":"outro",    "lines":["Stay with me","Stay with me tonight","Don't let go","Hold me tight"]},
        ]
    },
    {
        "title": "You Are My World",
        "sections": [
            {"type":"verse",    "lines":["Before you came into my life","Everything was black and white","Now the colors fill my days","You have set my heart ablaze"]},
            {"type":"prechorus","lines":["And I wonder how I ever","Lived my life without you near","You became my every answer","Every time I shed a tear"]},
            {"type":"chorus",   "lines":["You are my world, you are my sky","The reason that I laugh and cry","Without you here I'm not complete","You are the rhythm of my heartbeat"]},
            {"type":"verse",    "lines":["Your gentle touch, your tender kiss","A feeling I would always miss","If you were ever far from me","You are my heart, you are my peace"]},
            {"type":"chorus",   "lines":["You are my world, you are my sky","The reason that I laugh and cry","Without you here I'm not complete","You are the rhythm of my heartbeat"]},
            {"type":"bridge",   "lines":["Tell me you will never leave","Promise me you will believe","In this love that we have made","In this light that will not fade"]},
            {"type":"chorus",   "lines":["You are my world, you are my sky","The reason that I laugh and cry","Without you here I'm not complete","You are the rhythm of my heartbeat"]},
            {"type":"outro",    "lines":["My world, my sky","My love, my life","You are everything","My everything"]},
        ]
    },
    {
        "title": "Close To You",
        "sections": [
            {"type":"verse",    "lines":["Every morning when I wake","The first thought is of you I take","Every evening when I sleep","Your memory is mine to keep"]},
            {"type":"prechorus","lines":["I have crossed a thousand miles","Just to see your beautiful smiles","Every sacrifice was worth","Every single moment on this earth"]},
            {"type":"chorus",   "lines":["I just want to be close to you","Feel your heartbeat, hear you breathe","Every moment that I'm with you","Is the only place I need to be"]},
            {"type":"verse",    "lines":["In your arms the world stands still","Time slows down against my will","Every second feels like gold","A love story yet to be told"]},
            {"type":"chorus",   "lines":["I just want to be close to you","Feel your heartbeat, hear you breathe","Every moment that I'm with you","Is the only place I need to be"]},
            {"type":"bridge",   "lines":["Never want to say goodbye","Never want to wonder why","All I know is I need you","Every single day I do"]},
            {"type":"chorus",   "lines":["I just want to be close to you","Feel your heartbeat, hear you breathe","Every moment that I'm with you","Is the only place I need to be"]},
            {"type":"outro",    "lines":["Close to you","Always close to you","My heart, my home","I'm never alone"]},
        ]
    },
    {
        "title": "Forever Is You",
        "sections": [
            {"type":"verse",    "lines":["I used to think that love was just a word","A pretty song that no one ever heard","But then you came and changed everything","Made my heart open up and want to sing"]},
            {"type":"prechorus","lines":["You are the calm inside the storm","The place where I am safe and warm","I never have to look too far","My love, my light, you are my star"]},
            {"type":"chorus",   "lines":["Forever is you, forever is this","The warmth of your hug, the touch of your kiss","No matter how far the journey may go","Forever is you, I want you to know"]},
            {"type":"verse",    "lines":["Through every season, every year","I want to know that you are near","Through every chapter of this life","I want you as my love, my wife"]},
            {"type":"chorus",   "lines":["Forever is you, forever is this","The warmth of your hug, the touch of your kiss","No matter how far the journey may go","Forever is you, I want you to know"]},
            {"type":"bridge",   "lines":["Write your name across my heart","Promise me we'll never part","In a world that changes every day","My love for you will always stay"]},
            {"type":"chorus",   "lines":["Forever is you, forever is this","The warmth of your hug, the touch of your kiss","No matter how far the journey may go","Forever is you, I want you to know"]},
            {"type":"outro",    "lines":["Forever is you","Only you","My forever","My always"]},
        ]
    },
    {
        "title": "Every Breath",
        "sections": [
            {"type":"verse",    "lines":["I see you in the morning sun","I hear you when the day is done","Your laughter echoes in my mind","The sweetest sound I'll ever find"]},
            {"type":"prechorus","lines":["And every time I close my eyes","I see your face against the skies","You're not just someone that I love","You were sent to me from up above"]},
            {"type":"chorus",   "lines":["Every breath I take is yours","Every dream that I explore","Every wish upon a star","I'm so grateful that you are","The one who holds my hand tonight","The one who makes everything right"]},
            {"type":"verse",    "lines":["Your eyes reflect a thousand dreams","Love is deeper than it seems","When I'm with you all is clear","Nothing left for me to fear"]},
            {"type":"chorus",   "lines":["Every breath I take is yours","Every dream that I explore","Every wish upon a star","I'm so grateful that you are","The one who holds my hand tonight","The one who makes everything right"]},
            {"type":"bridge",   "lines":["If a lifetime isn't long enough","To show you all the ways I love","Then give me two, give me three","As long as you are here with me"]},
            {"type":"outro",    "lines":["Every breath is yours","Every heartbeat yours","My love, my life","You are everything"]},
        ]
    },
    {
        "title": "Take My Hand",
        "sections": [
            {"type":"verse",    "lines":["Standing at the edge of something new","All I know is I belong with you","Every road I've traveled led me here","To this moment, crystal bright and clear"]},
            {"type":"prechorus","lines":["I don't need a map or master plan","All I need is you to understand","That wherever life may take us both","You and I will face it, I will hold"]},
            {"type":"chorus",   "lines":["Take my hand and let's begin","A love story from deep within","Through the mountains, through the rain","Through the joy and through the pain","Take my hand, don't let me go","Into a love that we both know"]},
            {"type":"verse",    "lines":["In the silence between you and me","There's a language only we can see","Spoken in a glance, a smile, a sigh","Love that reaches past the open sky"]},
            {"type":"chorus",   "lines":["Take my hand and let's begin","A love story from deep within","Through the mountains, through the rain","Through the joy and through the pain","Take my hand, don't let me go","Into a love that we both know"]},
            {"type":"bridge",   "lines":["I have found my home in you","Everything I need is true","When you're near me I am whole","You complete my heart and soul"]},
            {"type":"chorus",   "lines":["Take my hand and let's begin","A love story from deep within","Through the mountains, through the rain","Through the joy and through the pain","Take my hand, don't let me go","Into a love that we both know"]},
            {"type":"outro",    "lines":["Take my hand","Never let go","My love, my life","My everything"]},
        ]
    },
]


def generate_lyrics(anthropic_api_key=None):
    if anthropic_api_key:
        try:
            return _claude_lyrics(anthropic_api_key)
        except Exception as e:
            print(f"  [lyrics] Claude failed ({str(e)[:60]}) — template")
    return _template_lyrics()


def _claude_lyrics(api_key):
    system = (
        "You are a romantic English songwriter. Write beautiful, emotional English-only "
        "romantic song lyrics (no Hindi, no Romanized Hindi). "
        "Return ONLY valid JSON. "
        'Format: {"title": "Song Title", "sections": ['
        '{"type": "verse|chorus|prechorus|bridge|outro", "lines": ["line1","line2","line3","line4"]}'
        ']}. Include: verse, prechorus, chorus, verse, chorus, bridge, chorus, outro. '
        "Write emotionally, poetically, like a hit romantic ballad."
    )
    themes = ["eternal love","first love","missing someone","togetherness",
              "soulmates","unconditional love","love at first sight"]
    user = f"Write a complete romantic song about: {random.choice(themes)}"
    headers = {"x-api-key":api_key,"anthropic-version":"2023-06-01","content-type":"application/json"}
    for model in CLAUDE_MODELS:
        try:
            r = requests.post(CLAUDE_API, headers=headers,
                json={"model":model,"max_tokens":1500,"system":system,
                      "messages":[{"role":"user","content":user}]}, timeout=40)
            if r.status_code == 200:
                raw  = r.json()["content"][0]["text"].strip()
                raw  = re.sub(r"^```json\s*|```$","",raw,flags=re.MULTILINE).strip()
                data = json.loads(raw)
                print(f"  [lyrics] Claude OK ({model}) ✓")
                return data
        except Exception as e:
            print(f"  [lyrics] {model}: {str(e)[:60]}")
    raise RuntimeError("Claude failed")


def _template_lyrics():
    song = random.choice(TEMPLATE_SONGS)
    print(f"  [lyrics] template: {song['title']} ✓")
    return song
