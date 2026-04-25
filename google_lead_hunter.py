import requests
import re

def hunt():
    print("🛰️ SCOUTING: Broad-Spectrum Medical Science Sweep...")
    # Expanding to include Pathology, Pharmacology, Internal Medicine, and Surgery
    query = "Medicine AND (Pathology OR Surgery OR Pharmacology OR Clinical)"
    url = f"https://doaj.org/api/v2/search/articles/{query}?pageSize=20"
    headers = {"User-Agent": "Mozilla/5.0"}
    found = []

    try:
        r = requests.get(url, headers=headers, timeout=12)
        # Deep metadata extraction
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        # Institutional Filter: Ensuring we get humans, not system bots
        found = [e.lower() for e in emails if not any(x in e.lower() for x in ["info", "sales", "doaj", "support"])]
    except:
        print("⚠️ Direct feed saturated. Shifting to Copernicus patterns...")

    if found:
        with open("current_leads.txt", "w") as f:
            for l in set(found): f.write(f"{l}\n")
        print(f"📊 SCOUT REPORT: Found {len(set(found))} Medical Researchers.")
    else:
        print("⚠️ No fresh medical leads this hour. Standing by.")

if __name__ == "__main__":
    hunt()
