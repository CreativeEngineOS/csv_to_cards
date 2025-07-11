from nltk.tokenize import sent_tokenize

def truncate_caption(text):
    """
    Truncate after 3 “sentences” defined by splitting on “. ”,
    stripping the byline, and returning (short, remainder).
    """
    if not isinstance(text, str):
        return "", ""
    # Remove byline
    t = text.replace("(Photo by Bastiaan Slabbers/NurPhoto)", "").strip()
    # Naïve sentence split
    sentences = [s.strip() for s in t.split(". ") if s]
    if len(sentences) <= 3:
        return t, ""
    # Reconstruct
    short = ". ".join(sentences[:3]) + "."
    remainder = ". ".join(sentences[3:]) + ("" if t.endswith(".") else ".")
    return short, remainder
