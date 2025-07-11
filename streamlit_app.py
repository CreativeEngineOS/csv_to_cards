import streamlit as st
import pandas as pd
import jinja2
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import os

nltk.download("punkt")
nltk.download("stopwords")

st.set_page_config(page_title="CSV to WordPress Cards", layout="wide")
st.title("📸 CSV to WordPress Media Cards")

# --- Button to refresh/re-run ---
if st.button("🔁 Refresh Template"):
    st.experimental_rerun()

# --- File uploader ---
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
if not uploaded_file:
    st.stop()

df = pd.read_csv(uploaded_file)

# --- Check required columns before processing ---
required_cols = ["Media Number", "Description", "Sales Count", "Total Earnings", "URL", "Thumbnail"]
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    st.error(f"Missing required column(s): {', '.join(missing_cols)}")
    st.stop()

# --- Deduplicate and tally ---
tally = df.groupby("Media Number").agg({
    "Description": "first",
    "Sales Count": "sum",
    "Total Earnings": "sum",
    "URL": "first",
    "Thumbnail": "first"
}).reset_index()

# --- Master keywords ---
master_keywords = {
    "Human Interest": ["f]()
