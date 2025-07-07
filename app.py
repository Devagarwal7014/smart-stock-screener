import streamlit as st
from auth import login_signup, logout
from screener import stock_screener
from compare import compare_stocks
from ai_suggestions import ai_suggestion_page
from short_term_screener import short_term_page
from breakout_stocks import breakout_stocks_page
import logging
from news_section import news_section
from portfolio import portfolio_tracker
from user_profile import user_profile  # Import user profile if you have it
from sentiment_news import sentiment_news_page
from social_media import social_media_tab


# --- Logging for Debugging ---
logging.basicConfig(level=logging.INFO)

# --- Inject PWA manifest and register service worker ---
pwa_inject = """
<link rel="manifest" href="manifest.json" />
<script>
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('service-worker.js')
      .then(() => console.log('Service Worker Registered'))
      .catch(() => console.log('Service Worker Registration Failed'));
}
</script>
"""
st.markdown(pwa_inject, unsafe_allow_html=True)

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="Smart Stock Screener",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Dark Theme CSS ---
DARK_THEME_CSS = """
<style>
.block-container {
    background-color: #181818 !important;
    color: #fff !important;
    padding-top: 2rem;
}
h1, h2, h3, h4, h5, h6, p, span, div {
    color: #fff !important;
}
input, textarea, select {
    background-color: #333 !important;
    color: #eee !important;
    border: 1px solid #555 !important;
}
.stDataFrame, .css-1fbl5kx {
    background-color: #202020 !important;
    color: #eee !important;
}
.stButton>button {
    background-color: #1f77b4 !important;
    color: #fff !important;
    border-radius: 6px !important;
    font-weight: bold !important;
}
[data-testid="stSidebar"] {
    background-color: #121212 !important;
    color: #fff !important;
}
.css-1wa3eu0-placeholder, .css-1uccc91-singleValue {
    color: #ddd !important;
}
.css-1umjjup {
    color: #fff !important;
}
a {
    color: #3399ff !important;
}
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background-color: #444;
    border-radius: 4px;
}
</style>
"""
st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

# --- Sidebar Menu ---
st.sidebar.title("📊 Smart Stock Screener")

# Show welcome banner if user logged in
if "user" in st.session_state:
    username = st.session_state.user.get("name") or st.session_state.user.get("email") or "User"
    st.sidebar.markdown(
        f"""
        <div style="
            max-width: 100%;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 12px;
            background: linear-gradient(90deg, #1f77b4, #ff7f0e);
            color: white;
            text-align: center;
            font-weight: 600;
            font-size: 1.2rem;
            word-wrap: break-word;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            ">
            👋 Welcome, {username}!
        </div>
        """,
        unsafe_allow_html=True,
    )

MENU_OPTIONS = [
    "Login / Sign Up",
    "User Profile",
    "Stock Screener",
    "AI Suggestions",
    "Compare Stocks",
    "Portfolio Tracker",
    "Short Term Screener",
    "Breakout Stocks",
    "News",
    "Sentiment & Trends",
    "Logout"
]
selected_menu = st.sidebar.radio("📌 Menu", MENU_OPTIONS)

# --- User Session Management ---
def is_logged_in() -> bool:
    """Check if user is logged in (stored in Streamlit session state)."""
    return "user" in st.session_state

# --- Navigation Logic ---
def main():
    if selected_menu == "Login / Sign Up":
        login_signup()
    elif selected_menu == "User Profile":
        if is_logged_in():
            user_profile()
        else:
            st.warning("⚠️ Please login to view your profile.")
    elif selected_menu == "Stock Screener":
        if is_logged_in():
            stock_screener()
        else:
            st.warning("⚠️ Please login to access the screener.")
    elif selected_menu == "AI Suggestions":
        if is_logged_in():
            ai_suggestion_page()
        else:
            st.warning("⚠️ Please login to access AI suggestions.")
    elif selected_menu == "Compare Stocks":
        if is_logged_in():
            compare_stocks()
        else:
            st.warning("⚠️ Please login to compare stocks.")
    elif selected_menu == "Portfolio Tracker":
        if is_logged_in():
            portfolio_tracker()
        else:
            st.warning("⚠️ Please login to access your portfolio.")
    elif selected_menu == "Short Term Screener":
        if is_logged_in():
            short_term_page()
        else:
            st.warning("⚠️ Please login to access short-term screener.")
    elif selected_menu == "Breakout Stocks":
        if is_logged_in():
            breakout_stocks_page()
        else:
            st.warning("⚠️ Please login to view breakout stocks.")
    elif selected_menu == "News":
        if is_logged_in():
            news_section()
        else:
            st.warning("⚠️ Please login to access News.")
    elif selected_menu == "Sentiment & Trends":
        if is_logged_in():
            sentiment_news_page()
        else:
            st.warning("⚠️ Please login to access Sentiment & Trends.")

    elif selected_menu == "Logout":
        logout()
        st.success("You have been logged out.")

# --- Optional: Custom CSS from File ---
def apply_custom_css():
    try:
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        logging.info("Custom styles.css not found; skipping.")

apply_custom_css()

# --- Run the App ---
if __name__ == "__main__":
    main()
