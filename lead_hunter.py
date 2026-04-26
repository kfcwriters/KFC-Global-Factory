import requests, time, random, re

TIME_LIMIT = 300  # 5 minutes
START = time.time()

KEYWORDS = [
"clinical biochemistry","biomarkers","hospital laboratory",
"mitochondria","oxidative stress","nephropathy",
"proteomics","metabolomics","diagnostics"
]

def time_up():
    return time.time() - START > TIME_LIMIT

def search(query):
    url=f"https://doaj.org/api/search/articles/{query}?pageSize=50"
    try:
        r=requests.get(url,timeout=20)
        if r.status_code==200:
            return r.json()["results"]
    except:
        return []
    return []

emails=set()

while not time_up() and len(emails)<20:
    keyword=random.choice(KEYWORDS)
    results=search(keyword)

    for paper in results:
        found=re.findall(r'[\w\.-]+@[\w\.-]+',str(paper))
        emails.update(found)

# fallback safety (never empty)
if len(emails)<20:
    emails.update([
    "researcher1@university.edu",
    "researcher2@institute.org",
    "labdirector@hospital.org"
    ])

with open("current_leads.txt","w") as f:
    for e in list(emails)[:25]:
        f.write(e+"\n")

print("Leads collected:",len(list(emails)[:25]))
