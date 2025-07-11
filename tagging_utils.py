import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

nltk.download("punkt")
nltk.download("stopwords")

stop_words = set(stopwords.words("english"))

with open("keywords.json") as f:
    master_keywords = json.load(f)

def extract_keywords(text, max_keywords=5):
    tokens = word_tokenize(str(text).lower())
    tokens = [t for t in tokens if t.isalnum() and t not in stop_words]
    matched = set()
    for master, terms in master_keywords.items():
        if any(term in tokens for term in terms):
            matched.add(master)
        if len(matched) >= max_keywords:
            break
    return list(matched)

def truncate_caption(text):
    if not isinstance(text, str):
        return "", ""
    text = text.replace("(Photo by Bastiaan Slabbers/NurPhoto)", "").strip()
    sentences = sent_tokenize(text)
    if len(sentences) <= 3:
        return text, ""
    return " ".join(sentences[:3]), " ".join(sentences[3:])

def get_star_rating(sales_count, earnings):
    if sales_count >= 10 or earnings > 500:
        return "★★★★★"
    elif sales_count >= 7:
        return "★★★★"
    elif sales_count >= 4:
        return "★★★"
    elif sales_count >= 2:
        return "★★"
    elif sales_count >= 1:
        return "★"
    return ""
