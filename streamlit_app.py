import streamlit as st
import pandas as pd
import jinja2
from io import StringIO

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

    # Count sales per Media Number
    df["Sales Count"] = df["Media Number"].map(df["Media Number"].value_counts())

    # Optional: Use earnings if column exists
    use_earnings = "Your Share" in df.columns
    if use_earnings:
        df["Total Earnings"] = df.groupby("Media Number")["Your Share"].transform("sum")
        earnings_percentile = df["Total Earnings"].rank(pct=True)
        df["Bonus Star"] = earnings_percentile > 0.95
    else:
        df["Bonus Star"] = False

    # Star logic
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

    # Load template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    template = env.get_template("card_template.html")

    # Group and render cards
    grouped = df.groupby("Media Number").first().reset_index()
    grouped["card_html"] = grouped.apply(lambda row: template.render(
        thumbnail=row["Thumbnail"].replace("width='100'", "style='width:100%; height:auto; display:block;'"),
        description=row.get("Description", ""),
        stars=row["Star Rating"]
    ), axis=1)

    # Display cards
    for _, row in grouped.iterrows():
        st.markdown("---")
        st.markdown(row["card_html"], unsafe_allow_html=True)

    # Export HTML
    all_cards = "\n\n".join(grouped["card_html"].tolist())
    export_html = f"<html><body>{all_cards}</body></html>"
    st.download_button("⬇️ Download WordPress HTML Export", export_html, file_name="media_cards.html", mime="text/html")