"""
Central config for the cartoon channel.
Edit this file to define your channel's identity, character style,
and episode settings. Keeping the style prompt consistent is what
makes random AI images look like "the same cartoon" instead of
random unrelated pictures.
"""

# ---- Channel / brand ----
CHANNEL_NAME = "Little Story Friends"          # used in video title/description
EPISODE_LENGTH_SCENES = 6                       # how many scenes per episode
LANGUAGE = "en"                                 # for TTS voice selection

# ---- Visual style lock (VERY important for consistency) ----
# This text is appended to EVERY image prompt so all scenes in an
# episode (and across episodes) look like the same show.
ART_STYLE = (
    "children's cartoon illustration, flat vector style, soft pastel colors, "
    "thick clean outlines, rounded friendly shapes, simple background, "
    "storybook style, no text, no watermark"
)

# A fixed "seed" keeps Pollinations.ai's output more consistent run-to-run.
# You can still get variety per scene because the prompt text changes.
IMAGE_SEED = 42

# ---- Narration voice (edge-tts voice name) ----
# Run `edge-tts --list-voices` to see options. Good kid-friendly picks:
TTS_VOICE = "en-US-AnaNeural"     # friendly, youthful female voice
# Alternatives: "en-US-JennyNeural", "en-GB-SoniaNeural", "en-US-GuyNeural"

# ---- Video settings ----
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
FPS = 30
KEN_BURNS_ZOOM = 1.15   # how much each image slowly zooms in over its scene

# ---- YouTube upload settings ----
YOUTUBE_CATEGORY_ID = "1"     # "Film & Animation"
YOUTUBE_PRIVACY = "public"    # "public" | "unlisted" | "private" (test with unlisted first!)
MADE_FOR_KIDS = True
