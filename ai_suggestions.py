import streamlit as st
import pandas as pd
import yfinance as yf
import joblib
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from streamlit_lottie import st_lottie
import requests

# ========== TECHNICAL FEATURE EXTRACTION ==========
def get_technical_features(symbol):
    try:
        ticker = yf.Ticker(symbol + ".NS")
        hist = ticker.history(period="1y", interval="1d")
        if len(hist) < 200:
            return {}
        close = hist["Close"]
        # RSI (14)
        delta = close.diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        ma_up = up.rolling(14).mean()
        ma_down = down.rolling(14).mean()
        rsi = 100 - (100 / (1 + ma_up / ma_down))
        # 50-day and 200-day moving averages
        ma_50 = close.rolling(window=50).mean().iloc[-1]
        ma_200 = close.rolling(window=200).mean().iloc[-1]
        # Price Momentum (last 30d)
        momentum_30 = close.iloc[-1] - close.iloc[-31]
        # Volatility (annualized std dev)
        volatility = close.pct_change().std() * np.sqrt(252)
        return {
            "RSI": float(rsi.iloc[-1]),
            "50_MA": float(ma_50),
            "200_MA": float(ma_200),
            "Price_Momentum_30": float(momentum_30),
            "Volatility": float(volatility),
        }
    except Exception:
        return {}

# ========== LOTTIE ANIMATION SUPPORT ==========
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# ========== MODEL LOADING ==========
@st.cache_resource(show_spinner="Loading AI model…")
def load_model():
    return joblib.load("ai_model.joblib")
model = load_model()

features = [
    "roe", "opm", "pb", "de_ratio", "fcf", "eps_growth", "revenue_growth",
    "RSI", "50_MA", "200_MA", "Price_Momentum_30", "Volatility"
]

def explain_pick(row):
    reasons = []
    if row.get("roe", 0) >= 15:
        reasons.append("High ROE")
    if row.get("opm", 0) >= 15:
        reasons.append("Good OPM")
    if row.get("pb", 999) <= 3:
        reasons.append("Fair Valuation (P/B)")
    if row.get("de_ratio", 999) <= 1:
        reasons.append("Low Debt")
    if row.get("fcf", 0) > 0:
        reasons.append("Positive FCF")
    if row.get("eps_growth", 0) > 0:
        reasons.append("EPS Growth")
    if row.get("revenue_growth", 0) > 0:
        reasons.append("Revenue Growth")
    # Technical reasons (add more if you wish!)
    if row.get("RSI", 0) > 35 and row.get("RSI", 0) < 70:
        reasons.append("Healthy RSI")
    if row.get("Price_Momentum_30", 0) > 0:
        reasons.append("Positive Price Momentum")
    return ", ".join(reasons)

def fetch_features(sym: str):
    try:
        ticker = yf.Ticker(sym + ".NS")
        info = ticker.info
        def safe_percent(val):
            try: return round(float(val) * 100, 2)
            except: return 0.0
        # Fundamentals
        fundamentals = {
            "symbol": sym,
            "roe": safe_percent(info.get("returnOnEquity", 0)),
            "opm": safe_percent(info.get("operatingMargins", 0)),
            "pb": float(info.get("priceToBook", 0) or 0),
            "de_ratio": float(info.get("debtToEquity", 0) or 0),
            "fcf": float(info.get("freeCashflow", 0) or 0) / 1e7,
            "eps_growth": safe_percent(info.get("earningsQuarterlyGrowth", 0)),
            "revenue_growth": safe_percent(info.get("revenueGrowth", 0))
        }
        # Technicals
        technicals = get_technical_features(sym)
        fundamentals.update(technicals)
        return fundamentals
    except Exception:
        return {}

def ai_suggestion_page():
    if "user" not in st.session_state:
        st.warning("⚠️ Please login to use AI Suggestions.")
        return

    st.title("🧠 AI-Powered Stock Suggestions")

    # Lottie loader before run
    lottie_ai = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_sSF6EGwDXK.json")
    if lottie_ai:
        st_lottie(lottie_ai, speed=1, height=220, key="ai_loading")
    else:
        st.info("🤖 Analyzing all NSE stocks... (loading animation unavailable)")

    st.info("Analyzing all NSE stocks with AI and technicals. This may take 2–10 minutes...")

    if st.button("🚀 Run AI Suggestions"):
        with st.spinner("Running AI engine and fetching all stocks…"):
            # Optional: Transparency expander
            with st.expander("What happens in the background?"):
                st.markdown(
                    "- Downloads list of all NSE stocks\n"
                    "- Fetches real-time financials **and technicals** in parallel (multi-threaded)\n"
                    "- Applies your custom-trained AI model\n"
                    "- Filters and explains the best picks\n"
                    "- Lets you download the suggestions as CSV"
                )

            df_symbols = pd.read_csv("https://archives.nseindia.com/content/equities/EQUITY_L.csv")
            symbols = df_symbols["SYMBOL"].dropna().tolist()

            suggestions = []
            batch_size = 50

            with ThreadPoolExecutor(max_workers=10) as executor:
                results = []
                for i in range(0, len(symbols), batch_size):
                    batch = symbols[i:i+batch_size]
                    futures = [executor.submit(fetch_features, sym) for sym in batch]
                    batch_results = []
                    for future in futures:
                        data_point = future.result()
                        # Only include if all features present
                        if data_point and all(f in data_point for f in features):
                            batch_results.append(data_point)
                    results.extend(batch_results)

            # AI Filtering and explanations
            for data_point in results:
                try:
                    features_df = pd.DataFrame([data_point])[features]
                    prediction = model.predict(features_df)[0]
                    if prediction == 1:
                        data_point["explanation"] = explain_pick(data_point)
                        suggestions.append(data_point)
                except Exception:
                    continue

            if suggestions:
                result_df = pd.DataFrame(suggestions)
                st.success(f"✅ {len(result_df)} Strong Stocks Found")
                st.dataframe(result_df, use_container_width=True)
                csv = result_df.to_csv(index=False)
                st.download_button("📥 Download Suggestions CSV", csv, "ai_suggestions.csv", "text/csv")
            else:
                st.error("❌ No strong stocks found.")
    else:
        st.info("Click above to run AI filter.")

