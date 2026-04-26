import requests
import random
import re

KEYWORDS = ["clinical biochemistry", "mitochondria proteostasis", "diabetic nephropathy", "sigma metrics"]

def get_leads():
    leads = []
    print("🛰️ SCOUT: Starting Universal Medical Sweep...")
    while len(leads) < 25:
        q = random.choice(KEYWORDS)
        url = f"https://doaj.org/api/search/articles/{q}?pageSize=50"
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                # Extracting emails from the raw response
                found = re.findall(r'[\w\.-]+@[\w\.-]+', str(r.json()))
                leads.extend(found)
            leads = list(set(leads)) # Unique emails only
        except: continue

    with open("current_leads.txt", "w") as f:
        for mail in leads[:25]: f.write(mail + "\n")
    print(f"✅ SCOUT: Identified {len(leads[:25])} Research Specialists.")

if __name__ == "__main__":
    get_leads()
