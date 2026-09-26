import os
import random
import traceback

from rubka import Robot

import config
import database
from questions import QUESTIONS


# =========================================================
# STARTUP
# =========================================================

database.init()

# وارد کردن خودکار سوال‌های questions.py به دیتابیس
try:
    database.seed_questions(QUESTIONS)
except Exception as e:
    print("❌ QUESTION SEED ERROR:", repr(e))
    traceback.print_exc()


bot = Robot(token=config.BOT_TOKEN)

ADMIN_ID = str(config.ADMIN_ID)

DEFAULT_SCORE = int(
    os.getenv("DEFAULT_SCORE", "3")
)

BOT_NAME = os.getenv(
    "BOT_NAME",
    "یار رسانه"
)


# =========================================================
# CHAPTERS
# =========================================================

CHAPTERS = {

    1: "ما و رسانه‌ها",

    2: "فنون خلق پیام رسانه‌ای",

    3: "نادیده‌های رسانه‌ها",

    4: "مخاطب‌شناسی",

    5: "رسانه و سبک زندگی",

    6: "رژیم مصرف رسانه‌ای",
}


# =========================================================
# LESSONS
# =========================================================

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


# =========================================================
# LESSON -> CHAPTER
# =========================================================

LESSON_CHAPTER = {

    1: 1,
    2: 1,
    3: 1,

    4: 2,
    5: 2,
    6: 2,
    7: 2,

    8: 3,
    9: 3,
    10: 3,

    11: 4,
    12: 4,
    13: 4,

    14: 5,
    15: 5,
    16: 5,
    17: 5,
    18: 5,

    19: 6,
    20: 6,
}


# =========================================================
# LESSON START PAGES
# =========================================================

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

    return (
        getattr(message, "text", "") or ""
    ).strip()


def get_sender_id(message):

    return sid(
        getattr(
            message,
            "sender_id",
            ""
        ) or ""
    )


def get_chat_id(message):

    return sid(
        getattr(
            message,
            "chat_id",
            ""
        ) or ""
    )


def get_student(user_id):

    return database.get_student(
        sid(user_id)
    )


def is_registered(user_id):

    return get_student(user_id) is not None


def register_required(message):

    user_id = get_sender_id(message)

    if not is_registered(user_id):

        message.reply(
            "⚠️ شما هنوز در لیست دانش‌آموزان ثبت نشده‌اید.\n\n"
            "از مدیر بخواهید شما را با آیدی کاربری‌تان ثبت کند."
        )

        return False

    return True


# =========================================================
# ID
# =========================================================

def id_reply_text(message):

    return (

        "🆔 آیدی شما:\n\n"

        f"`{get_sender_id(message)}`\n\n"

        "💬 آیدی این چت:\n\n"

        f"`{get_chat_id(message)}`"
    )


# =========================================================
# ANSWER NORMALIZER
# =========================================================

def normalize_answer(value):

    value = str(
        value
    ).strip().lower()

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

    return mapping.get(
        value,
        value
    )


# =========================================================
# CORRECT OPTION TEXT
# =========================================================

def correct_option_text(question):

    correct = normalize_answer(
        question["correct"]
    )

    options = {

        "a": question["option_a"],

        "b": question["option_b"],

        "c": question["option_c"],

        "d": question["option_d"],
    }

    return options.get(
        correct,
        "نامشخص"
    )


# =========================================================
# QUESTION KEYBOARD
# =========================================================

def question_keyboard(question):

    from rubka.button import InlineBuilder

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


# =========================================================
# QUESTION TEXT
# =========================================================

def question_text(question):

    chapter = question.get(
        "chapter",
        "-"
    )

    lesson = question.get(
        "lesson",
        "-"
    )

    page = question.get(
        "source_page",
        "-"
    )

    return (

        "📚 سؤال تفکر و سواد رسانه‌ای\n\n"

        f"📖 فصل: {chapter}\n"

        f"📘 درس: {lesson}\n\n"

        f"❓ {question['question']}\n\n"

        f"📌 منبع: صفحه {page}"
    )


# =========================================================
# RANDOM QUESTION
# =========================================================

def get_random_question(
    lesson=None,
    chapter=None
):

    try:

        rows = database.get_questions(

            lesson=lesson,

            chapter=chapter,

            enabled=1
        )

        if not rows:

            return None

        row = random.choice(
            rows
        )

        return dict(row)

    except Exception as e:

        print(
            "❌ GET QUESTION ERROR:",
            repr(e)
        )

        traceback.print_exc()

        return None


# =========================================================
# SEND QUESTION
# =========================================================

def send_question(
    message,
    lesson=None,
    chapter=None
):

    question = get_random_question(
        lesson=lesson,
        chapter=chapter
    )

    if not question:

        if lesson is not None:

            lesson_name = LESSONS.get(
                int(lesson),
                f"درس {lesson}"
            )

            message.reply(
                "❌ برای این درس هنوز سوالی ثبت نشده است.\n\n"
                f"📘 {lesson_name}\n"
                f"🔢 شماره درس: {lesson}\n\n"
                "اگر سوال‌ها را در questions.py گذاشته‌ای، "
                "مطمئن شو فایل ذخیره و Railway دوباره Deploy شده است."
            )

        else:

            message.reply(
                "❌ هنوز هیچ سوالی در بانک سوالات ثبت نشده است."
            )

        return

    text = question_text(
        question
    )

    try:

        message.reply(
            text,
            inline_keypad=question_keyboard(
                question
            )
        )

    except Exception as e:

        print(
            "❌ QUESTION KEYBOARD ERROR:",
            repr(e)
        )

        try:

            message.reply(
                text
            )

        except Exception as e2:

            print(
                "❌ QUESTION SEND ERROR:",
                repr(e2)
            )


# =========================================================
# START
# =========================================================

@bot.on_message(
    commands=["start"]
)
def start(bot, message):

    message.reply(

        f"🔥 {BOT_NAME}\n\n"

        "سلام! من یار رسانه هستم 🤖📚\n\n"

        "برای شروع می‌تونی بنویسی:\n\n"

        "• سوال\n"
        "• سوال ۱\n"
        "• سوال ۲\n"
        "• امتیاز\n"
        "• جدول\n"
        "• آیدی\n"
        "• راهنما\n\n"

        "موفق باشی دانش‌آموز رسانه‌ای 😎"
    )


# =========================================================
# ID COMMAND
# =========================================================

@bot.on_message(
    commands=["id", "myid"]
)
def id_command(
    bot,
    message
):

    message.reply(
        id_reply_text(message)
    )


# =========================================================
# HELP
# =========================================================

@bot.on_message(
    commands=["help"]
)
def help_command(
    bot,
    message
):

    message.reply(

        "📚 راهنمای یار رسانه\n\n"

        "📝 سوال\n"
        "یک سوال تصادفی از کل کتاب\n\n"

        "📝 سوال ۱\n"
        "سوال از درس ۱\n\n"

        "📝 سوال ۵\n"
        "سوال از درس ۵\n\n"

        "🏆 امتیاز\n"
        "مشاهده امتیاز شما\n\n"

        "🏆 جدول\n"
        "مشاهده رتبه‌بندی کلاس\n\n"

        "🆔 آیدی\n"
        "گرفتن آیدی شما و گروه\n\n"

        "🤖 ربات\n"
        "صدا زدن ربات"
    )


# =========================================================
# CALLBACK / ANSWERS
# =========================================================

@bot.on_callback()
def callback_handler(
    bot,
    message
):

    try:

        aux = getattr(
            message,
            "aux_data",
            None
        )

        if not aux:
            return

        button_id = getattr(
            aux,
            "button_id",
            ""
        ) or ""

        if not button_id.startswith(
            "q:"
        ):

            return

        parts = button_id.split(
            ":"
        )

        if len(parts) != 3:

            return

        question_id = int(
            parts[1]
        )

        selected = normalize_answer(
            parts[2]
        )

        user_id = get_sender_id(
            message
        )

        # -----------------------------------------
        # REGISTER CHECK
        # -----------------------------------------

        if not is_registered(
            user_id
        ):

            message.reply(

                "⚠️ شما هنوز ثبت‌نام نشده‌اید.\n\n"

                "از مدیر بخواهید ابتدا شما را "
                "با آیدی کاربری‌تان ثبت کند."
            )

            return

        # -----------------------------------------
        # GET QUESTION
        # -----------------------------------------

        question = database.get_question(
            question_id
        )

        if not question:

            message.reply(
                "❌ این سوال پیدا نشد."
            )

            return

        question = dict(
            question
        )

        correct = normalize_answer(
            question["correct"]
        )

        # -----------------------------------------
        # CHECK ANSWER
        # -----------------------------------------

        if selected == correct:

            score = int(
                question.get(
                    "score",
                    DEFAULT_SCORE
                )
                or DEFAULT_SCORE
            )

            saved = database.record_answer(

                user_id,

                question_id,

                selected,

                True,

                score
            )

            if not saved:

                message.reply(
                    "⚠️ شما قبلاً به این سوال پاسخ داده‌اید."
                )

                return

            message.reply(

                "🎉 آفرین! پاسخ درست بود.\n\n"

                f"✅ گزینه صحیح: {correct.upper()}\n"

                f"📌 پاسخ: "
                f"{correct_option_text(question)}\n\n"

                f"⭐ امتیاز شما: +{score}\n\n"

                f"📖 منبع: صفحه "
                f"{question.get('source_page', '-')}\n"

                f"📘 درس: "
                f"{question.get('lesson', '-')}"
            )

        else:

            saved = database.record_answer(

                user_id,

                question_id,

                selected,

                False,

                0
            )

            if not saved:

                message.reply(
                    "⚠️ شما قبلاً به این سوال پاسخ داده‌اید."
                )

                return

            message.reply(

                "❌ پاسخ اشتباه بود.\n\n"

                f"✅ پاسخ صحیح: گزینه "
                f"{correct.upper()}\n"

                f"📌 پاسخ صحیح: "
                f"{correct_option_text(question)}\n\n"

                f"📖 منبع: صفحه "
                f"{question.get('source_page', '-')}\n"

                f"📘 درس: "
                f"{question.get('lesson', '-')}"
            )

    except Exception as e:

        print(
            "❌ CALLBACK ERROR:",
            repr(e)
        )

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
def group_message(
    bot,
    message
):

    try:

        text = safe_text(
            message
        )

        user_id = get_sender_id(
            message
        )

        chat_id = get_chat_id(
            message
        )

        print(
            f"👥 GROUP | "
            f"chat={chat_id} | "
            f"user={user_id} | "
            f"text={text!r}"
        )

        if not text:

            return

        # =================================================
        # ID
        # =================================================

        normalized_id_check = (

            text
            .replace("‌", "")
            .strip()
            .lower()
        )

        if normalized_id_check in [

            "آیدی",
            "ایدی",
            "id",
            "آی دی"
        ]:

            message.reply(
                id_reply_text(message)
            )

            return

        # =================================================
        # ROBOT
        # =================================================

        if text.lower() in [

            "ربات",
            "بات",
            "یار رسانه"
        ]:

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

        # =================================================
        # HELP
        # =================================================

        if text.lower() in [

            "راهنما",
            "کمک",
            "help"
        ]:

            message.reply(

                "📚 راهنمای سریع\n\n"

                "📝 سوال\n"
                "سوال تصادفی از کل کتاب\n\n"

                "📝 سوال ۱\n"
                "سوال از درس ۱\n\n"

                "📝 سوال ۵\n"
                "سوال از درس ۵\n\n"

                "🏆 امتیاز\n"
                "امتیاز شما\n\n"

                "🏆 جدول\n"
                "جدول امتیازات کلاس\n\n"

                "🆔 آیدی\n"
                "آیدی شما و گروه\n\n"

                "🤖 ربات\n"
                "صدا زدن ربات"
            )

            return

        # =================================================
        # SCORE
        # =================================================

        if text in [

            "امتیاز",
            "نمره",
            "امتیاز من"
        ]:

            if not register_required(
                message
            ):

                return

            student = get_student(
                user_id
            )

            message.reply(

                "🏆 آمار شما\n\n"

                f"👤 {student['name']}\n"

                f"⭐ امتیاز: "
                f"{student['score']}\n"

                f"✅ درست: "
                f"{student['correct']}\n"

                f"❌ غلط: "
                f"{student['wrong']}\n"

                f"📝 پاسخ‌ها: "
                f"{student['total']}"
            )

            return

        # =================================================
        # LEADERBOARD
        # =================================================

        if text in [

            "جدول",
            "رتبه",
            "رتبه بندی",
            "رتبه‌بندی"
        ]:

            rows = database.leaderboard(
                limit=20
            )

            if not rows:

                message.reply(
                    "🏆 هنوز کسی امتیازی ثبت نکرده است."
                )

                return

            output = (
                "🏆 جدول امتیازات کلاس\n\n"
            )

            medals = [

                "🥇",
                "🥈",
                "🥉"
            ]

            for index, row in enumerate(
                rows,
                start=1
            ):

                name = row["name"]

                score = row["score"]

                if index <= 3:

                    rank = medals[
                        index - 1
                    ]

                else:

                    rank = f"{index}."

                output += (

                    f"{rank} "
                    f"{name} "
                    f"— ⭐ {score}\n"
                )

            message.reply(
                output
            )

            return

        # =================================================
        # QUESTION
        # =================================================

        normalized = (

            text
            .replace("سؤال", "سوال")
            .strip()
        )

        # -----------------------------------------
        # سوال تصادفی
        # -----------------------------------------

        if normalized == "سوال":

            if not register_required(
                message
            ):

                return

            send_question(
                message
            )

            return

        # -----------------------------------------
        # سوال شماره‌دار
        # -----------------------------------------

        if normalized.startswith(
            "سوال "
        ):

            if not register_required(
                message
            ):

                return

            value = normalized.replace(
                "سوال ",
                "",
                1
            ).strip()

            # -----------------------------------------
            # شماره درس
            # -----------------------------------------

            if value.isdigit():

                lesson = int(
                    value
                )

                if lesson not in LESSONS:

                    message.reply(

                        "❌ شماره درس باید بین "
                        "۱ تا ۲۰ باشد."
                    )

                    return

                send_question(

                    message,

                    lesson=lesson
                )

                return

        # =================================================
        # END NORMAL MESSAGE
        # =================================================

    except Exception as e:

        print(
            "❌ GROUP ERROR:",
            repr(e)
        )

        traceback.print_exc()


# =========================================================
# ADMIN PANEL
# =========================================================

@bot.on_message(
    commands=["admin"]
)
def admin_panel(
    bot,
    message
):

    if not is_admin(
        get_sender_id(message)
    ):

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

        "/id\n"
        "گرفتن آیدی خودتان"
    )


# =========================================================
# ADD STUDENT
# =========================================================

@bot.on_message(
    commands=["addstudent"]
)
def add_student(
    bot,
    message
):

    if not is_admin(
        get_sender_id(message)
    ):

        message.reply(
            "⛔ دسترسی ندارید."
        )

        return

    args = getattr(
        message,
        "args",
        []
    ) or []

    if len(args) < 2:

        message.reply(

            "❌ فرمت صحیح:\n\n"

            "/addstudent USER_ID NAME\n\n"

            "مثال:\n"

            "/addstudent 123456 پارسا"
        )

        return

    user_id = args[0]

    name = " ".join(
        args[1:]
    )

    database.add_student(
        user_id,
        name
    )

    message.reply(

        "✅ دانش‌آموز ثبت شد.\n\n"

        f"👤 نام: {name}\n"

        f"🆔 ID: {user_id}"
    )


# =========================================================
# DELETE STUDENT
# =========================================================

@bot.on_message(
    commands=["delstudent"]
)
def delete_student(
    bot,
    message
):

    if not is_admin(
        get_sender_id(message)
    ):

        message.reply(
            "⛔ دسترسی ندارید."
        )

        return

    args = getattr(
        message,
        "args",
        []
    ) or []

    if len(args) != 1:

        message.reply(

            "❌ فرمت:\n"

            "/delstudent USER_ID"
        )

        return

    database.delete_student(
        args[0]
    )

    message.reply(
        "✅ دانش‌آموز حذف شد."
    )


# =========================================================
# STUDENTS
# =========================================================

@bot.on_message(
    commands=["students"]
)
def students(
    bot,
    message
):

    if not is_admin(
        get_sender_id(message)
    ):

        message.reply(
            "⛔ دسترسی ندارید."
        )

        return

    rows = database.get_students()

    if not rows:

        message.reply(
            "👥 هنوز دانش‌آموزی ثبت نشده است."
        )

        return

    output = (
        "👥 دانش‌آموزان ثبت‌شده\n\n"
    )

    for index, row in enumerate(
        rows,
        start=1
    ):

        output += (

            f"{index}. "
            f"{row['name']}\n"

            f"🆔 {row['user_id']}\n"

            f"⭐ {row['score']}\n\n"
        )

    message.reply(
        output
    )


# =========================================================
# STATS
# =========================================================

@bot.on_message(
    commands=["stats"]
)
def stats(
    bot,
    message
):

    if not is_admin(
        get_sender_id(message)
    ):

        message.reply(
            "⛔ دسترسی ندارید."
        )

        return

    students = database.get_students()

    question_count = (
        database.count_questions()
    )

    total_score = 0

    total_correct = 0

    total_wrong = 0

    for row in students:

        total_score += int(
            row["score"] or 0
        )

        total_correct += int(
            row["correct"] or 0
        )

        total_wrong += int(
            row["wrong"] or 0
        )

    message.reply(

        "📊 آمار ربات\n\n"

        f"👥 دانش‌آموزان: "
        f"{len(students)}\n"

        f"❓ تعداد سوال‌ها: "
        f"{question_count}\n"

        f"⭐ مجموع امتیازات: "
        f"{total_score}\n"

        f"✅ پاسخ‌های درست: "
        f"{total_correct}\n"

        f"❌ پاسخ‌های غلط: "
        f"{total_wrong}"
    )


# =========================================================
# WARN
# =========================================================

@bot.on_message(
    commands=["warn"]
)
def warn(
    bot,
    message
):

    if not is_admin(
        get_sender_id(message)
    ):

        message.reply(
            "⛔ دسترسی ندارید."
        )

        return

    args = getattr(
        message,
        "args",
        []
    ) or []

    if len(args) != 1:

        message.reply(

            "❌ فرمت:\n"

            "/warn USER_ID"
        )

        return

    database.warn_student(
        args[0]
    )

    message.reply(

        f"⚠️ برای کاربر "
        f"{args[0]} یک اخطار ثبت شد."
    )


# =========================================================
# UNWARN
# =========================================================

@bot.on_message(
    commands=["unwarn"]
)
def unwarn(
    bot,
    message
):

    if not is_admin(
        get_sender_id(message)
    ):

        message.reply(
            "⛔ دسترسی ندارید."
        )

        return

    args = getattr(
        message,
        "args",
        []
    ) or []

    if len(args) != 1:

        message.reply(

            "❌ فرمت:\n"

            "/unwarn USER_ID"
        )

        return

    database.unwarn_student(
        args[0]
    )

    message.reply(

        f"✅ اخطارهای کاربر "
        f"{args[0]} حذف شد."
    )


# =========================================================
# SET LESSON
# =========================================================

@bot.on_message(
    commands=["setlesson"]
)
def set_lesson(
    bot,
    message
):

    if not is_admin(
        get_sender_id(message)
    ):

        message.reply(
            "⛔ دسترسی ندارید."
        )

        return

    args = getattr(
        message,
        "args",
        []
    ) or []

    if len(args) != 2:

        message.reply(

            "❌ فرمت:\n\n"

            "/setlesson CHAPTER LESSON\n\n"

            "مثال:\n"

            "/setlesson 2 6"
        )

        return

    try:

        chapter = int(
            args[0]
        )

        lesson = int(
            args[1]
        )

    except ValueError:

        message.reply(
            "❌ شماره فصل و درس باید عدد باشند."
        )

        return

    if chapter not in CHAPTERS:

        message.reply(
            "❌ شماره فصل باید بین ۱ تا ۶ باشد."
        )

        return

    if lesson not in LESSONS:

        message.reply(
            "❌ شماره درس باید بین ۱ تا ۲۰ باشد."
        )

        return

    if LESSON_CHAPTER.get(
        lesson
    ) != chapter:

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

        f"📚 فصل {chapter}: "
        f"{CHAPTERS[chapter]}\n"

        f"📘 درس {lesson}: "
        f"{LESSONS[lesson]}\n"

        f"📖 صفحه شروع: "
        f"{LESSON_PAGES[lesson]}"
    )


# =========================================================
# DELETE MESSAGE
# =========================================================

@bot.on_message(
    commands=["delmsg"]
)
def delete_message(
    bot,
    message
):

    if not is_admin(
        get_sender_id(message)
    ):

        message.reply(
            "⛔ دسترسی ندارید."
        )

        return

    args = getattr(
        message,
        "args",
        []
    ) or []

    if len(args) != 1:

        message.reply(

            "❌ فرمت:\n"

            "/delmsg MESSAGE_ID"
        )

        return

    try:

        bot.delete_message(

            get_chat_id(message),

            args[0]
        )

        message.reply(
            "🗑 پیام حذف شد."
        )

    except Exception as e:

        print(
            "❌ DELETE ERROR:",
            repr(e)
        )

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
            "command": "id",
            "description": "گرفتن آیدی"
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
            "description": "آمار ربات"
        },

    ])

    print(
        "✅ دستورات ربات ثبت شدند."
    )

except Exception as e:

    print(
        "⚠️ ثبت دستورات انجام نشد:",
        repr(e)
    )


# =========================================================
# STARTUP LOG
# =========================================================

print(
    "======================================"
)

print(
    f"🤖 {BOT_NAME}"
)

print(
    "📚 تفکر و سواد رسانه‌ای دهم"
)

print(
    "👥 گروه: فعال"
)

print(
    "📝 آزمون: فعال"
)

print(
    "🏆 امتیاز: فعال"
)

print(
    "🆔 آیدی‌یاب: فعال"
)

print(
    "👑 مدیریت: فعال"
)

print(
    f"❓ تعداد سوالات: "
    f"{database.count_questions()}"
)

print(
    "======================================"
)

print(
    "🟢 ربات آماده دریافت پیام است."
)

print(
    "======================================"
)


# =========================================================
# RUN
# =========================================================

bot.run()
