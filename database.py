import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    goal TEXT,
    streak INTEGER DEFAULT 0,
    last_active TEXT
)
""")

conn.commit()


def init_user(user_id):
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )
    conn.commit()


def get_user(user_id):
    cursor.execute(
        "SELECT goal, streak, last_active FROM users WHERE user_id=?",
        (user_id,)
    )

    row = cursor.fetchone()

    if row:
        return {
            "goal": row[0],
            "streak": row[1],
            "last_active": row[2]
        }

    return {
        "goal": None,
        "streak": 0,
        "last_active": None
    }


def set_goal(user_id, goal):
    cursor.execute(
        "UPDATE users SET goal=? WHERE user_id=?",
        (goal, user_id)
    )
    conn.commit()


def update_streak(user_id, streak):
    cursor.execute(
        "UPDATE users SET streak=? WHERE user_id=?",
        (streak, user_id)
    )
    conn.commit()


def set_last_active(user_id, last_active):
    cursor.execute(
        "UPDATE users SET last_active=? WHERE user_id=?",
        (last_active, user_id)
    )
    conn.commit()