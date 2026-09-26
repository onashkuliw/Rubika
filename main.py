import asyncio
import os

from rubka import Robot


TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN تنظیم نشده است")


bot = Robot(token=TOKEN)


@bot.on_message()
async def test_message(bot, message):
    try:
        text = getattr(message, "text", "") or ""

        if text.strip() == "ربات":
            await message.reply("🤖 سلام پارسا! ربات وصله ✅")

    except Exception as e:
        print("MESSAGE ERROR:", repr(e))


async def main():
    print("================================")
    print("🤖 TEST BOT")
    print("✅ TOKEN دریافت شد")
    print("🚀 شروع اتصال Rubka...")
    print("================================")

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
