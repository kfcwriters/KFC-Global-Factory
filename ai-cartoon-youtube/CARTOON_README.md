# AI Cartoon YouTube — Automated Pipeline (cartoon project)

Auto-generates and uploads short children's story episodes to YouTube
daily — free. AI-illustrated scenes with slow pan/zoom + narrated
story audio, stitched into video.

**This entire project lives inside the `ai-cartoon-youtube/` folder,
with every file uniquely named (`cartoon_*`), its own GitHub Actions
workflow file, and its own secret names. It will not touch, rename, or
overwrite anything from your other project(s) in this repo — including
the `ai-music-youtube/` music project, if that's also in this repo.**

| Step | Tool | Cost |
|---|---|---|
| Script | Groq API (free tier) | Free |
| Images | Pollinations.ai (free, no key) | Free |
| Voice | edge-tts (free, no key) | Free |
| Video assembly | ffmpeg | Free |
| Upload | YouTube Data API v3 | Free (~6 uploads/day) |
| Scheduler | GitHub Actions | Free (public repo) |

**Reality check:** this makes AI-illustrated scenes with camera
pan/zoom + narration — not fully hand-animated cartoons. That's what's
actually achievable free and automatable today.

---

## File map (all inside `ai-cartoon-youtube/`)

```
ai-cartoon-youtube/
├── scripts/
│   ├── cartoon_generate_script.py    ← Groq API story script
│   ├── cartoon_generate_images.py    ← Pollinations.ai scene images
│   ├── cartoon_generate_audio.py     ← edge-tts narration
│   ├── cartoon_assemble_video.py     ← ffmpeg pan/zoom + audio sync
│   └── cartoon_upload_youtube.py     ← YouTube Data API v3 upload
├── config/
│   └── cartoon_config.py             ← channel name, art style, voice, etc.
├── cartoon_main.py                   ← Main orchestrator
├── cartoon_requirements.txt
├── cartoon_get_youtube_refresh_token.py  ← Run once locally
└── CARTOON_README.md                 ← this file

.github/workflows/
└── cartoon_daily_upload.yml          ← Its own workflow, own name, runs independently
```

---

## One-time setup

### 1. Groq API key (free)
console.groq.com → sign up → create API key. You'll add it as secret `GROQ_API_KEY_CARTOON`.

### 2. YouTube API credentials
1. console.cloud.google.com → new project
2. APIs & Services → Library → enable **YouTube Data API v3**
3. OAuth consent screen → External → add your channel's Google account as Test user
4. Credentials → Create Credentials → OAuth client ID → **Desktop app** → download JSON → save as `ai-cartoon-youtube/cartoon_client_secret.json` (local only — already in `.gitignore`)
5. Locally, run:
   ```bash
   cd ai-cartoon-youtube
   pip install google-auth-oauthlib
   python cartoon_get_youtube_refresh_token.py
   ```
   It prints `YOUTUBE_CLIENT_ID_CARTOON`, `YOUTUBE_CLIENT_SECRET_CARTOON`, `YOUTUBE_REFRESH_TOKEN_CARTOON` — save these.

### 3. Add GitHub Secrets
**Settings → Secrets and variables → Actions → New repository secret.**
Names are namespaced so they can't collide with any other project's secrets in this repo:

| Secret name |
|---|
| `GROQ_API_KEY_CARTOON` |
| `YOUTUBE_CLIENT_ID_CARTOON` |
| `YOUTUBE_CLIENT_SECRET_CARTOON` |
| `YOUTUBE_REFRESH_TOKEN_CARTOON` |

### 4. Enable the workflow
**Actions** tab → find **"Daily Cartoon Episode (cartoon project)"** listed
separately from your other workflows → enable. Runs daily at 09:00 UTC,
or trigger manually with a custom topic via "Run workflow".

---

## Test locally first

```bash
cd ai-cartoon-youtube
pip install -r cartoon_requirements.txt
sudo apt install ffmpeg
export GROQ_API_KEY_CARTOON=your_key_here

python cartoon_main.py "a fox who learns to share" --no-upload
```
Check `cartoon_output/final_episode.mp4` before enabling real uploads.
Set `YOUTUBE_PRIVACY = "unlisted"` in `config/cartoon_config.py` to test a
real upload safely before going public.

---

## Customizing

Edit `config/cartoon_config.py` — channel name, art style (this text gets
appended to every image prompt, so it controls your whole show's look),
narration voice, scenes per episode, video size.

---

## Compliance notes

- Set `MADE_FOR_KIDS = True` in `cartoon_config.py` — required by
  YouTube/COPPA for children's content. Disables comments and
  personalized ads on the video.
- YouTube requires disclosure of realistic AI-generated/synthetic
  content — check YouTube Studio's content disclosure settings.
- Review episodes before making them fully public, especially early on.
- Free YouTube API quota (~10,000 units/day, ~6 uploads) is shared per
  YouTube account/project across **all** automations uploading to the
  same channel — keep that in mind if your music project uploads to the
  same channel on the same day.
