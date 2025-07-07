import streamlit as st
import yfinance as yf
import pandas as pd

# Example list of small-cap NSE symbols — you can expand this list
SMALL_CAP_SYMBOLS = ["BEML.NS", "IRFC.NS", "IDEA.NS", "RCOM.NS", "HFCL.NS", "SJVN.NS", "EIL.NS"]

def get_small_cap_stocks():
    results = []
    for symbol in SMALL_CAP_SYMBOLS:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            market_cap = info.get("marketCap", 0)

            # Filter market cap between ₹4,000 Cr and ₹25,000 Cr (in rupees)
            if market_cap and 4000 * 10**7 <= market_cap <= 25000 * 10**7:
                results.append({
                    "Symbol": symbol,
                    "Name": info.get("longName", symbol),
                    "Market Cap (₹ Cr)": round(market_cap / 10**7, 2),
                    "Current Price": info.get("currentPrice", "N/A"),
                    "PE Ratio": info.get("trailingPE", "N/A"),
                    "ROE": info.get("returnOnEquity", "N/A"),
                })
        except Exception as e:
            st.error(f"Error fetching {symbol}: {e}")
    return pd.DataFrame(results)

def short_term_page():
    st.subheader("⚡ Short-Term Screener — Small Cap Picks")
    st.markdown("Showing small-cap companies with Market Cap ₹4,000 Cr – ₹25,000 Cr")

    if st.button("🔍 Find Small Cap Opportunities", key="find_small_caps"):
        df = get_small_cap_stocks()
        if df.empty:
            st.warning("No matching small-cap stocks found.")
        else:
            st.success(f"✅ {len(df)} stocks found.")
            st.dataframe(df)
