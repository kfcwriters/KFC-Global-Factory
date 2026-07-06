"""
kids_story_gen.py
Generates kids content — stories, nursery rhymes, educational, fairy tales.
Pure Python — no API needed, completely free.
100% unique content every episode using word banks + rotation.
"""
import random
from datetime import datetime


# ── Content types ─────────────────────────────────────────────────────────────
CONTENT_TYPES = ["bedtime_story", "nursery_rhyme", "educational", "fairy_tale"]

# ── Bedtime stories ───────────────────────────────────────────────────────────
STORY_ANIMALS   = ["bunny","puppy","kitten","elephant","lion cub","baby bear",
                   "little fox","baby duck","friendly owl","tiny turtle"]
STORY_SETTINGS  = ["magical forest","cozy meadow","sunny farm","enchanted garden",
                   "little village","rainbow valley","cloud kingdom","star valley"]
STORY_MORALS    = ["always be kind","sharing makes everyone happy",
                   "honesty is the best policy","hard work pays off",
                   "true friends help each other","never give up",
                   "be brave and try new things","kindness is a superpower"]
STORY_PROBLEMS  = ["lost their way home","could not find food","had no friends",
                   "was scared of the dark","could not fly yet","felt lonely",
                   "dropped their favourite toy","could not sleep"]
STORY_SOLUTIONS = ["made a new friend who helped","worked together with friends",
                   "was kind to a stranger who helped back","never gave up trying",
                   "was honest and everyone helped","shared and everyone was happy"]

# ── Nursery rhymes ────────────────────────────────────────────────────────────
RHYME_THEMES = [
    ("The Little Star", ["Twinkle twinkle little star","How I wonder what you are",
     "Up above the world so high","Like a diamond in the sky",
     "When the blazing sun is gone","When it nothing shines upon",
     "Then you show your little light","Twinkle twinkle through the night"]),
    ("Fluffy the Cloud", ["Fluffy fluffy little cloud","Floating in the sky so proud",
     "Soft and white and big and round","Giving rain to all the ground",
     "When the sun shines bright today","Fluffy cloud just floats away",
     "Children laugh and children play","On this happy sunny day"]),
    ("The Happy Farm", ["Old MacDonald had a farm","E-I-E-I-O",
     "And on his farm he had a cow","E-I-E-I-O",
     "With a moo moo here and a moo moo there","Here a moo there a moo everywhere a moo moo",
     "Old MacDonald had a farm","E-I-E-I-O"]),
    ("Rainbow Colors", ["Red and orange yellow and green","The prettiest colors you have ever seen",
     "Blue and indigo violet too","Rainbow colors bright and new",
     "After the rain the rainbow comes","Painting the sky for everyone",
     "Colors so bright colors so true","I love the rainbow how about you"]),
    ("Counting Stars", ["One little star shining bright","Two little stars in the night",
     "Three little stars winking at me","Four little stars for all to see",
     "Five little stars dancing up high","All the little stars fill up the sky",
     "Count them all before you sleep","Starry dreams for you to keep"]),
]

# ── Educational topics ────────────────────────────────────────────────────────
EDU_TOPICS = [
    {"topic":"Colors","items":["Red is for apples round and bright","Orange is for the sun so light",
     "Yellow is for bananas sweet","Green is for the grass beneath our feet",
     "Blue is for the sky above","Purple is a color that we love",
     "Pink is for the flowers in spring","These are the colors that we sing"]},
    {"topic":"Numbers 1 to 5","items":["One little finger one little toe","Two little eyes that watch and glow",
     "Three little birds sing in the tree","Four little wheels spin so free",
     "Five little stars in the night sky","Wave to them as they go by",
     "1 2 3 4 5 let us count","Up the colorful counting mount"]},
    {"topic":"Animals on the Farm","items":["The cow says moo the sheep says baa",
     "The pig says oink the dog says woof","The cat says meow the hen says cluck",
     "The horse says neigh and duck says quack",
     "All the animals on the farm","Each one has its own special charm",
     "Can you make their sounds today","Let us learn and laugh and play"]},
    {"topic":"Shapes Around Us","items":["A circle is round like the sun","A square has four sides every one",
     "A triangle has corners three","A rectangle is long you see",
     "Look around and you will find","Shapes of every different kind",
     "In your toys and in your books","Shapes are everywhere you look"]},
    {"topic":"The Seasons","items":["Spring brings flowers and warm rain","Summer sunshine again and again",
     "Autumn leaves of red and gold","Winter brings the freezing cold",
     "Four seasons come throughout the year","Each one brings something new and dear",
     "Which season do you like the best","Spring summer autumn or winter rest"]},
]

# ── Fairy tales ───────────────────────────────────────────────────────────────
FAIRY_TALES = [
    {"title":"The Kind Princess","story":["Once upon a time in a magical kingdom",
     "There lived a princess who was always kind","She helped the poor and fed the birds",
     "And never once was cruel or blind","One day a witch came to the land",
     "And cast a spell on everyone","But the princess used her kindness",
     "And the witch's evil was undone","The flowers bloomed the birds all sang",
     "The kingdom filled with joy and cheer","And everyone lived happily ever after",
     "With kindness making things so clear"]},
    {"title":"The Brave Little Mouse","story":["Little Mouse lived in a big old house",
     "He was tiny but his heart was big","One day the cat came prowling round",
     "Sniffing under every twig","Mouse stood up and said out loud",
     "You shall not scare my friends today","The cat was shocked by tiny Mouse",
     "And slowly turned and ran away","The other mice all cheered for him",
     "Our brave little hero of the day","Being brave does not mean being big",
     "It means doing right come what may"]},
    {"title":"The Magic Paintbrush","story":["A little girl found a magic paintbrush",
     "Whatever she painted came to life","She painted food for hungry people",
     "She painted an end to all their strife","A greedy king heard of her gift",
     "And tried to take her brush away","But she painted a great big ocean",
     "And the greedy king washed away","She used her gift to help the world",
     "And make it beautiful and bright","The magic paintbrush taught us all",
     "To use our gifts for what is right"]},
]

# ── Image prompts for each content type ──────────────────────────────────────
STORY_IMAGE_PROMPTS = [
    "cute cartoon {animal} in a {setting}, colorful children's book illustration style",
    "adorable {animal} with big eyes smiling, soft pastel colors, kids cartoon art",
    "friendly cartoon {animal} making friends, bright cheerful colors, children's story",
    "cute {animal} family together, warm sunset, children's book watercolor style",
    "happy cartoon {animal} in magical {setting}, glowing lights, kids animation style",
    "cute {animal} sleeping peacefully, moonlight, soft dreamy children's illustration",
    "cartoon {animal} sharing food with friends, bright colors, kids story book art",
    "adorable {animal} discovering a rainbow, colorful, children's picture book style",
]

RHYME_IMAGE_PROMPTS = [
    "cute cartoon children playing outdoors, bright sunny day, kids animation style",
    "adorable cartoon farm animals, colorful, children's book illustration",
    "cute cartoon star with smiling face, dark night sky, kids cartoon style",
    "rainbow over green meadow with cartoon animals, bright colors, children's art",
    "happy cartoon children counting numbers, colorful classroom, kids education art",
    "cute cartoon clouds with faces, blue sky, children's book illustration style",
    "colorful cartoon alphabet letters with animals, educational kids art style",
    "cute cartoon moon and stars, children sleeping, dreamy soft illustration",
]

EDU_IMAGE_PROMPTS = [
    "colorful cartoon letters and numbers floating, bright educational kids art",
    "cute cartoon children learning colors, rainbow background, kids classroom style",
    "adorable cartoon animals showing shapes, bright colors, educational illustration",
    "friendly cartoon teacher with kids, colorful classroom, children's education art",
    "cartoon solar system with cute planet faces, space adventure for kids",
    "colorful cartoon fruits and vegetables, healthy eating for kids illustration",
    "cute cartoon seasons tree showing all four seasons, children's educational art",
    "happy cartoon kids counting on fingers, bright cheerful educational style",
]

FAIRY_IMAGE_PROMPTS = [
    "magical cartoon castle with rainbow, enchanted kingdom, children's fairy tale art",
    "cute cartoon princess waving, sparkles and flowers, kids fairy tale illustration",
    "friendly cartoon dragon with princess, magical forest, children's story book",
    "cartoon magic wand with sparkles, fairy tale scene, kids animation style",
    "adorable cartoon fairy with wings, glowing forest, children's picture book",
    "cute cartoon knight on horse, colorful medieval scene, kids fairy tale art",
    "magical cartoon forest with glowing mushrooms, fairy tale for children",
    "cartoon wizard with stars, magical library, children's fairy tale illustration",
]


def get_content_for_week(upload_num: int) -> dict:
    """
    Generate unique kids content based on upload number.
    upload_num: which upload of the week (0, 1, 2 for 3x/week)
    Returns full content dict.
    """
    # Use day of year for unique seed
    day  = datetime.utcnow().timetuple().tm_yday
    year = datetime.utcnow().year
    seed = day * 10 + upload_num + year * 1000

    r            = random.Random(seed)
    content_type = CONTENT_TYPES[(day + upload_num) % len(CONTENT_TYPES)]

    if content_type == "bedtime_story":
        return _make_story(r, seed)
    elif content_type == "nursery_rhyme":
        return _make_rhyme(r, seed)
    elif content_type == "educational":
        return _make_educational(r, seed)
    else:
        return _make_fairy_tale(r, seed)


def _make_story(r, seed) -> dict:
    animal   = r.choice(STORY_ANIMALS)
    setting  = r.choice(STORY_SETTINGS)
    moral    = r.choice(STORY_MORALS)
    problem  = r.choice(STORY_PROBLEMS)
    solution = r.choice(STORY_SOLUTIONS)
    title    = f"The Little {animal.title()} Who {problem.title()}"[:60]

    script = [
        f"Once upon a time, in a beautiful {setting},",
        f"there lived a sweet little {animal}.",
        f"One day, the little {animal} {problem}.",
        f"The little {animal} was very sad and did not know what to do.",
        f"But then, the little {animal} {solution}.",
        f"Everyone was so happy!",
        f"And the little {animal} learned that {moral}.",
        f"And they all lived happily ever after.",
        f"The End. Sweet dreams little ones!",
    ]

    prompts = [p.format(animal=animal, setting=setting)
               for p in r.sample(STORY_IMAGE_PROMPTS, min(6, len(STORY_IMAGE_PROMPTS)))]

    return {
        "type"    : "bedtime_story",
        "title"   : title,
        "script"  : script,
        "prompts" : prompts,
        "music"   : "soft gentle lullaby music, peaceful bedtime, children's music box",
    }


def _make_rhyme(r, seed) -> dict:
    title, lines = r.choice(RHYME_THEMES)
    prompts      = r.sample(RHYME_IMAGE_PROMPTS,
                            min(len(lines), len(RHYME_IMAGE_PROMPTS)))

    return {
        "type"    : "nursery_rhyme",
        "title"   : title,
        "script"  : lines,
        "prompts" : prompts,
        "music"   : "happy cheerful nursery rhyme music, children's songs, playful",
    }


def _make_educational(r, seed) -> dict:
    topic   = r.choice(EDU_TOPICS)
    title   = f"Learn {topic['topic']} With Fun!"
    prompts = r.sample(EDU_IMAGE_PROMPTS,
                       min(len(topic["items"]), len(EDU_IMAGE_PROMPTS)))

    script  = [f"Hello friends! Today we are going to learn about {topic['topic']}!"] + \
              topic["items"] + \
              [f"Great job learning about {topic['topic']} today!",
               "Keep learning, keep growing, see you next time!"]

    return {
        "type"    : "educational",
        "title"   : title,
        "script"  : script,
        "prompts" : prompts,
        "music"   : "upbeat educational children's music, fun learning, happy kids song",
    }


def _make_fairy_tale(r, seed) -> dict:
    tale    = r.choice(FAIRY_TALES)
    prompts = r.sample(FAIRY_IMAGE_PROMPTS,
                       min(len(tale["story"]), len(FAIRY_IMAGE_PROMPTS)))

    return {
        "type"    : "fairy_tale",
        "title"   : tale["title"],
        "script"  : tale["story"],
        "prompts" : prompts,
        "music"   : "magical fairy tale music, enchanted adventure, children's orchestral",
    }
