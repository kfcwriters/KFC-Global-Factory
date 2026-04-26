import requests
import random
import re
import time

KEYWORDS = ["clinical", "biochemistry", "pathology", "diabetes", "nephrology"]

def get_leads():
    leads = []
    start_time = time.time()
    print("🛰️ SPEED SCOUT: High-Velocity Sweep...")
    
    while len(leads) < 25:
        # EMERGENCY EXIT: Never run longer than 5 minutes
        if time.time() - start_time > 300: 
            print("🕒 TIMEOUT: Saving partial leads to keep factory moving.")
            break
            
        q = random.choice(KEYWORDS)
        # Using a higher pageSize to get more data at once
        url = f"https://doaj.org/api/search/articles/{q}?pageSize=100"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                found = re.findall(r'[\w\.-]+@[\w\.-]+', str(r.json()))
                leads.extend(found)
            leads = list(set([l.lower() for l in leads if "doaj" not in l.lower()]))
        except: continue

    with open("current_leads.txt", "w") as f:
        for mail in leads[:25]: f.write(mail + "\n")
    print(f"✅ SPEED SCOUT: {len(leads[:25])} leads ready.")

if __name__ == "__main__":
    get_leads()
