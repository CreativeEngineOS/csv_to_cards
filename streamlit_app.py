import streamlit as st
import pandas as pd
import jinja2
from tagging_utils import extract_keywords, truncate_caption, get_star_rating

st.set_page_config(page_title="CSV to WordPress Cards", layout="wide")
st.title("📸 CSV to WordPress Media Cards")

if st.button("🔁 Refresh Template"):
    st.experimental_rerun()

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
if not uploaded_file:
    st.stop()

df = pd.read_csv(uploaded_file)

required_cols = ["Media Number", "Description", "Sales Count", "Total Earnings", "URL", "Thumbnail"]
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    st.error(f"Missing required column(s): {', '.join(missing_cols)}")
    st.stop()

tally = df.groupby("Media Number").agg({
    "Description": "first",
    "Sales Count": "sum",
    "Total Earnings": "sum",
    "URL": "first",
    "Thumbnail": "first"
}).reset_index()

tally["Keywords"] = tally["Description"].apply(extract_keywords)
tally["Short Caption"], tally["Remainder Caption"] = zip(*tally["Description"].map(truncate_caption))
tally["Rating"] = tally.apply(lambda row: get_star_rating(row["Sales Count"], row["Total Earnings"]), axis=1)
tally = tally.sort_values(by="Media Number", ascending=False).reset_index(drop=True)

env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
template = env.get_template("media_card_template.html")

view = st.radio("Preview Size", ["Default (3 per row)", "Medium (5 per row)", "Small (fit max)"], horizontal=True)
per_row = {"Default (3 per row)": 3, "Medium (5 per row)": 5, "Small (fit max)": 7}[view]
per_page = per_row * 7

total = len(tally)
pages = (total - 1) // per_page + 1
page = st.number_input("Page", min_value=1, max_value=pages, value=1, step=1)

start = (page - 1) * per_page
end = start + per_page
visible_df = tally.iloc[start:end]

all_cards_html = ""
st.markdown("<div class='card-grid'>", unsafe_allow_html=True)
for _, row in visible_df.iterrows():
    html = template.render(
        image_url=row["Thumbnail"],
        caption=row["Short Caption"],
        full_caption=row["Remainder Caption"],
        stars=row["Rating"],
        tags=", ".join(row["Keywords"]),
        permalink=row["URL"]
    )
    all_cards_html += html
    st.markdown(html, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.write(f"Page {page} of {pages}")
st.download_button(
    label="💾 Download HTML Block (as .txt)",
    data=all_cards_html,
    file_name="media_cards.txt",
    mime="text/plain"
)
