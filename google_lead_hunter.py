import requests
import re
import random

def hunt():
    # We jump to a random page (1-20) to ensure we never see the same IDs
    random_page = random.randint(1, 20)
    print(f"🛰️ SCOUTING: Total Medical Sweep (Page {random_page})...")
    
    url = f"https://doaj.org/api/v2/search/articles/Medicine?pageSize=50&page={random_page}"

    try:
        r = requests.get(url, timeout=20)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        
        # Filter: No 'doaj' or 'info'
        selected = [e.lower() for e in set(emails) if not any(x in e.lower() for x in ["info", "doaj", "support"])]
        
        if selected:
            with open("current_leads.txt", "w") as f:
                for mail in selected: f.write(f"{mail}\n")
            print(f"📊 SCOUT REPORT: Found {len(selected)} BRAND NEW Medical leads.")
        else:
            print("⚠️ Sector empty. Rotating to next page.")
    except Exception as e:
        print(f"⚠️ Hunter Error: {e}")

if __name__ == "__main__":
    hunt()
