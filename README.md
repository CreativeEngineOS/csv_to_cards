# CSV to WordPress Media Cards (v7.2.3)

This Streamlit tool converts a CSV of media sales (including thumbnail URLs, captions, media numbers, etc.) into WordPress-friendly HTML "media cards".

## Features

- Upload CSV file with media data.
- Automatically generates:
  - Responsive image cards.
  - Keyword extraction based on master themes.
  - Popularity ratings (★ system).
- Export as `.txt` for easy Gutenberg copy-paste.

## Requirements

- Python 3.9+
- See `requirements.txt`

## Run Locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Keywords

Master keyword themes include:
- U.S. Elections
- Philadelphia
- Politics & Government
- Social Issues
- Human Interest
- Infrastructure
- Weather
- Sports
- Art/Culture/Entertainment
- Economy/Business/Finance