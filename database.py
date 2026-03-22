import sqlite3

def get_connection():
    return sqlite3.connect('users.db', check_same_thread=False)

def create_table():
    conn = get_connection()
    c = conn.cursor()

    # Users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT,
        password BLOB
    )
    ''')

    # Responses table
    c.execute('''
    CREATE TABLE IF NOT EXISTS responses (
        username TEXT,
        question TEXT,
        model_answer TEXT,
        student_answer TEXT,
        keywords TEXT,
        score REAL
    )
    ''')

    conn.commit()
    conn.close()