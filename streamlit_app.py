import streamlit as st
import pandas as pd
import nltk
import re

# Download necessary NLTK data
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)

from utils.keyword_utils import load_keywords, extract_keywords
from utils.caption_utils import truncate_caption
from utils.rating_utils import get_star_rating
from components.card_renderer import render_cards
from components.download import render_download_button

st.set_page_config(page_title="📸 CSV to WordPress Media Cards", layout="wide")
st.title("📸 CSV to WordPress Media Cards")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
if not uploaded_file:
    st.stop()

df = pd.read_csv(uploaded_file)

# Normalize and fill columns
df = df.rename(columns={
    "Media Link":     "URL",
    "Your Share":     "Total Earnings",
    "Your Share (%)": "Sales Count"
})

required_columns = {
    "Media Number":    "",
    "Description":     "",
    "Sales Count":     0,
    "Total Earnings":  0,
    "URL":             "",
    "Thumbnail":       ""
}
for col, default in required_columns.items():
    if col not in df.columns:
        df[col] = default
    df[col] = df[col].fillna(default)

def extract_img_src(html):
    if isinstance(html, str):
        match = re.search(r'src=[\'"]([^\'"]+)', html)
        return match.group(1) if match else ""
    return ""

df["Image"] = df["Thumbnail"].apply(extract_img_src)
df["Short Caption"], df["Remainder Caption"] = zip(*df["Description"].map(truncate_caption))
master_keywords = load_keywords()
df["Keywords"] = df["Description"].apply(lambda txt: extract_keywords(txt, master_keywords))
df["Media Number"] = df["Media Number"].astype(str)

# Dedup and tally
tally = (
    df.groupby("Media Number")
      .agg({
         "Short Caption": "first",
         "Remainder Caption": "first",
         "Sales Count": "sum",
         "Total Earnings": "sum",
         "Image": "first",
         "URL": "first",
         "Keywords": "first"
      })
      .reset_index()
      .sort_values("Media Number", ascending=False)
)

# Compute rating AFTER dedup
tally["Rating"] = tally.apply(lambda row: get_star_rating(row["Sales Count"], row["Total Earnings"]), axis=1)

view = st.radio("Preview Size", ["Default (3 per row)", "Medium (5 per row)", "Compact (7 per row)"], horizontal=True)
per_row = {"Default (3 per row)": 3, "Medium (5 per row)": 5, "Compact (7 per row)": 7}[view]

render_cards(tally, per_row)
render_download_button(tally)
