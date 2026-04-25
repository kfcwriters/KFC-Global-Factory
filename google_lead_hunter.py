import requests
import re
import random

def hunt():
    print("🛰️ GLOBAL SCOUTING: Expanding Sweep Parameters...")
    
    # Using the most common medical research terms to guarantee hits
    targets = ["Health", "Clinical", "Biomedical", "Laboratory"]
    q = random.choice(targets)
    page = random.randint(1, 200)
    
    url = f"https://doaj.org/api/v2/search/articles/{q}?pageSize=100&page={page}"

    try:
        r = requests.get(url, timeout=20)
        # Pulling every unique email from the broadest possible medical data
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        
        # Clean results to maintain professional lead quality
        clean = list(set([e.lower() for e in emails if not any(x in e.lower() for x in ["doaj", "info", "support"])]))
        
        if clean:
            selected = clean[:20]
            with open("current_leads.txt", "w") as f:
                for mail in selected: f.write(f"{mail}\n")
            print(f"📊 SCOUT REPORT: {len(selected)} NEW Universal Medical Leads identified.")
        else:
            print("⚠️ Sector quiet. Rotating global sensors.")
    except Exception as e:
        print(f"⚠️ Hunting Error: {e}")

if __name__ == "__main__":
    hunt()
