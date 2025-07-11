# 📸 CSV to WordPress Media Cards

This tool transforms a sales-based CSV report of visual media into clean, responsive HTML "media cards" designed to integrate seamlessly with **WordPress Gutenberg** blocks.

## 🚀 Features

- ✅ Combines and visualizes media metadata from CSV reports
- 📸 Responsive image cards with thumbnails, captions, and tag-based filtering
- ⭐ Popularity-based star rating system
- 🏷️ Automatic keyword extraction from captions using smart grouping logic
- 📤 Export HTML output (as `.txt`) for direct copy-paste into WordPress
- 🔎 Pagination, layout modes, and tag navigation

## 📂 Folder Structure

```bash
csv_to_cards/
├── streamlit_app.py          # Main app file (Streamlit)
├── templates/
│   └── media_card_template.html   # Jinja2 template for media cards
├── master_keywords.json      # Grouped keyword logic for tagging
├── requirements.txt          # Python dependencies
└── sample_input/
    └── sales_data.csv        # Example CSV input file
