import sqlite3
import os
from datetime import datetime


DB_PATH = os.getenv("DATABASE_PATH", "bot.db")


# =========================================================
# CONNECTION
# =========================================================

def connect():
    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# INIT DATABASE
# =========================================================

def init():
    conn = connect()
    cur = conn.cursor()

    # دانش‌آموزان
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

    # سوال‌ها
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

    # پاسخ‌ها
    cur.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            question_id INTEGER NOT NULL,
            answer TEXT,
            is_correct INTEGER DEFAULT 0,
            score_added INTEGER DEFAULT 0,
            created_at TEXT,
            UNIQUE(user_id, question_id)
        )
    """)

    # تنظیمات
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # لاگ ادمین
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

    # تنظیمات اولیه
    defaults = {
        "active_chapter": "1",
        "active_lesson": "1",
    }

    for key, value in defaults.items():

        cur.execute(
            """
            INSERT OR IGNORE INTO settings (key, value)
            VALUES (?, ?)
            """,
            (key, value)
        )

    conn.commit()
    conn.close()

    print("✅ Database initialized")


# =========================================================
# SETTINGS
# =========================================================

def set_setting(key, value):

    conn = connect()

    conn.execute(
        """
        INSERT OR REPLACE INTO settings (key, value)
        VALUES (?, ?)
        """,
        (str(key), str(value))
    )

    conn.commit()
    conn.close()


def get_setting(key, default=None):

    conn = connect()

    row = conn.execute(
        """
        SELECT value
        FROM settings
        WHERE key = ?
        """,
        (str(key),)
    ).fetchone()

    conn.close()

    if row is None:
        return default

    return row["value"]


# =========================================================
# STUDENTS
# =========================================================

def add_student(user_id, name):

    conn = connect()

    now = datetime.utcnow().isoformat()

    conn.execute(
        """
        INSERT INTO students
        (
            user_id,
            name,
            score,
            correct,
            wrong,
            total,
            warnings,
            registered_at
        )
        VALUES (?, ?, 0, 0, 0, 0, 0, ?)

        ON CONFLICT(user_id)
        DO UPDATE SET
            name = excluded.name
        """,
        (
            str(user_id),
            str(name),
            now
        )
    )

    conn.commit()
    conn.close()


def get_student(user_id):

    conn = connect()

    row = conn.execute(
        """
        SELECT *
        FROM students
        WHERE user_id = ?
        """,
        (str(user_id),)
    ).fetchone()

    conn.close()

    return row


def delete_student(user_id):

    conn = connect()

    conn.execute(
        """
        DELETE FROM students
        WHERE user_id = ?
        """,
        (str(user_id),)
    )

    conn.commit()
    conn.close()


def get_students():

    conn = connect()

    rows = conn.execute(
        """
        SELECT *
        FROM students
        ORDER BY name COLLATE NOCASE
        """
    ).fetchall()

    conn.close()

    return rows


def leaderboard(limit=20):

    conn = connect()

    rows = conn.execute(
        """
        SELECT *
        FROM students
        ORDER BY score DESC, correct DESC, name ASC
        LIMIT ?
        """,
        (int(limit),)
    ).fetchall()

    conn.close()

    return rows


# =========================================================
# QUESTIONS
# =========================================================

def add_question(
    chapter,
    lesson,
    question,
    option_a,
    option_b,
    option_c,
    option_d,
    correct,
    score=3,
    source_page=None,
    explanation=""
):

    conn = connect()

    cur = conn.execute(
        """
        INSERT INTO questions
        (
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
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
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
            explanation
        )
    )

    question_id = cur.lastrowid

    conn.commit()
    conn.close()

    return question_id


def get_question(question_id):

    conn = connect()

    row = conn.execute(
        """
        SELECT *
        FROM questions
        WHERE id = ?
        """,
        (int(question_id),)
    ).fetchone()

    conn.close()

    return row


def get_questions(
    lesson=None,
    chapter=None,
    enabled=1
):

    conn = connect()

    query = """
        SELECT *
        FROM questions
        WHERE enabled = ?
    """

    params = [int(enabled)]

    if lesson is not None:

        query += """
            AND lesson = ?
        """

        params.append(int(lesson))

    if chapter is not None:

        query += """
            AND chapter = ?
        """

        params.append(int(chapter))

    query += """
        ORDER BY id ASC
    """

    rows = conn.execute(
        query,
        params
    ).fetchall()

    conn.close()

    return rows


def count_questions():

    conn = connect()

    row = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM questions
        WHERE enabled = 1
        """
    ).fetchone()

    conn.close()

    return int(row["count"])


# =========================================================
# ANSWERS
# =========================================================

def record_answer(
    user_id,
    question_id,
    answer,
    is_correct,
    score_added
):

    conn = connect()

    user_id = str(user_id)
    question_id = int(question_id)

    # جلوگیری از جواب دادن دوباره به همان سؤال
    existing = conn.execute(
        """
        SELECT id
        FROM answers
        WHERE user_id = ?
        AND question_id = ?
        """,
        (
            user_id,
            question_id
        )
    ).fetchone()

    if existing:

        conn.close()

        return False

    now = datetime.utcnow().isoformat()

    conn.execute(
        """
        INSERT INTO answers
        (
            user_id,
            question_id,
            answer,
            is_correct,
            score_added,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            question_id,
            str(answer),
            1 if is_correct else 0,
            int(score_added),
            now
        )
    )

    if is_correct:

        conn.execute(
            """
            UPDATE students
            SET
                score = score + ?,
                correct = correct + 1,
                total = total + 1
            WHERE user_id = ?
            """,
            (
                int(score_added),
                user_id
            )
        )

    else:

        conn.execute(
            """
            UPDATE students
            SET
                wrong = wrong + 1,
                total = total + 1
            WHERE user_id = ?
            """,
            (user_id,)
        )

    conn.commit()
    conn.close()

    return True


# =========================================================
# WARNINGS
# =========================================================

def warn_student(user_id):

    conn = connect()

    conn.execute(
        """
        UPDATE students
        SET warnings = warnings + 1
        WHERE user_id = ?
        """,
        (str(user_id),)
    )

    conn.commit()
    conn.close()


def unwarn_student(user_id):

    conn = connect()

    conn.execute(
        """
        UPDATE students
        SET warnings = 0
        WHERE user_id = ?
        """,
        (str(user_id),)
    )

    conn.commit()
    conn.close()


# =========================================================
# LOG
# =========================================================

def log(
    admin_id,
    action,
    target_id=None,
    details=""
):

    conn = connect()

    conn.execute(
        """
        INSERT INTO logs
        (
            admin_id,
            action,
            target_id,
            details,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            str(admin_id),
            str(action),
            str(target_id) if target_id else "",
            str(details),
            datetime.utcnow().isoformat()
        )
    )

    conn.commit()
    conn.close()
