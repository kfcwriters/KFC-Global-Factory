import requests
import re
import random

def hunt():
    print("🛰️ SCOUTING: Global Multi-Specialty PhD Sweep...")
    # Randomized search terms to ensure zero repetition
    specialties = ["Oncology+Research", "Surgical+Quality", "Neurology+Clinical", "Pediatric+Pathology"]
    target = random.choice(specialties)
    
    # page=random skips the same old results we saw earlier
    page = random.randint(1, 100)
    url = f"https://doaj.org/api/v2/search/articles/{target}?pageSize=50&page={page}"

    try:
        r = requests.get(url, timeout=20)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        
        # Filtering for unique, professional institutional leads
        clean = [e.lower() for e in set(emails) if not any(x in e.lower() for x in ["info", "support", "doaj"])]
        
        selected = clean[:15]
        if selected:
            with open("current_leads.txt", "w") as f:
                for mail in selected: f.write(f"{mail}\n")
            print(f"📊 SCOUT REPORT: {len(selected)} NEW Specialists identified in [{target}].")
        else:
            print("⚠️ Sector quiet. Rotating sensors.")
    except:
        print("⚠️ Connection reset. Standardizing.")

if __name__ == "__main__":
    hunt()
