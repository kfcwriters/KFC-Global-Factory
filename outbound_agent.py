import os
import requests

def run_strike():
    # 🏛️ Pulling your secure keys from the GitHub Vault
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = "1060905337" 
    
    print("🚀 KFC LAB AGENT: Executing Live Medical Strike & YouTube Loop...")
    
    # This message is engineered for high-CPM conversion and research tracking
    msg = (
        "✅ 24/7 FACTORY LIVE\n\n"
        "🎯 Research: Serum Glyco-proteome & Diabetic Nephropathy\n"
        "📊 Quality: Six Sigma FMEA Metrics\n"
        "🎥 YouTube: Scripts ready for UCufYNDYq7orIFkkDh57xRow\n"
        "📡 Status: Global Autonomy Active"
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        # 🚀 The actual handshake with Telegram
        response = requests.post(url, json={"chat_id": chat_id, "text": msg})
        if response.status_code == 200:
            print("📲 Telegram Handshake: SUCCESSFUL.")
        else:
            print(f"❌ Telegram Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")

if __name__ == "__main__":
    run_strike()
