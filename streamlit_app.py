import streamlit as st
import pandas as pd
import jinja2
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import json
import base64
import os

nltk.download("punkt")
nltk.download("stopwords")

# --- Page Setup ---
st.set_page_config(page_title="CSV to WordPress Media Cards", layout="wide")
st.title("📸 CSV to WordPress Media Cards")

if st.button("🔁 Refresh Template"):
    st.experimental_rerun()

# --- File Upload ---
uploaded_file = st.file_uploader("Upload a combined CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # --- Clean + Prepare Data ---
    df = df.drop(columns=["Fee", "Currency", "Your Share (%)", "Your Share"], errors="ignore")
    df = df.dropna(subset=["Media Number"])

    # --- Aggregate Media Numbers ---
    sales_data = df.groupby("Media Number").agg(
        Sales_Count=("Media Number", "count"),
        Total_Earnings=("Filename", "count")  # Dummy aggregation if not present
    ).rename(columns={"Total_Earnings": "Total Earnings"}).reset_index()
    df = pd.merge(df, sales_data, on="Media Number", how="left")

    # --- Generate Star Rating ---
    def get_star_rating(sales, earnings):
        score = int(sales)
        if earnings > 1000: score += 2
        elif earnings > 500: score += 1
        stars = min(5, max(1, score // 2))
        return "\u2605" * stars

    df["Rating"] = df.apply(lambda row: get_star_rating(row["Sales_Count"], row["Total Earnings"]), axis=1)

    # --- Caption Truncation ---
    def truncate_caption(text):
        if pd.isna(text): return "", ""
        text = str(text).replace("(Photo by Bastiaan Slabbers/NurPhoto)", "").strip()
        sentences = sent_tokenize(text)
        if len(sentences) <= 3:
            return text, ""
        return " ".join(sentences[:3]), " ".join(sentences[3:])

    df["Short Caption"], df["Remainder Caption"] = zip(*df["Description"].map(truncate_caption))

    # --- Keywords ---
    with open("keywords/master_keywords.json") as f:
        master_keywords = json.load(f)
    stop_words = set(stopwords.words("english"))

    def extract_keywords(text, max_keywords=5):
        tokens = word_tokenize(str(text).lower())
        tokens = [t for t in tokens if t.isalnum() and t not in stop_words]
        matched = set()
        for master, terms in master_keywords.items():
            if any(t in tokens for t in terms):
                matched.add(master)
                if len(matched) >= max_keywords:
                    break
        return list(matched)[:max_keywords]

    df["Keywords"] = df["Description"].apply(extract_keywords)

    # --- Sort by Recency (new to old) ---
    df = df[::-1].reset_index(drop=True)

    # --- Load Template ---
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    template = env.get_template("card_template.html")

    # --- Display Settings ---
    view = st.radio("Preview Size", ["Default (3 per row)", "Medium (5 per row)", "Small (Thumbnail Grid)"])
    if view == "Small (Thumbnail Grid)":
        card_width = 15
    elif view == "Medium (5 per row)":
        card_width = 20
    else:
        card_width = 30

    per_page = 21
    total_pages = (len(df) + per_page - 1) // per_page
    page = st.number_input("Page", 1, total_pages, step=1) - 1

    start = page * per_page
    end = start + per_page
    page_df = df.iloc[start:end]

    # --- HTML Block Output ---
    html_blocks = []
    st.markdown("""<div style='display:flex;flex-wrap:wrap;'>""", unsafe_allow_html=True)
    for _, row in page_df.iterrows():
        html = template.render(
            thumbnail=row["Thumbnail"],
            short_caption=row["Short Caption"],
            remainder_caption=row["Remainder Caption"],
            stars=row["Rating"],
            keywords=row["Keywords"],
            card_width=card_width
        )
        html_blocks.append(html)
        st.markdown(html, unsafe_allow_html=True)
    st.markdown("""</div>""", unsafe_allow_html=True)

    # --- HTML Export as .txt ---
    if html_blocks:
        all_html = "\n".join(html_blocks)
        txt = all_html.encode("utf-8")
        b64 = base64.b64encode(txt).decode()
        href = f'<a href="data:text/plain;base64,{b64}" download="media_cards_export.txt">📥 Download HTML block as .txt</a>'
        st.markdown(href, unsafe_allow_html=True)
