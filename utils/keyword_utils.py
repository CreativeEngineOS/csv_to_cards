import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

stop_words = set(stopwords.words("english"))

def load_keywords():
    with open("keywords.json") as f:
        return json.load(f)

def extract_keywords(text, master_keywords, max_keywords=5):
    if not isinstance(text, str):
        return []
    tokens = word_tokenize(text.lower())
    tokens = [t for t in tokens if t.isalnum() and t not in stop_words]
    matched = []
    for master, terms in master_keywords.items():
        if any(term in tokens for term in terms):
            matched.append(master)
        if len(matched) >= max_keywords:
            break
    return matched
