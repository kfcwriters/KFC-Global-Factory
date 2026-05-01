import requests
import os
import random

def generate_scientific_content():
    # Tailored for High-Authority LinkedIn & Viral Pinterest Reach
    topics = [
        "Metabolic Reset: Why Myonectin is the key to Insulin Sensitivity.",
        "Renal Health Protocol: Balancing pH through Clinical Biochemistry.",
        "Weight Loss Science: Why Hormonal Signaling beats Calorie Counting.",
        "Laboratory Insights: How to audit your own Blood Reports for Health."
    ]
    topic = random.choice(topics)
    return f"🔬 Clinical Insight from Dr. Abhishek Bansal (PhD Researcher):\n\n{topic}\n\n✅ Scientific Approach. ✅ No Starvation.\n📩 Consult: bansallab@outlook.com"

def post_to_socials():
    content = generate_scientific_content()
    api_key = os.environ.get('AYRSHARE_API_KEY')
    
    payload = {
        "post": content,
        "platforms": ["linkedin", "pinterest"],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post("https://app.ayrshare.com/api/post", json=payload, headers=headers)
    
    if response.status_code == 200:
        print("🚀 Global Billboard Updated Successfully!")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    post_to_socials()
