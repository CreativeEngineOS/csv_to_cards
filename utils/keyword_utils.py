import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

stop_words = set(stopwords.words("english"))

def load_keywords():
    with open("keywords.json") as f:
        return json.load(f)

def extract_keywords(text, master_keywords, max_keywords=5):
    tokens = word_tokenize(str(text).lower())
    tokens = [t for t in tokens if t.isalnum() and t not in stop_words]
    matched = set()
    for master, terms in master_keywords.items():
        if any(t in tokens for t in terms):
            matched.add(master)
        if len(matched) >= max_keywords:
            break
    return ", ".join(sorted(matched))
