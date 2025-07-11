import streamlit as st
import jinja2

def render_download_button(df):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    template = env.get_template("media_cards.html")
    html = template.render(items=df.to_dict(orient="records"), per_row=3)  # or the current per_row selection
    st.download_button("📥 Download HTML (as .txt)", html, file_name="media_cards.txt", mime="text/plain")
