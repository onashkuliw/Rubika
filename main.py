# ============================================================
# یار رسانه | ربات تفکر و سواد رسانه‌ای پایه دهم
# Rubika Bot - Rubka
# ============================================================

import asyncio
import os
import sqlite3
from datetime import datetime

from rubka import Robot, Message
from rubka.button import InlineBuilder

import config


# ============================================================
# تنظیمات
# ============================================================

BOT_NAME = getattr(config, "BOT_NAME", "یار رسانه")
DB_PATH = getattr(config, "DATABASE_PATH", "bot.db")
ADMIN_ID = str(config.ADMIN_ID)

DEFAULT_SCORE = int(getattr(config, "DEFAULT_SCORE", 3))


# ============================================================
# ساخت ربات
# ============================================================

bot = Robot(token=config.BOT_TOKEN)


# ============================================================
# فصل‌های کتاب
# ============================================================

CHAPTERS = {
    1: "ما و رسانه‌ها",
    2: "فنون خلق پیام رسانه‌ای",
    3: "نادیده‌های رسانه‌ها",
    4: "مخاطب‌شناسی",
    5: "رسانه و سبک زندگی",
    6: "رژیم مصرف رسانه‌ای",
}


# ============================================================
# درس‌های کتاب
# ============================================================

LESSONS = {
    1: "درس ۱ - رسانه چیست؟",
    2: "درس ۲ - پیام‌های رسانه‌ای",
    3: "درس ۳ - ارتباط و رسانه",
    4: "درس ۴ - عناصر پیام رسانه‌ای",
    5: "درس ۵ - قالب‌های رسانه‌ای",
    6: "درس ۶ - زبان رسانه",
    7: "درس ۷ - تفکر سریع و کند",
    8: "درس ۸ - نادیده‌های رسانه",
    9: "درس ۹ - متن و فرامتن",
    10: "درس ۱۰ - واقعیت رسانه‌ای",
    11: "درس ۱۱ - مخاطب",
    12: "درس ۱۲ - مخاطب فعال",
    13: "درس ۱۳ - تحلیل مخاطب",
    14: "درس ۱۴ - رسانه و زندگی",
    15: "درس ۱۵ - سبک زندگی رسانه‌ای",
    16: "درس ۱۶ - رسانه و خانواده",
    17: "درس ۱۷ - رسانه و هویت",
    18: "درس ۱۸ - رسانه و الگوهای زندگی",
    19: "درس ۱۹ - مصرف رسانه‌ای",
    20: "درس ۲۰ - مدیریت مصرف رسانه‌ای",
}


# ============================================================
# دیتابیس
# ============================================================

def db():
    return sqlite3.connect(DB_PATH)


def init_database():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            score INTEGER DEFAULT 0,
            correct INTEGER DEFAULT 0,
            wrong INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0,
            warnings INTEGER DEFAULT 0,
            registered_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter INTEGER,
            lesson INTEGER,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct TEXT NOT NULL,
            score INTEGER DEFAULT 3,
            source_page INTEGER,
            explanation TEXT,
            enabled INTEGER DEFAULT 1
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            question_id INTEGER,
            answer TEXT,
            is_correct INTEGER,
            score_added INTEGER,
            created_at TEXT,
            UNIQUE(user_id, question_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id TEXT,
            action TEXT,
            target_id TEXT,
            details TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# دانش‌آموز
# ============================================================

def get_student(user_id):
    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT user_id,name,score,correct,wrong,total,warnings "
        "FROM students WHERE user_id=?",
        (str(user_id),)
    )

    row = cur.fetchone()
    conn.close()

    return row


def add_student(user_id, name):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO students
        (user_id,name,score,correct,wrong,total,warnings,registered_at)
        VALUES (
            ?,
            ?,
            COALESCE((SELECT score FROM students WHERE user_id=?),0),
            COALESCE((SELECT correct FROM students WHERE user_id=?),0),
            COALESCE((SELECT wrong FROM students WHERE user_id=?),0),
            COALESCE((SELECT total FROM students WHERE user_id=?),0),
            COALESCE((SELECT warnings FROM students WHERE user_id=?),0),
            COALESCE(
                (SELECT registered_at FROM students WHERE user_id=?),
                ?
            )
        )
    """, (
        str(user_id),
        name,
        str(user_id),
        str(user_id),
        str(user_id),
        str(user_id),
        str(user_id),
        str(user_id),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def delete_student(user_id):
    conn = db()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM students WHERE user_id=?",
        (str(user_id),)
    )

    conn.commit()
    conn.close()


def get_students():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id,name,score,correct,wrong,total,warnings
        FROM students
        ORDER BY score DESC, correct DESC
    """)

    rows = cur.fetchall()
    conn.close()

    return rows


def get_leaderboard():
    return get_students()


# ============================================================
# سؤال‌ها
# ============================================================

def get_question(question_id):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            chapter,
            lesson,
            question,
            option_a,
            option_b,
            option_c,
            option_d,
            correct,
            score,
            source_page,
            explanation,
            enabled
        FROM questions
        WHERE id=? AND enabled=1
    """, (question_id,))

    row = cur.fetchone()
    conn.close()

    return row


def get_questions(lesson=None):
    conn = db()
    cur = conn.cursor()

    if lesson is None:
        cur.execute("""
            SELECT *
            FROM questions
            WHERE enabled=1
            ORDER BY id
        """)
    else:
        cur.execute("""
            SELECT *
            FROM questions
            WHERE lesson=? AND enabled=1
            ORDER BY id
        """, (lesson,))

    rows = cur.fetchall()
    conn.close()

    return rows


def question_count():
    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM questions WHERE enabled=1"
    )

    count = cur.fetchone()[0]
    conn.close()

    return count


# ============================================================
# ثبت پاسخ
# ============================================================

def answer_question(user_id, question_id, answer):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM answers
        WHERE user_id=? AND question_id=?
    """, (str(user_id), question_id))

    already = cur.fetchone()

    if already:
        conn.close()
        return None

    question = get_question(question_id)

    if not question:
        conn.close()
        return None

    correct_answer = str(question[8]).lower()
    score = int(question[9] or DEFAULT_SCORE)

    is_correct = str(answer).lower() == correct_answer
    score_added = score if is_correct else 0

    cur.execute("""
        INSERT INTO answers
        (user_id,question_id,answer,is_correct,score_added,created_at)
        VALUES (?,?,?,?,?,?)
    """, (
        str(user_id),
        question_id,
        str(answer),
        1 if is_correct else 0,
        score_added,
        datetime.now().isoformat()
    ))

    if is_correct:
        cur.execute("""
            UPDATE students
            SET
                score=score+?,
                correct=correct+1,
                total=total+1
            WHERE user_id=?
        """, (score_added, str(user_id)))
    else:
        cur.execute("""
            UPDATE students
            SET
                wrong=wrong+1,
                total=total+1
            WHERE user_id=?
        """, (str(user_id),))

    conn.commit()
    conn.close()

    return {
        "correct": is_correct,
        "score": score_added,
        "correct_answer": correct_answer,
        "question": question
    }


# ============================================================
# تنظیمات ربات
# ============================================================

def set_setting(key, value):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO settings(key,value)
        VALUES (?,?)
    """, (key, str(value)))

    conn.commit()
    conn.close()


def get_setting(key, default=None):
    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT value FROM settings WHERE key=?",
        (key,)
    )

    row = cur.fetchone()
    conn.close()

    if row:
        return row[0]

    return default


# ============================================================
# تشخیص ادمین
# ============================================================

def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID)


def admin_only(message):
    if not is_admin(message.sender_id):
        message.reply(
            "⛔ این بخش فقط برای مالک ربات است."
        )
        return False

    return True


# ============================================================
# کیبورد سؤال
# ============================================================

def question_keyboard(question_id):
    builder = InlineBuilder()

    keyboard = (
        builder
        .row(
            builder.button_simple(
                id=f"q:{question_id}:a",
                text="🅰️ گزینه اول"
            ),
            builder.button_simple(
                id=f"q:{question_id}:b",
                text="🅱️ گزینه دوم"
            )
        )
        .row(
            builder.button_simple(
                id=f"q:{question_id}:c",
                text="©️ گزینه سوم"
            ),
            builder.button_simple(
                id=f"q:{question_id}:d",
                text="🆎 گزینه چهارم"
            )
        )
        .build()
    )

    return keyboard


# ============================================================
# نمایش سؤال
# ============================================================

def send_question(message, lesson=None):

    student = get_student(message.sender_id)

    if not student:
        message.reply(
            "⛔ شما هنوز توسط مدیر ثبت نشده‌اید.\n\n"
            "از مدیر بخواهید شما را با دستور زیر ثبت کند:\n"
            "/addstudent USER_ID NAME"
        )
        return

    questions = get_questions(lesson)

    if not questions:
        message.reply(
            "⚠️ فعلاً برای این درس سؤالی ثبت نشده است."
        )
        return

    # انتخاب سؤال
    # برای جلوگیری از سؤال تکراری، سؤال‌هایی که کاربر قبلاً جواب داده را حذف می‌کنیم.
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT question_id
        FROM answers
        WHERE user_id=?
    """, (str(message.sender_id),))

    answered = {row[0] for row in cur.fetchall()}

    conn.close()

    available = [
        q for q in questions
        if q[0] not in answered
    ]

    if not available:
        message.reply(
            "🎉 آفرین!\n"
            "شما تمام سؤال‌های این بخش را پاسخ داده‌اید."
        )
        return

    question = available[0]

    qid = question[0]
    chapter = question[1]
    lesson_number = question[2]
    text = question[3]

    a = question[4]
    b = question[5]
    c = question[6]
    d = question[7]

    source_page = question[10]

    lesson_name = LESSONS.get(
        lesson_number,
        f"درس {lesson_number}"
    )

    chapter_name = CHAPTERS.get(
        chapter,
        f"فصل {chapter}"
    )

    msg = (
        f"📚 {chapter_name}\n"
        f"📖 {lesson_name}\n\n"
        f"❓ {text}\n\n"
        f"🅰️ {a}\n"
        f"🅱️ {b}\n"
        f"©️ {c}\n"
        f"🆎 {d}\n\n"
        f"🏆 امتیاز سؤال: {question[9]} نمره\n"
        f"📄 منبع: صفحه {source_page}\n\n"
        f"👇 جواب درست رو انتخاب کن:"
    )

    message.reply_inline(
        msg,
        question_keyboard(qid)
    )


# ============================================================
# /start
# ============================================================

@bot.on_message(commands=["start"])
async def start(bot, message: Message):

    student = get_student(message.sender_id)

    if student:
        message.reply(
            f"🔥 سلام {student[1]}!\n\n"
            f"به «{BOT_NAME}» خوش اومدی 📚\n\n"
            f"🧠 آماده‌ای دانشت رو امتحان کنی؟\n\n"
            f"📝 سوال\n"
            f"🏆 امتیاز\n"
            f"📊 جدول\n"
            f"👤 من"
        )
    else:
        message.reply(
            f"🔥 به «{BOT_NAME}» خوش اومدی!\n\n"
            "📚 ربات درس تفکر و سواد رسانه‌ای پایه دهم\n\n"
            "⚠️ برای شرکت در مسابقه باید ابتدا توسط مدیر ثبت شوی."
        )


# ============================================================
# /help
# ============================================================

@bot.on_message(commands=["help"])
async def help_command(bot, message: Message):

    text = (
        "📚 راهنمای یار رسانه\n\n"
        "📝 سوال\n"
        "دریافت سؤال جدید\n\n"
        "📝 سوال 5\n"
        "دریافت سؤال از درس ۵\n\n"
        "🏆 امتیاز\n"
        "نمایش امتیاز شما\n\n"
        "📊 جدول\n"
        "نمایش جدول امتیازات\n\n"
        "👤 من\n"
        "نمایش آمار شما\n"
    )

    if is_admin(message.sender_id):
        text += (
            "\n👑 دستورات مدیر:\n\n"
            "/addstudent USER_ID NAME\n"
            "/delstudent USER_ID\n"
            "/students\n"
            "/stats\n"
            "/setlesson CHAPTER LESSON\n"
            "/addq ...\n"
            "/warn USER_ID\n"
            "/unwarn USER_ID\n"
            "/delmsg MESSAGE_ID\n"
        )

    message.reply(text)


# ============================================================
# سوال
# ============================================================

@bot.on_message(commands=["question", "q"])
async def question_command(bot, message: Message):

    active_lesson = get_setting("active_lesson")

    if active_lesson:
        try:
            active_lesson = int(active_lesson)
        except:
            active_lesson = None

    send_question(message, active_lesson)


# ============================================================
# امتیاز
# ============================================================

@bot.on_message(commands=["score"])
async def score_command(bot, message: Message):

    student = get_student(message.sender_id)

    if not student:
        message.reply("⛔ شما هنوز ثبت نشده‌اید.")
        return

    message.reply(
        f"👤 {student[1]}\n\n"
        f"🏆 امتیاز: {student[2]}\n"
        f"✅ درست: {student[3]}\n"
        f"❌ غلط: {student[4]}\n"
        f"📝 پاسخ داده‌شده: {student[5]}\n"
        f"⚠️ اخطار: {student[6]}"
    )


# ============================================================
# من
# ============================================================

@bot.on_message(commands=["me"])
async def me_command(bot, message: Message):

    student = get_student(message.sender_id)

    if not student:
        message.reply("⛔ شما هنوز ثبت نشده‌اید.")
        return

    message.reply(
        "👤 پروفایل شما\n\n"
        f"نام: {student[1]}\n"
        f"🆔 آیدی: {student[0]}\n\n"
        f"🏆 امتیاز: {student[2]}\n"
        f"✅ پاسخ صحیح: {student[3]}\n"
        f"❌ پاسخ غلط: {student[4]}\n"
        f"📚 تعداد پاسخ: {student[5]}\n"
        f"⚠️ اخطار: {student[6]}"
    )


# ============================================================
# جدول امتیازات
# ============================================================

@bot.on_message(commands=["leaderboard", "table"])
async def leaderboard_command(bot, message: Message):

    students = get_leaderboard()

    if not students:
        message.reply(
            "📊 هنوز هیچ دانش‌آموزی ثبت نشده است."
        )
        return

    text = "🏆 جدول امتیازات\n\n"

    medals = ["🥇", "🥈", "🥉"]

    for index, student in enumerate(students, start=1):

        medal = medals[index - 1] if index <= 3 else f"{index}."

        text += (
            f"{medal} {student[1]}\n"
            f"   🏆 {student[2]} امتیاز\n"
            f"   ✅ {student[3]} درست | ❌ {student[4]} غلط\n\n"
        )

    message.reply(text)


# ============================================================
# پاسخ به دکمه‌های سؤال
# ============================================================

@bot.on_callback()
async def callback_handler(bot, message: Message):

    try:
        button_id = message.aux_data.button_id
    except Exception:
        return

    if not button_id:
        return

    if not button_id.startswith("q:"):
        return

    parts = button_id.split(":")

    if len(parts) != 3:
        return

    try:
        question_id = int(parts[1])
    except:
        return

    answer = parts[2].lower()

    student = get_student(message.sender_id)

    if not student:
        message.reply(
            "⛔ شما هنوز توسط مدیر ثبت نشده‌اید."
        )
        return

    result = answer_question(
        message.sender_id,
        question_id,
        answer
    )

    if result is None:
        message.reply(
            "⚠️ این سؤال قبلاً توسط شما پاسخ داده شده یا وجود ندارد."
        )
        return

    question = result["question"]

    correct_answer = result["correct_answer"]

    answer_names = {
        "a": "گزینه اول",
        "b": "گزینه دوم",
        "c": "گزینه سوم",
        "d": "گزینه چهارم",
    }

    correct_name = answer_names.get(
        correct_answer,
        correct_answer
    )

    if result["correct"]:

        new_student = get_student(message.sender_id)

        message.reply(
            "🎉 آفرین! پاسخ درست بود.\n\n"
            f"✅ پاسخ صحیح: {correct_name}\n"
            f"🏆 امتیاز این سؤال: +{result['score']}\n"
            f"💰 امتیاز فعلی شما: {new_student[2]}\n\n"
            f"📄 منبع: صفحه {question[10]}\n"
            f"📚 {LESSONS.get(question[2], f'درس {question[2]}')}"
        )

        if question[11]:
            message.reply(
                f"💡 توضیح:\n{question[11]}"
            )

    else:

        new_student = get_student(message.sender_id)

        message.reply(
            "❌ پاسخ اشتباه بود.\n\n"
            f"✅ پاسخ صحیح: {correct_name}\n"
            f"🏆 امتیاز این سؤال: +0\n"
            f"💰 امتیاز فعلی شما: {new_student[2]}\n\n"
            f"📄 منبع: صفحه {question[10]}"
        )

        if question[11]:
            message.reply(
                f"💡 توضیح:\n{question[11]}"
            )


# ============================================================
# افزودن دانش‌آموز
# ============================================================

@bot.on_message(commands=["addstudent"])
async def addstudent_command(bot, message: Message):

    if not admin_only(message):
        return

    text = (message.text or "").strip()

    parts = text.split(maxsplit=2)

    if len(parts) < 3:
        message.reply(
            "❌ فرمت اشتباه است.\n\n"
            "مثال:\n"
            "/addstudent u0xxxxxxxx پارسا"
        )
        return

    user_id = parts[1]
    name = parts[2]

    add_student(user_id, name)

    message.reply(
        "✅ دانش‌آموز با موفقیت ثبت شد.\n\n"
        f"👤 نام: {name}\n"
        f"🆔 آیدی: {user_id}"
    )


# ============================================================
# حذف دانش‌آموز
# ============================================================

@bot.on_message(commands=["delstudent"])
async def delstudent_command(bot, message: Message):

    if not admin_only(message):
        return

    text = (message.text or "").strip()
    parts = text.split()

    if len(parts) < 2:
        message.reply(
            "❌ مثال:\n"
            "/delstudent u0xxxxxxxx"
        )
        return

    user_id = parts[1]

    student = get_student(user_id)

    if not student:
        message.reply(
            "❌ چنین دانش‌آموزی ثبت نشده است."
        )
        return

    delete_student(user_id)

    message.reply(
        f"🗑 دانش‌آموز «{student[1]}» حذف شد."
    )


# ============================================================
# لیست دانش‌آموزان
# ============================================================

@bot.on_message(commands=["students"])
async def students_command(bot, message: Message):

    if not admin_only(message):
        return

    students = get_students()

    if not students:
        message.reply(
            "📭 هنوز دانش‌آموزی ثبت نشده است."
        )
        return

    text = "👥 لیست دانش‌آموزان\n\n"

    for i, student in enumerate(students, 1):
        text += (
            f"{i}. {student[1]}\n"
            f"🆔 {student[0]}\n"
            f"🏆 {student[2]} امتیاز\n\n"
        )

    message.reply(text)


# ============================================================
# آمار ربات
# ============================================================

@bot.on_message(commands=["stats"])
async def stats_command(bot, message: Message):

    if not admin_only(message):
        return

    students = get_students()
    questions = question_count()

    total_answers = 0

    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM answers")
    total_answers = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM answers WHERE is_correct=1"
    )
    correct_answers = cur.fetchone()[0]

    conn.close()

    message.reply(
        "📊 آمار ربات\n\n"
        f"👥 دانش‌آموزان: {len(students)}\n"
        f"❓ سؤال‌ها: {questions}\n"
        f"📝 پاسخ‌ها: {total_answers}\n"
        f"✅ پاسخ‌های صحیح: {correct_answers}"
    )


# ============================================================
# انتخاب درس فعال
# ============================================================

@bot.on_message(commands=["setlesson"])
async def setlesson_command(bot, message: Message):

    if not admin_only(message):
        return

    text = (message.text or "").strip()
    parts = text.split()

    if len(parts) < 3:
        message.reply(
            "❌ فرمت:\n"
            "/setlesson CHAPTER LESSON\n\n"
            "مثال:\n"
            "/setlesson 1 3"
        )
        return

    try:
        chapter = int(parts[1])
        lesson = int(parts[2])
    except:
        message.reply("❌ شماره فصل و درس باید عدد باشد.")
        return

    if chapter not in CHAPTERS:
        message.reply("❌ چنین فصلی وجود ندارد.")
        return

    if lesson not in LESSONS:
        message.reply("❌ چنین درسی وجود ندارد.")
        return

    set_setting("active_lesson", lesson)
    set_setting("active_chapter", chapter)

    message.reply(
        "✅ درس فعال تغییر کرد.\n\n"
        f"📚 فصل: {chapter} - {CHAPTERS[chapter]}\n"
        f"📖 {LESSONS[lesson]}"
    )


# ============================================================
# افزودن سؤال
# ============================================================

@bot.on_message(commands=["addq"])
async def addq_command(bot, message: Message):

    if not admin_only(message):
        return

    message.reply(
        "ℹ️ برای بانک سؤال اصلی کتاب، سؤال‌ها را از فایل "
        "questions.py وارد می‌کنیم.\n\n"
        "این دستور فعلاً برای جلوگیری از خراب شدن فرمت سؤال "
        "غیرفعال نگه داشته شده است."
    )


# ============================================================
# اخطار
# ============================================================

@bot.on_message(commands=["warn"])
async def warn_command(bot, message: Message):

    if not admin_only(message):
        return

    text = (message.text or "").strip()
    parts = text.split()

    if len(parts) < 2:
        message.reply(
            "❌ مثال:\n"
            "/warn u0xxxxxxxx"
        )
        return

    user_id = parts[1]

    student = get_student(user_id)

    if not student:
        message.reply(
            "❌ این کاربر در لیست دانش‌آموزان نیست."
        )
        return

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE students
        SET warnings=warnings+1
        WHERE user_id=?
    """, (str(user_id),))

    conn.commit()
    conn.close()

    new_student = get_student(user_id)

    message.reply(
        f"⚠️ یک اخطار برای {student[1]} ثبت شد.\n\n"
        f"تعداد اخطارها: {new_student[6]}"
    )


# ============================================================
# لغو اخطار
# ============================================================

@bot.on_message(commands=["unwarn"])
async def unwarn_command(bot, message: Message):

    if not admin_only(message):
        return

    text = (message.text or "").strip()
    parts = text.split()

    if len(parts) < 2:
        message.reply(
            "❌ مثال:\n"
            "/unwarn u0xxxxxxxx"
        )
        return

    user_id = parts[1]

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE students
        SET warnings=CASE
            WHEN warnings > 0 THEN warnings-1
            ELSE 0
        END
        WHERE user_id=?
    """, (str(user_id),))

    conn.commit()
    conn.close()

    message.reply(
        "✅ یک اخطار از کاربر کم شد."
    )


# ============================================================
# حذف پیام
# ============================================================

@bot.on_message(commands=["delmsg"])
async def delmsg_command(bot, message: Message):

    if not admin_only(message):
        return

    text = (message.text or "").strip()
    parts = text.split()

    if len(parts) < 2:
        message.reply(
            "❌ مثال:\n"
            "/delmsg MESSAGE_ID"
        )
        return

    message_id = parts[1]

    try:
        bot.delete_message(
            message.chat_id,
            message_id
        )

        message.reply("🗑 پیام حذف شد.")

    except Exception as e:
        print("Delete message error:", e)
        message.reply(
            "❌ نتونستم پیام رو حذف کنم.\n"
            "ممکنه ربات دسترسی حذف پیام نداشته باشه."
        )


# ============================================================
# پیام‌های متنی معمولی
# ============================================================

@bot.on_message()
async def text_handler(bot, message: Message):

    text = (message.text or "").strip()

    if not text:
        return

    # دستورات را اینجا دوباره پردازش نکن
    if text.startswith("/"):
        return

    normalized = text.replace("‌", "").strip()

    # --------------------------------------------
    # ربات
    # --------------------------------------------

    if normalized.lower() == "ربات":
        message.reply(
            "سلام 😎🔥\n"
            "در خدمتم!\n\n"
            "بیا ببینیم توی تفکر و سواد رسانه‌ای چند چندی 📚🧠\n"
            "بگو «سوال» تا شروع کنیم."
        )
        return

    # --------------------------------------------
    # سوال
    # --------------------------------------------

    if normalized in [
        "سوال",
        "سؤال",
        "سوال بعدی",
        "سؤال بعدی"
    ]:
        active_lesson = get_setting(
            "active_lesson"
        )

        try:
            active_lesson = int(active_lesson)
        except:
            active_lesson = None

        send_question(
            message,
            active_lesson
        )
        return

    # --------------------------------------------
    # امتیاز
    # --------------------------------------------

    if normalized in [
        "امتیاز",
        "امتیاز من",
        "نمره"
    ]:
        student = get_student(message.sender_id)

        if not student:
            message.reply(
                "⛔ شما هنوز ثبت نشده‌اید."
            )
            return

        message.reply(
            f"🏆 امتیاز شما: {student[2]}\n"
            f"✅ درست: {student[3]}\n"
            f"❌ غلط: {student[4]}"
        )
        return

    # --------------------------------------------
    # جدول
    # --------------------------------------------

    if normalized in [
        "جدول",
        "رتبه",
        "رنک",
        "لیدربورد"
    ]:
        students = get_leaderboard()

        if not students:
            message.reply(
                "📊 هنوز کسی ثبت نشده."
            )
            return

        text_out = "🏆 جدول امتیازات\n\n"

        for i, student in enumerate(
            students[:20],
            1
        ):
            text_out += (
                f"{i}. {student[1]} — "
                f"{student[2]} امتیاز\n"
            )

        message.reply(text_out)
        return

    # --------------------------------------------
    # من
    # --------------------------------------------

    if normalized in [
        "من",
        "پروفایل",
        "پروفایل من"
    ]:
        student = get_student(message.sender_id)

        if not student:
            message.reply(
                "⛔ هنوز ثبت نشده‌ای."
            )
            return

        message.reply(
            f"👤 {student[1]}\n\n"
            f"🏆 {student[2]} امتیاز\n"
            f"✅ {student[3]} درست\n"
            f"❌ {student[4]} غلط\n"
            f"📝 {student[5]} پاسخ"
        )
        return


# ============================================================
# راه‌اندازی
# ============================================================

init_database()

print("======================================")
print(f"🤖 {BOT_NAME}")
print("📚 ربات تفکر و سواد رسانه‌ای")
print("🚀 Rubika Bot")
print("======================================")


# ============================================================
# اجرای اصلی
#
# نکته مهم:
# Rubka در نسخه‌ای که روی Railway داری برای اجرای run
# به یک event loop فعال نیاز دارد.
# بنابراین bot.run() را داخل asyncio.run اجرا می‌کنیم.
# ============================================================

async def main():

    try:
        # set_commands در نسخه فعلی Rubka به صورت async اجرا می‌شود.
        await bot.set_commands([
            {
                "command": "start",
                "description": "شروع ربات"
            },
            {
                "command": "help",
                "description": "راهنما"
            },
            {
                "command": "question",
                "description": "سؤال جدید"
            },
            {
                "command": "score",
                "description": "امتیاز من"
            },
            {
                "command": "leaderboard",
                "description": "جدول امتیازات"
            },
            {
                "command": "me",
                "description": "پروفایل من"
            }
        ])

        print("✅ دستورات ربات ثبت شدند.")

    except Exception as e:
        print(
            "⚠️ ثبت دستورات انجام نشد، "
            "ولی ربات ادامه می‌دهد:"
        )
        print(e)

    print("🟢 ربات آماده دریافت پیام است.")

    # اجرای Rubka داخل event loop فعال
    bot.run()


if __name__ == "__main__":
    asyncio.run(main())
