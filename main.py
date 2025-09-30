import streamlit as st
import pandas as pd
import sqlite3
import tweepy
from PIL import Image
from datetime import date
import json
import os

# ==============================
# TWITTER API SETUP (Tweepy)
# ==============================
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAL394QEAAAAA1hQhvdMOxGvPgXkDwBhxubp19U8%3DQjvdNuagA9CdQoMG0zwD5iwOon6o0iDhyxdzgqhJAI94I125wj"  # Replace with your real token
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# ==============================
# DATABASE SETUP (SQLite3)
# ==============================
conn = sqlite3.connect("tweets.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS tweets (
        id TEXT PRIMARY KEY,
        date TEXT,
        username TEXT,
        content TEXT
    )
''')
conn.commit()

# ==============================
# STREAMLIT WEB APP
# ==============================
def main():
    st.title("Twitter Scraping App (SQLite + Streamlit)")

    menu = ["Home", "About", "Search", "Display", "Download"]
    choice = st.sidebar.selectbox("Menu", menu)

    # HOME TAB
    if choice == "Home":
        st.write('''
        This app scrapes recent tweets using the Twitter API and saves them into a local SQLite3 database.
        You can display the tweets and download them as CSV or JSON.
        ''')
        image_path = ("D:\Desktop\Project_1\elonmusktwt.png") # Update path if needed
        if os.path.exists(image_path):
            image = Image.open(image_path)
            st.image(image, caption="Twitter Scraping", use_column_width=True)
        else:
            st.warning("Image not found at specified path.")

    # ABOUT TAB
    elif choice == "About":
        with st.expander("About Tweepy"):
            st.write("Tweepy is the official Python library to access Twitter's API safely and reliably.")
        with st.expander("About SQLite"):
            st.write("SQLite is a lightweight, file-based database — perfect for small projects like this.")
        with st.expander("About Streamlit"):
            st.write("Streamlit turns Python scripts into beautiful web apps for data science and ML.")

    # SEARCH TAB
    elif choice == "Search":
        with st.form(key="search_form"):
            st.subheader("Search Tweets by Username 🔍")
            username = st.text_input("Enter Twitter username (without @)")
            limit = st.slider("Number of tweets to fetch", 10, 100, 20)
            submit = st.form_submit_button("Fetch Tweets")

        if submit:
            if not username:
                st.warning("Please enter a username.")
            else:
                st.info(f"Fetching tweets from @{username} ...")
                try:
                    # Get user ID from username
                    user_data = client.get_user(username=username)
                    user_id = user_data.data.id

                    # Fetch recent tweets from this user
                    tweets = client.get_users_tweets(
                        id=user_id,
                        max_results=limit,
                        tweet_fields=["created_at"]
                    )

                    if tweets.data:
                        inserted = 0
                        for tweet in tweets.data:
                            tid = tweet.id
                            content = tweet.text
                            tdate = str(tweet.created_at)

                            try:
                                c.execute(
                                    "INSERT INTO tweets (id, date, username, content) VALUES (?, ?, ?, ?)",
                                    (tid, tdate, username, content)
                                )
                                conn.commit()
                                inserted += 1
                            except sqlite3.IntegrityError:
                                pass  # Duplicate tweet

                        st.success(f"{inserted} new tweets from @{username} inserted into database.")
                    else:
                        st.warning(f"No tweets found for @{username}.")

                except Exception as e:
                    st.error(f"Error occurred: {e}")

    # DISPLAY TAB
    elif choice == "Display":
        st.subheader("Stored Tweets 🗃️")
        df = pd.read_sql_query("SELECT * FROM tweets ORDER BY date DESC", conn)
        st.dataframe(df)

    # DOWNLOAD TAB
    elif choice == "Download":
        df = pd.read_sql_query("SELECT * FROM tweets ORDER BY date DESC", conn)

        col1, col2 = st.columns(2)

        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name='tweets.csv',
                mime='text/csv'
            )

        with col2:
            json_data = df.to_json(orient="records", indent=2)
            st.download_button(
                label="Download as JSON",
                data=json_data,
                file_name='tweets.json',
                mime='application/json'
            )

        st.success("Download complete.")

# ==============================
# RUN APP
# ==============================
if __name__ == '__main__':
    main()