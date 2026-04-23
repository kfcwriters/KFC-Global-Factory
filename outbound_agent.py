import os
import requests

def run_strike():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = "1060905337" # Your verified ID
    
    print("🚀 KFC GLOBAL FACTORY: Initiating 24/7 Strike...")
    
    msg = "🚀 KFC FACTORY ONLINE: System is now running 24/7. First medical strike complete."
    
    # Send to Telegram
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": msg}
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("✅ Telegram Handshake Successful!")
    else:
        print(f"❌ Telegram Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    run_strike()
