def get_star_rating(sales, earnings):
    try:
        sales = float(sales)
        earnings = float(earnings)
    except:
        return "★☆☆☆☆"

    score = 1
    if sales >= 3 or earnings > 200:
        score = 2
    if sales >= 5 or earnings > 500:
        score = 3
    if sales >= 10 or earnings > 1000:
        score = 4
    if sales >= 20 or earnings > 2000:
        score = 5
    return "★" * score + "☆" * (5 - score)
