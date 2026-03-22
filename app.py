import streamlit as st
from auth import add_user, login_user
from database import create_table, get_connection
from model_utils import grade_answer
from data_store import save_response
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- SETUP ----------------
create_table()

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

st.set_page_config(page_title="AI Answer Grader", layout="centered")

st.markdown("<h1 style='text-align:center;'>🧠 AI Answer Grader</h1>", unsafe_allow_html=True)

# ---------------- LOGIN / SIGNUP ----------------
if not st.session_state.logged_in:

    menu = ["Login", "Sign Up"]
    choice = st.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("🔐 Login")

        username = st.text_input("👤 Name")
        password = st.text_input("🔑 Password", type='password')

        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.user = username

                # Admin check
                if username == "admin":
                    st.session_state.is_admin = True
                else:
                    st.session_state.is_admin = False

                st.rerun()
            else:
                st.error("❌ Invalid credentials")

    else:
        st.subheader("📝 Create Account")

        new_user = st.text_input("👤 Name")
        new_pass = st.text_input("🔑 Password", type='password')

        if st.button("Sign Up"):
            add_user(new_user, new_pass)
            st.success("✅ Account created! Go to Login.")

# ---------------- MAIN APP ----------------
else:

    st.success(f"Welcome, {st.session_state.user} 👋")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.is_admin = False
        st.rerun()

    # ---------------- USER PANEL ----------------
    if not st.session_state.is_admin:

        st.subheader("📘 Grade Answers")

        question = st.text_input("Question")
        model_answer = st.text_area("Model Answer")
        student_answer = st.text_area("Student Answer")
        keywords = st.text_input("Keywords")

        if st.button("Grade Answer"):

            if question and model_answer and student_answer:

                final, bert, rel, key, words, relevance = grade_answer(
                    question, model_answer, student_answer, keywords
                )

                st.subheader("📊 Result")
                st.progress(final / 10)
                st.write(f"### ⭐ Final Score: {final}/10")

                # Save to DB
                save_response(
                    st.session_state.user,
                    question,
                    model_answer,
                    student_answer,
                    keywords,
                    final
                )

                st.success("✅ Result saved successfully!")

            else:
                st.warning("⚠️ Fill all fields")

        # -------- HISTORY --------
        st.subheader("📜 Your Previous Results")

        conn = get_connection()
        c = conn.cursor()

        c.execute("""
        SELECT question, score FROM responses 
        WHERE username=? 
        ORDER BY rowid DESC
        """, (st.session_state.user,))

        rows = c.fetchall()

        if rows:
            for row in rows:
                st.write(f"📘 {row[0]} → ⭐ {row[1]}/10")
        else:
            st.info("No previous records found.")

        conn.close()

    # ---------------- ADMIN PANEL ----------------
    else:

        st.subheader("🧑‍💼 Admin Dashboard")

        conn = get_connection()
        df = pd.read_sql("SELECT * FROM responses", conn)

        if not df.empty:

            users = df["username"].unique()
            selected_user = st.selectbox("👤 Select User", users)

            user_df = df[df["username"] == selected_user]

            st.write(f"### 📊 Performance of {selected_user}")

            avg_score = user_df["score"].mean()
            total_attempts = len(user_df)

            col1, col2 = st.columns(2)

            with col1:
                st.metric("📊 Average Score", round(avg_score, 2))

            with col2:
                st.metric("📝 Total Attempts", total_attempts)

            # -------- TABLE --------
            st.write("### 📋 User Records")
            st.dataframe(user_df)

            # -------- GRAPH FIXED --------
            st.write("### 📈 Score Trend")

            if not user_df.empty and "score" in user_df.columns:

                scores = user_df["score"].dropna()

                if len(scores) > 0:
                    plt.figure()
                    plt.plot(scores.values, marker='o')
                    plt.xlabel("Attempt")
                    plt.ylabel("Score")
                    plt.title("Score Trend")

                    st.pyplot(plt)
                else:
                    st.warning("No valid scores to display.")

            else:
                st.warning("No data available for this user.")

        else:
            st.info("No data available.")

        conn.close()