import requests
import re

def hunt():
    print("🛰️ SCOUTING: Scraping PubMed Snippets for LIVE Authors...")
    # Using a direct search query for recent biochemistry papers
    url = "https://pubmed.ncbi.nlm.nih.gov/?term=clinical+biochemistry&sort=date"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        # Regex to find professional emails in the search results
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        found = [e.lower() for e in emails if not any(x in e.lower() for x in ["info", "admin", "example"])]
        
        # 🛡️ ONLY save if we found real emails. No more placeholders.
        if found:
            with open("current_leads.txt", "w") as f:
                for l in set(found): f.write(f"{l}\n")
            print(f"📊 SCOUT REPORT: Found {len(set(found))} LIVE researchers.")
        else:
            print("⚠️ No live leads found this hour. Standing by to avoid bounces.")
    except Exception as e:
        print(f"❌ Hunter Error: {e}")

if __name__ == "__main__":
    hunt()
