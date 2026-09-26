import sqlite3
import os
from datetime import datetime


# =========================================================
# DATABASE CONFIG
# =========================================================

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

    # =====================================================
    # STUDENTS
    # =====================================================

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

    # =====================================================
    # QUESTIONS
    # =====================================================

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

    # =====================================================
    # ANSWERS
    # =====================================================

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

    # =====================================================
    # SETTINGS
    # =====================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (

            key TEXT PRIMARY KEY,

            value TEXT
        )
    """)

    # =====================================================
    # LOGS
    # =====================================================

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

    # =====================================================
    # DEFAULT SETTINGS
    # =====================================================

    defaults = {

        "active_chapter": "1",

        "active_lesson": "1",

    }

    for key, value in defaults.items():

        cur.execute(
            """
            INSERT OR IGNORE INTO settings
            (
                key,
                value
            )
            VALUES (?, ?)
            """,
            (
                str(key),
                str(value)
            )
        )

    conn.commit()

    conn.close()

    print("======================================")
    print("✅ Database initialized")
    print(f"📁 Database: {DB_PATH}")
    print("======================================")


# =========================================================
# SETTINGS
# =========================================================

def set_setting(key, value):

    conn = connect()

    conn.execute(
        """
        INSERT OR REPLACE INTO settings
        (
            key,
            value
        )
        VALUES (?, ?)
        """,
        (
            str(key),
            str(value)
        )
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
        (
            str(key),
        )
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

    user_id = str(user_id)
    name = str(name)

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
            user_id,
            name,
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
        (
            str(user_id),
        )
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
        (
            str(user_id),
        )
    )

    conn.commit()

    conn.close()


def get_students():

    conn = connect()

    rows = conn.execute(
        """
        SELECT *
        FROM students

        ORDER BY
            name COLLATE NOCASE ASC
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

        ORDER BY
            score DESC,
            correct DESC,
            name ASC

        LIMIT ?
        """,
        (
            int(limit),
        )
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

        VALUES
        (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            1
        )
        """,
        (
            int(chapter),
            int(lesson),
            str(question),
            str(option_a),
            str(option_b),
            str(option_c),
            str(option_d),
            str(correct),
            int(score),
            source_page,
            str(explanation)
        )
    )

    question_id = cur.lastrowid

    conn.commit()

    conn.close()

    return question_id


# =========================================================
# SEED QUESTIONS
# =========================================================

def seed_questions(questions):

    conn = connect()

    added = 0

    skipped = 0

    for q in questions:

        try:

            chapter = int(q["chapter"])

            lesson = int(q["lesson"])

            question_text = str(
                q["question"]
            ).strip()

            option_a = str(
                q["option_a"]
            ).strip()

            option_b = str(
                q["option_b"]
            ).strip()

            option_c = str(
                q["option_c"]
            ).strip()

            option_d = str(
                q["option_d"]
            ).strip()

            correct = str(
                q["correct"]
            ).strip()

            score = int(
                q.get("score", 3)
            )

            source_page = q.get(
                "source_page",
                None
            )

            explanation = str(
                q.get("explanation", "")
            )

            # ---------------------------------------------
            # CHECK DUPLICATE
            # ---------------------------------------------

            exists = conn.execute(
                """
                SELECT id

                FROM questions

                WHERE
                    chapter = ?

                    AND lesson = ?

                    AND question = ?

                LIMIT 1
                """,
                (
                    chapter,
                    lesson,
                    question_text
                )
            ).fetchone()

            if exists:

                skipped += 1

                continue

            # ---------------------------------------------
            # INSERT QUESTION
            # ---------------------------------------------

            conn.execute(
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

                VALUES
                (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    1
                )
                """,
                (
                    chapter,
                    lesson,
                    question_text,
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

            added += 1

        except Exception as e:

            print(
                "❌ Question seed error:",
                repr(e)
            )

    conn.commit()

    conn.close()

    print(
        f"📚 Questions added: {added}"
    )

    print(
        f"⏭ Questions skipped: {skipped}"
    )

    return added


# =========================================================
# GET ONE QUESTION
# =========================================================

def get_question(question_id):

    conn = connect()

    row = conn.execute(
        """
        SELECT *
        FROM questions
        WHERE id = ?
        """,
        (
            int(question_id),
        )
    ).fetchone()

    conn.close()

    return row


# =========================================================
# GET QUESTIONS
# =========================================================

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

    params = [
        int(enabled)
    ]

    # -----------------------------------------
    # LESSON
    # -----------------------------------------

    if lesson is not None:

        query += """
            AND lesson = ?
        """

        params.append(
            int(lesson)
        )

    # -----------------------------------------
    # CHAPTER
    # -----------------------------------------

    if chapter is not None:

        query += """
            AND chapter = ?
        """

        params.append(
            int(chapter)
        )

    query += """
        ORDER BY id ASC
    """

    rows = conn.execute(
        query,
        params
    ).fetchall()

    conn.close()

    return rows


# =========================================================
# COUNT QUESTIONS
# =========================================================

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

    return int(
        row["count"]
    )


# =========================================================
# COUNT QUESTIONS BY LESSON
# =========================================================

def count_questions_by_lesson(lesson):

    conn = connect()

    row = conn.execute(
        """
        SELECT COUNT(*) AS count

        FROM questions

        WHERE
            lesson = ?

            AND enabled = 1
        """,
        (
            int(lesson),
        )
    ).fetchone()

    conn.close()

    return int(
        row["count"]
    )


# =========================================================
# COUNT QUESTIONS BY CHAPTER
# =========================================================

def count_questions_by_chapter(chapter):

    conn = connect()

    row = conn.execute(
        """
        SELECT COUNT(*) AS count

        FROM questions

        WHERE
            chapter = ?

            AND enabled = 1
        """,
        (
            int(chapter),
        )
    ).fetchone()

    conn.close()

    return int(
        row["count"]
    )


# =========================================================
# ENABLE / DISABLE QUESTION
# =========================================================

def set_question_enabled(
    question_id,
    enabled
):

    conn = connect()

    conn.execute(
        """
        UPDATE questions

        SET enabled = ?

        WHERE id = ?
        """,
        (
            1 if enabled else 0,
            int(question_id)
        )
    )

    conn.commit()

    conn.close()


# =========================================================
# DELETE QUESTION
# =========================================================

def delete_question(question_id):

    conn = connect()

    conn.execute(
        """
        DELETE FROM questions

        WHERE id = ?
        """,
        (
            int(question_id),
        )
    )

    conn.commit()

    conn.close()


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

    question_id = int(
        question_id
    )

    # -----------------------------------------
    # CHECK DUPLICATE ANSWER
    # -----------------------------------------

    existing = conn.execute(
        """
        SELECT id

        FROM answers

        WHERE
            user_id = ?

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

    # -----------------------------------------
    # SAVE ANSWER
    # -----------------------------------------

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

        VALUES
        (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )
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

    # -----------------------------------------
    # CORRECT
    # -----------------------------------------

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

    # -----------------------------------------
    # WRONG
    # -----------------------------------------

    else:

        conn.execute(
            """
            UPDATE students

            SET
                wrong = wrong + 1,

                total = total + 1

            WHERE user_id = ?
            """,
            (
                user_id,
            )
        )

    conn.commit()

    conn.close()

    return True


# =========================================================
# USER ANSWER HISTORY
# =========================================================

def get_user_answers(
    user_id,
    limit=50
):

    conn = connect()

    rows = conn.execute(
        """
        SELECT
            answers.*,

            questions.question,

            questions.lesson,

            questions.chapter

        FROM answers

        LEFT JOIN questions

        ON answers.question_id = questions.id

        WHERE answers.user_id = ?

        ORDER BY answers.id DESC

        LIMIT ?
        """,
        (
            str(user_id),
            int(limit)
        )
    ).fetchall()

    conn.close()

    return rows


# =========================================================
# WARNING SYSTEM
# =========================================================

def warn_student(user_id):

    conn = connect()

    conn.execute(
        """
        UPDATE students

        SET warnings = warnings + 1

        WHERE user_id = ?
        """,
        (
            str(user_id),
        )
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
        (
            str(user_id),
        )
    )

    conn.commit()

    conn.close()


def get_warnings(user_id):

    conn = connect()

    row = conn.execute(
        """
        SELECT warnings

        FROM students

        WHERE user_id = ?
        """,
        (
            str(user_id),
        )
    ).fetchone()

    conn.close()

    if row is None:

        return 0

    return int(
        row["warnings"] or 0
    )


# =========================================================
# LOG SYSTEM
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

        VALUES
        (
            ?,
            ?,
            ?,
            ?,
            ?
        )
        """,
        (
            str(admin_id),
            str(action),
            str(target_id)
            if target_id else "",

            str(details),

            datetime.utcnow().isoformat()
        )
    )

    conn.commit()

    conn.close()


# =========================================================
# GET LOGS
# =========================================================

def get_logs(limit=50):

    conn = connect()

    rows = conn.execute(
        """
        SELECT *

        FROM logs

        ORDER BY id DESC

        LIMIT ?
        """,
        (
            int(limit),
        )
    ).fetchall()

    conn.close()

    return rows


# =========================================================
# DATABASE TEST
# =========================================================

if __name__ == "__main__":

    print("======================================")
    print("🗄 Database Test")
    print("======================================")

    init()

    print(
        "👥 Students:",
        len(get_students())
    )

    print(
        "❓ Questions:",
        count_questions()
    )

    print("======================================")
    print("✅ Database is ready")
    print("======================================")
