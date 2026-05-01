import requests, os, random

def post_to_socials():
    # Diversified Scientific Insights
    insights = [
        "Metabolic Reset: Myonectin signaling is the primary driver for insulin sensitivity.",
        "Renal Protocol: Clinical biochemistry is essential for chronic stone prevention.",
        "Weight Science: Hormonal pathways dictate fat distribution more than calories.",
        "Diagnostic Audit: Clinical lab analysis is the foundation of precision health."
    ]
    
    # Expanded Scientific Image Library (No more repeats!)
    medical_images = [
        "https://images.pexels.com/photos/356040/pexels-photo-356040.jpeg", # Microscope/Lab
        "https://images.pexels.com/photos/3912981/pexels-photo-3912981.jpeg", # Lab glassware/Science
        "https://images.pexels.com/photos/3735770/pexels-photo-3735770.jpeg", # Molecular/DNA data
        "https://images.pexels.com/photos/3825539/pexels-photo-3825539.jpeg", # Modern medical technology
        "https://images.pexels.com/photos/3825368/pexels-photo-3825368.jpeg"  # Clinical testing environment
    ]
    
    tags = "#MetabolicHealth #DiabetesReversal #RenalDiet #ClinicalNutrition #MedicalTourism"
    
    # The machine picks a unique combination every time
    content = f"🔬 Bansal Metabolic Lab: {random.choice(insights)}\n\n📩 Consult: bansallab@outlook.com\n\n{tags}"
    selected_image = random.choice(medical_images)
    
    payload = {
        "post": content,
        "platforms": ["linkedin", "pinterest"],
        "mediaUrls": [selected_image] 
    }
    
    headers = {
        "Authorization": f"Bearer {os.environ['AYRSHARE_API_KEY']}",
        "Content-Type": "application/json"
    }
    
    response = requests.post("https://app.ayrshare.com/api/post", json=payload, headers=headers)
    print(f"Global Billboard Status: {response.status_code}")

if __name__ == "__main__":
    post_to_socials()
