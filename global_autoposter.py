import requests, os, random

def post_to_socials():
    insights = [
        "Metabolic Reset: Myonectin signaling is the primary driver for cellular insulin sensitivity.",
        "Renal Protocol: Clinical biochemistry indicates that pH balance is essential for stone prevention.",
        "Weight Management: Hormonal signaling pathways dictate adipose tissue distribution more than caloric intake.",
        "Diagnostic Audit: Clinical lab report analysis is the first step in precision nutrition."
    ]
    
    # Strictly Institutional Branding - No Names
    content = f"🔬 Clinical Insight from Bansal Metabolic Lab:\n\n{random.choice(insights)}\n\n✅ Evidence-Based Protocol. ✅ PhD-Led Research.\n📩 Professional Consultation: bansallab@outlook.com"
    
    payload = {
        "post": content,
        "platforms": ["linkedin", "pinterest"],
        # Using a ultra-reliable Wikimedia Commons medical image link
        "mediaUrls": ["https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Magnetite_in_biochemistry.jpg/640px-Magnetite_in_biochemistry.jpg"] 
    }
    
    headers = {
        "Authorization": f"Bearer {os.environ['AYRSHARE_API_KEY']}",
        "Content-Type": "application/json"
    }
    
    response = requests.post("https://app.ayrshare.com/api/post", json=payload, headers=headers)
    print(f"Broadcast Status: {response.text}")

if __name__ == "__main__":
    post_to_socials()
