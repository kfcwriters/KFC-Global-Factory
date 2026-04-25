import requests
import re
import random

def hunt():
    # Force a jump to a random page to get fresh IDs every time
    page = random.randint(1, 100)
    print(f"🛰️ SCOUTING: Global Medical Sweep (Sector {page})...")
    
    url = f"https://doaj.org/api/v2/search/articles/Medicine?pageSize=50&page={page}"

    try:
        r = requests.get(url, timeout=20)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        
        # Filter junk and remove duplicates
        clean = [e.lower() for e in set(emails) if not any(x in e.lower() for x in ["info", "doaj", "support"])]
        
        if clean:
            with open("current_leads.txt", "w") as f:
                for mail in clean: f.write(f"{mail}\n")
            print(f"📊 SCOUT REPORT: {len(clean)} BRAND NEW Leads identified.")
        else:
            print("⚠️ Sector empty. Rotating...")
    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    hunt()
