import bcrypt
from database import get_connection

# -------- ADD USER (HASH PASSWORD) --------
def add_user(username, password):
    conn = get_connection()
    c = conn.cursor()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    c.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)", 
        (username, hashed)
    )

    conn.commit()
    conn.close()


# -------- LOGIN USER (VERIFY PASSWORD) --------
def login_user(username, password):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()

    conn.close()

    if result:
        stored_password = result[0]

        try:
            if isinstance(stored_password, str):
                stored_password = stored_password.encode()

            return bcrypt.checkpw(password.encode(), stored_password)

        except ValueError:
            # 🔥 Handles invalid salt error safely
            return False