import yfinance as yf
import pandas as pd

# Load NSE symbols
nse_df = pd.read_csv("https://archives.nseindia.com/content/equities/EQUITY_L.csv")
symbols = sorted(nse_df["SYMBOL"].dropna().tolist())
sample_symbols = [s + ".NS" for s in symbols[:20]]

def fetch_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        roe = info.get("returnOnEquity", None)
        opm = info.get("operatingMargins", None)
        pb = info.get("priceToBook", None)
        de = info.get("debtToEquity", None)
        fcf = info.get("freeCashflow", 0)

        hist = stock.history(period="6mo")
        if hist.empty:
            return None

        close = hist["Close"]
        ma_50 = close.rolling(50).mean().iloc[-1]
        ma_200 = close.rolling(200).mean().iloc[-1]
        momentum_30 = close.pct_change(30).iloc[-1]
        rsi = 100 - (100 / (1 + (close.pct_change().gt(0).sum() / close.pct_change().lt(0).sum())))
        volatility = close.pct_change().std()

        return {
            "symbol": symbol,
            "roe": roe * 100 if roe else None,
            "opm": opm * 100 if opm else None,
            "pb": pb,
            "de_ratio": de,
            "fcf": fcf / 1e7 if fcf else None,
            "50_MA": ma_50,
            "200_MA": ma_200,
            "Price_Momentum_30": momentum_30,
            "RSI": rsi,
            "Volatility": volatility
        }
    except:
        return None

# Fetch and save
results = [fetch_stock_data(symbol) for symbol in sample_symbols]
df = pd.DataFrame([r for r in results if r is not None])
df.to_csv("phase2_sample_data.csv", index=False)
print("✅ Sample data saved as 'phase2_sample_data.csv'")
