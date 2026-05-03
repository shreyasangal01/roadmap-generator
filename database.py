import sqlite3

def get_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)
    cursor.execute("""
CREATE TABLE IF NOT EXISTS roadmaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    field TEXT,
    level TEXT,
    duration INTEGER,
    roadmap_text TEXT
)
""")
    
    # Progress tracking table
    cursor.execute("""
CREATE TABLE IF NOT EXISTS progress_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    roadmap_index INTEGER,
    completed_weeks TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")
    
    conn.commit()
    conn.close()

def save_roadmap(user_id, field, level, duration, roadmap_text):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO roadmaps (user_id, field, level, duration, roadmap_text)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, field, level, duration, roadmap_text))

    conn.commit()
    conn.close()


def get_user_roadmaps(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM roadmaps WHERE user_id=?", (user_id,))
    roadmaps = cursor.fetchall()

    conn.close()
    return roadmaps
