import streamlit as st
import requests
import os
from textblob import TextBlob

# Load Bearer Token from environment variable (never hardcode it!)
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

if not BEARER_TOKEN:
    st.error("Twitter API Bearer Token not found. Please set TWITTER_BEARER_TOKEN env variable.")
    st.stop()

def get_tweets(query, max_results=50):
    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }
    params = {
        "query": query + " -is:retweet lang:en",  # filter out retweets, English only
        "max_results": max_results,
        "tweet.fields": "created_at,text"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        st.error(f"Error fetching tweets: {response.status_code} - {response.text}")
        return []
    data = response.json()
    return data.get("data", [])

def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"

def social_media_trends():
    st.title("📈 Social Media Trends & Sentiment Analysis")
    query = st.text_input("Enter a topic or stock symbol to analyze", value="NSE")
    max_tweets = st.slider("Number of tweets to analyze", 10, 100, 50)

    if st.button("Analyze"):
        with st.spinner("Fetching tweets and analyzing sentiment..."):
            tweets = get_tweets(query, max_tweets)
            if not tweets:
                st.warning("No tweets found for this query.")
                return
            
            sentiments = {"Positive": 0, "Neutral": 0, "Negative": 0}
            for tweet in tweets:
                sentiment = analyze_sentiment(tweet["text"])
                sentiments[sentiment] += 1

            total = sum(sentiments.values())
            st.subheader(f"Sentiment summary for '{query}' (analyzed {total} tweets)")
            st.write(f"**Positive:** {sentiments['Positive']} ({sentiments['Positive']/total*100:.1f}%)")
            st.write(f"**Neutral:** {sentiments['Neutral']} ({sentiments['Neutral']/total*100:.1f}%)")
            st.write(f"**Negative:** {sentiments['Negative']} ({sentiments['Negative']/total*100:.1f}%)")

            st.markdown("---")
            st.subheader("Sample Tweets")
            for tweet in tweets[:10]:
                st.write(f"- {tweet['text']}")

