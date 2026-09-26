import re
import time
from rubka import Robot, Message
from rubka.button import InlineBuilder

import config
import database as database
from questions import seed_questions

database.init_db()

# بانک اولیه فقط یک بار ساخته می‌شود.
if database.question_count(1, 1) == 0:
    seed_questions(database.add_question)

bot = Robot(token=config.BOT_TOKEN)

CHAPTERS = {
    1: "ما و رسانه‌ها",
    2: "فنون خلق پیام رسانه‌ای",
    3: "نادیده‌های رسانه‌ها",
    4: "مخاطب‌شناسی",
    5: "رسانه و سبک زندگی",
    6: "رژیم مصرف رسانه‌ای",
}

LESSONS = {
    1: "مسابقه رسانه‌ها با زمان", 2: "آن سوی متن",
    3: "پنجگانه سواد رسانه‌ای", 4: "تصاویر بی‌طرف نیستند",
    5: "از بازنمایی تا کلیشه", 6: "فنون اقناع",
    7: "ذهن فریب‌پذیر", 8: "مهندسان پیام",
    9: "بازیگردانان بزرگ", 10: "دروازه‌بانی خبر",
    11: "مخاطب خاص", 12: "مخاطب فعال یا منفعل",
    13: "حقوق مخاطب", 14: "هر چیز که در جستن آنی، آنی",
    15: "کلیشه بدن", 16: "بازی، جدی است",
    17: "زندگی دوم", 18: "علیه اخبار جعلی",
    19: "سلامت رسانه‌ای", 20: "اخلاق رسانه‌ای",
}

def is_admin(user_id):
    return str(user_id) == str(config.ADMIN_ID)

def active_lesson():
    return int(database.setting("active_lesson", "1"))

def active_chapter():
    return int(database.setting("active_chapter", "1"))

def norm(s):
    return (s or "").strip().replace("ي", "ی").replace("ك", "ک")

def home_text():
    ch = active_chapter()
    le = active_lesson()
    return (
        "🎓 یار رسانه\n\n"
        "ربات آموزشی کلاس دهم — تفکر و سواد رسانه‌ای\n\n"
        f"📚 فصل فعال: {ch} — {CHAPTERS.get(ch,'')}\n"
        f"📖 درس فعال: {le} — {LESSONS.get(le,'')}\n\n"
        "دستورها:\n"
        "❓ سوال — سؤال بعدی\n"
        "❓ سوال ۱ — سؤال شماره ۱ درس فعال\n"
        "📊 امتیاز من\n"
        "🏆 جدول — رتبه‌بندی کلاس\n"
        "ℹ️ راهنما\n\n"
        "ادمین: /admin"
    )

def question_keypad(qid):
    b = InlineBuilder()
    b = b.row(
        b.button_simple(f"q:{qid}:a", "الف"),
        b.button_simple(f"q:{qid}:b", "ب")
    )
    b = b.row(
        b.button_simple(f"q:{qid}:c", "ج"),
        b.button_simple(f"q:{qid}:d", "د")
    )
    return b.build()

def send_question(chat_id, number=None, reply_to=None):
    ch, le = active_chapter(), active_lesson()
    number = number or 1
    q = database.question_by_number(number, ch, le)
    if not q:
        return bot.send_message(
            chat_id,
            f"⚠️ برای فصل {ch} و درس {le} سؤال شماره {number} ثبت نشده."
        )
    text = (
        f"🧠 سؤال {number}\n"
        f"📚 {CHAPTERS[ch]} | درس {le}: {LESSONS[le]}\n\n"
        f"{q['question']}\n\n"
        f"الف) {q['option_a']}\n"
        f"ب) {q['option_b']}\n"
        f"ج) {q['option_c']}\n"
        f"د) {q['option_d']}\n\n"
        f"🎯 امتیاز: {q['score']}"
    )
    return bot.send_message(
        chat_id, text,
        inline_keypad=question_keypad(q["id"]),
        reply_to_message_id=reply_to
    )

@bot.on_message(commands=["start"])
def start(bot, message):
    database.add_student(message.sender_id, message.sender_id)
    message.reply(home_text())

@bot.on_message(commands=["help"])
def help_cmd(bot, message):
    message.reply(home_text())

@bot.on_message(commands=["question", "q"])
def question_cmd(bot, message):
    n = 1
    if getattr(message, "args", None):
        try:
            n = int(message.args[0])
        except ValueError:
            pass
    if not database.get_student(message.sender_id):
        message.reply("⛔ اول باید توسط ادمین ثبت‌نام شوی.")
        return
    send_question(message.chat_id, n, message.message_id)

@bot.on_message(commands=["score", "me"])
def score_cmd(bot, message):
    s = database.get_student(message.sender_id)
    if not s:
        message.reply("⛔ هنوز ثبت‌نام نشده‌ای.")
        return
    message.reply(
        f"👤 {s['name']}\n"
        f"🏆 امتیاز: {s['score']}\n"
        f"✅ درست: {s['correct']}\n"
        f"❌ غلط: {s['wrong']}\n"
        f"📝 پاسخ داده‌شده: {s['total']}\n"
        f"⚠️ اخطار: {s['warnings']}"
    )

@bot.on_message(commands=["leaderboard", "table"])
def table_cmd(bot, message):
    rows = database.leaderboard(20)
    if not rows:
        message.reply("هنوز دانش‌آموزی ثبت نشده.")
        return
    lines = ["🏆 جدول امتیازات\n"]
    for i, r in enumerate(rows, 1):
        lines.append(f"{i}. {r['name']} — {r['score']} امتیاز")
    message.reply("\n".join(lines))

@bot.on_message(commands=["admin"])
def admin_cmd(bot, message):
    if not is_admin(message.sender_id):
        message.reply("⛔ دسترسی ادمین نداری.")
        return
    message.reply(
        "🛠 پنل مدیریت\n\n"
        "/addstudent USER_ID NAME\n"
        "/delstudent USER_ID\n"
        "/setlesson CHAPTER LESSON\n"
        "/students\n"
        "/stats\n"
        "/addq CHAPTER LESSON SCORE PAGE CORRECT | QUESTION | A | B | C | D | EXPLANATION\n"
        "/warn USER_ID\n"
        "/unwarn USER_ID\n"
        "/delmsg MESSAGE_ID\n\n"
        "مثال:\n"
        "/setlesson 2 5\n"
        "/addstudent u123 علی رضایی"
    )

@bot.on_message(commands=["addstudent"])
def add_student_cmd(bot, message):
    if not is_admin(message.sender_id):
        message.reply("⛔")
        return
    args = getattr(message, "args", [])
    if len(args) < 2:
        message.reply("فرمت: /addstudent USER_ID NAME")
        return
    uid, name = args[0], " ".join(args[1:])
    database.add_student(uid, name)
    database.log(message.sender_id, "add_student", uid, name)
    message.reply(f"✅ {name} ثبت شد.")

@bot.on_message(commands=["delstudent"])
def del_student_cmd(bot, message):
    if not is_admin(message.sender_id):
        message.reply("⛔")
        return
    args = getattr(message, "args", [])
    if not args:
        message.reply("فرمت: /delstudent USER_ID")
        return
    database.remove_student(args[0])
    database.log(message.sender_id, "delete_student", args[0])
    message.reply("✅ دانش‌آموز حذف شد.")

@bot.on_message(commands=["setlesson"])
def set_lesson_cmd(bot, message):
    if not is_admin(message.sender_id):
        message.reply("⛔")
        return
    args = getattr(message, "args", [])
    if len(args) != 2:
        message.reply("فرمت: /setlesson CHAPTER LESSON")
        return
    try:
        ch, le = int(args[0]), int(args[1])
        if ch not in CHAPTERS or le not in LESSONS:
            raise ValueError
    except ValueError:
        message.reply("❌ شماره فصل یا درس نامعتبر است.")
        return
    database.set_setting("active_chapter", ch)
    database.set_setting("active_lesson", le)
    database.log(message.sender_id, "set_lesson", "", f"{ch}/{le}")
    message.reply(f"✅ درس فعال شد:\nفصل {ch}: {CHAPTERS[ch]}\nدرس {le}: {LESSONS[le]}")

@bot.on_message(commands=["students"])
def students_cmd(bot, message):
    if not is_admin(message.sender_id):
        message.reply("⛔")
        return
    rows = database.all_students()
    if not rows:
        message.reply("هیچ دانش‌آموزی ثبت نشده.")
        return
    text = "👥 دانش‌آموزان:\n\n" + "\n".join(
        f"{i}. {r['name']} — {r['user_id']}" for i, r in enumerate(rows, 1)
    )
    message.reply(text[:4000])

@bot.on_message(commands=["stats"])
def stats_cmd(bot, message):
    if not is_admin(message.sender_id):
        message.reply("⛔")
        return
    rows = database.all_students()
    total_answers = sum(r["total"] for r in rows)
    total_score = sum(r["score"] for r in rows)
    message.reply(
        f"📊 آمار\n\n"
        f"👥 دانش‌آموز: {len(rows)}\n"
        f"📝 پاسخ‌ها: {total_answers}\n"
        f"🏆 مجموع امتیاز: {total_score}\n"
        f"📚 فصل فعال: {active_chapter()}\n"
        f"📖 درس فعال: {active_lesson()}"
    )

@bot.on_message(commands=["warn"])
def warn_cmd(bot, message):
    if not is_admin(message.sender_id):
        message.reply("⛔")
        return
    args = getattr(message, "args", [])
    if not args:
        message.reply("فرمت: /warn USER_ID")
        return
    uid = args[0]
    count = database.warn(uid)
    database.log(message.sender_id, "warn", uid)
    message.reply(f"⚠️ اخطار ثبت شد. تعداد اخطار: {count}")

@bot.on_message(commands=["unwarn"])
def unwarn_cmd(bot, message):
    if not is_admin(message.sender_id):
        message.reply("⛔")
        return
    args = getattr(message, "args", [])
    if not args:
        message.reply("فرمت: /unwarn USER_ID")
        return
    database.unwarn(args[0])
    database.log(message.sender_id, "unwarn", args[0])
    message.reply("✅ یک اخطار کم شد.")

@bot.on_message(commands=["delmsg"])
def delmsg_cmd(bot, message):
    if not is_admin(message.sender_id):
        message.reply("⛔")
        return
    args = getattr(message, "args", [])
    if not args:
        message.reply("فرمت: /delmsg MESSAGE_ID")
        return
    try:
        bot.delete_message(message.chat_id, args[0])
        database.log(message.sender_id, "delete_message", args[0])
        message.reply("🗑 پیام حذف شد.")
    except Exception as e:
        message.reply(f"❌ حذف پیام انجام نشد: {e}")

@bot.on_message(commands=["addq"])
def addq_cmd(bot, message):
    if not is_admin(message.sender_id):
        message.reply("⛔")
        return
    raw = message.text.split(" ", 1)[1] if " " in message.text else ""
    head, sep, body = raw.partition("|")
    parts = [x.strip() for x in body.split("|")] if sep else []
    try:
        h = head.split()
        chapter, lesson, score, page = map(int, h[:4])
        correct = h[4].lower()
        q, a, b, c, d = parts[:6]
        explanation = parts[6] if len(parts) > 6 else ""
        if correct not in ("a","b","c","d"):
            raise ValueError
        qid = database.add_question(
            chapter, lesson, q,
            {"a":a,"b":b,"c":c,"d":d},
            correct, score, page, explanation
        )
        database.log(message.sender_id, "add_question", str(qid))
        message.reply(f"✅ سؤال با شناسه {qid} اضافه شد.")
    except Exception:
        message.reply(
            "❌ فرمت اشتباه است.\n"
            "نمونه:\n"
            "/addq 1 1 3 12 a | متن سؤال | گزینه الف | گزینه ب | گزینه ج | گزینه د | توضیح"
        )

@bot.on_callback()
def callback(bot, message):
    button = getattr(getattr(message, "aux_data", None), "button_id", "") or ""
    if not button.startswith("q:"):
        return

    parts = button.split(":")
    if len(parts) != 3:
        return

    try:
        qid = int(parts[1])
        answer = parts[2].lower()
    except ValueError:
        message.reply("❌ پاسخ نامعتبر است.")
        return

    student = database.get_student(message.sender_id)
    if not student:
        message.reply("⛔ اول باید توسط ادمین ثبت‌نام شوی.")
        return

    result, info = database.record_answer(message.sender_id, qid, answer)
    if result is None:
        message.reply(f"⚠️ {info}")
        return

    if info["correct"]:
        status = f"✅ درست! +{info['added']} امتیاز"
    else:
        status = f"❌ نادرست. پاسخ صحیح: {result['correct'].upper()}"

    source = f"📖 منبع: درس {result['lesson']}، صفحه {result['source_page']}" \
             if result["source_page"] else f"📖 منبع: درس {result['lesson']}"

    message.reply(
        f"{status}\n\n"
        f"💡 {result['explanation']}\n"
        f"{source}\n\n"
        f"🏆 امتیاز فعلی: {database.get_student(message.sender_id)['score']}"
    )

# پاسخ‌های متنی داخل گروه؛ برای اینکه بچه‌ها مجبور نباشند همیشه اسلش بزنند.
@bot.on_message_text()
def group_text(bot, message):
    text = norm(message.text)
    if text.startswith("/"):
        return

    # اگر دانش‌آموز ثبت شده باشد، عبارت‌های ساده آموزشی را تشخیص می‌دهیم.
    if text in ("سوال", "سؤال", "سوال بعدی", "سؤال بعدی"):
        if not database.get_student(message.sender_id):
            message.reply("⛔ اول باید توسط ادمین ثبت‌نام شوی.")
            return
        send_question(message.chat_id, 1, message.message_id)
        return

    m = re.fullmatch(r"(?:سوال|سؤال)\s*(\d+)", text)
    if m:
        if not database.get_student(message.sender_id):
            message.reply("⛔ اول باید توسط ادمین ثبت‌نام شوی.")
            return
        send_question(message.chat_id, int(m.group(1)), message.message_id)
        return

    if text in ("امتیاز من", "امتیاز"):
        s = database.get_student(message.sender_id)
        if s:
            message.reply(f"🏆 {s['name']} — {s['score']} امتیاز")
        else:
            message.reply("⛔ هنوز ثبت‌نام نشده‌ای.")
        return

    if text in ("جدول", "رتبه", "رتبه بندی", "رتبه‌بندی"):
        rows = database.leaderboard(10)
        if rows:
            message.reply("🏆 جدول:\n" + "\n".join(
                f"{i}. {r['name']} — {r['score']}" for i, r in enumerate(rows, 1)
            ))
        return

    if text == "ربات":
        message.reply("سلام 👋 در خدمتم؛ بیا با هم سواد رسانه‌ای تمرین کنیم!")

print("🤖 یار رسانه روشن شد.")
bot.set_commands([
    {"command": "start", "description": "شروع"},
    {"command": "question", "description": "سؤال"},
    {"command": "score", "description": "امتیاز من"},
    {"command": "leaderboard", "description": "جدول امتیازات"},
    {"command": "help", "description": "راهنما"},
    {"command": "admin", "description": "پنل ادمین"},
])
bot.run(debug=True)
