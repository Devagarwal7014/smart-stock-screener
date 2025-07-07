import streamlit as st
from textblob import TextBlob
import requests
import pandas as pd
import altair as alt
import os
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# --- Load NSE symbols ---
@st.cache_data
def load_nse_symbols():
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    df = pd.read_csv(url)
    return sorted(df["SYMBOL"].dropna().tolist())

# --- NewsAPI setup ---
NEWS_API_KEY = "4ff211e250a74772a484c7ec07a46916"

def fetch_news(stock_symbol):
    url = f"https://newsapi.org/v2/everything?q={stock_symbol}&apiKey={NEWS_API_KEY}&language=en&pageSize=10&sortBy=publishedAt"
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        return data.get("articles", [])
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return []

# --- Twitter API setup ---
TWITTER_BEARER_TOKEN = ("AAAAAAAAAAAAAAAAAAAAAI/M2wEAAAAAoqMa1XtmNi/lu49eVJkphFPiXjQ=UidjQuA21uKh9oASHvizDwJAMrjsVosDmXdKx3Vzt2gMiySHru")

def get_tweets(query, max_results=50):
    if not TWITTER_BEARER_TOKEN:
        st.error("Twitter API Bearer Token not found. Please set TWITTER_BEARER_TOKEN env variable.")
        st.stop()
    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    params = {
        "query": f"{query} -is:retweet lang:en",
        "max_results": max_results,
        "tweet.fields": "created_at,text"
    }
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        st.error(f"Error fetching tweets: {resp.status_code} - {resp.text}")
        return []
    return resp.json().get("data", [])

# --- Sentiment analysis ---
def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity

# --- Word Cloud ---
def create_wordcloud(text):
    wordcloud = WordCloud(width=600, height=400, background_color='white').generate(text)
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt)

# --- Main Page ---
def sentiment_news_page():
    st.title("📈 Stock Sentiment & Social Media Trends")

    symbols = load_nse_symbols()
    symbol = st.selectbox("Select Stock Symbol", symbols)

    st.markdown(f"### News and Sentiment for {symbol}")

    # --- News Section ---
    articles = fetch_news(symbol)
    if not articles:
        st.info("No recent news found.")
    else:
        news_sentiments = []
        all_news_text = ""
        for article in articles:
            title = article.get("title", "")
            description = article.get("description", "")
            combined_text = title + " " + description
            polarity = analyze_sentiment(combined_text)
            news_sentiments.append(polarity)
            all_news_text += combined_text + " "

            with st.expander(f"{title} (Sentiment: {polarity:.2f})"):
                st.write(description)
                st.markdown(f"[Read full article]({article.get('url', '#')})")

        avg_news_sentiment = sum(news_sentiments) / len(news_sentiments) if news_sentiments else 0.0
        st.markdown(f"#### Average News Sentiment Score: {avg_news_sentiment:.2f}")

        if avg_news_sentiment > 0.1:
            st.success("Overall Positive News Sentiment 👍")
        elif avg_news_sentiment < -0.1:
            st.error("Overall Negative News Sentiment 👎")
        else:
            st.warning("Neutral News Sentiment 😐")

        st.markdown("##### Top News Words")
        stopwords = set([
            'the', 'and', 'to', 'of', 'in', 'for', 'on', 'is', 'with', 'at', 'by', 'from', 
            'this', 'that', 'it', 'as', 'are', 'was', 'be', 'or', 'an', 'have', 'has', 'but'
        ])
        news_words = [word.lower() for word in all_news_text.split() if word.isalpha() and word.lower() not in stopwords]
        news_freq = Counter(news_words)
        common_news_words = news_freq.most_common(20)
        for word, count in common_news_words:
            st.write(f"{word}: {count}")

        st.markdown("##### News Word Cloud")
        create_wordcloud(all_news_text)

    st.markdown("---")

    # --- Twitter Section ---
    st.subheader("🐦 Social Media Trends on Twitter")
    max_tweets = st.slider("Number of Tweets to Analyze", min_value=10, max_value=100, value=50)

    if st.button("Analyze Twitter Sentiment"):
        with st.spinner("Fetching tweets and analyzing sentiment..."):
            tweets = get_tweets(symbol, max_tweets)
            if not tweets:
                st.warning("No tweets found for this query.")
                return

            all_tweet_text = ""
            sentiments = {"Positive": 0, "Neutral": 0, "Negative": 0}

            for tweet in tweets:
                all_tweet_text += tweet["text"] + " "
                sentiment = analyze_sentiment(tweet["text"])
                if sentiment > 0.1:
                    sentiments["Positive"] += 1
                elif sentiment < -0.1:
                    sentiments["Negative"] += 1
                else:
                    sentiments["Neutral"] += 1

            total = sum(sentiments.values())
            st.write(f"**Positive:** {sentiments['Positive']} ({sentiments['Positive']/total*100:.1f}%)")
            st.write(f"**Neutral:** {sentiments['Neutral']} ({sentiments['Neutral']/total*100:.1f}%)")
            st.write(f"**Negative:** {sentiments['Negative']} ({sentiments['Negative']/total*100:.1f}%)")

            st.markdown("---")
            st.subheader("Top Twitter Words (Excluding Common Stopwords)")

            tweet_words = [word.lower() for word in all_tweet_text.split() if word.isalpha() and word.lower() not in stopwords]
            tweet_freq = Counter(tweet_words)
            common_tweet_words = tweet_freq.most_common(20)
            for word, count in common_tweet_words:
                st.write(f"{word}: {count}")

            st.markdown("---")
            st.subheader("Twitter Word Cloud")
            create_wordcloud(all_tweet_text)

            st.markdown("---")
            st.subheader("Sample Tweets")
            for tweet in tweets[:10]:
                st.write(f"- {tweet['text']}")
