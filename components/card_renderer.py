import streamlit as st

def render_cards(df):
    per_row = 3
    rows_per_page = 7
    cards_per_page = rows_per_page * per_row
    total_pages = -(-len(df) // cards_per_page)
    page = st.number_input("Page", 1, total_pages, 1)

    start = (page - 1) * cards_per_page
    end = start + cards_per_page
    cols = st.columns(per_row)

    for idx, row in enumerate(df.iloc[start:end].itertuples()):
        with cols[idx % per_row]:
            st.image(row.URL, use_column_width=True)
            st.markdown(f"**{row.Short_Caption}**")
            if row.Remainder_Caption:
                with st.expander("Read more"):
                    st.markdown(row.Remainder_Caption)
            if row.Rating:
                st.markdown(f"⭐️ {row.Rating}", unsafe_allow_html=True)
            if row.Keywords:
                tags = [
                    f'<a href="/tag/{kw.replace(" ", "-").lower()}" target="_blank">{kw.upper()}</a>'
                    for kw in row.Keywords.split(", ")[:5]
                ]
                st.markdown(f"<div style='text-align: right; font-size: 0.9em;'>{', '.join(tags)}</div>", unsafe_allow_html=True)

    st.markdown(f"Page {page} of {total_pages}")
