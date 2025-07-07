import streamlit as st
import requests
import os
from textblob import TextBlob
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

if not BEARER_TOKEN:
    st.error("Twitter API Bearer Token not found. Please set TWITTER_BEARER_TOKEN env variable.")
    st.stop()

def get_tweets(query, max_results=50):
    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
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

def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"

def create_wordcloud(text):
    wordcloud = WordCloud(width=600, height=400, background_color='white').generate(text)
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt)

def social_media_tab():
    st.title("📊 Social Media Trends + Sentiment Analysis")

    query = st.text_input("Enter topic, keyword, or stock symbol", value="NSE")
    max_tweets = st.slider("Number of Tweets to Analyze", min_value=10, max_value=100, value=50)

    if st.button("Analyze"):
        with st.spinner("Fetching tweets and analyzing sentiment..."):
            tweets = get_tweets(query, max_tweets)
            if not tweets:
                st.warning("No tweets found for this query.")
                return

            sentiments = {"Positive": 0, "Neutral": 0, "Negative": 0}
            all_text = ""

            for tweet in tweets:
                all_text += tweet["text"] + " "
                sentiment = analyze_sentiment(tweet["text"])
                sentiments[sentiment] += 1

            total = sum(sentiments.values())

            st.subheader(f"Sentiment Summary for '{query}' (from {total} tweets):")
            st.write(f"**Positive:** {sentiments['Positive']} ({sentiments['Positive']/total*100:.1f}%)")
            st.write(f"**Neutral:** {sentiments['Neutral']} ({sentiments['Neutral']/total*100:.1f}%)")
            st.write(f"**Negative:** {sentiments['Negative']} ({sentiments['Negative']/total*100:.1f}%)")

            st.markdown("---")
            st.subheader("Top Trending Words (Excluding Common Stopwords)")

            # Simple word frequency excluding common stopwords
            stopwords = set([
                'the', 'and', 'to', 'of', 'in', 'for', 'on', 'is', 'with', 'at', 'by', 'from', 
                'this', 'that', 'it', 'as', 'are', 'was', 'be', 'or', 'an', 'have', 'has', 'but'
            ])
            words = [word.lower() for word in all_text.split() if word.isalpha() and word.lower() not in stopwords]
            freq = Counter(words)
            common_words = freq.most_common(20)
            for word, count in common_words:
                st.write(f"{word}: {count}")

            st.markdown("---")
            st.subheader("Word Cloud")
            create_wordcloud(all_text)

            st.markdown("---")
            st.subheader("Sample Tweets")
            for tweet in tweets[:10]:
                st.write(f"- {tweet['text']}")
