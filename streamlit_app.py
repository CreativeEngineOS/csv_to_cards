import streamlit as st
import pandas as pd
import nltk

# Download necessary NLTK data (for tokenization in utils)
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)

from utils.keyword_utils import load_keywords, extract_keywords
from utils.caption_utils import truncate_caption
from utils.rating_utils import get_star_rating
from components.card_renderer import render_cards
from components.download import render_download_button

# Page config
st.set_page_config(page_title="📸 CSV to WordPress Media Cards", layout="wide")
st.title("📸 CSV to WordPress Media Cards")

# File upload
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
if not uploaded_file:
    st.stop()

df = pd.read_csv(uploaded_file)

# Ensure required columns exist, with safe defaults
defaults = {
    "Media Number": "",
    "Description": "",
    "Sales Count": 0,
    "Total Earnings": 0,
    "URL": ""
}
for col, default in defaults.items():
    if col not in df.columns:
        st.warning(f"Missing column '{col}', filling with default.")
        df[col] = default

# Truncate captions
df["Short Caption"], df["Remainder Caption"] = zip(
    *df["Description"].map(truncate_caption)
)

# Load and apply keyword extraction
master_keywords = load_keywords()
df["Keywords"] = df["Description"].apply(
    lambda txt: extract_keywords(txt, master_keywords)
)

# Compute star ratings
df["Rating"] = df.apply(
    lambda row: get_star_rating(row["Sales Count"], row["Total Earnings"]),
    axis=1
)

# Deduplicate by Media Number and tally
tally = (
    df.groupby("Media Number")
      .agg({
         "Short Caption": "first",
         "Remainder Caption": "first",
         "Sales Count": "sum",
         "Total Earnings": "sum",
         "URL": "first",
         "Keywords": "first",
         "Rating": "first"
      })
      .reset_index()
      .sort_values("Media Number", ascending=False)
)

# Choose layout
view = st.radio(
    "Preview Size",
    ["Default (3 per row)", "Medium (5 per row)", "Compact (7 per row)"],
    horizontal=True
)
per_row = {
    "Default (3 per row)": 3,
    "Medium (5 per row)": 5,
    "Compact (7 per row)": 7
}[view]

# Render cards and download button
render_cards(tally, per_row)
render_download_button(tally)
