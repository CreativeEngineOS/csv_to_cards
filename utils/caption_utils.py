from nltk.tokenize import sent_tokenize

def truncate_caption(text):
    if not isinstance(text, str):
        return "", ""
    text = text.replace("(Photo by Bastiaan Slabbers/NurPhoto)", "").strip()
    sentences = sent_tokenize(text)
    if not sentences:
        return "", ""
    if len(sentences) <= 3:
        return text, ""
    return " ".join(sentences[:3]), " ".join(sentences[3:])
