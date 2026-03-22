from database import get_connection

def save_response(username, question, model_answer, student_answer, keywords, score):
    conn = get_connection()
    c = conn.cursor()

    c.execute('''
    INSERT INTO responses (username, question, model_answer, student_answer, keywords, score)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, question, model_answer, student_answer, keywords, score))

    conn.commit()
    conn.close()