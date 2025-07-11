import streamlit as st
import pandas as pd
import jinja2
from io import StringIO

st.set_page_config(page_title="CSV to WordPress Media Cards", layout="wide")
st.title("📸 CSV to WordPress Media Cards Generator")

uploaded_files = st.file_uploader("Upload one or more CSV files", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    # Combine CSVs
    dfs = [pd.read_csv(f) for f in uploaded_files]
    df = pd.concat(dfs, ignore_index=True)

    # Drop unwanted columns
    drop_cols = ["Fee", "Currency", "Your Share (%)", "Your Share"]
    df = df.drop(columns=[col for col in drop_cols if col in df.columns])

    # Count sales per Media Number
    sales_counts = df["Media Number"].value_counts().to_dict()
    df["Sales Count"] = df["Media Number"].map(sales_counts)
    df = df.sort_values("Sales Count", ascending=False)

    # Load template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    template = env.get_template("card_template.html")

    # Group and render cards
    grouped = df.groupby("Media Number").first().reset_index()
    grouped["card_html"] = grouped.apply(lambda row: template.render(
        thumbnail=row["Thumbnail"],
        media_number=row["Media Number"],
        job_slug=row.get("Filename", ""),
        capture_date=row.get("Original Filename", "")[:8],
        description=row.get("Description", ""),
        sales_count=row["Sales Count"]
    ), axis=1)

    # Display previews
    for _, row in grouped.iterrows():
        st.markdown("---")
        st.markdown(row["card_html"], unsafe_allow_html=True)

    # Export all cards to HTML
    all_cards = "\n\n".join(grouped["card_html"].tolist())
    export_html = f"<html><body>{all_cards}</body></html>"
    st.download_button("⬇️ Download WordPress HTML Export", export_html, file_name="media_cards.html", mime="text/html")