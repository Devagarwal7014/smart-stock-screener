import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
from firebase_config import db

@st.cache_data
def load_stock_symbols():
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    df = pd.read_csv(url)
    return sorted(df["SYMBOL"].dropna().tolist())

def get_current_price(symbol):
    try:
        ticker = yf.Ticker(symbol + ".NS")
        info = ticker.info
        return info.get("currentPrice", None)
    except:
        return None

def load_portfolio(user_email):
    email_key = user_email.replace('.', '-')
    data = db.child("portfolios").child(email_key).get().val()
    if data:
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return list(data.values())
    return []

def save_portfolio(user_email, portfolio_list):
    email_key = user_email.replace('.', '-')
    db.child("portfolios").child(email_key).set(portfolio_list)

def sparkline_chart(prices, height=40, width=150):
    df = pd.DataFrame({'price': prices})
    chart = (
        alt.Chart(df.reset_index())
        .mark_line(color="#1f77b4")
        .encode(
            x=alt.X('index', axis=None),
            y=alt.Y('price', axis=None)
        )
        .properties(height=height, width=width)
    )
    return chart

def portfolio_tracker():
    st.title("💼 Portfolio Tracker")

    st.markdown("""
    <style>
    button[kind="secondary"] {
        margin-top: 23px;
    }
    </style>
    """, unsafe_allow_html=True)

    if "user" not in st.session_state:
        st.warning("⚠️ Please login to use Portfolio Tracker.")
        return

    user_email = st.session_state.user["email"]

    if "portfolio_loaded" not in st.session_state:
        st.session_state.portfolio = load_portfolio(user_email)
        st.session_state.portfolio_loaded = True

    symbols_list = load_stock_symbols()

    with st.form("add_stock"):
        symbol = st.selectbox("Select Stock Symbol", symbols_list, key="symbol_input")
        shares = st.number_input("Shares Owned", min_value=1, step=1, key="shares_input")
        buy_price = st.number_input("Buy Price per Share (₹)", min_value=0.0, format="%.2f", key="buy_price_input")
        submitted = st.form_submit_button("Add to Portfolio")

    if submitted:
        if symbol and shares > 0 and buy_price > 0:
            current_price = get_current_price(symbol)
            if current_price:
                st.success(f"Current market price of {symbol} is ₹{current_price:.2f}")
            else:
                st.warning(f"Could not fetch current price for {symbol}")

            st.session_state.portfolio.append({
                "symbol": symbol,
                "shares": shares,
                "buy_price": buy_price
            })
            save_portfolio(user_email, st.session_state.portfolio)
            st.success(f"Added {shares} shares of {symbol} at ₹{buy_price:.2f} to portfolio.")
            st.info("After making changes, please click the '🔄 Refresh Portfolio' button below to update the portfolio display.")
        else:
            st.error("Please enter valid inputs.")

    st.info("After making changes (add/update/delete), please click the '🔄 Refresh Portfolio' button below to apply changes.")
    if st.button("🔄 Refresh Portfolio"):
        if "portfolio_loaded" in st.session_state:
            del st.session_state["portfolio_loaded"]
        st.rerun()

    if not st.session_state.portfolio:
        st.info("Your portfolio is empty. Add stocks above.")
        return

    search_query = st.text_input("🔍 Filter portfolio by symbol (type to filter):").upper().strip()

    filtered_portfolio = [
        item for item in st.session_state.portfolio
        if search_query in item["symbol"].upper()
    ] if search_query else st.session_state.portfolio

    if not filtered_portfolio:
        st.warning("No stocks match your filter.")
        return

    symbols = [item["symbol"] for item in filtered_portfolio]
    yf_symbols = [sym + ".NS" for sym in symbols]

    prices = yf.download(yf_symbols, period="1mo", progress=False)["Close"]
    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    rows = []
    for item in filtered_portfolio:
        sym = item["symbol"]
        shares = item["shares"]
        buy_price = item["buy_price"]

        yf_sym = sym + ".NS"
        current_price = None
        price_history = []

        if not prices.empty:
            if isinstance(prices, pd.Series):
                if yf_symbols and yf_symbols[0] == yf_sym:
                    current_price = prices.iloc[-1]
                    price_history = prices.dropna().tolist()
            elif yf_sym in prices.columns:
                series = prices[yf_sym].dropna()
                if not series.empty:
                    current_price = series.iloc[-1]
                    price_history = series.tolist()

        invested = shares * buy_price
        current_value = shares * current_price if current_price is not None else None
        profit_loss = current_value - invested if current_value is not None else None
        profit_loss_pct = (profit_loss / invested * 100) if profit_loss is not None else None

        rows.append({
            "Symbol": sym,
            "Shares": shares,
            "Buy Price": buy_price,
            "Current Price": current_price if current_price is not None else "N/A",
            "Invested (₹)": invested,
            "Current Value (₹)": current_value if current_value is not None else "N/A",
            "P/L (₹)": profit_loss if profit_loss is not None else "N/A",
            "P/L (%)": profit_loss_pct if profit_loss_pct is not None else None,
            "Price History": price_history
        })

    df = pd.DataFrame(rows)

    def style_pl(val):
        if val is None:
            return ""
        color = 'green' if val >= 0 else 'red'
        return f'color: {color}'

    styled_df = df.style.format({
        'Buy Price': '₹{:.2f}',
        'Current Price': lambda v: f"₹{v:.2f}" if isinstance(v, (int,float)) else v,
        'Invested (₹)': '₹{:.2f}',
        'Current Value (₹)': lambda v: f"₹{v:.2f}" if isinstance(v, (int,float)) else v,
        'P/L (₹)': lambda v: f"₹{v:.2f}" if isinstance(v, (int,float)) else v,
        'P/L (%)': '{:.2f}%',
    }).applymap(style_pl, subset=['P/L (₹)', 'P/L (%)'])

    total_invested = sum(item["shares"]*item["buy_price"] for item in st.session_state.portfolio)
    total_current_value = 0
    for item in st.session_state.portfolio:
        sym = item["symbol"]
        shares = item["shares"]
        current_price = None
        yf_sym = sym + ".NS"
        if not prices.empty:
            if isinstance(prices, pd.Series):
                if yf_symbols and yf_symbols[0] == yf_sym:
                    current_price = prices.iloc[-1]
            elif yf_sym in prices.columns:
                series = prices[yf_sym]
                if not series.empty:
                    current_price = series.iloc[-1]
        if current_price is not None:
            total_current_value += shares*current_price

    total_pl = total_current_value - total_invested
    total_pl_pct = (total_pl / total_invested) * 100 if total_invested > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Invested (₹)", f"{total_invested:,.2f}")
    col2.metric("Total Current Value (₹)", f"{total_current_value:,.2f}")
    pl_label = "Profit" if total_pl >= 0 else "Loss"
    pl_value = f"₹{abs(total_pl):,.2f} ({abs(total_pl_pct):.2f}%)"
    col3.metric(pl_label, pl_value, delta=f"{total_pl_pct:.2f}%")

    st.markdown("---")
    left_col, right_col = st.columns([3, 1])

    with left_col:
        with st.expander(f"Show/Hide Detailed Portfolio ({len(df)} stocks)"):
            st.dataframe(
                df.drop(columns=["Price History"]).style.format({
                    'Buy Price': '₹{:.2f}',
                    'Current Price': lambda v: f"₹{v:.2f}" if isinstance(v, (int,float)) else v,
                    'Invested (₹)': '₹{:.2f}',
                    'Current Value (₹)': lambda v: f"₹{v:.2f}" if isinstance(v, (int,float)) else v,
                    'P/L (₹)': lambda v: f"₹{v:.2f}" if isinstance(v, (int,float)) else v,
                    'P/L (%)': '{:.2f}%',
                }).applymap(style_pl, subset=['P/L (₹)', 'P/L (%)']),
                use_container_width=True)

            for row in rows:
                cols = st.columns([1, 1, 1, 0.7])
                sym = row["Symbol"]
                cols[0].write(sym)

                new_shares = cols[1].number_input("Shares", min_value=1, key=f"shares_{sym}", value=row["Shares"])
                new_buy_price = cols[2].number_input("Buy Price", min_value=0.0, format="%.2f", key=f"buyprice_{sym}", value=row["Buy Price"])
                
                if cols[3].button("❌ Delete", key=f"del_{sym}", use_container_width=True):
                    # Remove by symbol
                    st.session_state.portfolio = [item for item in st.session_state.portfolio if item["symbol"] != sym]
                    save_portfolio(user_email, st.session_state.portfolio)
                    st.info("Please click the '🔄 Refresh Portfolio' button above to update the portfolio display.")
                
                if (new_shares != row["Shares"]) or (new_buy_price != row["Buy Price"]):
                    for item in st.session_state.portfolio:
                        if item["symbol"] == sym:
                            item["shares"] = new_shares
                            item["buy_price"] = new_buy_price
                            save_portfolio(user_email, st.session_state.portfolio)
                            st.info("Please click the '🔄 Refresh Portfolio' button above to update the portfolio display.")
                            break
    with right_col:
        st.subheader("Portfolio Allocation")
        pie_data = pd.DataFrame({
            'Stock': df['Symbol'],
            'Invested': df['Invested (₹)']
        })
        chart = alt.Chart(pie_data).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="Invested", type="quantitative"),
            color=alt.Color(field="Stock", type="nominal"),
            tooltip=["Stock", "Invested"]
        )
        st.altair_chart(chart, use_container_width=True)

    st.markdown("---")
    st.subheader("Recent Price Trends")
    for row in rows:
        if row["Price History"] and len(row["Price History"]) > 1:
            st.write(f"{row['Symbol']}")
            chart = sparkline_chart(row["Price History"])
            st.altair_chart(chart, use_container_width=False)
        else:
            st.write(f"{row['Symbol']} - No recent price data")
