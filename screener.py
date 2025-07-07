import streamlit as st
import yfinance as yf
import pandas as pd
import io
from firebase_config import db
from datetime import datetime, timedelta
from typing import Optional, List

# Inject dark mode CSS globally in this page
dark_css = """
<style>
/* Main content background */
.block-container {
    background-color: #181818 !important;
    color: #fff !important;
}

/* Headers and text */
h1, h2, h3, h4, h5, h6, p, span {
    color: #fff !important;
}

/* Input fields and selects */
input, textarea, select {
    background-color: #333 !important;
    color: #eee !important;
    border: 1px solid #555 !important;
}

/* Dataframe backgrounds */
.stDataFrame, .css-1fbl5kx {
    background-color: #202020 !important;
    color: #eee !important;
}

/* Button styling */
.stButton>button {
    background-color: #1f77b4 !important;
    color: #fff !important;
    border-radius: 6px !important;
    font-weight: bold !important;
}

/* Metric component */
.css-1umjjup {
    color: #fff !important;
}

/* Charts */
.vega-embed {
    background-color: #181818 !important;
}

/* Scrollbars for dataframe */
.css-1v3fvcr {
    background-color: #333 !important;
    color: #eee !important;
}
</style>
"""
st.markdown(dark_css, unsafe_allow_html=True)

# --- 1. Fast & Reliable Symbol Loader ---
@st.cache_data(show_spinner="Loading NSE symbols...")
def load_nse_symbols() -> List[str]:
    """Load all NSE symbols from the official CSV file."""
    try:
        url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        df = pd.read_csv(url)
        return sorted(df["SYMBOL"].dropna().tolist())
    except Exception as e:
        st.error(f"Failed to load NSE stock list: {e}")
        return []

# --- 2. Utility Functions with Type Hints & Docstrings ---
def estimate_growth_rate(symbol: str) -> float:
    """Estimate stock revenue CAGR from financials (fallback = 10%)."""
    try:
        stock = yf.Ticker(symbol)
        financials = stock.financials
        if 'Total Revenue' in financials.index:
            revenues = financials.loc['Total Revenue'].dropna()
            if len(revenues) >= 2:
                start, end = revenues[-1], revenues[0]
                years = len(revenues) - 1
                cagr = ((end / start) ** (1 / years) - 1) * 100
                return round(cagr, 1)
    except Exception:
        pass
    return 10.0

def get_fcf(symbol: str) -> Optional[float]:
    """Estimate Free Cash Flow (in ₹ Cr) from cashflow or op income."""
    try:
        stock = yf.Ticker(symbol)
        cashflow = stock.cashflow
        if "Total Cash From Operating Activities" in cashflow.index and "Capital Expenditures" in cashflow.index:
            op_cash = cashflow.loc["Total Cash From Operating Activities"].dropna().values[0]
            capex = cashflow.loc["Capital Expenditures"].dropna().values[0]
            return round((op_cash - capex) / 1e7, 2)
        financials = stock.financials
        if "Operating Income" in financials.index:
            op_income = financials.loc["Operating Income"].dropna().values[0]
            return round(op_income / 1e7, 2)
    except Exception:
        pass
    return None

# --- 3. Stock Screener Main Function ---
def stock_screener():
    if "user" not in st.session_state:
        st.warning("⚠️ Please login to use the screener.")
        return

    stock_list = load_nse_symbols()
    st.subheader("📌 Choose or Search for a Stock")

    col0, col1, col2, col3 = st.columns([2, 3, 2, 1])
    with col0:
        exchange = st.selectbox("Exchange", ["NSE", "BSE"])
    with col1:
        selected_stock = st.selectbox(
            "Select from NSE List", stock_list,
            index=stock_list.index("RELIANCE") if "RELIANCE" in stock_list else 0
        )
    with col2:
        manual_input = st.text_input("Or enter symbol manually (e.g. INFY, TCS)")
    with col3:
        search_clicked = st.button("🔍 Search", key="search_btn")

    if search_clicked:
        if manual_input:
            st.session_state.symbol = manual_input.upper().strip()
        else:
            st.session_state.symbol = selected_stock.upper().strip()

        if exchange == "NSE" and not st.session_state.symbol.endswith(".NS"):
            st.session_state.symbol += ".NS"
        elif exchange == "BSE" and not st.session_state.symbol.endswith(".BO"):
            st.session_state.symbol += ".BO"

    symbol = st.session_state.get("symbol", None)

    if symbol:
        try:
            with st.spinner(f"Fetching data for {symbol}..."):
                stock = yf.Ticker(symbol)
                info = stock.info

            # --- Stock Overview Panel ---
            st.markdown(f"## {info.get('longName', 'N/A')} (`{symbol}`)")
            cols = st.columns(3)
            cols[0].metric("Price", f"₹ {info.get('currentPrice', 'N/A')}")
            cols[1].metric("PE Ratio", info.get('trailingPE', 'N/A'))
            cols[2].metric("ROE", info.get('returnOnEquity', 'N/A'))

            cols = st.columns(3)
            cols[0].metric("EPS", info.get('trailingEps', 'N/A'))
            cols[1].metric("Dividend Yield", info.get('dividendYield', 'N/A'))
            cols[2].metric("Debt to Equity", info.get('debtToEquity', 'N/A'))

            cols = st.columns(3)
            cols[0].metric("Revenue", f"₹ {info.get('totalRevenue', 'N/A'):,}")
            cols[1].metric("Price to Book", info.get('priceToBook', 'N/A'))
            cols[2].metric("Market Cap", f"₹ {info.get('marketCap', 'N/A'):,}")

            # --- Historical Price Chart ---
            st.subheader("📅 Select Historical Price Range")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", datetime.now() - timedelta(days=180))
            with col2:
                end_date = st.date_input("End Date", datetime.now())

            if start_date >= end_date:
                st.warning("⚠️ Start date must be earlier than end date.")
            else:
                with st.spinner("Loading historical price data..."):
                    hist_data = stock.history(start=start_date, end=end_date)
                st.subheader("📉 Historical Price Chart")
                if not hist_data.empty:
                    st.line_chart(hist_data["Close"])
                else:
                    st.warning("No historical price data available.")

            st.markdown("---")
            st.header("💰 DCF Calculator")

            with st.form("dcf_form"):
                estimated_growth = estimate_growth_rate(symbol)
                auto_fcf = get_fcf(symbol)
                fcf = st.number_input("Free Cash Flow (₹ Cr)", value=auto_fcf if auto_fcf else 5000.0)
                growth = st.number_input("Growth Rate (%)", value=estimated_growth)
                discount = st.number_input("Discount Rate (%)", value=11.0)
                years = st.slider("Years", 1, 10, 5)
                submit = st.form_submit_button("Calculate DCF")

            if submit:
                try:
                    g = growth / 100
                    r = discount / 100

                    if g >= r:
                        st.error("❌ Growth rate must be less than Discount rate to calculate Terminal Value.")
                        return

                    fcf_cr = fcf * 1e7
                    dcf_value = sum([(fcf_cr * ((1 + g) ** t)) / ((1 + r) ** t) for t in range(1, years + 1)])
                    tv = (fcf_cr * (1 + g)) / (r - g)
                    discounted_tv = tv / ((1 + r) ** years)
                    total_value = dcf_value + discounted_tv
                    total_value_cr = total_value / 1e7

                    st.markdown(f"🔍 **DCF Value (without Terminal):** ₹ {dcf_value / 1e7:,.2f} Cr")
                    st.markdown(f"🏁 **Terminal Value (discounted):** ₹ {discounted_tv / 1e7:,.2f} Cr")
                    st.success(f"**Estimated Fair Value (Total Company):** ₹ {total_value_cr:,.2f} Cr")

                    shares_outstanding = info.get("sharesOutstanding", None)
                    if shares_outstanding:
                        intrinsic_per_share = total_value / shares_outstanding
                        st.info(f"📌 **Intrinsic Value per Share:** ₹ {intrinsic_per_share:,.2f}")
                    else:
                        st.warning("⚠️ Couldn't fetch number of shares outstanding.")

                    current = info.get("currentPrice", None)
                    if current and shares_outstanding:
                        if current < intrinsic_per_share:
                            verdict = "Undervalued"
                            st.success("✅ Undervalued")
                        elif current > intrinsic_per_share:
                            verdict = "Overvalued"
                            st.error("⚠️ Overvalued")
                        else:
                            verdict = "Fairly Valued"
                            st.warning("⚖️ Fairly Valued")
                    else:
                        verdict = "Unknown"
                        st.warning("⚠️ Current price not available")

                    # Save to Firebase portfolio
                    email_key = st.session_state.user['email'].replace('.', '-')
                    db.child("portfolio").child(email_key).push({
                        "symbol": symbol,
                        "fair_value": round(total_value_cr, 2),
                        "intrinsic_per_share": round(intrinsic_per_share, 2) if shares_outstanding else None,
                        "market_price": current,
                        "verdict": verdict
                    })

                    # Download DCF results as CSV
                    df = pd.DataFrame({
                        "FCF": [fcf],
                        "Growth": [growth],
                        "Discount": [discount],
                        "Years": [years],
                        "Fair Value (₹ Cr)": [total_value_cr],
                        "Intrinsic per Share": [intrinsic_per_share if shares_outstanding else "N/A"]
                    })
                    csv = io.StringIO()
                    df.to_csv(csv, index=False)
                    st.download_button("📥 Download CSV", csv.getvalue(), f"{symbol}_dcf.csv", "text/csv")

                except Exception as e:
                    st.error(f"Error calculating DCF: {e}")

        except Exception as e:
            st.error(f"Error fetching data: {e}")


import streamlit as st
import yfinance as yf
import pandas as pd

@st.cache_data(show_spinner=True)
def load_stock_list():
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    df = pd.read_csv(url)
    return sorted(df["SYMBOL"].dropna().tolist())

@st.cache_data(show_spinner=True)
def fetch_stock_info(symbols):
    data = []
    for symbol in symbols:
        ticker = yf.Ticker(symbol + ".NS")
        try:
            info = ticker.info
        except Exception:
            info = {}
        data.append({
            "Symbol": symbol,
            "Market Cap (Cr)": info.get("marketCap", 0) / 1e7,  # in Crores
            "PE Ratio": info.get("trailingPE", None),
            "ROE (%)": info.get("returnOnEquity", None) * 100 if info.get("returnOnEquity") is not None else None,
            "Debt to Equity": info.get("debtToEquity", None),
            "Dividend Yield (%)": info.get("dividendYield", None) * 100 if info.get("dividendYield") is not None else None,
            "Current Price": info.get("currentPrice", None),
            "Sector": info.get("sector", "Unknown"),
        })
    return pd.DataFrame(data)

def advanced_stock_screener():
    st.title("📈 Advanced Stock Screener")

    # Load list of NSE symbols
    stock_list = load_stock_list()

    # User selects subset or all stocks
    selected_stocks = st.multiselect(
        "Select Stocks to Screen (leave empty to screen all NSE stocks)",
        options=stock_list,
        default=[],
        help="For faster loading, select only stocks you want to screen."
    )

    if not selected_stocks:
        stocks_to_fetch = stock_list[:100]  # limit to 100 stocks for demo
        st.info("Showing screener results for top 100 NSE stocks by default. Select stocks above to customize.")
    else:
        stocks_to_fetch = selected_stocks

    with st.spinner(f"Fetching data for {len(stocks_to_fetch)} stocks..."):
        df = fetch_stock_info(stocks_to_fetch)

    # Remove rows with no Market Cap or PE Ratio to avoid filter errors
    df = df.dropna(subset=["Market Cap (Cr)", "PE Ratio"])

    # Filters UI
    st.sidebar.header("Filter Options")

    min_market_cap = st.sidebar.number_input("Minimum Market Cap (Cr)", min_value=0.0, value=5000.0, step=100)
    max_pe = st.sidebar.number_input("Maximum PE Ratio", min_value=0.0, value=30.0, step=0.5)
    min_roe = st.sidebar.slider("Minimum ROE (%)", min_value=0.0, max_value=100.0, value=15.0, step=0.5)
    max_debt_equity = st.sidebar.slider("Maximum Debt to Equity", min_value=0.0, max_value=5.0, value=1.0, step=0.1)
    min_dividend_yield = st.sidebar.slider("Minimum Dividend Yield (%)", min_value=0.0, max_value=20.0, value=1.0, step=0.1)

    sector_list = sorted(df["Sector"].dropna().unique().tolist())
    selected_sectors = st.sidebar.multiselect("Select Sectors", options=sector_list, default=sector_list)

    # Filter dataframe based on selections
    filtered_df = df[
        (df["Market Cap (Cr)"] >= min_market_cap) &
        (df["PE Ratio"] <= max_pe) &
        (df["ROE (%)"] >= min_roe) &
        (df["Debt to Equity"] <= max_debt_equity) &
        (df["Dividend Yield (%)"] >= min_dividend_yield) &
        (df["Sector"].isin(selected_sectors))
    ]

    st.subheader(f"Filtered Stocks: {len(filtered_df)} found")

    # Sort by Market Cap descending by default
    filtered_df = filtered_df.sort_values(by="Market Cap (Cr)", ascending=False).reset_index(drop=True)

    st.dataframe(filtered_df)

    # Optionally, user can download the filtered result
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", csv, "filtered_stocks.csv", "text/csv")

