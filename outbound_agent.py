import os
import requests

def run_strike():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = "1060905337" 
    
    print("🚀 KFC LAB AGENT: Connecting to 24/7 Global Factory...")
    
    msg = (
        "✅ FACTORY ONLINE: 24/7 Autonomy Confirmed.\n\n"
        "🎯 Ph.D. Focus: Serum Glyco-proteome\n"
        "🔬 Quality: Six Sigma FMEA Metrics\n"
        "🎥 YouTube: UCufYNDYq7orIFkkDh57xRow\n"
        "📡 Status: Global Strikes Active."
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        response = requests.post(url, json={"chat_id": chat_id, "text": msg}, timeout=10)
        if response.status_code == 200:
            print("📲 Telegram PING: SUCCESSFUL.")
        else:
            print(f"❌ Telegram Error: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")

if __name__ == "__main__":
    run_strike()
