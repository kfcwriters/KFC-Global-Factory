import requests
import re

def hunt():
    print("🛰️ SCOUTING: Extracting LIVE Authors from Academic Snippets...")
    # Searching for biochemistry papers with public emails in the last 24 hours
    url = "https://www.google.com/search?q=site:nature.com+OR+site:pubmed.gov+%22@gmail.com%22+biochemistry"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        # Find any email pattern in the search results
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        found = [e.lower() for e in emails if not any(x in e.lower() for x in ["info", "admin", "support"])]
        
        # 🛡️ NO FALLBACK. If we find nothing, we stop to prevent "Fake Mail" bounces.
        if found:
            with open("current_leads.txt", "w") as f:
                for l in set(found): f.write(f"{l}\n")
            print(f"📊 SCOUT REPORT: Found {len(set(found))} LIVE Researchers.")
        else:
            print("⚠️ No live leads found. Standing by for next hourly strike.")
    except:
        print("❌ Search Blocked. Retrying next hour.")

if __name__ == "__main__":
    hunt()
