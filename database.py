import sqlite3
from contextlib import contextmanager
from config import DATABASE_PATH, DEFAULT_SCORE

@contextmanager
def db():
    conn = sqlite3.connect(DATABASE_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS students(
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            score INTEGER NOT NULL DEFAULT 0,
            correct INTEGER NOT NULL DEFAULT 0,
            wrong INTEGER NOT NULL DEFAULT 0,
            total INTEGER NOT NULL DEFAULT 0,
            warnings INTEGER NOT NULL DEFAULT 0,
            registered_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS questions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter INTEGER NOT NULL,
            lesson INTEGER NOT NULL,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct TEXT NOT NULL CHECK(correct IN ('a','b','c','d')),
            score INTEGER NOT NULL DEFAULT 3,
            source_page INTEGER,
            explanation TEXT DEFAULT '',
            enabled INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS answers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            question_id INTEGER NOT NULL,
            answer TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            score_added INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, question_id)
        );

        CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id TEXT,
            action TEXT NOT NULL,
            target_id TEXT,
            details TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)

        c.execute(
            "INSERT OR IGNORE INTO settings(key,value) VALUES('active_chapter','1')"
        )
        c.execute(
            "INSERT OR IGNORE INTO settings(key,value) VALUES('active_lesson','1')"
        )
        c.execute(
            "INSERT OR IGNORE INTO settings(key,value) VALUES('default_score',?)",
            (str(DEFAULT_SCORE),)
        )

def setting(key, default=""):
    with db() as c:
        row = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default

def set_setting(key, value):
    with db() as c:
        c.execute(
            "INSERT INTO settings(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, str(value))
        )

def add_student(user_id, name):
    with db() as c:
        c.execute(
            "INSERT INTO students(user_id,name) VALUES(?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET name=excluded.name",
            (str(user_id), name.strip())
        )

def get_student(user_id):
    with db() as c:
        return c.execute(
            "SELECT * FROM students WHERE user_id=?", (str(user_id),)
        ).fetchone()

def remove_student(user_id):
    with db() as c:
        c.execute("DELETE FROM students WHERE user_id=?", (str(user_id),))

def all_students():
    with db() as c:
        return c.execute(
            "SELECT * FROM students ORDER BY score DESC, correct DESC, total ASC"
        ).fetchall()

def leaderboard(limit=20):
    with db() as c:
        return c.execute(
            "SELECT * FROM students ORDER BY score DESC, correct DESC, total ASC LIMIT ?",
            (limit,)
        ).fetchall()

def add_question(chapter, lesson, question, options, correct, score=None,
                 source_page=None, explanation=""):
    score = score or int(setting("default_score", DEFAULT_SCORE))
    with db() as c:
        cur = c.execute(
            """INSERT INTO questions
            (chapter,lesson,question,option_a,option_b,option_c,option_d,
             correct,score,source_page,explanation)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (chapter, lesson, question, options["a"], options["b"],
             options["c"], options["d"], correct.lower(), score,
             source_page, explanation)
        )
        return cur.lastrowid

def get_question(qid):
    with db() as c:
        return c.execute(
            "SELECT * FROM questions WHERE id=? AND enabled=1", (qid,)
        ).fetchone()

def question_by_number(number, chapter, lesson):
    with db() as c:
        return c.execute(
            """SELECT * FROM questions
               WHERE chapter=? AND lesson=? AND enabled=1
               ORDER BY id LIMIT 1 OFFSET ?""",
            (chapter, lesson, number - 1)
        ).fetchone()

def question_count(chapter, lesson):
    with db() as c:
        return c.execute(
            "SELECT COUNT(*) AS n FROM questions WHERE chapter=? AND lesson=? AND enabled=1",
            (chapter, lesson)
        ).fetchone()["n"]

def record_answer(user_id, qid, answer):
    with db() as c:
        q = c.execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone()
        if not q:
            return None, "سؤال پیدا نشد."
        try:
            c.execute(
                "INSERT INTO answers(user_id,question_id,answer,is_correct,score_added) VALUES(?,?,?,?,?)",
                (str(user_id), qid, answer.lower(), 0, 0)
            )
        except sqlite3.IntegrityError:
            return None, "این سؤال را قبلاً جواب داده‌ای."

        correct = answer.lower() == q["correct"]
        added = q["score"] if correct else 0
        c.execute(
            """UPDATE answers
               SET is_correct=?, score_added=?
               WHERE user_id=? AND question_id=?""",
            (1 if correct else 0, added, str(user_id), qid)
        )
        c.execute(
            """UPDATE students SET
               score=score+?, correct=correct+?, wrong=wrong+?, total=total+1
               WHERE user_id=?""",
            (added, 1 if correct else 0, 0 if correct else 1, str(user_id))
        )
        return q, {"correct": correct, "added": added}

def warn(user_id):
    with db() as c:
        c.execute(
            "UPDATE students SET warnings=warnings+1 WHERE user_id=?",
            (str(user_id),)
        )
        row = c.execute(
            "SELECT warnings FROM students WHERE user_id=?", (str(user_id),)
        ).fetchone()
        return row["warnings"] if row else 0

def unwarn(user_id):
    with db() as c:
        c.execute(
            "UPDATE students SET warnings=MAX(warnings-1,0) WHERE user_id=?",
            (str(user_id),)
        )

def log(admin_id, action, target_id="", details=""):
    with db() as c:
        c.execute(
            "INSERT INTO logs(admin_id,action,target_id,details) VALUES(?,?,?,?)",
            (str(admin_id), action, str(target_id), details)
        )
