import requests, os, random

def post_to_socials():
    insights = [
        "Metabolic Reset: Myonectin is key for insulin sensitivity.",
        "Renal Protocol: pH balance is essential for stone prevention.",
        "Weight Science: Hormones dictate fat loss more than calories.",
        "Diagnostic Audit: Clinical lab analysis is the first step."
    ]
    
    medical_images = [
        "https://images.pexels.com/photos/356040/pexels-photo-356040.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "https://images.pexels.com/photos/3912981/pexels-photo-3912981.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
    ]
    
    # Simplified text to prevent "400" errors
    content = f"🔬 Bansal Metabolic Lab Insight: {random.choice(insights)} 📩 Consult: bansallab@outlook.com"
    
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
