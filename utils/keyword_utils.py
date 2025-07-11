# utils/keyword_utils.py

import json
import re

# Load your master keyword themes
def load_keywords():
    with open("keywords.json") as f:
        return json.load(f)

# A simple tokenizer that splits on word boundaries
_token_re = re.compile(r"\b\w+\b")

def extract_keywords(text, master_keywords, max_keywords=5):
    """
    Extract up to max_keywords theme names whose terms appear in the text.
    Uses a regex tokenizer to avoid any NLTK dependencies.
    """
    if not isinstance(text, str):
        return []
    tokens = [t.lower() for t in _token_re.findall(text)]
    matched = []
    for master, terms in master_keywords.items():
        for term in terms:
            if term.lower() in tokens:
                matched.append(master)
                break
        if len(matched) >= max_keywords:
            break
    return matched
