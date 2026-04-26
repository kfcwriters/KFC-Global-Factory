import requests
import re
import random

def hunt():
    print("🛰️ SCOUTING: Universal Medical Sweep...")
    keywords = ["Clinical", "Biochemistry", "Pathology"]
    target = random.choice(keywords)
    page = random.randint(1, 100)
    
    url = f"https://doaj.org/api/v2/search/articles/{target}?pageSize=50&page={page}"
    try:
        r = requests.get(url, timeout=20)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        clean = list(set([e.lower() for e in emails if "doaj" not in e.lower()]))
        
        with open("current_leads.txt", "w") as f:
            for m in clean[:20]: f.write(f"{m}\n")
        print(f"📊 SCOUT REPORT: Found {len(clean[:20])} leads.")
    except Exception as e:
        print(f"⚠️ Hunting Error: {e}")

if __name__ == "__main__":
    hunt()
