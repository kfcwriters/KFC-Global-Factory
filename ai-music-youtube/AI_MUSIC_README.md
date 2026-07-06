# AI Music YouTube — Automated Pipeline (music project)

Auto-generates and uploads AI music videos to YouTube daily — **free**.

```
Text prompt → MusicGen → SDXL images → FFmpeg video → YouTube
```

**This entire project lives inside the `ai-music-youtube/` folder, with
every file uniquely named (`ai_music_*`, `music_*`), and its own GitHub
Actions workflow file with its own name and its own secret names. It
will not touch, rename, or overwrite anything from your other
project(s) in this repo.**

| Step | Tool | Cost |
|------|------|------|
| Generate music | HuggingFace MusicGen API | Free |
| Generate images | HuggingFace SDXL API | Free |
| Generate title/tags | Claude API (optional) | Free tier |
| Create thumbnail | Pillow | Free |
| Assemble video | FFmpeg | Free |
| Upload to YouTube | YouTube Data API v3 | Free (~6 videos/day) |
| Runs automatically | GitHub Actions | Free (public repo) |

**Reality check on "free":** HuggingFace's free serverless Inference API
for MusicGen/SDXL can be slow to warm up (503 errors) and its policies
around free access to larger models change over time. Both `music_gen.py`
and `image_gen.py` retry automatically and fall back to a procedurally
generated tone / gradient image if the API is unavailable, so the
pipeline always finishes a video — but if HF is unreliable for you, that
fallback content will look/sound noticeably simpler than true MusicGen/SDXL
output.

---

## File map (all inside `ai-music-youtube/`)

```
ai-music-youtube/
├── src/
│   ├── music_gen.py           ← HuggingFace MusicGen API + fallback
│   ├── image_gen.py           ← HuggingFace SDXL API + fallback
│   ├── video_assembly.py      ← FFmpeg video builder
│   ├── metadata_gen.py        ← Claude API / template titles+tags
│   ├── thumbnail_gen.py       ← Pillow thumbnail
│   └── youtube_upload.py      ← YouTube Data API v3 upload
├── config/
│   └── music_niches.json      ← Edit to customise your channel content
├── ai_music_pipeline.py       ← Main orchestrator
├── ai_music_requirements.txt
├── ai_music_setup_youtube_auth.py  ← Run once locally to get credentials
└── AI_MUSIC_README.md         ← this file

.github/workflows/
└── music_daily_upload.yml     ← Its own workflow, own name, runs independently
```

---

## One-time setup

### 1. HuggingFace token (free)
1. Create an account at huggingface.co
2. Settings → Access Tokens → New token → Role: **Read**
3. You'll add it as secret `HF_TOKEN`

### 2. YouTube API credentials
1. console.cloud.google.com → new project (e.g. "AI Music Bot")
2. APIs & Services → Library → enable **YouTube Data API v3**
3. APIs & Services → Credentials → Create Credentials → OAuth client ID → **Desktop app** → download JSON → save as `ai-music-youtube/client_secrets.json` (local only, never commit — it's already in `.gitignore`)
4. OAuth consent screen → add your email as Test user → set Publishing status to **In production** (avoids the 7-day refresh-token expiry)

### 3. Generate credentials locally (once)
```bash
cd ai-music-youtube
pip install google-auth-oauthlib
python ai_music_setup_youtube_auth.py
```
Log in via the browser window that opens, then copy the full JSON block it prints.

### 4. Add GitHub Secrets
**Settings → Secrets and variables → Actions → New repository secret.**
Use these exact names — chosen to be distinct from any secrets your other
project(s) in this repo may already use:

| Secret name | Value |
|---|---|
| `HF_TOKEN` | Your HuggingFace token |
| `YOUTUBE_CREDENTIALS_MUSIC` | Full JSON block from step 3 |
| `ANTHROPIC_API_KEY` | (optional) Claude API key, for better titles |

### 5. Enable the workflow
Go to the **Actions** tab → you'll see **"Daily AI Music Upload (music project)"**
listed separately from your other workflows → enable it. It runs daily at
10:00 UTC, and can also be triggered manually with a "Run workflow" button.

---

## Testing before it goes live

```bash
cd ai-music-youtube
pip install -r ai_music_requirements.txt
sudo apt install ffmpeg     # or brew install ffmpeg
export HF_TOKEN=your_token_here

python ai_music_pipeline.py --test
```
Check `ai_music_output/final_video.mp4` before enabling real uploads.
You can also force a specific niche while testing:
```bash
python ai_music_pipeline.py --test --niche 3
```

Or trigger it from GitHub: **Actions → Daily AI Music Upload (music project) →
Run workflow → test_mode: true** — the finished video downloads from the
run's **Artifacts** section instead of uploading to YouTube.

---

## Customizing your channel

Edit `config/music_niches.json` — add/remove niches, change music/image
prompts. The pipeline rotates through them by day of year (or use `--niche N`
to force one).

---

## Compliance notes

- YouTube requires disclosure of realistic AI-generated/synthetic content — the auto-generated description already notes AI-assisted content; double check YouTube Studio's content disclosure settings too.
- Custom thumbnails require a phone-verified YouTube account (`youtube.com/verify`) — otherwise `youtube_upload.py` will skip setting one and continue without failing the run.
- Free YouTube API quota (~10,000 units/day) allows roughly 6 uploads/day across **all** projects using the same YouTube account/quota — keep that in mind if your other project in this repo also uploads to the same channel/project on the same day.
