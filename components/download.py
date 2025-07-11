import streamlit as st
import jinja2

def render_download_button(df):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    template = env.get_template("media_cards.html")
    html = template.render(items=df.to_dict(orient="records"))
    st.download_button("📥 Download HTML Output", html, file_name="cards_output.txt", mime="text/plain")
