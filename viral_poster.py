import requests
import random
import os

# Safely pull your new API key from GitHub Secrets
API_KEY = os.getenv("AYRSHARE_BRAND_TOKEN")

# THE VIRAL WEALTH LIBRARY
# I have pre-filled these with top 2026 trends. 
# REPLACE the 'link' with your actual Amazon SiteStripe Short Links.
viral_library = [
    {
        "title": "Viral 10% Niacinamide Serum ✨",
        "link": "https://amzn.to/your-link-1", 
        "desc": "The secret to 'Glass Skin' for under ₹600. A must-have for your 2026 routine! #ad #SkincareHacks #ViralBeauty",
        "img": "https://m.media-amazon.com/images/I/71D0A8-v-8L.jpg"
    },
    {
        "title": "Aesthetic Smart LED Strip Lights 💡",
        "link": "https://amzn.to/your-link-2",
        "desc": "Upgrade your room vibe instantly. App-controlled and budget-friendly. #ad #RoomMakeover #AestheticHome",
        "img": "https://m.media-amazon.com/images/I/81-0X-vU-DL.jpg"
    },
    {
        "title": "Digital LCD Memo Tablet 📝",
        "link": "https://amzn.to/your-link-3",
        "desc": "The ultimate productivity hack for notes or kids' sketches. Eco-friendly! #ad #WorkFromHome #AmazonFinds",
        "img": "https://m.media-amazon.com/images/I/61v-v-9-xLL.jpg"
    },
    {
        "title": "Invisible Acne Relief Patches 🩹",
        "link": "https://amzn.to/your-link-4",
        "desc": "Flatten pimples overnight! These are a literal lifesaver for clear skin. #ad #BeautySecrets #Skincare",
        "img": "https://m.media-amazon.com/images/I/61v-v-8-xLL.jpg"
    }
]

def post_to_pinterest():
    if not API_KEY:
        print("Error: AYRSHARE_BRAND_TOKEN not found in Secrets.")
        return

    item = random.choice(viral_library)
    payload = {
        "post": f"{item['title']}\n\n{item['desc']}\n\nShop here: {item['link']}",
        "platforms": ["pinterest"],
        "mediaUrls": [item['img']],
        "pinterestOptions": {
            "title": item['title'],
            "link": item['link']
        }
    }
    headers = {'Authorization': f'Bearer {API_KEY}'}
    r = requests.post('https://api.ayrshare.com/api/post', json=payload, headers=headers)
    print(f"Posted: {item['title']} - Status: {r.status_code}")

if __name__ == "__main__":
    post_to_pinterest()
