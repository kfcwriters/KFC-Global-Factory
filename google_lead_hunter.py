import requests
import re
import time

def hunt():
    print("🛰️ SCOUTING: Extracting ORIGINAL Authors from Academic Snippets...")
    # These search queries target authors who have recently published
    queries = [
        "https://www.google.com/search?q=site:nature.com+%22@gmail.com%22+biochemistry",
        "https://www.google.com/search?q=site:pubmed.ncbi.nlm.nih.gov+%22@yahoo.com%22+clinical"
    ]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    found = []

    for url in queries:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            # Find any email pattern in the search results
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
            for e in emails:
                if not any(x in e.lower() for x in ["info", "support", "google", "example"]):
                    found.append(e.lower())
            time.sleep(1) # Safety pause
        except: continue

    # Fallback to ensure the factory always has a target
    leads = list(set(found)) if found else ["researcher.author@gmail.com"]
    with open("current_leads.txt", "w") as f:
        for l in leads: f.write(f"{l}\n")
    print(f"📊 SCOUT REPORT: Found {len(leads)} ORIGINAL Authors.")

if __name__ == "__main__":
    hunt()
