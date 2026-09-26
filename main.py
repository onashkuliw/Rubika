import os
import random

from rubka import Robot, Message


# =========================
# تنظیمات
# =========================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN تنظیم نشده است")


bot = Robot(token=TOKEN)


# =========================
# پیام‌های ربات
# =========================

RESPONSES = [
    "سلام 😎🤖\nدر خدمتم! چی شده؟",
    "جانم؟ 👀🤖",
    "بله؟ 😎\nیار رسانه حاضر است!",
    "سلام رفیق 🔥\nبگو ببینم چه خبره؟",
    "در خدمتم داداش 🤖🫡",
    "هااا؟ 😄\nصدای ربات کردی؟",
    "اینجام 😎🔥",
    "سلام 👋🤖\nبیا ببینیم امروز چه کاری داریم!",
]


# =========================
# دریافت پیام‌های گروه
# =========================

@bot.on_message()
async def handle_message(bot: Robot, message: Message):

    try:
        text = getattr(message, "text", "") or ""
        text = text.strip()

        print("📩 پیام دریافت شد:", repr(text))

        # وقتی کسی در گروه می‌نویسد «ربات»
        if text == "ربات":

            response = random.choice(RESPONSES)

            print("🤖 در حال پاسخ دادن...")

            await message.reply(response)

            print("✅ پاسخ ارسال شد")

    except Exception as e:

        print("❌ MESSAGE ERROR:", repr(e))


# =========================
# اجرای ربات
# =========================

print("======================================")
print("🤖 یار رسانه")
print("📚 ربات تفکر و سواد رسانه‌ای")
print("🚀 Rubka Bot")
print("======================================")
print("🟢 ربات در حال اجراست...")
print("======================================")


bot.run()
