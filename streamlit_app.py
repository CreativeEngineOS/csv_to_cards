import streamlit as st
import pandas as pd
import jinja2
import nltk
import nltk.data
from nltk.corpus import stopwords
from nltk.tokenize import TreebankWordTokenizer
import json
import math

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)

st.set_page_config(page_title="📸 CSV to WordPress Cards", layout="wide")
st.title("📸 CSV to WordPress Media Cards")

if st.button("🔁 Refresh Template"):
    st.experimental_rerun()

uploaded_file = st.file_uploader("Upload Combined CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df = df.sort_values(by="Media Number", ascending=False)

    with open("keywords/master_keywords.json") as f:
        master_keywords = json.load(f)

    stop_words = set(stopwords.words("english"))

    def extract_keywords(text, max_keywords=5):
        tokens = TreebankWordTokenizer().tokenize(str(text).lower())
        tokens = [t for t in tokens if t.isalnum() and t not in stop_words]
        matched = set()
        for master, terms in master_keywords.items():
            for term in terms:
                if term.lower() in tokens:
                    matched.add(master)
                    break
        return list(matched)[:max_keywords]

    df["Keywords"] = df["Description"].apply(extract_keywords)

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

    def truncate_caption(text):
        text = text.replace("(Photo by Bastiaan Slabbers/NurPhoto)", "").strip()
        sentences = text.split(". ")
        if len(sentences) <= 2:
            return text, ""
        short = ". ".join(sentences[:2]) + "."
        rest = ". ".join(sentences[2:])
        return short, rest

    df["Short Caption"], df["Remainder Caption"] = zip(*df["Description"].map(truncate_caption))

    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    template = env.get_template("card_template.html")

    view_mode = st.radio("Preview Size", ["Default (3 per row)", "Medium (5 per row)", "Small (6 per row)"])
    per_row = {"Default (3 per row)": 3, "Medium (5 per row)": 5, "Small (6 per row)": 6}[view_mode]
    per_page = 7 * per_row
    total_cards = len(df)
    total_pages = math.ceil(total_cards / per_page)
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)

    start = (page - 1) * per_page
    end = start + per_page

    cards = []
    for _, row in df.iloc[start:end].iterrows():
        card_html = template.render(
            thumbnail=row["Thumbnail"],
            description=row["Description"],
            short_caption=row["Short Caption"],
            remainder_caption=row["Remainder Caption"],
            stars=row["Rating"],
            keywords=row["Keywords"],
            card_width=100 / per_row
        )
        cards.append(card_html)

    st.markdown("<div style='display:flex; flex-wrap:wrap; justify-content:space-between;'>", unsafe_allow_html=True)
    for card in cards:
        st.markdown(card, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<p style='text-align:center;'>Page {page} of {total_pages}</p>", unsafe_allow_html=True)