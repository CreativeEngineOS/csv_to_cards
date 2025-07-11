from nltk.tokenize import sent_tokenize

def truncate_caption(text):
    text = str(text).replace("(Photo by Bastiaan Slabbers/NurPhoto)", "").strip()
    sentences = sent_tokenize(text)
    short = " ".join(sentences[:2])
    remainder = " ".join(sentences[2:])
    return short, remainder
