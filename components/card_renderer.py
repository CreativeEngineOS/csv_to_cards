import streamlit as st
import jinja2

def render_cards(df, per_row):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    template = env.get_template("media_cards.html")
    total = len(df)
    pages = (total - 1) // (per_row * 7) + 1
    page = st.number_input("Page", min_value=1, max_value=pages, value=1, step=1)
    start = (page - 1) * per_row * 7
    end = start + per_row * 7
    subset = df.iloc[start:end]

    st.markdown(template.render(items=subset.to_dict(orient="records"), per_row=per_row), unsafe_allow_html=True)
    st.write(f"Page {page} of {pages}")

    cols = st.columns(per_row)
    for idx, row in enumerate(subset.itertuples()):
        with cols[idx % per_row]:
            st.markdown(template.render(item=row._asdict()), unsafe_allow_html=True)
    st.write(f"Page {page} of {pages}")
