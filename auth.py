import streamlit as st
from firebase_config import auth

def login_signup():
    st.sidebar.title("🔐 Login / Sign Up")
    choice = st.sidebar.selectbox("Choose", ["Login", "Sign Up"])
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if choice == "Sign Up":
        if st.sidebar.button("Create Account"):
            try:
                auth.create_user_with_email_and_password(email, password)
                st.sidebar.success("Account created. Now you can log in.")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

    if choice == "Login":
        if st.sidebar.button("Login"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.user = user
                st.sidebar.success("Logged in successfully!")
            except Exception as e:
                st.sidebar.error(f"Login failed: {e}")

def logout():
    if "user" in st.session_state:
        del st.session_state.user
        st.success("Logged out successfully.")