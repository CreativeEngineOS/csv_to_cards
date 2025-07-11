
import streamlit as st
import pandas as pd
import jinja2
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import base64
import io
import re
import textwrap

nltk.download("punkt")
nltk.download("stopwords")

st.set_page_config(page_title="📸 CSV to WP Cards", layout="wide")
st.title("📸 CSV to WordPress Media Cards")

# HTML Export Function
def generate_download_link(html_content):
    b64 = base64.b64encode(html_content.encode()).decode()
    href = f'<a href="data:text/plain;base64,{b64}" download="media_cards.txt">📥 Download HTML as .txt</a>'
    return href

# Keyword grouping
master_keywords = {
    "Politics & Government": ["government", "senate", "law", "white house", "kamala", "biden", "trump"],
    "U.S. Elections": ["elections", "voting", "ballot", "polling", "campaign"],
    "Philadelphia": ["philadelphia", "philly", "fishtown", "germantown", "south philly"],
    "Human Interest": ["community", "people", "local", "family", "neighborhood"],
    "Social Issues": ["homeless", "protest", "rights", "justice", "activist"],
    "Infrastructure": ["bridge", "road", "transportation", "construction"],
    "Art/Culture/Entertainment": ["art", "music", "festival", "parade", "culture"],
    "Sports": ["football", "baseball", "soccer", "game", "team", "athlete"],
    "Weather": ["rain", "snow", "storm", "sun", "weather"],
    "Economy/Business/Finance": ["business", "finance", "market", "store", "inflation"]
}

stop_words = set(stopwords.words("english"))

def extract_keywords(text, max_keywords=5):
    tokens = word_tokenize(str(text).lower())
    tokens = [t for t in tokens if t.isalnum() and t not in stop_words]
    matched = []
    for master, terms in master_keywords.items():
        if any(term in tokens for term in terms):
            matched.append(master)
            if len(matched) >= max_keywords:
                break
    return ", ".join(matched)

def truncate_caption(text):
    text = str(text).replace("(Photo by Bastiaan Slabbers/NurPhoto)", "").strip()
    sentences = sent_tokenize(text)
    if len(sentences) <= 3:
        return text, ""
    return " ".join(sentences[:3]), " ".join(sentences[3:])

def get_star_rating(count, total):
    if count >= 10 or total >= 300:
        return "★★★★★"
    elif count >= 7:
        return "★★★★"
    elif count >= 4:
        return "★★★"
    elif count >= 2:
        return "★★"
    elif count >= 1:
        return "★"
    else:
        return ""

# Upload
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
if uploaded_file:
    df_raw = pd.read_csv(uploaded_file)
    df = df_raw.copy()

    # Deduplicate and tally
    tally = df.groupby("Media Number").agg({
        "Description": "first",
        "Thumbnail": "first",
        "Sales Count": "sum",
        "Total Earnings": "sum",
        "URL": "first"
    }).reset_index()

    tally["Keywords"] = tally["Description"].apply(extract_keywords)
    tally["Short Caption"], tally["Remainder Caption"] = zip(*tally["Description"].map(truncate_caption))
    tally["Rating"] = tally.apply(lambda row: get_star_rating(row["Sales Count"], row["Total Earnings"]), axis=1)

    # Sort by descending order (new to old)
    tally = tally.sort_values(by="Media Number", ascending=False).reset_index(drop=True)

    # Pagination and card size
    size = st.radio("Card Size", ["Default (3/row)", "Medium (5/row)", "Compact"], horizontal=True)
    per_row = {"Default (3/row)": 3, "Medium (5/row)": 5, "Compact": 8}[size]
    per_page = per_row * 7
    total_pages = (len(tally) + per_page - 1) // per_page
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)

    # Subset of cards for the current page
    subset = tally.iloc[(page-1)*per_page:page*per_page]

    # Render HTML cards using Jinja2
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    template = env.get_template("card_template.html")
    html_cards = template.render(data=subset.to_dict(orient="records"), columns=per_row)

    # Show download link
    st.markdown(generate_download_link(html_cards), unsafe_allow_html=True)

    # Show cards
    st.components.v1.html(html_cards, height=1600, scrolling=True)
