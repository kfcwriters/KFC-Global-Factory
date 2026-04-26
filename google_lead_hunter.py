import requests
import re
import random

def hunt():
    print("🛰️ SCOUTING: Universal Medical Researcher Sweep...")
    # Broad keywords to guarantee hits in the DOAJ database
    keywords = ["Clinical", "Biochemistry", "Medicine", "Pathology"]
    target = random.choice(keywords)
    page = random.randint(1, 100)
    
    url = f"https://doaj.org/api/v2/search/articles/{target}?pageSize=100&page={page}"
    try:
        r = requests.get(url, timeout=20)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        clean = list(set([e.lower() for e in emails if "doaj" not in e.lower()]))
        
        with open("current_leads.txt", "w") as f:
            for m in clean[:20]: f.write(f"{m}\n")
        print(f"📊 SCOUT REPORT: {len(clean[:20])} NEW Specialists found.")
    except Exception as e:
        print(f"⚠️ Hunting Error: {e}")

if __name__ == "__main__":
    hunt()
