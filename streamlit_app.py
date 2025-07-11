import streamlit as st
import pandas as pd
import jinja2
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import json

# Ensure NLTK data
nltk.download("punkt")
nltk.download("stopwords")

st.set_page_config(page_title="CSV to WP Cards", layout="wide")
st.title("📸 CSV to WordPress Media Cards")

# File upload
uploaded = st.file_uploader("Upload CSV", type=["csv"])
if not uploaded:
    st.stop()
df = pd.read_csv(uploaded)

# Column fallback
required = {"Media Number": "", "Description": "", "Sales Count": 0, "Total Earnings": 0, "URL": ""}
for col, default in required.items():
    if col not in df.columns:
        df[col] = default

# Caption truncation
def truncate(text):
    if not isinstance(text, str):
        return "", ""
    text = text.replace("(Photo by Bastiaan Slabbers/NurPhoto)", "").strip()
    s = sent_tokenize(text)
    if len(s) <= 3:
        return text, ""
    return " ".join(s[:3]), " ".join(s[3:])
df["Short"], df["Rest"] = zip(*df["Description"].map(truncate))

# Keywords
with open("keywords.json") as f:
    master = json.load(f)
stop = set(stopwords.words("english"))
def extract(text):
    tokens = [t for t in word_tokenize(text.lower()) if t.isalnum() and t not in stop]
    tags = []
    for k, terms in master.items():
        if any(term in tokens for term in terms):
            tags.append(k)
    return tags[:5]
df["Tags"] = df["Description"].apply(extract)

# Rating
def star(s, e):
    score = s + e/50
    if score>15: return "★★★★★"
    if score>10: return "★★★★"
    if score>5: return "★★★"
    if score>2: return "★★"
    if score>0: return "★"
    return ""
df["Stars"] = df.apply(lambda r: star(r["Sales Count"], r["Total Earnings"]), axis=1)

# Dedupe
t = df.groupby("Media Number").agg({
    "Short": "first", "Rest": "first", "Stars": "first", "URL": "first", "Tags": "first"
}).reset_index()

# Render
per_row = 3
env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
tpl = env.get_template("media_cards.html")
html = "".join([tpl.render(item=r._asdict()) for r in t.itertuples()])

st.download_button("Download HTML (.txt)", html, "cards.txt", "text/plain")
st.components.v1.html(html, height=600, scrolling=True)
