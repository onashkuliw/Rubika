# ============================================================
# ربات آیدی‌یاب | Rubika ID Bot
# کافیه توکن ربات رو پایین بذاری و اجرا کنی.
# توی خصوصی یا گروه بنویس «آیدی» یا بزن /id تا جواب بگیری.
# ============================================================

import asyncio
import os
from rubka import Robot, Message

# ------------------------------------------------------------
# توکن رو از Environment Variable ریلوی می‌خونه.
# توی پنل ریلوی برو Variables و یه متغیر به اسم BOT_TOKEN بساز.
# ------------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "TOKEN_ربات_خودتو_اینجا_بذار")

bot = Robot(token=BOT_TOKEN)


def id_reply_text(message: Message) -> str:
    return (
        "🆔 آیدی شما:\n"
        f"`{message.sender_id}`\n\n"
        "💬 آیدی این چت (گروه/خصوصی):\n"
        f"`{message.chat_id}`"
    )


@bot.on_message(commands=["id", "myid"])
async def id_command(bot, message: Message):
    message.reply(id_reply_text(message))


@bot.on_message()
async def id_text_trigger(bot, message: Message):
    text = (message.text or "").strip()

    if not text or text.startswith("/"):
        return

    normalized = text.replace("‌", "").strip().lower()

    if normalized in ["آیدی", "ایدی", "id", "آی دی"]:
        message.reply(id_reply_text(message))


# ============================================================
# راه‌اندازی
# ============================================================

print("======================================")
print("🤖 ربات آیدی‌یاب روشن شد")
print("======================================")


async def main():
    try:
        await bot.set_commands([
            {"command": "id", "description": "گرفتن آیدی خودم و آیدی چت"},
        ])
        print("✅ دستورات ربات ثبت شدند.")
    except Exception as e:
        print("⚠️ ثبت دستورات انجام نشد، ولی ربات ادامه می‌دهد:")
        print(e)

    print("🟢 ربات آماده دریافت پیام است.")
    bot.run()


if __name__ == "__main__":
    asyncio.run(main())
