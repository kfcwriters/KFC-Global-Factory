# 🎵 AI Music YouTube — Fully Automated Pipeline

Auto-generates and uploads AI music videos to YouTube every day — **completely free**.

```
Text prompt → MusicGen → SDXL images → FFmpeg video → YouTube
```

---

## What It Does (Daily, Automatically)

| Step | Tool | Cost |
|------|------|------|
| 🎵 Generate music | HuggingFace MusicGen API | Free |
| 🖼️ Generate images | HuggingFace SDXL API | Free |
| 📝 Generate title/tags | Claude API (optional) | Free tier |
| 🖼️ Create thumbnail | Pillow | Free |
| 🎬 Assemble video | FFmpeg | Free |
| 📤 Upload to YouTube | YouTube Data API v3 | Free (~6 videos/day) |
| ⚙️ Runs automatically | GitHub Actions | Free (public repo) |

---

## One-Time Setup (~30 minutes)

### Step 1 — Fork this repo

Click **Fork** on GitHub. Keep it **Public** (GitHub Actions is unlimited for public repos).

---

### Step 2 — HuggingFace Token (free)

1. Create account at [huggingface.co](https://huggingface.co)
2. Go to **Settings → Access Tokens → New token**
3. Role: **Read**
4. Copy the token — you'll add it as `HF_TOKEN` in Step 5

---

### Step 3 — YouTube API Setup (free)

#### 3a. Create a Google Cloud project
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g. "AI Music Bot")

#### 3b. Enable YouTube Data API v3
1. APIs & Services → **Library**
2. Search "YouTube Data API v3" → **Enable**

#### 3c. Create OAuth credentials
1. APIs & Services → **Credentials** → **Create Credentials** → **OAuth client ID**
2. Application type: **Desktop app**
3. Name: anything (e.g. "AI Music Bot")
4. Click **Download JSON** → save as `client_secrets.json` in your local clone

#### 3d. Configure OAuth consent screen
1. APIs & Services → **OAuth consent screen**
2. Add your YouTube account email as a **Test user**
3. Set **Publishing status → In production** *(prevents the 7-day refresh token expiry)*
   - Click "Publish App" → confirm — this is fine for your own personal use

---

### Step 4 — Generate YouTube credentials (run locally once)

```bash
# Clone your fork locally
git clone https://github.com/YOUR_USERNAME/ai-music-youtube
cd ai-music-youtube

# Install the one dependency needed for this step
pip install google-auth-oauthlib

# Place client_secrets.json in this directory, then run:
python setup_youtube_auth.py
```

- A browser tab opens → log in with your YouTube channel account
- Copy the entire JSON block printed in the terminal
- You'll paste it as `YOUTUBE_CREDENTIALS` in the next step

---

### Step 5 — Add GitHub Secrets

Go to your forked repo on GitHub:
**Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Value | Required |
|-------------|-------|----------|
| `HF_TOKEN` | Your HuggingFace token (Step 2) | ✅ Yes |
| `YOUTUBE_CREDENTIALS` | Full JSON from Step 4 | ✅ Yes |
| `ANTHROPIC_API_KEY` | Claude API key (for better titles/tags) | ⬜ Optional |

---

### Step 6 — Enable GitHub Actions

1. Go to **Actions** tab in your fork
2. Click **"I understand my workflows, go ahead and enable them"**
3. The workflow runs daily at **10:00 AM UTC (3:30 PM IST)**

---

## Manual Run / Testing

### Test without uploading (saves video locally as artifact):
1. Go to **Actions → 🎵 Daily AI Music Upload → Run workflow**
2. Set `test_mode` to `true`
3. Download the generated video from the **Artifacts** section after it finishes

### Force a specific niche:
- Set `niche_index` (0–5) when triggering manually

### Run locally:
```bash
export HF_TOKEN="hf_..."
export YOUTUBE_CREDENTIALS='{"token": "...", "refresh_token": "...", ...}'
export ANTHROPIC_API_KEY="sk-ant-..."   # optional

python pipeline.py            # full run + upload
python pipeline.py --test     # generate only, saved to ./output/
python pipeline.py --niche 3  # use niche index 3
```

---

## Customise Your Channel

Edit `config/niches.json` to change the content:

```json
{
  "niches": [
    {
      "name": "thyroid health music",
      "music_prompts": [
        "gentle healing music with 432hz frequency for thyroid wellness",
        "calming ambient music for hormonal balance and stress relief"
      ],
      "image_prompts": [
        "peaceful nature scene with morning light and flowing water",
        "serene meditation space with plants and soft lighting"
      ]
    }
  ]
}
```

The pipeline rotates through all niches by day — add as many as you like.

---

## Project Structure

```
ai-music-youtube/
├── .github/workflows/
│   └── daily_upload.yml      ← GitHub Actions (runs daily)
├── src/
│   ├── music_gen.py           ← HuggingFace MusicGen API
│   ├── image_gen.py           ← HuggingFace SDXL API
│   ├── video_assembly.py      ← FFmpeg video builder
│   ├── metadata_gen.py        ← Claude API / template titles+tags
│   ├── thumbnail_gen.py       ← Pillow thumbnail
│   └── youtube_upload.py      ← YouTube Data API v3 upload
├── config/
│   └── niches.json            ← Edit to customise your channel
├── pipeline.py                ← Main orchestrator
├── requirements.txt
├── setup_youtube_auth.py      ← Run once locally to get credentials
└── README.md
```

---

## Free Tier Limits

| Limit | Impact | Workaround |
|-------|--------|------------|
| YouTube API: ~6 uploads/day | Daily posting is fine | Use 2 Google accounts for more |
| HuggingFace: rate limited | Retries built-in | Rarely an issue for 1/day |
| GitHub Actions: unlimited | ✅ No limit for public repos | — |

---

## Troubleshooting

**`HF_TOKEN not set`** — Add it to GitHub Secrets (Step 5)

**`YOUTUBE_CREDENTIALS not set`** — Run `setup_youtube_auth.py` (Step 4)

**`403: The caller does not have permission`** — Make sure you added your account as a Test user in the OAuth consent screen

**`quotaExceeded`** — YouTube API daily quota hit. Wait until midnight Pacific time for reset.

**Thumbnail not set** — YouTube requires a verified phone number on your account for custom thumbnails. Verify at [youtube.com/verify](https://www.youtube.com/verify).

**MusicGen returns 503** — Model is warming up on HuggingFace. The pipeline retries automatically (up to 6 times with delays). This is normal.

---

## Niche Ideas for Health/Wellness Channels

Especially relevant if your audience overlaps with metabolic health or clinical nutrition:

- `"thyroid health and healing music"` — targets people with hypothyroidism searching for wellness content
- `"hormonal balance meditation"` — PCOS, menopause, perimenopause audiences
- `"kidney health relaxation music"` — CKD patient wellbeing
- `"medical student study music"` — captures a huge study-music search demographic
- `"metabolic health focus music"` — diabetes, insulin resistance niche

Each channel can funnel viewers to your nutrition coaching practice via the video description.
