import requests
import re
import random

def hunt():
    print("🛰️ GLOBAL SCOUTING: Total Medical Sweep (Universal Keywords)...")
    
    # Using broader keywords to guarantee lead discovery
    keywords = ["Clinical", "Biochemistry", "Pathology", "Medical+Research"]
    target = random.choice(keywords)
    page = random.randint(1, 100)
    
    url = f"https://doaj.org/api/v2/search/articles/{target}?pageSize=100&page={page}"

    try:
        r = requests.get(url, timeout=20)
        # Extract every unique email found in the journal data
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        
        # Clean results to keep only high-value research leads
        clean = list(set([e.lower() for e in emails if not any(x in e.lower() for x in ["doaj", "info", "support"])]))
        
        if clean:
            selected = clean[:20]
            with open("current_leads.txt", "w") as f:
                for mail in selected: f.write(f"{mail}\n")
            print(f"📊 SCOUT REPORT: {len(selected)} NEW Research Leads identified.")
        else:
            print("⚠️ Sector quiet. Rotating sensors for maximum reach.")
    except Exception as e:
        print(f"⚠️ Hunting Error: {e}")

if __name__ == "__main__":
    hunt()
