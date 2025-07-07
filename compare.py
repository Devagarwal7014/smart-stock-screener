import streamlit as st
import yfinance as yf
import pandas as pd

@st.cache_data
def load_stock_symbols():
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    df = pd.read_csv(url)
    return sorted(df["SYMBOL"].dropna().tolist())

def compare_stocks():
    st.markdown("---")
    st.header("🔍 Compare Two Stocks")

    symbols = load_stock_symbols()

    col1, col2 = st.columns(2)
    with col1:
        s1 = st.selectbox("Stock 1 Symbol", options=symbols, key="stock1")
    with col2:
        s2 = st.selectbox("Stock 2 Symbol", options=symbols, key="stock2")

    if s1 and s2:
        try:
            stock1 = yf.Ticker(s1 + ".NS") if not s1.endswith(".NS") else yf.Ticker(s1)
            stock2 = yf.Ticker(s2 + ".NS") if not s2.endswith(".NS") else yf.Ticker(s2)
            info1 = stock1.info
            info2 = stock2.info

            col1, col2 = st.columns(2)
            with col1:
                st.subheader(info1.get("longName", s1.upper()))
                st.write(f"📍 Price: ₹ {info1.get('currentPrice', 'N/A')}")
                st.write(f"💹 PE: {info1.get('trailingPE', 'N/A')}")
                st.write(f"📈 ROE: {info1.get('returnOnEquity', 'N/A')}")
                st.write(f"💰 Revenue: ₹ {info1.get('totalRevenue', 'N/A'):,}")
            with col2:
                st.subheader(info2.get("longName", s2.upper()))
                st.write(f"📍 Price: ₹ {info2.get('currentPrice', 'N/A')}")
                st.write(f"💹 PE: {info2.get('trailingPE', 'N/A')}")
                st.write(f"📈 ROE: {info2.get('returnOnEquity', 'N/A')}")
                st.write(f"💰 Revenue: ₹ {info2.get('totalRevenue', 'N/A'):,}")
        except Exception as e:
            st.error(f"Comparison error: {e}")
