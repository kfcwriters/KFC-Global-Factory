import requests
import re
import random

def hunt():
    print("🛰️ MORNING SWEEP: Global Clinical Database Access...")
    # Diversified search to bypass empty sectors
    targets = ["Clinical+Biochemistry", "Pathology", "Endocrinology", "Surgery", "Internal+Medicine"]
    q = random.choice(targets)
    page = random.randint(1, 200) # Deep search for unique leads
    
    url = f"https://doaj.org/api/v2/search/articles/{q}?pageSize=100&page={page}"

    try:
        r = requests.get(url, timeout=20)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        # Filter for professional researcher emails only
        unique = list(set([e.lower() for e in emails if not any(x in e.lower() for x in ["doaj", "info", "support"])]))
        
        if unique:
            selected = unique[:25]
            with open("current_leads.txt", "w") as f:
                for mail in selected: f.write(f"{mail}\n")
            print(f"📊 SCOUT REPORT: {len(selected)} NEW Clinical Specialists identified.")
        else:
            print("⚠️ Sector quiet. Rotating sensors for next run.")
    except Exception as e:
        print(f"⚠️ Hunter Error: {e}")

if __name__ == "__main__":
    hunt()
