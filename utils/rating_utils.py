def get_star_rating(sales, earnings):
    score = sales + earnings / 50
    if score > 15:
        return "★★★★★"
    elif score > 10:
        return "★★★★"
    elif score > 5:
        return "★★★"
    elif score > 2:
        return "★★"
    elif score > 0:
        return "★"
    return ""
