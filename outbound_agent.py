import os
import requests

def run_strike():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = "1060905337" 
    
    print("🚀 KFC LAB AGENT: Initiating Diagnostic Strike...")
    
    msg = "✅ FACTORY STATUS: 24/7 Autonomy Confirmed.\n\nBiochemistry Topics: Glyco-proteomics & Six Sigma Quality.\nYouTube channel: UCufYNDYq7orIFkkDh57xRow"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        response = requests.post(url, json={"chat_id": chat_id, "text": msg})
        if response.status_code == 200:
            print("📲 Telegram Handshake: SUCCESSFUL.")
        else:
            print(f"❌ Telegram Handshake: FAILED. Error: {response.text}")
    except Exception as e:
        print(f"❌ System Error: {str(e)}")

if __name__ == "__main__":
    run_strike()
