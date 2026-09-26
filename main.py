from pyrogram import Client, filters

app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.text)
async def id_handler(client, message):
    text = message.text.strip().lower()

    if text in ["آیدی", "ایدی", "id"]:
        user_id = message.from_user.id

        await message.reply_text(
            f"🆔 آیدی عددی شما:\n\n`{user_id}`"
        )

app.run()
