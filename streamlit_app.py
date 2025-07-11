import streamlit as st
import pandas as pd
import jinja2
import nltk
import json
import os

from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

# Download necessary NLTK data
nltk.download("punkt")
nltk.download("stopwords")

# App settings
st.set_page_config(page_title="📸 CSV to Media Cards", layout="wide")
st.title("📸 CSV to WordPress Media Cards")

# Upload CSV
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if not uploaded_file:
    st.stop()

# Load CSV
df = pd.read_csv(uploaded_file)

# Show preview of loaded columns
st.write("🧾 Loaded columns:", df.columns.tolist())
st.write(df.head())

# Validate required columns
required_columns = {"Media Number", "Description", "Sales Count", "Total Earnings", "URL"}
missing = required_columns - set(df.columns)
if missing:
    st.warning(f"⚠️ Missing required column(s): {', '.join(missing)}. The app will still run but some features may not work.")
    # Add placeholder columns so rest of app doesn't break
    for col in missing:
        df[col] = 0 if 'Count' in col or 'Earnings' in col else ""

# Truncate caption
def truncate_caption(text):
    text = str(text).replace("(Photo by Bastiaan Slabbers/NurPhoto)", "").strip()
    sentences = sent_tokenize(text)
    short = " ".join(sentences[:2])
    remainder = " ".join(sentences[2:])
    return short, remainder

df["Short Caption"], df["Remainder Caption"] = zip(*df["Description"].map(truncate_caption))

# Keyword extraction
stop_words = set(stopwords.words("english"))
try:
    with open("keywords.json") as f:
        master_keywords = json.load(f)
except Exception as e:
    st.error("Missing or invalid keywords.json file.")
    st.stop()

def extract_keywords(text, max_keywords=5):
    tokens = word_tokenize(str(text).lower())
    tokens = [t for t in tokens if t.isalnum() and t not in stop_words]
    matched = set()
    for master, terms in m
