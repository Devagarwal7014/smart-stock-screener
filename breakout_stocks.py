import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List

# --- 1. Batch Data Fetcher ---
@st.cache_data(show_spinner="Downloading batch stock data…")
def fetch_batch_data(symbols: List[str], period: str = "6mo", interval: str = "1d") -> Dict[str, pd.DataFrame]:
    """Fetch OHLCV for multiple symbols in a single batch with yfinance."""
    uploads = [s if s.endswith((".NS", ".BO")) else s + ".NS" for s in symbols]
    df = yf.download(
        uploads, period=period, interval=interval, group_by="ticker",
        threads=True, progress=False
    )
    # Handles both multi-index (many tickers) and single-ticker download
    if isinstance(df.columns, pd.MultiIndex):
        return {sym: df[sym].copy() for sym in uploads if sym in df}
    elif uploads and not df.empty:
        return {uploads[0]: df.copy()}
    return {}

# --- 2. Main Breakout Finder Page ---
def breakout_stocks_page():
    st.subheader("📈 Breakout Stocks (1D Candle Analysis)")
    st.markdown("""
    Identify stocks whose **latest close** is within **1–3%** of their **20-day high**.<br>
    See how often a true breakout occurred in the next 1–5 days.
    """, unsafe_allow_html=True)

    # --- 1) Load symbols & UI controls ---
    try:
        all_syms = pd.read_csv("data/full_nse_predictions.csv")["SYMBOL"].tolist()
    except Exception as e:
        st.error(f"Could not load symbols: {e}")
        return

    limit = st.slider("Symbols to scan", 50, len(all_syms), 200, 50)
    symbols = all_syms[:limit]

    # --- 2) Fetch all data in one batch ---
    with st.spinner(f"Downloading data for {len(symbols)} symbols…"):
        hist_data = fetch_batch_data(symbols)

    # --- 3) Scan for breakout candidates ---
    candidates = []
    for sym in symbols:
        df = hist_data.get(sym + ".NS")
        if df is None:
            df = hist_data.get(sym)
        if df is None or len(df) < 30:
            continue
        df = df.copy()
        df["High20"] = df["High"].rolling(20).max()
        last = df.iloc[-1]
        if pd.isna(last["High20"]):
            continue
        close, high20 = last["Close"], last["High20"]
        gap = (high20 - close) / high20 * 100

        # Near breakout (within 3% of high)
        if 0.97 * high20 <= close <= high20:
            success = total = 0
            for i in range(20, len(df) - 5):
                h20 = df["High20"].iloc[i]
                future = df["High"].iloc[i+1:i+6].max()
                if pd.notna(h20):
                    total += 1
                    if future > h20:
                        success += 1
            rate = round(success/total*100, 2) if total > 0 else None

            candidates.append({
                "Symbol": sym,
                "Last Close": f"{close:,.2f}",
                "20D High": f"{high20:,.2f}",
                "Gap (%)": round(gap, 2),
                "Success Rate (%)": rate
            })

    # --- 4) Results Table and Download ---
    if not candidates:
        st.warning("❌ No breakout candidates found.")
        return

    df_out = pd.DataFrame(candidates).sort_values("Gap (%)").reset_index(drop=True)
    st.success(f"✅ Found {len(df_out)} candidates. Showing top 50.")
    st.dataframe(df_out.head(50), use_container_width=True)

    csv = df_out.to_csv(index=False).encode()
    st.download_button("📥 Download All", csv, "breakouts.csv", "text/csv")

    # --- 5) Charts for All Breakout Candidates ---
    st.markdown("## 📊 Breakout Charts (Last 90 Days)")

    for idx, row in df_out.head(50).iterrows():
        symbol = row["Symbol"]
        with st.expander(f"{symbol} — Last 90 Days Candles", expanded=False):
            chart_df = hist_data.get(symbol + ".NS")
            if chart_df is None:
                chart_df = hist_data.get(symbol)
            if chart_df is not None and not chart_df.empty:
                last90 = chart_df.tail(90)
                fig = go.Figure(data=[go.Candlestick(
                    x=last90.index,
                    open=last90["Open"],
                    high=last90["High"],
                    low=last90["Low"],
                    close=last90["Close"]
                )])
                fig.update_layout(
                    title=f"{symbol} — 90d 1d Candles",
                    margin=dict(t=30, b=10, l=10, r=10),
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No price data available.")

