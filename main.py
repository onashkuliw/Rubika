import os
import random

from rubka import Robot, Message


# =========================
# TOKEN
# =========================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN تنظیم نشده است")


# =========================
# BOT
# =========================

bot = Robot(token=TOKEN)


# =========================
# پاسخ‌های ربات
# =========================

RESPONSES = [
    "سلام 😎🤖 در خدمتم!",
    "جانم؟ 👀",
    "بله؟ 🤖 بگو ببینم!",
    "سلام رفیق 🔥",
    "در خدمتم داداش 🫡",
    "اینجام 😎",
    "صدای ربات کردی؟ 😂🤖",
    "بله بله، یار رسانه حاضر است 📚🤖",
]


# ==================================================
# پیام‌های خصوصی
# ==================================================

@bot.on_message_private()
async def private_message(bot: Robot, message: Message):

    try:

        text = getattr(message, "text", "") or ""
        text = text.strip()

        print("📩 PRIVATE:", repr(text))

        if text == "ربات":

            answer = random.choice(RESPONSES)

            await message.reply(answer)

            print("✅ پاسخ خصوصی ارسال شد")

    except Exception as e:

        print("❌ PRIVATE ERROR:", repr(e))


# ==================================================
# پیام‌های گروه
# ==================================================

@bot.on_message_group()
async def group_message(bot: Robot, message: Message):

    try:

        text = getattr(message, "text", "") or ""
        text = text.strip()

        print("📩 GROUP:", repr(text))

        # فقط وقتی دقیقاً نوشته شود «ربات»
        if text == "ربات":

            answer = random.choice(RESPONSES)

            print("🤖 پاسخ به گروه:", answer)

            await message.reply(answer)

            print("✅ پاسخ گروه ارسال شد")

    except Exception as e:

        print("❌ GROUP ERROR:", repr(e))


# ==================================================
# START
# ==================================================

print("======================================")
print("🤖 یار رسانه")
print("📚 تفکر و سواد رسانه‌ای")
print("🚀 Rubka Bot")
print("======================================")
print("🟢 ربات آماده است")
print("📩 پیام خصوصی: فعال")
print("👥 پیام گروه: فعال")
print("======================================")


# اجرای ربات
bot.run()
