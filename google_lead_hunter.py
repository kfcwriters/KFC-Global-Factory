import requests
import re
import random

def hunt():
    print("🛰️ SCOUTING: Total Global Institutional Sweep...")
    # New specialized sectors
    queries = ["Laboratory+Management", "Clinical+Pathology", "Endocrinology+Metabolism"]
    q = random.choice(queries)
    
    # Using a random page (1-50) ensures fresh IDs
    page = random.randint(1, 50)
    url = f"https://doaj.org/api/v2/search/articles/{q}?pageSize=100&page={page}"

    try:
        r = requests.get(url, timeout=20)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        
        # Taking 20 fresh leads
        unique = list(set([e.lower() for e in emails if not any(x in e.lower() for x in ["info", "doaj", "support"])]))
        selected = unique[:20]
        
        if selected:
            with open("current_leads.txt", "w") as f:
                for m in selected: f.write(f"{m}\n")
            print(f"📊 SCOUT REPORT: {len(selected)} NEW Clinical Specialists identified.")
    except:
        print("⚠️ Calibrating sensors...")

if __name__ == "__main__":
    hunt()
