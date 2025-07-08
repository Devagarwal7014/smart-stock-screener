import streamlit as st
import yfinance as yf
from datetime import datetime

# --- Import your real dashboard modules here ---
from auth import login_signup, logout
from screener import stock_screener
from compare import compare_stocks
from ai_suggestions import ai_suggestion_page
from short_term_screener import short_term_page
from breakout_stocks import breakout_stocks_page
from news_section import news_section
from portfolio import portfolio_tracker
from user_profile import user_profile
from sentiment_news import sentiment_news_page
from social_media import social_media_tab

# --- PAGE CONFIG & STATE ---
st.set_page_config(page_title="Smart Stock Screener", page_icon="📊", layout="wide")
if "show_login" not in st.session_state:
    st.session_state.show_login = False

def get_live_indian_indices_ticker():
    indices = {
        "^NSEI": "NIFTY 50",
        "^NSEBANK": "BANKNIFTY",
        "^BSESN": "SENSEX"
    }
    ticker_items = []
    now = datetime.now().strftime("%b %d, %Y, %I:%M %p")
    ticker_items.append(f"<span style='color:#39FF14; font-weight:700;'>🕒 {now}</span>")

    for symbol, name in indices.items():
        try:
            data = yf.Ticker(symbol).history(period="5d")
            if data.shape[0] < 2:
                continue
            prev_close = data['Close'].iloc[-2]
            last_close = data['Close'].iloc[-1]
            change = last_close - prev_close
            pct_change = (change / prev_close) * 100 if prev_close != 0 else 0
            change_str = f"{change:+.2f}"
            pct_change_str = f"{pct_change:+.2f}%"

            if change > 0:
                color_class = "ticker-green"
            elif change < 0:
                color_class = "ticker-red"
            else:
                color_class = "ticker-neutral"

            ticker_html = (
                f"<span><b>{name}</b> "
                f"<span class='{color_class}'>"
                f"{last_close:.2f} ({change_str}, {pct_change_str})"
                f"</span></span>"
            )

            ticker_items.append(ticker_html)
        except Exception:
            continue

    return " &nbsp;&nbsp;&nbsp; ".join(ticker_items)

st.markdown("""
<style>
.ticker-bar {
  position: fixed;
  top: 65px;  /* Just below your navbar height */
  left: 0;
  width: 100vw;
  background: #131e22;
  height: 45px;
  overflow: hidden;
  white-space: nowrap;
  border-bottom: 1px solid #1f282e;
  box-sizing: border-box;
  z-index: 1050;
}

.ticker-content {
  display: inline-block;
  padding-left: 100%;
  animation: ticker-scroll 20s linear infinite;
  white-space: nowrap;
  font-size: 1.12em;
  color: #fff;
}

.ticker-content span {
  padding: 0 2rem;
}

@keyframes ticker-scroll {
  0% {
    transform: translateX(0%);
  }
  100% {
    transform: translateX(-100%);
  }
}


</style>
""", unsafe_allow_html=True)


# --- CSS STYLE (navbar, landing, dashboard, etc) ---
st.markdown("""
<style>
body, .stApp { background: #101820 !important; }
.block-container { background: transparent !important; padding-top: 15px !important; }
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-thumb { background: #202833; border-radius: 8px; }

.top-navbar {
  width: 100vw;
  position: fixed;
  top: 0; left: 0;
  z-index: 1000;
  background: #090f13;
  height: 62px;
  display: flex;
  align-items: center;
  border-bottom: 1.5px solid #202933;
  box-shadow: 0 2px 24px #0007;
}
.top-navbar-inner {
  width: 97vw;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.nav-logo {
  font-weight: 900;
  font-size: 2.1rem;
  color: #39FF14;
  margin-right: 40px;
  letter-spacing: 1.5px;
  font-family: 'Montserrat', Arial, sans-serif;
}
.nav-links {
  display: flex;
  gap: 34px;
  font-size: 1.12em;
  font-weight: 600;
}
.nav-link {
  color: #fff;
  text-decoration: none;
  padding: 4px 12px;
  border-radius: 4px;
  transition: background 0.13s;
}
.nav-link:hover, .nav-link.active {
  background: #141e16;
  color: #39FF14;
}
.nav-auth {
  display: flex;
  gap: 12px;
}
.nav-btn, .nav-btn-outline {
  border-radius: 5px;
  padding: 8px 22px;
  font-weight: 700;
  font-size: 1.08em;
  transition: 0.14s;
  border: 2px solid #39FF14;
  margin-left: 8px;
}
.nav-btn {
  background: #39FF14;
  color: #090f13;
}
.nav-btn:hover {
  background: #26ad10;
  color: #fff;
}
.nav-btn-outline {
  background: transparent;
  color: #39FF14;
}
.nav-btn-outline:hover {
  background: #212f26;
  border-color: #39FF14;
  color: #fff;
}

.ticker-bar {
  width: 100vw;
  background: #131e22;
  padding: 0.66em 1.1em;
  margin-top: -16px;
  margin-bottom: 1.7em;
  display: flex;
  gap: 1.2em;
  overflow-x: auto;
  font-size: 1.12em;
  border-bottom: 1px solid #1f282e;
}
.ticker-red {
  color: #ff4444;
  font-weight: 600;
}
.ticker-green {
  color: #39FF14;
  font-weight: 600;
}
.ticker-neutral {
  color: #ccc;
  font-weight: 600;
}

.hero {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  margin-top: 2.5em;
}
.hero-left {
  flex: 2;
  min-width: 320px;
}
.hero-right {
  flex: 1.2;
  min-width: 300px;
}
.headline {
  font-size: 2.6rem;
  font-weight: 800;
  color: #fff;
  line-height: 1.08;
  margin-bottom: 0.35em;
}
.headline span {
  color: #39FF14;
}
.desc {
  color: #aaa;
  font-size: 1.19rem;
  margin: 1.3em 0 2em 0;
  max-width: 600px;
}
.cta-btn {
  background: #39FF14;
  color: #111;
  padding: 0.78em 2.1em;
  font-weight: 700;
  border: none;
  border-radius: 6px;
  font-size: 1.18em;
  margin-top: 1.2em;
  transition: 0.13s;
  box-shadow: 0 2px 10px #39ff1440;
  cursor: pointer;
}
.cta-btn:hover {
  background: #1fb100;
  color: #fff;
}

.metrics-card {
  background: #131b23;
  border-radius: 14px;
  padding: 2em 2.2em 2em 2.2em;
  margin-top: 1em;
  box-shadow: 0 2px 20px #008C50AA;
  color: #fff;
  min-width: 340px;
}
.metrics-title {
  color: #39FF14;
  font-size: 1.27em;
  font-weight: 700;
  margin-bottom: 1.1em;
}
.metrics-row {
  margin-bottom: 0.92em;
  font-weight: 600;
  font-size: 1.09em;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.metrics-bar {
  height: 8px;
  border-radius: 5px;
  background: #202833;
  overflow: hidden;
  margin-top: 3px;
}
.bar-inner {
  height: 100%;
  border-radius: 5px;
  background: #39FF14;
}

.section-title {
  font-size: 2.2em;
  font-weight: 800;
  color: #39FF14;
  margin-top: 2.8em;
  margin-bottom: 0.35em;
}
.section-sub {
  color: #b7e9c7;
  font-size: 1.2em;
  margin-bottom: 2em;
}
.pros-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1.7em;
  margin-bottom: 2em;
}
.pros-card {
  flex: 1;
  background: #151d27;
  border-radius: 15px;
  padding: 1.45em 1.4em 1.2em 1.4em;
  min-width: 240px;
  color: #b7e9c7;
  border: 1.2px solid #223;
}
.pros-card h4 {
  color: #39FF14;
  font-size: 1.19em;
  font-weight: 700;
  margin-bottom: 0.18em;
}
.pros-card .icon {
  font-size: 1.38em;
  vertical-align: middle;
}
.creator-row {
  display: flex;
  flex-wrap: wrap;
  gap: 2em;
  margin-top: 2.5em;
}
.creator-card, .help-card {
  background: #141b27;
  border-radius: 18px;
  padding: 2em;
  flex: 1;
  min-width: 270px;
  color: #e7fcef;
  border: 1.2px solid #1d2231;
}
.creator-title {
  color: #3ec3ff;
  font-size: 1.35em;
  font-weight: 700;
  margin-bottom: 1.1em;
}
.creator-info {
  margin-bottom: 0.7em;
}
.creator-info .icon {
  font-size: 1.12em;
  margin-right: 0.55em;
}
.help-card {
  color: #7bffd6;
}
.help-title {
  color: #39FF14;
  font-size: 1.18em;
  font-weight: 700;
  margin-bottom: 0.95em;
}
.help-btn, .telegram-btn {
  display:block;
  background: #222;
  border: none;
  border-radius: 8px;
  font-size: 1.14em;
  color: #39FF14;
  margin: 1.2em 0 0 0;
  padding: 0.73em 0;
  font-weight: 700;
  cursor: pointer;
}
.help-btn:hover, .telegram-btn:hover {
  background: #182b1f;
}
.telegram-btn {
  background: #294c6c;
  color: #aaf;
  margin-bottom: 0;
}
.howworks-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1.6em;
  margin-bottom: 2em;
}
.howworks-card {
  flex: 1;
  background: #181e27;
  border-radius: 16px;
  padding: 1.25em 1.15em 1em 1.15em;
  min-width: 240px;
  color: #b7e9c7;
  border: 1.2px solid #1c2731;
}
.howworks-card h5 {
  color: #fff;
  font-size: 1.14em;
  font-weight: 700;
  margin-bottom: 0.22em;
}
.testimonials-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1.7em;
  margin-bottom: 2em;
}
.testimonial-card {
  flex: 1;
  background: #181e27;
  border-radius: 15px;
  padding: 1.2em 1.1em 1.2em 1.1em;
  min-width: 260px;
  color: #eee;
  border: 1.2px solid #1c2731;
}
.testimonial-card .name {
  color: #b7e9c7;
  font-weight: 700;
}
.finalcta {
  background: linear-gradient(90deg, #092c17 65%, #101820 100%);
  border-radius: 19px;
  margin-top: 2em;
  padding: 2.5em 2em 2.5em 2.5em;
  text-align: center;
  color: #fff;
}
.finalcta .bigtext {
  font-size: 2.15em;
  font-weight: 800;
  margin-bottom: 0.5em;
}
.finalcta .cta-btn {
  font-size: 1.14em;
}
.footer {
  background: #151d27;
  padding: 2.2em 0 1.3em 0;
  margin-top: 2em;
  color: #88a2b6;
}
.footer-inner {
  display: flex;
  flex-wrap: wrap;
  gap: 2.6em;
  justify-content: space-between;
  margin-bottom: 1.3em;
}
.footer-col h4 {
  color: #39FF14;
  font-size: 1.1em;
  font-weight: 800;
  margin-bottom: 0.55em;
}
.footer a {
  color: #3ec3ff;
  text-decoration: none;
}
.dashboard-menu-box {
  margin: 2em 0 2em 0;
  background: #131b23;
  border-radius: 16px;
  padding: 1.3em 2.2em;
}

/* MOBILE RESPONSIVE STYLES */
@media (max-width: 900px) {
  .hero, .pros-row, .creator-row, .howworks-row, .testimonials-row, .footer-inner {
    flex-direction: column;
  }
  .hero-left, .hero-right, .pros-card, .creator-card, .help-card, .howworks-card, .testimonial-card {
    min-width: unset !important;
  }
}

@media (max-width: 600px) {
  .top-navbar-inner {
    flex-direction: column !important;
    align-items: flex-start !important;
    gap: 12px !important;
  }
  .nav-links {
    flex-direction: column !important;
    width: 100% !important;
  }
  .nav-link {
    padding: 12px 10px !important;
    font-size: 1.2em !important;
    width: 100% !important;
  }
  .nav-auth {
    justify-content: center !important;
    width: 100% !important;
  }
  .headline {
    font-size: 1.8rem !important;
  }
  .desc {
    font-size: 1rem !important;
  }
  .cta-btn {
    width: 100% !important;
    padding: 1em !important;
  }
  .ticker-bar {
    font-size: 1em !important;
    padding: 0.5em 0.8em !important;
  }
  .hero-left, .hero-right {
    flex: 1 1 100% !important;
  }
}
</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
.overlay-bg {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(10,20,30,0.77); z-index:1001;
}
.modal-center {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 1002;
}
.login-modal {
    background: #232c36; border-radius: 18px; box-shadow: 0 8px 32px #000c;
    padding: 2.3em 2.1em 1.8em 2.1em; text-align: center; min-width: 340px; max-width: 94vw;
}
</style>
""", unsafe_allow_html=True)


# --- NAVBAR ---
st.markdown("""
<div class="top-navbar">
  <div class="top-navbar-inner">
    <div class="nav-logo">Smart Stock Screener</div>
    <div class="nav-links">
      <a class="nav-link active" href="#">Home</a>
      <a class="nav-link" href="#dashboard">Dashboard</a>
    </div>
    <div class="nav-auth">
      <!-- STREAMLIT BUTTONS WILL GO BELOW -->
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Only ONE set of Streamlit buttons just below navbar!
login_col, signup_col = st.columns([1, 1])
with login_col:
    if st.button("Login", key="navbar_login"):
        st.session_state.show_login = True
with signup_col:
    if st.button("Sign Up", key="navbar_signup"):
        st.session_state.show_login = True


# --- LANDING PAGE FUNCTION ---
def landing_page():
    ticker_html = get_live_indian_indices_ticker()
    # Duplicate ticker_html twice for smooth scrolling
    full_ticker_html = f"""
    <div class="ticker-content">
        {ticker_html}
    </div>
    <div class="ticker-content">
        {ticker_html}
    </div>
    """
    st.markdown(
        f"""
        <div class="ticker-bar">
            {full_ticker_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
    # ...rest of your landing page code...

    st.markdown(
        """
    <div class="hero">
      <div class="hero-left">
        <div class="headline">Smart <span>Trading Algorithms</span><br>for Smarter Investors</div>
        <div class="desc">
            The Smart Stock Screener provides advanced algorithmic trading strategies with real-time market analysis and actionable insights.<br>
            Our AI-powered platform helps you make data-driven investment decisions.
        </div>
        <button class="cta-btn">Get Started</button>
      </div>
      <div class="hero-right">
        <div class="metrics-card">
          <div class="metrics-title">Performance Metrics</div>
          <div class="metrics-row">Success Rate <span>87.5%</span></div>
          <div class="metrics-bar"><div class="bar-inner" style="width: 87.5%"></div></div>
          <div class="metrics-row">Avg. Monthly Return <span>12.3%</span></div>
          <div class="metrics-bar"><div class="bar-inner" style="width: 67%"></div></div>
          <div class="metrics-row">Risk Management Score <span>9.2/10</span></div>
          <div class="metrics-bar"><div class="bar-inner" style="width: 92%"></div></div>
          <div style="margin-top:1.6em;font-size:0.97em;color:#bbb;">
            Last updated: July 8, 2025 <span style="color:#39FF14;">Live</span>
          </div>
        </div>
      </div>
    </div>
    <div class="section-title">Trading Algorithm System</div>
    <div class="section-sub">Automated, Precise, and Emotion-Free Trading</div>
    <div style="color:#39FF14; font-size: 1.45em; font-weight: 700; margin-bottom: 1.1em;">Pros Of Being Part Of It</div>
    <div class="pros-row">
      <div class="pros-card">
        <span class="icon">✔️</span>
        <h4>Automated Trading</h4>
        <div>You know the system but sometimes you get busy so you can't find the trades. The algo will do it for you.</div>
      </div>
      <div class="pros-card">
        <span class="icon">✔️</span>
        <h4>Error-Free Execution</h4>
        <div>If something is taught to a human then human can make mistakes, but if something is taught to a robot then it can't make mistakes.</div>
      </div>
      <div class="pros-card">
        <span class="icon">✔️</span>
        <h4>Emotion-Free Trading</h4>
        <div>A human can have emotions and other works. The robot has no emotions and only 1 work – analyzing the market for you.</div>
      </div>
    </div>
    <div class="creator-row">
      <div class="creator-card">
        <div class="creator-title">Creator Information</div>
        <div class="creator-info"><span class="icon">👤</span> <b>Name:</b> Dev Agarwal</div>
        <div class="creator-info"><span class="icon">🎓</span> <b>Background:</b> BTech Student, IT</div>
        <div class="creator-info"><span class="icon">🎂</span> <b>Age:</b> 20 years</div>
        <div class="creator-info"><span class="icon">📍</span> <b>Location:</b> Jaipur, Rajasthan</div>
      </div>
      <div class="help-card">
        <div class="help-title">Help Centre</div>
        <div>Need assistance? Contact us on WhatsApp or Telegram</div>
        <div style="margin:1.2em 0 0.2em 0;"><b>WhatsApp Number</b></div>
        <div style="font-size:1.2em; color:#39FF14;"><b>+91 7014692756</b></div>
        <button class="telegram-btn">Telegram Support</button>
        <button class="help-btn">Contact on WhatsApp</button>
      </div>
    </div>
    <div class="section-title" style="color:#fff;">How Smart Stock Screener Works</div>
    <div class="section-sub">Our proprietary algorithm analyzes market data, identifies patterns, and provides actionable trading insights.</div>
    <div class="howworks-row">
      <div class="howworks-card">
        <h5>AI-Powered Analysis</h5>
        <div>Advanced machine learning algorithms analyze thousands of market variables in real-time.</div>
      </div>
      <div class="howworks-card">
        <h5>Pattern Recognition</h5>
        <div>Identify high-probability trading setups based on historical pattern analysis and market behavior.</div>
      </div>
      <div class="howworks-card">
        <h5>Risk Management</h5>
        <div>Precise entry and exit points with stop-loss recommendations to protect your capital.</div>
      </div>
    </div>
    <div class="section-title" style="color:#fff;">What Our Subscribers Say</div>
    <div class="section-sub">Join thousands of satisfied traders who have transformed their trading with Smart Stock Screener.</div>
    <div class="testimonials-row">
      <div class="testimonial-card">
        <div style="font-size:1.08em; margin-bottom:0.65em;">"The entry and exit points are incredibly precise. I've seen a 32% increase in my portfolio since subscribing!"</div>
        <div class="name">Rajesh Kumar</div>
        <div style="color:#99a;">Swing Trader, 8 months</div>
      </div>
      <div class="testimonial-card">
        <div style="font-size:1.08em; margin-bottom:0.65em;">"The risk management aspect is what sets it apart. I know exactly where to place my stop losses and take profits."</div>
        <div class="name">Anita Patel</div>
        <div style="color:#99a;">Forex Trader, 1 year</div>
      </div>
      <div class="testimonial-card">
        <div style="font-size:1.08em; margin-bottom:0.65em;">"As a beginner, I was skeptical at first, but every trade recommendation has been educational and profitable."</div>
        <div class="name">Vikram Singh</div>
        <div style="color:#99a;">New Investor, 4 months</div>
      </div>
    </div>
    <div class="finalcta">
      <div class="bigtext">Ready to Transform Your Trading?</div>
      <div>Join the Smart Stock Screener community today and gain access to professional-grade trading signals backed by advanced algorithms.</div>
      <button class="cta-btn" style="margin-top:1.8em;">Get Started Now</button>
    </div>
    <div class="footer">
      <div class="footer-inner">
        <div class="footer-col">
          <h4>The Smart Stock Screener</h4>
          <div>Advanced trading algorithms for modern investors.</div>
        </div>
        <div class="footer-col">
          <h4>Services</h4>
          <div>Swing Trading<br>Trading Education<br>Market Analysis<br>Risk Management</div>
        </div>
        <div class="footer-col">
          <h4>Contact Us</h4>
          <div>info@smartstockscreener.com<br>+91 7014682756<br>Jaipur, India</div>
        </div>
      </div>
      <div style="font-size:0.98em; text-align:center; color:#3ec3ff;">
        © 2025 Smart Stock Screener. All rights reserved. Trading involves risk. Past performance is not indicative of future results.<br>
        <a href="#">Privacy Policy</a> | <a href="#">Terms of Service</a> | <a href="#">Disclaimer</a>
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


# --- LOGIN FORM MODAL ---
def show_login():
    # Simulate a modal by adding vertical space and centering the box
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown(
            """
            <div style='
                margin-left:auto;margin-right:auto;
                background:#232c36;
                border-radius:16px;
                box-shadow:0 8px 32px #000b;
                padding:2.3em 2.2em 2em 2.2em;
                color:#fff;
                min-width:350px; max-width:94vw;
                text-align:center;'>
                <span style='font-size:1.65em;font-weight:900;color:#39FF14;'>Login to Dashboard</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")  # A little space
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        col1, col2 = st.columns(2)
        login_btn = col1.button("Login")
        cancel_btn = col2.button("Cancel")
        if login_btn:
            if email and pwd:
                st.session_state.user = {"email": email, "name": email.split("@")[0]}
                st.session_state.show_login = False
                st.success("✅ Logged in! Redirecting to dashboard...")
                st.rerun()
            else:
                st.error("Please enter both email and password.")
        if cancel_btn:
            st.session_state.show_login = False
            st.rerun()


# --- MAIN ROUTING ---
if "user" in st.session_state:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="dashboard-menu-box">', unsafe_allow_html=True)
    selected_menu = st.selectbox(
        "📌 Dashboard Menu",
        [
            "User Profile",
            "Stock Screener",
            "AI Suggestions",
            "Compare Stocks",
            "Portfolio Tracker",
            "Short Term Screener",
            "Breakout Stocks",
            "News",
            "Sentiment & Trends",
            "Logout",
        ],
        key="dashboard_menu",
    )
    st.markdown("</div>", unsafe_allow_html=True)
    if selected_menu == "User Profile":
        user_profile()
    elif selected_menu == "Stock Screener":
        stock_screener()
    elif selected_menu == "AI Suggestions":
        ai_suggestion_page()
    elif selected_menu == "Compare Stocks":
        compare_stocks()
    elif selected_menu == "Portfolio Tracker":
        portfolio_tracker()
    elif selected_menu == "Short Term Screener":
        short_term_page()
    elif selected_menu == "Breakout Stocks":
        breakout_stocks_page()
    elif selected_menu == "News":
        news_section()
    elif selected_menu == "Sentiment & Trends":
        sentiment_news_page()
    elif selected_menu == "Logout":
        del st.session_state.user
        st.success("You have been logged out.")
        st.experimental_rerun()
else:
    landing_page()
    if st.session_state.show_login:
        st.markdown("---")
        show_login()
