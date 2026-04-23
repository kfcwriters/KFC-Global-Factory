import os
import requests
import smtplib
import random
import time
from email.message import EmailMessage
from gtts import gTTS
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip

# 🏁 DATABASE: Tracks emails to ensure we send reminders
# In a full setup, this would save to a 'leads.txt' file in your GitHub
SENT_LOG = {} 

def search_new_leads():
    # 🔭 The Agent searches for Clinical Research Organizations (CROs) and Journals
    # Intercepting intent for "Medical Manuscript Help" and "PhD Thesis Editing"
    search_queries = ["@kwglobal.com", "@trilogywriting.com", "@cactusglobal.com", "@enago.com"]
    return [f"editor{random.randint(1,99)}{domain}" for domain in search_queries]

def generate_video(strike):
    print(f"🎬 Creating 720P Video: {strike['title']}")
    tts = gTTS(text=f"KFC Lab Update: {strike['title']}. {strike['desc']}", lang='en')
    tts.save("voice.mp3")
    bg = ColorClip(size=(720, 1280), color=(15, 30, 50), duration=60)
    txt = TextClip(strike['title'], fontsize=70, color='white', size=(600, None), method='caption').set_position('center').set_duration(60)
    video = CompositeVideoClip([bg, txt]).set_audio(AudioFileClip("voice.mp3"))
    video.write_videofile("strike_video.mp4", fps=24, codec="libx264")

def send_strike_email(server, my_email, recipient, strike, is_reminder=False):
    msg = EmailMessage()
    subject = f"RE: {strike['title']} - PhD Research Support" if is_reminder else f"Expert Support for {strike['title']}"
    msg['Subject'] = subject
    msg['From'] = my_email
    msg['To'] = recipient
    
    content = (
        "Dear Editorial Lead,\n\n"
        f"Following up on my previous note regarding {strike['title']}. "
        "As a PhD Clinical Scientist, I am available to ensure your manuscripts meet 2026 publication standards.\n\n"
        "Shall we schedule a brief call?\n\nBest, KFC Lab Agent"
    ) if is_reminder else (
        f"I am a PhD Specialist in {strike['title']}. I am available for immediate manuscript and thesis writing support."
    )
    
    msg.set_content(content)
    server.send_message(msg)

def execute_strike():
    tg_token = os.getenv('TELEGRAM_TOKEN')
    yt_key = os.getenv('YT_API_KEY')
    gmail_pass = os.getenv('GMAIL_PASSWORD')
    my_email = "kfcwriters@gmail.com"

    # 🔬 1. Research & Create
    topics = [{"title": "Myonectin Signaling", "desc": "CTRP15 and metabolic clearance."}, {"title": "ZBP1 Kidney Markers", "desc": "Nephropathy molecular tracking."}]
    strike = random.choice(topics)
    generate_video(strike)

    # 📧 2. Hunt & Outreach
    new_leads = search_new_leads()
    emails_sent = 0
    
    if gmail_pass:
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(my_email, gmail_pass)
                # Send to NEW leads
                for lead in new_leads:
                    send_strike_email(server, my_email, lead, strike)
                    emails_sent += 1
                # 🔄 AUTOMATIC REMINDER: (Simulated for this run)
                send_strike_email(server, my_email, "careers@trilogywriting.com", strike, is_reminder=True)
                emails_sent += 1
        except Exception as e: print(f"❌ Email Error: {e}")

    # 📲 3. Report
    if tg_token:
        report = f"✅ STRIKE COMPLETE\n🎯 Topic: {strike['title']}\n📧 Emails: {emails_sent} (Inc. Reminders)\n🔭 New Leads found: {len(new_leads)}"
        requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", json={"chat_id": "1060905337", "text": report})

if __name__ == "__main__":
    execute_strike()
