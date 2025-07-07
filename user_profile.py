import streamlit as st
from firebase_config import db, auth  # Make sure your firebase_config.py exports auth instance too
import pandas as pd
import yfinance as yf
import datetime
import re

def is_valid_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def get_portfolio_summary(user_email):
    email_key = user_email.replace('.', '-')
    data = db.child("portfolios").child(email_key).get().val()
    if not data:
        return None
    if isinstance(data, dict):
        portfolio = list(data.values())
    elif isinstance(data, list):
        portfolio = data
    else:
        portfolio = []
    if not portfolio:
        return None

    symbols = [item['symbol'] for item in portfolio]
    yf_symbols = [sym + ".NS" for sym in symbols]

    prices = yf.download(yf_symbols, period="1d", progress=False)["Close"]
    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    total_invested = 0
    total_current_value = 0

    for item in portfolio:
        sym = item['symbol']
        shares = item['shares']
        buy_price = item['buy_price']
        invested = shares * buy_price

        yf_sym = sym + ".NS"
        current_price = None
        if not prices.empty:
            if isinstance(prices, pd.Series):
                if yf_symbols and yf_symbols[0] == yf_sym:
                    current_price = prices.iloc[-1]
            elif yf_sym in prices.columns:
                series = prices[yf_sym]
                if not series.empty:
                    current_price = series.iloc[-1]

        current_value = shares * current_price if current_price is not None else None

        total_invested += invested
        if current_value is not None:
            total_current_value += current_value

    return total_invested, total_current_value

def user_profile():
    if "user" not in st.session_state:
        st.warning("⚠️ Please login to view profile.")
        return

    user = st.session_state.user
    email = user.get("email", "")
    current_name = user.get("name", "")
    email_key = email.replace('.', '-')

    # Fetch user metadata from Firebase (if saved)
    user_meta = db.child("users").child(email_key).get().val() or {}

    st.title("👤 Your Profile")

    with st.form("update_profile"):
        st.write("### Account Information")
        st.text_input("Email (cannot be changed)", value=email, disabled=True)

        new_name = st.text_input("Display Name", value=current_name)
        submitted = st.form_submit_button("Update Profile")

        if submitted:
            if not new_name.strip():
                st.error("Display Name cannot be empty.")
            else:
                # Update name in Firebase & session state
                db.child("users").child(email_key).update({"name": new_name.strip()})
                st.session_state.user["name"] = new_name.strip()
                st.success("Profile updated successfully!")

    # Show signup date and last login if available
    signup_date = user_meta.get("signup_date")
    last_login = user_meta.get("last_login")

    if signup_date:
        try:
            dt = datetime.datetime.fromisoformat(signup_date)
            st.write(f"**Signup Date:** {dt.strftime('%B %d, %Y')}")
        except Exception:
            st.write(f"**Signup Date:** {signup_date}")

    if last_login:
        try:
            dt = datetime.datetime.fromisoformat(last_login)
            st.write(f"**Last Login:** {dt.strftime('%B %d, %Y, %H:%M:%S')}")
        except Exception:
            st.write(f"**Last Login:** {last_login}")

    # Password reset button
    if st.button("Send Password Reset Email"):
        try:
            auth.send_password_reset_email(email)
            st.success("Password reset email sent. Check your inbox.")
        except Exception as e:
            st.error(f"Error sending reset email: {e}")

    # Mini portfolio summary
    st.markdown("---")
    st.write("### Portfolio Summary")

    portfolio_summary = get_portfolio_summary(email)
    if portfolio_summary:
        invested, current_value = portfolio_summary
        profit_loss = current_value - invested
        profit_loss_pct = (profit_loss / invested * 100) if invested > 0 else 0
        st.write(f"**Total Invested:** ₹{invested:,.2f}")
        st.write(f"**Current Portfolio Value:** ₹{current_value:,.2f}")
        color = "green" if profit_loss >= 0 else "red"
        st.markdown(f"**Profit/Loss:** <span style='color:{color}'>{profit_loss:,.2f} ({profit_loss_pct:.2f}%)</span>", unsafe_allow_html=True)
        st.info("Click on 'Portfolio Tracker' in the menu for full details.")
    else:
        st.info("No portfolio data found.")

