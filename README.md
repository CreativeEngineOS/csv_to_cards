# CSV to WordPress Media Cards (v7.4.1)

Modular Streamlit app generating responsive HTML media cards from CSV inputs.

## Structure
- `streamlit_app.py`: Main application.
- `utils/`: Caption truncation, keyword extraction, rating logic.
- `components/`: Card rendering and download button.
- `templates/media_cards.html`: Jinja2 template for each card.
- `keywords.json`: Master keyword themes.
- `requirements.txt`: Dependencies.

## Run
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
