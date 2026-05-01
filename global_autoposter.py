import requests, os, random

def post_to_socials():
    insights = [
        "Metabolic Reset: Myonectin signaling is the primary driver for cellular insulin sensitivity.",
        "Renal Protocol: Clinical biochemistry indicates that pH balance is essential for stone prevention.",
        "Weight Management: Hormonal signaling pathways dictate adipose tissue distribution more than caloric intake.",
        "Diagnostic Audit: Clinical lab report analysis is the first step in precision nutrition."
    ]
    
    # Professional Medical Images that trigger "Trust" in Global Patients
    medical_images = [
        "https://images.unsplash.com/photo-1579152276503-6175b96143c7?auto=format&fit=crop&w=1000", # Lab Tech
        "https://images.unsplash.com/photo-1532187875605-1fc3459468e2?auto=format&fit=crop&w=1000", # Microscope
        "https://images.unsplash.com/photo-1581595221475-ad669b82d0c3?auto=format&fit=crop&w=1000"  # Clinical Data
    ]
    
    content = f"🔬 Clinical Insight from Bansal Metabolic Lab:\n\n{random.choice(insights)}\n\n✅ Evidence-Based Protocol. ✅ PhD-Led Research.\n📩 Professional Consultation: bansallab@outlook.com"
    
    payload = {
        "post": content,
        "platforms": ["linkedin", "pinterest"],
        "mediaUrls": [random.choice(medical_images)] 
    }
    
    headers = {
        "Authorization": f"Bearer {os.environ['AYRSHARE_API_KEY']}",
        "Content-Type": "application/json"
    }
    
    response = requests.post("https://app.ayrshare.com/api/post", json=payload, headers=headers)
    print(f"Global Billboard Updated: {response.status_code}")

if __name__ == "__main__":
    post_to_socials()
