import streamlit as st
import pandas as pd
import jinja2
import nltk
import nltk.data
from nltk.corpus import stopwords
from nltk.tokenize import TreebankWordTokenizer
import json
import math

# Safer NLTK data loading
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)

# App config
st.set_page_config(page_title="📸 CSV to WordPress Cards", layout="wide")
st.title("📸 CSV to WordPress Media Cards")

# Refresh button
if st.button("🔁 Refresh Template"):
    st.experimental_rerun()

uploaded_file = st.file_uploader("Upload Combined CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df = df.sort_values(by="Media Number", ascending=False)

    # Load master keywords
    with open("keywords/master_keywords.json") as f:
        master_keywords = json.load(f)

    stop_words = set(stopwords.words("english"))

    # Keyword extraction logic
    def extract_keywords(text, max_keywords=5):
        if not isinstance(text, str):
            return []
        tokens = TreebankWordTokenizer().tokenize(text.lower())
        tokens = [t for t in tokens if t.isalnum() and t not in stop_words]
        matched = set()
        for master, terms in master_keywords.items():
            for term in terms:
                if term.lower() in tokens:
                    matched.add(master)
                    break
        return list(matched)[:max_keywords]

    df["Keywords"] = df["Description"].apply(extract_keywords)

    # Popularity rating logic
    def get_star_rating(sales_count, total_earnings):
        if sales_count >= 10 or total_earnings > 1000:
            return "★★★★★"
        elif sales_count >= 5 or total_earnings > 500:
            return "★★★★"
        elif sales_count >= 3 or total_earnings > 200:
            return "★★★"
        elif sales_count >= 2:
            return "★★"
        elif sales_count >= 1:
            return "★"
        else:
            return ""

    df["Sales Count"] = df.groupby("Media Number")["Media Number"].transform("count")
    df["Total Earnings"] = df.groupby("Media Number")["Your Share"].transform("sum")
    df["Rating"] = df.apply(lambda row: get_star_rating(row["Sales Count"], row["Total Earnings"]), axis=1)
, row["Total E]()
