import random

def generate_ad():
    ads = [
        {
            "title": "⚖️ METABOLIC WEIGHT RESET",
            "body": "Fat loss isn't about calories; it's about signaling proteins like Myonectin. Stop starving and start fixing your biochemistry.",
            "cta": "Apply for the 90-Day Hormone Reset."
        },
        {
            "title": "🔬 THE LAB REPORT AUDIT",
            "body": "Don't just read your blood reports; understand them. I analyze your HbA1c and Lipid Profile to design your perfect diet.",
            "cta": "Book a Clinical Audit today."
        }
    ]
    selected = random.choice(ads)
    content = f"--- 🏛️ BANSAL CLINICAL NUTRITION ---\n\n{selected['title']}\n\n{selected['body']}\n\n👉 {selected['cta']}\n👨‍⚕️ Dr. Abhishek Bansal (PhD Researcher)\n📩 [Your WhatsApp/Telegram Link]"
    
    with open('daily_ad.txt', 'w') as f:
        f.write(content)

if __name__ == "__main__":
    generate_ad()
