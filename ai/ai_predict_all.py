import yfinance as yf
import pandas as pd
import joblib

model = joblib.load("ai_model.joblib")

nse_url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
nse_df = pd.read_csv(nse_url)
symbols = sorted(nse_df["SYMBOL"].dropna().unique().tolist())
symbols = [sym + ".NS" for sym in symbols][:2000]  # Limit for testing

def fetch_features(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        roe = info.get("returnOnEquity")
        opm = info.get("operatingMargins")
        pb = info.get("priceToBook")
        de = info.get("debtToEquity")
        fcf = info.get("freeCashflow")
        eps_growth = info.get("earningsQuarterlyGrowth")
        revenue_growth = info.get("revenueGrowth")
        if None in [roe, opm, pb, de, fcf, eps_growth, revenue_growth]:
            return None
        return {
            "symbol": symbol,
            "roe": roe * 100,
            "opm": opm * 100,
            "pb": pb,
            "de_ratio": de,
            "fcf": fcf / 1e7,
            "eps_growth": eps_growth * 100,
            "revenue_growth": revenue_growth * 100
        }
    except:
        return None

records = [fetch_features(sym) for sym in symbols]
df = pd.DataFrame([r for r in records if r])

features_cols = ["roe", "opm", "pb", "de_ratio", "fcf", "eps_growth", "revenue_growth"]
df["is_undervalued"] = model.predict(df[features_cols])
df["confidence"] = model.predict_proba(df[features_cols])[:, 1]

def explain(row):
    reasons = []
    if row["roe"] >= 15: reasons.append("High ROE")
    if row["opm"] >= 15: reasons.append("Strong OPM")
    if row["pb"] <= 3: reasons.append("Attractive P/B")
    if row["de_ratio"] <= 1: reasons.append("Low Debt")
    if row["fcf"] > 0: reasons.append("Positive FCF")
    if row["eps_growth"] > 0: reasons.append("EPS Growth")
    if row["revenue_growth"] > 0: reasons.append("Revenue Growth")
    return ", ".join(reasons)

df["Why Picked"] = df.apply(explain, axis=1)
suggestions = df[df["is_undervalued"] == 1].sort_values("confidence", ascending=False)

# Save to CSV
suggestions.to_csv("ai_stock_suggestions.csv", index=False)
print("✅ Suggestions saved to ai_stock_suggestions.csv")
