import streamlit as st
import pandas as pd
import jinja2
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import json
from datetime import datetime

# Ensure necessary NLTK data is downloaded
nltk.download("punkt")
nltk.download("stopwords")

# Master keyword themes
with open("keywords/master_keywords.json") as f:
    master_keywords = json.load(f)
stop_words = set(stopwords.words("english"))

# Rating system
def get_star_rating(sales, total):
    if sales >= 10 or total > 1000:
        return "★★★★★"
    elif sales >= 7 or total > 500:
        return "★★★★"
    elif sales >= 4 or total > 250:
        return "★★★"
    elif sales >= 2 or total > 100:
        return "★★"
    elif sales >= 1:
        return "★"
    return ""

# Keyword extraction
def extract_keywords(text, max_keywords=5):
    tokens = word_tokenize(str(text).lower())
    tokens = [t for t in tokens if t.isalnum() and t not in stop_words]
    matched = set()
    for master, terms in master_keywords.items():
        for t in tokens:
            if t in terms:
                matched.add(master)
                break
    return ", ".join(sorted(matched))[:max_keywords]

# Caption truncation
def truncate_caption(text):
    text = str(text).replace("(Photo by Bastiaan Slabbers/NurPhoto)", "").strip()
    tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
    sentences = tokenizer.tokenize(text)
    if len(sentences) <= 3:
        return text, ""
    short = " ".join(sentences[:2])
    remainder = " ".join(sentences[2:])
    return short, remainder

# Streamlit UI
st.set_page_config(page_title="CSV to WordPress Cards", layout="wide")
st.title("📸 CSV to WordPress Media Cards")

if st.button("🔁 Refresh Template"):
    st.experimental_rerun()

uploaded_file = st.file_uploader("Upload combined CSV file", type=["csv"])
preview_size = st.selectbox("Preview Size", ["Default (3 per row)", "Medium (5 per row)", "Small (7 per row)"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df["Sales Count"] = df.groupby("Media Number")["Media Number"].transform("count")
    df["Total Earnings"] = df.groupby("Media Number")["Your Share"].transform("sum")
    df = df.sort_values("Media Number", ascending=False)

    df["Rating"] = df.apply(lambda row: get_star_rating(row["Sales Count"], row["Total Earnings"]), axis=1)
    df["Keywords"] = df["Description"].apply(extract_keywords)
    df["Short Caption"], df["Remainder Caption"] = zip(*df["Description"].map(truncate_caption))

    # Load Jinja2 template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    template = env.get_template("media_card_template.html")

    # Pagination
    per_row = {"Default (3 per row)": 3, "Medium (5 per row)": 5, "Small (7 per row)": 7}[preview_size]
    rows_per_page = 7
    cards_per_page = per_row * rows_per_page
    total_pages = (len(df) + cards_per_page - 1) // cards_per_page
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)

    start = (page - 1) * cards_per_page
    end = start + cards_per_page
    paginated_df = df.iloc[start:end]

    col_count = 0
    cols = st.columns(per_row)
    for i, (_, row) in enumerate(paginated_df.iterrows()):
        with cols[i % per_row]:
            html = template.render(
                thumbnail=row["Thumbnail"],
                link=row["Media Link"],
                rating=row["Rating"],
                caption=row["Short Caption"],
                remainder=row["Remainder Caption"],
                keywords=row["Keywords"],
            )
            st.components.v1.html(html, height=360)
            col_count += 1

    # HTML export
    all_cards = ""
    for _, row in df.iterrows():
        all_cards += template.render(
            thumbnail=row["Thumbnail"],
            link=row["Media Link"],
            rating=row["Rating"],
            caption=row["Short Caption"],
            remainder=row["Remainder Caption"],
            keywords=row["Keywords"],
        )

    st.download_button("📥 Download HTML Cards", data=all_cards, file_name="media_cards.txt", mime="text/plain")