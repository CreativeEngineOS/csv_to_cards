import streamlit as st
import pandas as pd
import jinja2
import json
import re
from io import StringIO
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')
nltk.download('stopwords')

st.set_page_config(page_title="CSV to WordPress Cards", layout="wide")
st.title("📸 CSV to WordPress Media Cards")

if st.button("🔁 Refresh Template"):
    st.experimental_rerun()

uploaded_files = st.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    # Combine and clean CSVs
    dfs = [pd.read_csv(f) for f in uploaded_files]
    df = pd.concat(dfs, ignore_index=True)

    drop_cols = ["Fee", "Currency", "Your Share (%)", "Your Share"]
    df = df.drop(columns=[col for col in drop_cols if col in df.columns])

    df["Sales Count"] = df["Media Number"].map(df["Media Number"].value_counts())
    use_earnings = "Your Share" in df.columns
    if use_earnings:
        df["Total Earnings"] = df.groupby("Media Number")["Your Share"].transform("sum")
        earnings_percentile = df["Total Earnings"].rank(pct=True)
        df["Bonus Star"] = earnings_percentile > 0.95
    else:
        df["Bonus Star"] = False

    def sales_to_stars(sales, bonus=False):
        if sales >= 15:
            stars = 4
        elif sales >= 10:
            stars = 3
        elif sales >= 6:
            stars = 2
        elif sales >= 3:
            stars = 1
        else:
            stars = 0
        if bonus:
            stars += 1
        return "★" * stars + "☆" * (5 - stars)

    df["Star Rating"] = df.apply(lambda r: sales_to_stars(r["Sales Count"], r["Bonus Star"]), axis=1)

    # Load keyword mapping
    with open("keywords/master_keywords.json", "r") as f:
        master_keywords = json.load(f)

    stop_words = set(stopwords.words("english"))

    def extract_keywords(text, max_keywords=5):
        tokens = word_tokenize(str(text).lower())
        tokens = [t for t in tokens if t.isalnum() and t not in stop_words]
        matched = set()
        for master, terms in master_keywords.items():
            for term in terms:
                if re.search(r'\b' + re.escape(term.lower()) + r'\b', text.lower()):
                    matched.add(master)
                    break
        return list(matched)[:max_keywords]

    df["Keywords"] = df["Description"].apply(extract_keywords)

    # Load template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    template = env.get_template("card_template.html")

    grouped = df.groupby("Media Number").first().reset_index()
    grouped["card_html"] = grouped.apply(lambda row: template.render(
        thumbnail=row["Thumbnail"].replace("width='100'", "style='width:100%; height:auto; display:block;'"),
        description=row.get("Description", ""),
        stars=row["Star Rating"],
        keywords=row["Keywords"]
    ), axis=1)

    st.markdown("### Preview")
    st.markdown('<div class="wp-block-group is-layout-flex" style="display:flex;flex-wrap:wrap;gap:16px;">', unsafe_allow_html=True)
    for _, row in grouped.iterrows():
        st.markdown(row["card_html"], unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Export HTML
    cards_export = "".join(grouped["card_html"].tolist())
    full_html = f'''
    <html>
    <body>
    <div class="wp-block-group is-layout-flex" style="display:flex;flex-wrap:wrap;gap:16px;">
    {cards_export}
    </div>
    </body>
    </html>
    '''
    st.download_button("⬇️ Download WordPress HTML Export", full_html, file_name="media_cards.html", mime="text/html")