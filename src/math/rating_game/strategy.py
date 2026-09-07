# Never choose to reset, baseline.

def strategy(
    historical_ratings,
    current_rating,
    day,
    total_days,
    threshold,
    min_ratings,
):
    return 0