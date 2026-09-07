# Always reset if current rating drops below threshold,
# but only after reaching the minimum number of ratings.

def strategy(
    historical_ratings,
    current_rating,
    day,
    total_days,
    threshold,
    min_ratings,
):
    if len(historical_ratings) < min_ratings:
        return 0

    if current_rating < threshold:
        return 1

    return 0
