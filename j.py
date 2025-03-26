import requests
import telebot

# التوكنات المضمنة مباشرة في الكود (استبدلها بقيمك الخاصة)
TELEGRAM_BOT_TOKEN = "7333263562:AAE7SGKtGMwlbkxNroPyh3MBvY8EUc2PCmU"
GROQ_API_KEY = "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"

# تهيئة البوت
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# إعدادات Groq API
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama3-70b-8192"

# رسالة الترحيب
WELCOME_MESSAGE = """
✨ **مرحبًا بك في بوت Junai - Pqqqf!** ✨

اكتب لي أي شيء وسأجيبك فورًا!

🚀 ابدأ المحادثة الآن...
"""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, WELCOME_MESSAGE, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "messages": [{"role": "user", "content": message.text}],
            "model": MODEL_NAME
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        reply_content = response.json()["choices"][0]["message"]["content"]

        # تقسيم الرسائل الطويلة
        for i in range(0, len(reply_content), 4096):
            bot.send_message(message.chat.id, reply_content[i:i+4096])

    except requests.exceptions.RequestException as e:
        bot.send_message(message.chat.id, f"⚠️ فشل الاتصال بالخادم: {str(e)}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ خطأ غير متوقع: {str(e)}")

if __name__ == "__main__":
    print("🤖 البوت يعمل الآن...")
    bot.infinity_polling()
