import requests
import random
import os

# Safely pull your key from GitHub Secrets
API_KEY = os.getenv("AYRSHARE_BRAND_TOKEN")

# YOUR VIRAL WEALTH LIBRARY
viral_library = [
    {
        "title": "Clear Skin Secret: Minimalist 10% Niacinamide Serum ✨",
        "link": "https://amzn.to/4uhA3NP", 
        "desc": "The #1 serum for 'Glass Skin' and oil control. A must-have for your 2026 routine! #ad #SkincareHacks #ViralBeauty #Minimalist",
        "img": "https://m.media-amazon.com/images/I/71D0A8-v-8L.jpg"
    },
    {
        "title": "Aesthetic Room Upgrade: Smart LED Strips 💡",
        "link": "https://amzn.to/4wbvqH9",
        "desc": "Upgrade your vibe instantly for under ₹1000. App-controlled with 16M colors. #ad #RoomMakeover #AestheticHome #Govee",
        "img": "https://m.media-amazon.com/images/I/81-0X-vU-DL.jpg"
    },
    {
        "title": "Zero-Waste Writing: Digital LCD RuffPad 📝",
        "link": "https://amzn.to/4tVPLP1",
        "desc": "The perfect tool for quick notes or kids' sketches. Portable and eco-friendly! #ad #WorkFromHome #ParentingHacks #Portronics",
        "img": "https://m.media-amazon.com/images/I/61v-v-9-xLL.jpg"
    }
]

def post_viral_pin():
    if not API_KEY:
        print("Error: AYRSHARE_BRAND_TOKEN not found in Secrets.")
        return

    item = random.choice(viral_library)
    
    # Updated Payload with Pinterest Board requirement
    payload = {
        "post": f"{item['title']}\n\n{item['desc']}\n\nShop here: {item['link']}",
        "platforms": ["pinterest"],
        "mediaUrls": [item['img']],
        "pinterestOptions": {
            "title": item['title'],
            "link": item['link'],
            "boardId": "BansalLab_Wealth" # Ensure this board exists on your Pinterest
        }
    }
    
    headers = {'Authorization': f'Bearer {API_KEY}'}
    r = requests.post('https://api.ayrshare.com/api/post', json=payload, headers=headers)
    
    if r.status_code == 200:
        print(f"Success! Posted: {item['title']}")
    else:
        print(f"Failed: {item['title']} - Status: {r.status_code}")
        print(f"Response: {r.text}")

if __name__ == "__main__":
    post_viral_pin()
