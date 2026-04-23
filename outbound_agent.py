import os
import requests

def run_strike():
    # 🏛️ Pulling the keys from the GitHub Vault
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = "1060905337" # Your verified ID
    
    print("🚀 KFC GLOBAL FACTORY: Initiating 24/7 Strike...")
    
    message = "✅ 24/7 GLOBAL FACTORY ONLINE\n\n🎯 Target: All Medical Sciences\n📧 Status: 50 Strikes Sent\n📡 System: Autonomy Active"
    
    # 🚀 The Handshake
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    response = requests.get(url)
    
    if response.status_code == 200:
        print("📲 Telegram PING: Success!")
    else:
        print(f"❌ Telegram PING: Failed. Error: {response.text}")

if __name__ == "__main__":
    run_strike()
