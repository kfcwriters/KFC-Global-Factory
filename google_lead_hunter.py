import requests
import re

def hunt():
    print("🛰️ SCOUTING: Total-Field Global Medical Sweep (Every Specialty)...")
    
    # Searching all of 'Medicine' for maximum diversity
    url = "https://doaj.org/api/v2/search/articles/Medicine?pageSize=50"

    try:
        r = requests.get(url, timeout=20)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        
        # Filter junk only
        selected = [e.lower() for e in set(emails) if not any(x in e.lower() for x in ["info", "doaj", "support"])]
        
        if selected:
            with open("current_leads.txt", "w") as f:
                for mail in selected: f.write(f"{mail}\n")
            print(f"📊 SCOUT REPORT: {len(selected)} NEW Researchers identified globally.")
        else:
            print("⚠️ Rotating sensors...")
    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    hunt()
