import requests, os, random

def post_to_socials():
    # High-Authority Medical Insights
    insights = [
        "Metabolic Reset: Myonectin signaling is the primary driver for insulin sensitivity.",
        "Renal Protocol: Clinical biochemistry is essential for chronic stone prevention.",
        "Weight Science: Hormonal pathways dictate fat distribution more than calories.",
        "Diagnostic Audit: Clinical lab analysis is the foundation of precision health."
    ]
    
    # Global Search Keywords (The "GPS" for patients)
    # These stay at the bottom so the post looks professional
    tags = "#MetabolicHealth #DiabetesReversal #RenalDiet #ClinicalNutrition #HealthUK #HealthUSA"
    
    medical_images = [
        "https://images.pexels.com/photos/356040/pexels-photo-356040.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "https://images.pexels.com/photos/3912981/pexels-photo-3912981.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
    ]
    
    content = f"🔬 Bansal Metabolic Lab: {random.choice(insights)}\n\n📩 Consult: bansallab@outlook.com\n\n{tags}"
    
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
    print(f"Global Billboard Status: {response.status_code}")

if __name__ == "__main__":
    post_to_socials()
