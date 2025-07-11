import streamlit as st
import pandas as pd
import nltk
from utils.keyword_utils import load_keywords, extract_keywords
from utils.caption_utils import truncate_caption
from utils.rating_utils import get_star_rating
from components.card_renderer import render_cards
from components.download import render_download_button

# NLTK setup
nltk.download("punkt")
nltk.download("stopwords")

# App config
st.set_page_config(page_title="📸 CSV to Media Cards", layout="wide")
st.title("📸 CSV to WordPress Media Cards")

# Upload
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if not uploaded_file:
    st.stop()

df = pd.read_csv(uploaded_file)

# Column check
required_cols = {"Media Number", "Description", "Sales Count", "Total Earnings", "URL"}
missing = required_cols - set(df.columns)
if missing:
    st.warning(f"Missing columns: {', '.join(missing)}")
    for col in missing:
        df[col] = 0 if 'Count' in col or 'Earnings' in col else ""

# Process data
df["Short Caption"], df["Remainder Caption"] = zip(*df["Description"].map(truncate_caption))
keywords_data = load_keywords()
df["Keywords"] = df["Description"].apply(lambda x: extract_keywords(x, keywords_data))
df["Rating"] = df.apply(lambda row: get_star_rating(row["Sales Count"], row["Total Earnings"]), axis=1)

# Deduplication
tally = df.groupby("Media Number").agg({
    "Description": "first",
    "Short Caption": "first",
    "Remainder Caption": "first",
    "Sales Count": "sum",
    "Total Earnings": "sum",
    "URL": "first",
    "Keywords": "first",
    "Rating": "first"
}).reset_index().sort_values("Media Number", ascending=False)

# UI: Render Cards + Download
render_cards(tally)
render_download_button(tally)
