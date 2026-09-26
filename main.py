import os
import random
import traceback

from rubka import Robot, Message
from rubka.button import InlineBuilder

import config
import database
from questions import QUESTIONS


# =========================================================
# STARTUP
# =========================================================

database.init()

bot = Robot(token=config.BOT_TOKEN)

ADMIN_ID = str(config.ADMIN_ID)

DEFAULT_SCORE = int(os.getenv("DEFAULT_SCORE", "3"))
BOT_NAME = os.getenv("BOT_NAME", "یار رسانه")


# =========================================================
# CHAPTERS / LESSONS
# =========================================================

CHAPTERS = {
    1: "ما و رسانه‌ها",
    2: "فنون خلق پیام رسانه‌ای",
    3: "نادیده‌های رسانه‌ها",
    4: "مخاطب‌شناسی",
    5: "رسانه و سبک زندگی",
    6: "رژیم مصرف رسانه‌ای",
}

LESSONS = {
    1: "مسابقه رسانه‌ها با زمان",
    2: "آن سوی متن",
    3: "پنجگانه سواد رسانه‌ای",

    4: "تصاویر بی‌طرف نیستند",
    5: "از بازنمایی تا کلیشه",
    6: "فنون اقناع",
    7: "ذهن فریب‌پذیر",

    8: "مهندسان پیام",
    9: "بازیگردانان بزرگ",
    10: "دروازه‌بانی خبر",

    11: "مخاطب خاص",
    12: "مخاطب فعال یا منفعل",
    13: "حقوق مخاطب",

    14: "هر چیز که در جستن آنی، آنی",
    15: "کلیشه بدن",
    16: "بازی، جدی است",
    17: "زندگی دوم",
    18: "علیه اخبار جعلی",

    19: "سلامت رسانه‌ای",
    20: "اخلاق رسانه‌ای",
}


LESSON_CHAPTER = {
    1: 1, 2: 1, 3: 1,
    4: 2, 5: 2, 6: 2, 7: 2,
    8: 3, 9: 3, 10: 3,
    11: 4, 12: 4, 13: 4,
    14: 5, 15: 5, 16: 5, 17: 5, 18: 5,
    19: 6, 20: 6,
}


# صفحات شروع درس‌ها طبق فهرست کتاب
LESSON_PAGES = {
    1: 12,
    2: 19,
    3: 24,

    4: 32,
    5: 39,
    6: 45,
    7: 57,

    8: 66,
    9: 73,
    10: 81,

    11: 92,
    12: 99,
    13: 109,

    14: 118,
    15: 125,
    16: 130,
    17: 140,
    18: 145,

    19: 154,
    20: 164,
}


# =========================================================
# HELPERS
# =========================================================

def sid(value):
    return str(value)


def is_admin(user_id):
    return sid(user_id) == ADMIN_ID


def safe_text(message):
    return (getattr(message, "text", "") or "").strip()


def get_sender_id(message):
    return sid(getattr(message, "sender_id", "") or "")


def get_chat_id(message):
    return sid(getattr(message, "chat_id", "") or "")


def get_student(user_id):
    return database.get_student(sid(user_id))


def is_registered(user_id):
    return get_student(user_id) is not None


def register_required(message):
    user_id = get_sender_id(message)

    if not is_registered(user_id):
        message.reply(
            "⚠️ شما هنوز در لیست دانش‌آموزان ثبت نشده‌اید.\n\n"
            "از مدیر بخواهید شما را با شناسه کاربری‌تان ثبت کند."
        )
        return False

    return True


def question_keyboard(question):
    builder = InlineBuilder()

    builder = builder.row(
        builder.button_simple(
            f"q:{question['id']}:a",
            f"🅰️ {question['option_a']}"
        )
    )

    builder = builder.row(
        builder.button_simple(
            f"q:{question['id']}:b",
            f"🅱️ {question['option_b']}"
        )
    )

    builder = builder.row(
        builder.button_simple(
            f"q:{question['id']}:c",
            f"©️ {question['option_c']}"
        )
    )

    builder = builder.row(
        builder.button_simple(
            f"q:{question['id']}:d",
            f"🅳 {question['option_d']}"
        )
    )

    return builder.build()


def question_text(question):
    lesson = question.get("lesson", "")
    chapter = question.get("chapter", "")
    page = question.get("source_page", "")

    return (
        "📚 **سؤال تفکر و سواد رسانه‌ای**\n\n"
        f"📖 فصل: {chapter}\n"
        f"📘 درس: {lesson}\n\n"
        f"❓ {question['question']}\n\n"
        f"📌 منبع: صفحه {page}"
    )


def normalize_answer(value):
    value = str(value).strip().lower()

    mapping = {
        "a": "a",
        "b": "b",
        "c": "c",
        "d": "d",

        "الف": "a",
        "ب": "b",
        "ج": "c",
        "د": "d",
    }

    return mapping.get(value, value)


def correct_option_text(question):
    correct = normalize_answer(question["correct"])

    options = {
        "a": question["option_a"],
        "b": question["option_b"],
        "c": question["option_c"],
        "d": question["option_d"],
    }

    return options.get(correct, "نامشخص")


def get_random_question(lesson=None):
    try:
        if lesson is not None:
            rows = database.get_questions(
                lesson=int(lesson),
                enabled=1
            )
        else:
            rows = database.get_questions(
                enabled=1
            )

        if not rows:
            return None

        row = random.choice(rows)

        if isinstance(row, dict):
            return row

        return dict(row)

    except Exception:
        traceback.print_exc()
        return None


def send_question(message, lesson=None):
    question = get_random_question(lesson)

    if not question:
        message.reply(
            "❌ فعلاً برای این درس سؤال ثبت نشده است."
        )
        return

    text = question_text(question)

    try:
        message.reply(
            text,
            inline_keypad=question_keyboard(question)
        )
    except Exception:
        # بعضی نسخه‌های Rubka پارامتر را متفاوت می‌گیرند.
        try:
            message.reply(
                text,
                inline_keypad=question_keyboard(question)
            )
        except Exception as e:
            print("QUESTION SEND ERROR:", repr(e))
            message.reply(text)


# =========================================================
# START
# =========================================================

@bot.on_message(commands=["start"])
def start(bot, message):

    message.reply(
        f"🔥 {BOT_NAME}\n\n"
        "سلام! من یار رسانه هستم 🤖📚\n\n"
        "برای شروع می‌تونی بنویسی:\n"
        "• سوال\n"
        "• سوال ۳\n"
        "• امتیاز\n"
        "• جدول\n"
        "• راهنما\n\n"
        "موفق باشی دانش‌آموز رسانه‌ای 😎"
    )


# =========================================================
# HELP
# =========================================================

@bot.on_message(commands=["help"])
def help_command(bot, message):

    message.reply(
        "📚 راهنمای یار رسانه\n\n"
        "📝 سوال\n"
        "یک سؤال تصادفی از کتاب\n\n"
        "📝 سوال ۳\n"
        "سؤال از درس ۳\n\n"
        "🏆 امتیاز\n"
        "مشاهده امتیاز شما\n\n"
        "🏆 جدول\n"
        "مشاهده رتبه‌بندی کلاس\n\n"
        "🤖 ربات\n"
        "سلام کردن به ربات\n\n"
        "مدیر:\n"
        "/admin"
    )


# =========================================================
# CALLBACK / ANSWERS
# =========================================================

@bot.on_callback()
def callback_handler(bot, message):

    try:

        aux = getattr(message, "aux_data", None)

        if not aux:
            return

        button_id = getattr(aux, "button_id", "") or ""

        if not button_id.startswith("q:"):
            return

        parts = button_id.split(":")

        if len(parts) != 3:
            return

        question_id = int(parts[1])
        selected = normalize_answer(parts[2])

        user_id = get_sender_id(message)

        if not is_registered(user_id):

            message.reply(
                "⚠️ شما هنوز ثبت‌نام نشده‌اید.\n"
                "از مدیر بخواهید ابتدا شما را ثبت کند."
            )
            return

        question = database.get_question(question_id)

        if not question:

            message.reply("❌ این سؤال پیدا نشد.")
            return

        # تبدیل sqlite row به dict
        try:
            question = dict(question)
        except Exception:
            pass

        correct = normalize_answer(question["correct"])

        if selected == correct:

            score = int(
                question.get(
                    "score",
                    DEFAULT_SCORE
                ) or DEFAULT_SCORE
            )

            database.record_answer(
                user_id,
                question_id,
                selected,
                True,
                score
            )

            message.reply(
                "🎉 پاسخ درست بود!\n\n"
                f"✅ گزینه صحیح: {correct.upper()}\n"
                f"📌 پاسخ: {correct_option_text(question)}\n\n"
                f"⭐ امتیاز شما: +{score}\n\n"
                f"📖 منبع: صفحه {question.get('source_page', '-')}\n"
                f"📚 درس: {question.get('lesson', '-')}"
            )

        else:

            database.record_answer(
                user_id,
                question_id,
                selected,
                False,
                0
            )

            message.reply(
                "❌ پاسخ اشتباه بود.\n\n"
                f"✅ پاسخ صحیح: گزینه {correct.upper()}\n"
                f"📌 {correct_option_text(question)}\n\n"
                f"📖 منبع: صفحه {question.get('source_page', '-')}\n"
                f"📚 درس: {question.get('lesson', '-')}"
            )

    except Exception as e:

        print("CALLBACK ERROR:", repr(e))
        traceback.print_exc()

        try:
            message.reply(
                "❌ هنگام بررسی پاسخ مشکلی پیش آمد."
            )
        except Exception:
            pass


# =========================================================
# GROUP MESSAGES
# =========================================================

@bot.on_message_group()
def group_message(bot, message):

    try:

        text = safe_text(message)
        user_id = get_sender_id(message)
        chat_id = get_chat_id(message)

        print(
            f"👥 GROUP | chat={chat_id} "
            f"user={user_id} text={text!r}"
        )

        if not text:
            return

        # -----------------------------------------
        # ربات
        # -----------------------------------------

        if text.lower() in ["ربات", "بات", "یار رسانه"]:

            message.reply(
                random.choice([
                    "سلام 😎🤖 در خدمتم!",
                    "جانم؟ 👀",
                    "بله؟ 🤖 بگو ببینم!",
                    "یار رسانه حاضر است 🔥📚",
                    "در خدمتم 🫡",
                ])
            )
            return

        # -----------------------------------------
        # راهنما
        # -----------------------------------------

        if text in ["راهنما", "کمک", "help"]:

            message.reply(
                "📚 راهنمای سریع\n\n"
                "📝 سوال ← سؤال تصادفی\n"
                "📝 سوال ۵ ← سؤال از درس ۵\n"
                "🏆 امتیاز ← امتیاز شما\n"
                "🏆 جدول ← رتبه‌بندی کلاس\n"
                "🤖 ربات ← صدا زدن من"
            )
            return

        # -----------------------------------------
        # امتیاز
        # -----------------------------------------

        if text in ["امتیاز", "نمره", "امتیاز من"]:

            if not register_required(message):
                return

            student = get_student(user_id)

            message.reply(
                "🏆 آمار شما\n\n"
                f"👤 {student['name']}\n"
                f"⭐ امتیاز: {student['score']}\n"
                f"✅ درست: {student['correct']}\n"
                f"❌ غلط: {student['wrong']}\n"
                f"📝 پاسخ‌ها: {student['total']}"
            )
            return

        # -----------------------------------------
        # جدول
        # -----------------------------------------

        if text in ["جدول", "رتبه", "رتبه بندی", "رتبه‌بندی"]:

            rows = database.leaderboard(limit=20)

            if not rows:

                message.reply(
                    "🏆 هنوز کسی امتیازی ثبت نکرده است."
                )
                return

            output = "🏆 جدول امتیازات کلاس\n\n"

            medals = ["🥇", "🥈", "🥉"]

            for index, row in enumerate(rows, start=1):

                try:
                    name = row["name"]
                    score = row["score"]
                except Exception:
                    name = row[1]
                    score = row[2]

                medal = medals[index - 1] if index <= 3 else f"{index}."

                output += (
                    f"{medal} {name} — ⭐ {score}\n"
                )

            message.reply(output)
            return

        # -----------------------------------------
        # سوال
        # -----------------------------------------

        normalized = text.replace("سؤال", "سوال").strip()

        if normalized == "سوال":

            if not register_required(message):
                return

            send_question(message)
            return

        if normalized.startswith("سوال "):

            if not register_required(message):
                return

            value = normalized.replace("سوال ", "", 1).strip()

            if value.isdigit():

                lesson = int(value)

                if lesson not in LESSONS:

                    message.reply(
                        "❌ شماره درس باید بین ۱ تا ۲۰ باشد."
                    )
                    return

                send_question(message, lesson)
                return

        # -----------------------------------------
        # پیام عادی
        # -----------------------------------------

        # فقط برای کلمه‌های مشخص جواب می‌دهیم
        # تا ربات وسط صحبت کلاس مزاحم نشود.

    except Exception as e:

        print("GROUP ERROR:", repr(e))
        traceback.print_exc()


# =========================================================
# ADMIN COMMANDS
# =========================================================

@bot.on_message(commands=["admin"])
def admin_panel(bot, message):

    user_id = get_sender_id(message)

    if not is_admin(user_id):

        message.reply(
            "⛔ این بخش فقط برای مدیر ربات است."
        )
        return

    message.reply(
        "👑 پنل مدیریت\n\n"
        "/students\n"
        "لیست دانش‌آموزان\n\n"
        "/stats\n"
        "آمار ربات\n\n"
        "/addstudent USER_ID NAME\n"
        "ثبت دانش‌آموز\n\n"
        "/delstudent USER_ID\n"
        "حذف دانش‌آموز\n\n"
        "/setlesson CHAPTER LESSON\n"
        "تنظیم درس فعال\n\n"
        "/warn USER_ID\n"
        "ثبت اخطار\n\n"
        "/unwarn USER_ID\n"
        "حذف اخطار\n\n"
        "/addq ...\n"
        "افزودن سؤال"
    )


# =========================================================
# ADD STUDENT
# =========================================================

@bot.on_message(commands=["addstudent"])
def add_student(bot, message):

    if not is_admin(get_sender_id(message)):
        message.reply("⛔ دسترسی ندارید.")
        return

    args = getattr(message, "args", []) or []

    if len(args) < 2:

        message.reply(
            "فرمت:\n"
            "/addstudent USER_ID NAME"
        )
        return

    user_id = args[0]
    name = " ".join(args[1:])

    database.add_student(user_id, name)

    message.reply(
        "✅ دانش‌آموز ثبت شد.\n\n"
        f"👤 نام: {name}\n"
        f"🆔 ID: {user_id}"
    )


# =========================================================
# DELETE STUDENT
# =========================================================

@bot.on_message(commands=["delstudent"])
def delete_student(bot, message):

    if not is_admin(get_sender_id(message)):
        message.reply("⛔ دسترسی ندارید.")
        return

    args = getattr(message, "args", []) or []

    if len(args) != 1:

        message.reply(
            "فرمت:\n"
            "/delstudent USER_ID"
        )
        return

    database.delete_student(args[0])

    message.reply(
        "✅ دانش‌آموز حذف شد."
    )


# =========================================================
# STUDENTS
# =========================================================

@bot.on_message(commands=["students"])
def students(bot, message):

    if not is_admin(get_sender_id(message)):
        message.reply("⛔ دسترسی ندارید.")
        return

    rows = database.get_students()

    if not rows:

        message.reply(
            "👥 هنوز دانش‌آموزی ثبت نشده است."
        )
        return

    output = "👥 دانش‌آموزان ثبت‌شده\n\n"

    for index, row in enumerate(rows, 1):

        try:
            name = row["name"]
            user_id = row["user_id"]
            score = row["score"]
        except Exception:
            name = row[1]
            user_id = row[0]
            score = row[2]

        output += (
            f"{index}. {name}\n"
            f"🆔 {user_id}\n"
            f"⭐ {score}\n\n"
        )

    message.reply(output)


# =========================================================
# STATS
# =========================================================

@bot.on_message(commands=["stats"])
def stats(bot, message):

    if not is_admin(get_sender_id(message)):
        message.reply("⛔ دسترسی ندارید.")
        return

    students = database.get_students()
    count = database.count_questions()

    total_score = 0
    total_correct = 0
    total_wrong = 0

    for row in students:

        try:
            total_score += int(row["score"] or 0)
            total_correct += int(row["correct"] or 0)
            total_wrong += int(row["wrong"] or 0)
        except Exception:
            pass

    message.reply(
        "📊 آمار ربات\n\n"
        f"👥 دانش‌آموزان: {len(students)}\n"
        f"❓ تعداد سؤال‌ها: {count}\n"
        f"⭐ مجموع امتیازات: {total_score}\n"
        f"✅ پاسخ‌های درست: {total_correct}\n"
        f"❌ پاسخ‌های غلط: {total_wrong}"
    )


# =========================================================
# WARN
# =========================================================

@bot.on_message(commands=["warn"])
def warn(bot, message):

    if not is_admin(get_sender_id(message)):
        message.reply("⛔ دسترسی ندارید.")
        return

    args = getattr(message, "args", []) or []

    if len(args) != 1:

        message.reply(
            "فرمت:\n"
            "/warn USER_ID"
        )
        return

    database.warn_student(args[0])

    message.reply(
        f"⚠️ برای کاربر {args[0]} یک اخطار ثبت شد."
    )


# =========================================================
# UNWARN
# =========================================================

@bot.on_message(commands=["unwarn"])
def unwarn(bot, message):

    if not is_admin(get_sender_id(message)):
        message.reply("⛔ دسترسی ندارید.")
        return

    args = getattr(message, "args", []) or []

    if len(args) != 1:

        message.reply(
            "فرمت:\n"
            "/unwarn USER_ID"
        )
        return

    database.unwarn_student(args[0])

    message.reply(
        f"✅ اخطارهای کاربر {args[0]} حذف شد."
    )


# =========================================================
# SET LESSON
# =========================================================

@bot.on_message(commands=["setlesson"])
def set_lesson(bot, message):

    if not is_admin(get_sender_id(message)):
        message.reply("⛔ دسترسی ندارید.")
        return

    args = getattr(message, "args", []) or []

    if len(args) != 2:

        message.reply(
            "فرمت:\n"
            "/setlesson CHAPTER LESSON\n\n"
            "مثال:\n"
            "/setlesson 2 6"
        )
        return

    chapter = int(args[0])
    lesson = int(args[1])

    if chapter not in CHAPTERS:

        message.reply("❌ شماره فصل باید بین ۱ تا ۶ باشد.")
        return

    if lesson not in LESSONS:

        message.reply("❌ شماره درس باید بین ۱ تا ۲۰ باشد.")
        return

    if LESSON_CHAPTER.get(lesson) != chapter:

        message.reply(
            "❌ این درس مربوط به این فصل نیست."
        )
        return

    database.set_setting(
        "active_chapter",
        str(chapter)
    )

    database.set_setting(
        "active_lesson",
        str(lesson)
    )

    message.reply(
        "✅ درس فعال تغییر کرد.\n\n"
        f"📚 فصل {chapter}: {CHAPTERS[chapter]}\n"
        f"📘 درس {lesson}: {LESSONS[lesson]}\n"
        f"📖 صفحه شروع: {LESSON_PAGES[lesson]}"
    )


# =========================================================
# ADD QUESTION
# =========================================================

@bot.on_message(commands=["addq"])
def add_question(bot, message):

    if not is_admin(get_sender_id(message)):
        message.reply("⛔ دسترسی ندارید.")
        return

    message.reply(
        "ℹ️ برای جلوگیری از خراب شدن سؤال‌ها، "
        "بانک اصلی سؤال‌ها از فایل questions.py مدیریت می‌شود.\n\n"
        "بعداً پنل حرفه‌ای افزودن سؤال را هم به همین ربات اضافه می‌کنیم."
    )


# =========================================================
# DELETE MESSAGE
# =========================================================

@bot.on_message(commands=["delmsg"])
def delete_message(bot, message):

    if not is_admin(get_sender_id(message)):
        message.reply("⛔ دسترسی ندارید.")
        return

    args = getattr(message, "args", []) or []

    if len(args) != 1:

        message.reply(
            "فرمت:\n"
            "/delmsg MESSAGE_ID"
        )
        return

    try:

        bot.delete_message(
            get_chat_id(message),
            args[0]
        )

        message.reply("🗑 پیام حذف شد.")

    except Exception as e:

        print("DELETE ERROR:", repr(e))

        message.reply(
            "❌ حذف پیام انجام نشد."
        )


# =========================================================
# COMMANDS
# =========================================================

try:

    bot.set_commands([
        {
            "command": "start",
            "description": "شروع ربات"
        },
        {
            "command": "help",
            "description": "راهنمای ربات"
        },
        {
            "command": "admin",
            "description": "پنل مدیریت"
        },
        {
            "command": "students",
            "description": "دانش‌آموزان"
        },
        {
            "command": "stats",
            "description": "آمار"
        },
    ])

    print("✅ دستورات ربات ثبت شدند.")

except Exception as e:

    print(
        "⚠️ ثبت دستورات انجام نشد:",
        repr(e)
    )


# =========================================================
# RUN
# =========================================================

print("======================================")
print(f"🤖 {BOT_NAME}")
print("📚 تفکر و سواد رسانه‌ای دهم")
print("👥 گروه: فعال")
print("📝 آزمون: فعال")
print("🏆 امتیاز: فعال")
print("👑 مدیریت: فعال")
print("======================================")
print("🟢 ربات آماده دریافت پیام است.")
print("======================================")


bot.run()
