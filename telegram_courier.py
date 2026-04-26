import os, requests

def send():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendVideo"
    with open("final_video.mp4", "rb") as v:
        requests.post(url, data={'chat_id': chat_id, 'caption': "🔬 PHD MASTERCLASS READY"}, files={'video': v})
    print("✅ COURIER: Delivered to Telegram.")

if __name__ == "__main__":
    send()
