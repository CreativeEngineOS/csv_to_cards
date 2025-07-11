import streamlit as st
import jinja2

def render_download_button(df):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    template = env.get_template("media_cards.html")
    html = "".join(template.render(item=row) for row in df.to_dict(orient="records"))
    st.download_button("📥 Download HTML (as .txt)", html, file_name="media_cards.txt", mime="text/plain")
