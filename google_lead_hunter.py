import requests
import re
import random

def hunt():
    # Broader keywords to bypass quiet sectors and guarantee results
    keywords = ["Clinical", "Biochemistry", "Pathology", "Oncology"]
    target = random.choice(keywords)
    page = random.randint(1, 100)
    
    url = f"https://doaj.org/api/v2/search/articles/{target}?pageSize=50&page={page}"
    try:
        r = requests.get(url, timeout=20)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        clean = list(set([e.lower() for e in emails if "doaj" not in e.lower()]))
        
        if clean:
            with open("current_leads.txt", "w") as f:
                for m in clean[:25]: f.write(f"{m}\n")
    except Exception as e:
        print(f"⚠️ Hunting Error: {e}")

if __name__ == "__main__":
    hunt()
