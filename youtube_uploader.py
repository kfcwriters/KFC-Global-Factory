import os
import subprocess
from gtts import gTTS
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_master_script():
    topic = "PHD RESEARCH: SIGMA METRIC ANALYSIS"
    # Word-level segments with precise timing for 'decent' size text
    sync_segs = [
        {"text": "WELCOME TO THE KFC LAB", "start": 0, "end": 4},
        {"text": "ADVANCED SIGMA METRICS", "start": 4, "end": 9},
        {"text": "ANALYTICAL PRECISION", "start": 9, "end": 14},
        {"text": "WORLD-CLASS STANDARDS", "start": 14, "end": 20}
    ]
    script = "Welcome to the KFC Lab. Today we analyze advanced Sigma Metrics for analytical precision and world-class standards."
    return {"t": topic, "s": script, "sync": sync_segs}

def render_720p(lecture):
    print("🎬 RENDERING: Professional Word-Synced PhD Broadcast...")
    tts = gTTS(text=lecture['s'], lang='en')
    tts.save("master_voice.mp3")

    # Fontsize 75: 'Decent' size, clearly visible but not overwhelming
    filters = []
    for s in lecture['sync']:
        filters.append(
            f"drawtext=text='{s['text']}':fontcolor=white:fontsize=75:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.6:enable='between(t,{s['start']},{s['end']})'"
        )
    filter_chain = ",".join(filters)
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=22",
        "-i", "master_voice.mp3",
        "-vf", (
            f"drawgrid=w=100:h=100:t=2:c=white@0.1, "
            f"drawtext=text='PHD RESEARCH SERIES':fontcolor=gold:fontsize=35:x=50:y=50, "
            f"{filter_chain}"
        ),
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "synced_lecture.mp4"
    ]
    subprocess.run(cmd, check=True)

# ... (Upload function remains the same, checking for quota) ...
