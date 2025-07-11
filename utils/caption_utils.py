from nltk.tokenize import sent_tokenize

# utils/caption_utils.py

def truncate_caption(text):
    """
    Truncate a caption after 3 “sentences” (split on “. ”), strip the byline,
    and return (short, remainder).
    """
    if not isinstance(text, str) or not text.strip():
        return "", ""
    # Strip the byline
    t = text.replace("(Photo by Bastiaan Slabbers/NurPhoto)", "").strip()
    # Naïve “sentence” split on period+space
    parts = [s.strip() for s in t.split(". ") if s.strip()]
    if len(parts) <= 3:
        return t, ""
    # Rejoin first three, and the rest
    short = ". ".join(parts[:3]) + "."
    rest  = ". ".join(parts[3:]) + ("" if t.endswith(".") else ".")
    return short, rest

