import requests
import random
import os

API_KEY = os.getenv("AYRSHARE_BRAND_TOKEN")

# THE VIRAL WEALTH LIBRARY (Updated with stable links)
viral_library = [
    {
        "title": "Clear Skin Secret: Minimalist 10% Niacinamide Serum ✨",
        "link": "https://www.amazon.in/dp/B08F97NH6P?tag=bansallab01-21", 
        "desc": "The #1 serum for 'Glass Skin' and oil control. #ad #SkincareHacks #ViralBeauty #Minimalist",
        "img": "https://m.media-amazon.com/images/I/71D0A8-v-8L.jpg"
    },
    {
        "title": "Aesthetic Room Upgrade: Smart LED Strips 💡",
        "link": "https://www.amazon.in/dp/B08L7STDM9?tag=bansallab01-21",
        "desc": "Upgrade your vibe instantly for under ₹1000. #ad #RoomMakeover #AestheticHome #Govee",
        "img": "https://m.media-amazon.com/images/I/81-0X-vU-DL.jpg"
    },
    {
        "title": "Zero-Waste Writing: Digital LCD RuffPad 📝",
        "link": "https://www.amazon.in/dp/B08XMS7G1C?tag=bansallab01-21",
        "desc": "The perfect tool for quick notes or kids' sketches. #ad #WorkFromHome #ParentingHacks #Portronics",
        "img": "https://m.media-amazon.com/images/I/61v-v-9-xLL.jpg"
    }
]

def post_viral_pin():
    if not API_KEY:
        print("Error: AYRSHARE_BRAND_TOKEN not found.")
        return

    item = random.choice(viral_library)
    
    payload = {
        "post": f"{item['title']}\n\n{item['desc']}\n\nShop here: {item['link']}",
        "platforms": ["pinterest"],
        "mediaUrls": [item['img']],
        "pinterestOptions": {
            "title": item['title'],
            "link": item['link'],
            "board": "Bansal Lab Approved" 
        }
    }
    
    headers = {'Authorization': f'Bearer {API_KEY}'}
    r = requests.post('https://api.ayrshare.com/api/post', json=payload, headers=headers)
    
    print(f"Post Attempt: {item['title']}")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

if __name__ == "__main__":
    post_viral_pin()
