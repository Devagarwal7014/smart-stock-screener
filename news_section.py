import streamlit as st
import requests
import time
import datetime

NEWS_API_KEY = "4ff211e250a74772a484c7ec07a46916"

def get_news(query, page_size=5):
    now = datetime.datetime.utcnow()
    one_min_ago = now - datetime.timedelta(minutes=1)
    from_time = one_min_ago.isoformat("T") + "Z"

    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={query}&"
        f"language=en&"
        f"pageSize={page_size}&"
        f"from={from_time}&"
        f"sortBy=publishedAt&"
        f"apiKey={NEWS_API_KEY}"
    )
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json().get("articles", [])
    else:
        st.error(f"Failed to fetch news: {resp.status_code}")
        return []

def news_section():
    st.subheader("📰 Latest Stock Market News")

    query = st.text_input("Search news (e.g. Reliance, Nifty, Sensex)", "stock market India")

    refresh_interval = 15  # seconds

    last_fetch = st.session_state.get("last_news_fetch", 0)
    now = time.time()

    manual_refresh = st.button("Get News Now")

    if manual_refresh or (now - last_fetch > refresh_interval) or ("news_articles" not in st.session_state):
        with st.spinner("Fetching news..."):
            articles = get_news(query)
            st.session_state["news_articles"] = articles
            st.session_state["last_news_fetch"] = now
    else:
        articles = st.session_state.get("news_articles", [])

    if articles:
        for article in articles:
            st.markdown(
                f"""### <a href="{article['url']}" target="_blank" style="text-decoration:none;color:#1f77b4;">{article['title']}</a>""",
                unsafe_allow_html=True
            )
            desc = article.get('description', '')
            if desc:
                if len(desc) > 300:
                    desc = desc[:300] + "..."
                st.write(desc)
            pub_date = article['publishedAt'][:10]
            source = article['source']['name']
            st.markdown(f"🗓️ {pub_date} | 📍 Source: **{source}**")
            st.markdown("---")
    else:
        st.warning("No news found.")
