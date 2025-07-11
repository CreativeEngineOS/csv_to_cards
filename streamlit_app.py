import streamlit as st
import pandas as pd
import jinja2
import json
import re
from nltk.corpus import stopwords

st.set_page_config(page_title="CSV to WordPress Media Cards", layout="wide")

st.title("📸 CSV to WordPress Media Cards")
st.markdown("Upload your CSV and generate WordPress-ready media cards.")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Predefined master keywords
    master_keywords = {
        "U.S. Elections": ["election", "voting", "democracy", "kamala harris", "joe biden"],
        "Philadelphia": ["philadelphia", "philly", "fishtown", "germantown"],
        "Politics & Government": ["senate", "congress", "legislation"],
        "Social Issues": ["protest", "inequality", "racism"],
        "Human Interest": ["community", "people", "local"],
        "Infrastructure": ["bridge", "road", "transport"],
        "Weather": ["storm", "snow", "hurricane"],
        "Sports": ["soccer", "basketball", "football"],
        "Art/Culture/Entertainment": ["museum", "gallery", "concert"],
        "Economy/Business/Finance": ["stock", "finance", "bank"]
    }

    def simple_tokenize(text):
        return re.findall(r"\b\w+\b", str(text).lower())

    def extract_keywords(text, max_keywords=5):
        stop_words = set(stopwords.words("english"))
        tokens = simple_tokenize(text)
        tokens = [t for t in tokens if t not in stop_words]

        matched = set()
        for master, terms in master_keywords.items():
            for term in terms:
                if term.lower() in tokens:
                    matched.add(master)
                    break

        return list(matched)[:max_keywords]

    df["Keywords"] = df["Description"].apply(extract_keywords)

    st.write("### Preview")
    for _, row in df.iterrows():
        st.image(row["Thumbnail"].split("src='")[1].split("'")[0], width=300)
        st.markdown(f"**Caption:** {row['Description']}")
        st.markdown(f"**Keywords:** {', '.join(row['Keywords'])}")
        st.markdown("---")

    # Export button
    def render_card_html(row):
        thumb_url = row["Thumbnail"].split("src='")[1].split("'")[0]
        keywords = ", ".join(row["Keywords"])
        html = f"""
<div style='width:100%; max-width:400px; margin:10px;'>
  <a href='{row["Media Link"]}' target='_blank'>
    <img src='{thumb_url}' style='width:100%; height:auto;'/>
  </a>
  <p>{row["Description"]}</p>
  <p style='text-align:right; font-size:0.8em; color:#666;'>Tags: {keywords}</p>
</div>
"""
        return html

    if st.button("📥 Download HTML as .txt"):
        html_output = "\n".join(df.apply(render_card_html, axis=1))
        st.download_button(
            label="Download HTML Cards as .txt",
            data=html_output,
            file_name="media_cards.txt",
            mime="text/plain"
        )