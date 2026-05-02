import requests
import random
import os

API_KEY = os.getenv("AYRSHARE_BRAND_TOKEN")

# THINK DIFFERENT: Lifestyle Library (Pinterest-Favorite Visuals)
# These images are guaranteed to be "reachable" by Pinterest's crawler.
viral_library = [
    {
        "title": "My Morning Glass Skin Routine ✨",
        "link": "https://www.amazon.in/dp/B08F97NH6P?tag=bansallab01-21", 
        "desc": "How I achieved clear skin for under ₹600. The Niacinamide serum that actually works. #ad #SkincareRoutine #GlassSkin #Aesthetic",
        "img": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=80" 
    },
    {
        "title": "The Ultimate 2026 Room Glow-Up 💡",
        "link": "https://www.amazon.in/dp/B08L7STDM9?tag=bansallab01-21",
        "desc": "Change your room vibe instantly with these smart lights. Best home upgrade of the year! #ad #RoomMakeover #AestheticHome #DreamRoom",
        "img": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=800&q=80"
    },
    {
        "title": "How I Stopped Wasting Paper Forever 📝",
        "link": "https://www.amazon.in/dp/B08XMS7G1C?tag=bansallab01-21",
        "desc": "This digital ruffpad is my new favorite productivity tool for quick notes and sketches. #ad #WorkFromHome #ProductivityHacks",
        "img": "https://images.unsplash.com/photo-1517842645767-c639042777db?auto=format&fit=crop&w=800&q=80"
    }
]

def post_viral_pin():
    if not API_KEY:
        print("Error: AYRSHARE_BRAND_TOKEN not found.")
        return

    item = random.choice(viral_library)
    
    payload = {
        "post": f"{item['title']}\n\n{item['desc']}\n\nGrab yours: {item['link']}",
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
    print(f"Final Outcome: {r.text}")

if __name__ == "__main__":
    post_viral_pin()
