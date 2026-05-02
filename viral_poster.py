import requests
import random
import os

# Safely pull your key from GitHub Secrets
API_KEY = os.getenv("AYRSHARE_BRAND_TOKEN")

# VIRAL WEALTH LIBRARY (Using Pinterest-Friendly Image CDNs)
viral_library = [
    {
        "title": "Clear Skin Secret: Minimalist 10% Niacinamide Serum ✨",
        "link": "https://www.amazon.in/dp/B08F97NH6P?tag=bansallab01-21", 
        "desc": "The #1 serum for 'Glass Skin' and oil control. #ad #SkincareHacks #ViralBeauty #Minimalist",
        # Using a direct, non-Amazon link for the image
        "img": "https://be-minimalist.com/cdn/shop/products/Niacinamide10_1.jpg"
    },
    {
        "title": "Aesthetic Room Upgrade: Smart LED Strips 💡",
        "link": "https://www.amazon.in/dp/B08L7STDM9?tag=bansallab01-21",
        "desc": "Upgrade your vibe instantly for under ₹1000. #ad #RoomMakeover #AestheticHome #Govee",
        # Using a standard lifestyle image URL
        "img": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=800&q=80"
    },
    {
        "title": "Zero-Waste Writing: Digital LCD RuffPad 📝",
        "link": "https://www.amazon.in/dp/B08XMS7G1C?tag=bansallab01-21",
        "desc": "The perfect tool for quick notes or kids' sketches. #ad #WorkFromHome #ParentingHacks #Portronics",
        # Using the brand's own public image CDN
        "img": "https://www.portronics.com/cdn/shop/products/Ruffpad15M1.jpg"
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
    # Using a 10-second timeout to allow Pinterest to resolve the URL
    r = requests.post('https://api.ayrshare.com/api/post', json=payload, headers=headers, timeout=15)
    
    print(f"Post Attempt: {item['title']}")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

if __name__ == "__main__":
    post_viral_pin()
