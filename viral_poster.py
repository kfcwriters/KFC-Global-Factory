import requests
import os

API_KEY = os.getenv("AYRSHARE_BRAND_TOKEN")

def find_my_board_id():
    if not API_KEY:
        print("Error: API Key missing.")
        return

    # This asks Ayrshare to look at your Pinterest account
    headers = {'Authorization': f'Bearer {API_KEY}'}
    r = requests.get('https://api.ayrshare.com/api/profiles', headers=headers)
    
    print("--- SEARCHING FOR YOUR BOARD ID ---")
    print(f"Server Response: {r.text}")
    print("-----------------------------------")
    print("Look for a long 18-digit number in the text above.")

if __name__ == "__main__":
    find_my_board_id()
