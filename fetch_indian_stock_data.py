import requests
import pandas as pd
from bs4 import BeautifulSoup

def get_screener_fundamentals(symbol: str) -> dict:
    """
    Scrape key fundamentals from Screener.in company page.
    Returns a dict with fields: roe, opm, pb, de_ratio, fcf, eps_growth, revenue_growth.
    """
    url = f"https://www.screener.in/company/{symbol}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        def parse_value(label):
            el = soup.find("span", string=label)
            if el and el.parent and el.parent.find_next_sibling("span"):
                text = el.parent.find_next_sibling("span").text.strip().replace("%", "").replace(",", "")
                try:
                    return float(text)
                except:
                    pass
            return None
        return {
            "symbol": symbol,
            "roe": parse_value("Return on equity"),
            "opm": parse_value("Operating profit margin"),
            "pb": parse_value("Price to book value"),
            "de_ratio": parse_value("Debt to equity"),
            "fcf": parse_value("Free cash flow"),
            "eps_growth": parse_value("EPS growth"),
            "revenue_growth": parse_value("Sales growth")
        }
    except Exception as e:
        print(f"Error fetching fundamentals for {symbol}: {e}")
        return {"symbol": symbol}

def get_nse_price(symbol: str) -> dict:
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        resp = session.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        info = data["priceInfo"]
        return {
            "symbol": symbol,
            "last_price": info.get("lastPrice"),
            "day_high": info["intraDayHighLow"].get("max"),
            "day_low": info["intraDayHighLow"].get("min"),
            "volume": info.get("quantityTraded")
        }
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return {"symbol": symbol}

def get_full_stock_data(symbol: str) -> dict:
    data = get_screener_fundamentals(symbol)
    data.update(get_nse_price(symbol))
    return data

# Example usage: fetch data for top 5 NSE stocks
if __name__ == "__main__":
    nse_list = pd.read_csv("https://archives.nseindia.com/content/equities/EQUITY_L.csv")["SYMBOL"].dropna().tolist()
    symbols = nse_list[:5]  # Change this to any number you want!
    all_data = [get_full_stock_data(sym) for sym in symbols]
    df = pd.DataFrame(all_data)
    print(df)
