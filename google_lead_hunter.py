import os
import requests
import re
import time

def hunt_medical_authors():
    print("🛰️ GLOBAL STRIKE: Deep-Scraping PubMed & ResearchGate for ORIGINAL Authors...")
    
    # 🎯 HIGH-PRECISION ACADEMIC DORKS
    # These find real email strings indexed in Google's "Author Info" snippets
    queries = [
        'site:researchgate.net "corresponding author" "@gmail.com" medical',
        'site:pubmed.ncbi.nlm.nih.gov "author information" "@yahoo.com"',
        'site:nature.com "correspondence to" "@gmail.com"',
        '"author for correspondence" "@gmail.com" manuscript India'
    ]
    
    # Using a professional Browser Header to bypass the "Robot Block"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    real_leads = []

    for query in queries:
        print(f"🔍 Scouting Academic Database: {query}")
        try:
            # We add a small delay and a "Search Parameter" to look like a human
            search_url = f"https://www.google.com/search?q={query}&num=20"
            response = requests.get(search_url, headers=headers, timeout=15)
            
            # 🧬 THE EXTRACTOR: Pulling original emails from the HTML code
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
            
            for e in emails:
                # CEO RULE: Only individual names, block generic prefixes like 'info'
                addr = e.lower()
                if not any(x in addr for x in ["info", "admin", "support", "contact", "sales", "google", "example", "png", "jpg"]):
                    real_leads.append(addr)
        except Exception as err:
            print(f"⚠️ Search error: {err}")
            
        time.sleep(2) # Human-like pause

    final_list = list(set(real_leads))
    print(f"📊 SCOUT REPORT: Found {len(final_list)} ORIGINAL academic leads.")
    return final_list

if __name__ == "__main__":
    # Import the outreach agent
    try:
        from outreach_specialist import send_outreach
        leads = hunt_medical_authors()
        send_outreach(leads)
    except Exception as e:
        print(f"❌ Handshake Error: {e}")
