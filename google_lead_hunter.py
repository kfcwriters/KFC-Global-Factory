import requests
import re
import random

def hunt():
    print("🛰️ INSTITUTIONAL SCOUT: Global Medical Sweep...")
    # Using universal high-traffic keywords to ensure 100% success
    targets = ["Medicine", "Clinical", "Biochemistry", "Pathology"]
    q = random.choice(targets)
    page = random.randint(1, 100)
    
    url = f"https://doaj.org/api/v2/search/articles/{q}?pageSize=100&page={page}"
    try:
        r = requests.get(url, timeout=20)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        # Filters for unique academic leads
        clean = list(set([e.lower() for e in emails if not any(x in e.lower() for x in ["doaj", "info"])]))
        
        if clean:
            with open("current_leads.txt", "w") as f:
                for mail in clean[:20]: f.write(f"{mail}\n")
            print(f"📊 SCOUT REPORT: {len(clean[:20])} NEW Research Leads identified.")
        else:
            print("⚠️ Sector quiet. Rotating global sensors.")
    except Exception as e:
        print(f"⚠️ Hunting Error: {e}")

if __name__ == "__main__":
    hunt()
