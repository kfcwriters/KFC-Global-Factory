import os
import requests
import sys

def create_video(topic, script, quality="720p"):
    api_key = os.getenv('ARCREEL_API_KEY')
    print(f"🎬 ArcReel Agent: Generating {quality} asset for {topic}...")
    
    url = "https://api.arcreel.ai/v1/projects"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    payload = {
        "name": topic,
        "script": script,
        "resolution": "1280x720" if quality == "720p" else "1920x1080",
        "template": "clinical_scientist_minimalist",
        "fps": 30
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        project_id = response.json().get('id')
        with open("render_id.txt", "w") as f: f.write(project_id)
        print(f"✅ 720p Project Queued: {project_id}")
    except Exception as e:
        print(f"❌ Render Error: {e}")

if __name__ == "__main__":
    create_video(sys.argv[1], sys.argv[2], sys.argv[3])
