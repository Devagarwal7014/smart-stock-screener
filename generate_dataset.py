import yfinance as yf
import pandas as pd
import numpy as np

def calculate_technical_indicators(df):
    df["50_MA"] = df["Close"].rolling(window=50).mean()
    df["200_MA"] = df["Close"].rolling(window=200).mean()
    df["Price_Momentum_30"] = df["Close"].pct_change(periods=30) * 100
    df["Volatility"] = df["Close"].rolling(window=30).std()
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

symbols = [
    "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ITC.NS",
    "ASIANPAINT.NS", "RELIANCE.NS", "MARUTI.NS", "SBIN.NS",
    "BAJFINANCE.NS", "LT.NS", "DMART.NS", "KOTAKBANK.NS"
]

data = []
for symbol in symbols:
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        hist = stock.history(period="1y")

        if len(hist) < 200:
            continue

        hist = calculate_technical_indicators(hist)
        latest = hist.iloc[-1]

        roe = info.get("returnOnEquity", None)
        opm = info.get("operatingMargins", None)
        pb = info.get("priceToBook", None)
        de = info.get("debtToEquity", None)
        fcf = info.get("freeCashflow", 0)
        eps_growth = info.get("earningsQuarterlyGrowth", 0)
        revenue_growth = info.get("revenueGrowth", 0)

        current_price = info.get("currentPrice", None)
        intrinsic = info.get("bookValue", 0) * pb if pb else None
        is_undervalued = 1 if intrinsic and current_price and current_price < intrinsic else 0

        data.append({
            "symbol": symbol,
            "roe": roe * 100 if roe else None,
            "opm": opm * 100 if opm else None,
            "pb": pb,
            "de_ratio": de,
            "fcf": fcf / 1e7 if fcf else 0,
            "eps_growth": eps_growth * 100 if eps_growth else 0,
            "revenue_growth": revenue_growth * 100 if revenue_growth else 0,
            "50_MA": latest["50_MA"],
            "200_MA": latest["200_MA"],
            "Price_Momentum_30": latest["Price_Momentum_30"],
            "Volatility": latest["Volatility"],
            "RSI": latest["RSI"],
            "is_undervalued": is_undervalued
        })

    except Exception as e:
        print(f"Error with {symbol}: {e}")
        continue

df = pd.DataFrame(data)
df = df.dropna()
df.to_csv("stock_training_data.csv", index=False)
print("✅ Dataset saved to stock_training_data.csv")
