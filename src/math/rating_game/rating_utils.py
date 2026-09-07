
import random

def calculate_probabilities(ratings):
    """
    Calculate probability of each rating.
    
    Args: 
        ratings (dict) - rating counts.
    
    Returns: 
        dict - rating probabilities.
    """
    total = sum(ratings.values())

    if total == 0:
        return {rating: 0.0 for rating in ratings}

    probabilities = {}

    for rating, count in ratings.items():
        probabilities[rating] = count / total

    return probabilities

# def generate_ratings(ratings, n, method="fixed_distribution"):
#     """
#     Generate n ratings using a fixed, random, or third distribution.

#     Args:
#         ratings (dict): Mapping of rating -> count.
#         n (int): Number of ratings to generate.
#         method (str): "fixed_distribution", "random", or "third".

#     Returns:
#         list: Generated ratings.

#     Raises:
#         ValueError: If inputs are invalid.
#     """

#     if not isinstance(ratings, dict) or not ratings:
#         raise ValueError("ratings must be a non-empty dictionary")

#     if not isinstance(n, int) or n < 0:
#         raise ValueError("n must be a non-negative integer")

#     if any(count < 0 for count in ratings.values()):
#         raise ValueError("rating counts cannot be negative")

#     if n == 0:
#         return []

#     total = sum(ratings.values())

#     if total == 0:
#         raise ValueError("total rating count must be greater than zero")

#     keys = list(ratings.keys())

#     if method == "fixed_distribution":
#         # Largest-remainder method:
#         # guarantees exactly n results while keeping the distribution
#         # as close as possible to the original distribution.
#         exact_counts = {
#             rating: ratings[rating] * n / total
#             for rating in keys
#         }

#         counts = {
#             rating: int(exact_counts[rating])
#             for rating in keys
#         }

#         remaining = n - sum(counts.values())

#         # Give leftover ratings to the largest fractional remainders.
#         remainders = sorted(
#             keys,
#             key=lambda rating: exact_counts[rating] - counts[rating],
#             reverse=True
#         )

#         for rating in remainders[:remaining]:
#             counts[rating] += 1

#         generated = [
#             rating
#             for rating, count in counts.items()
#             for _ in range(count)
#         ]

#         random.shuffle(generated)
#         return generated

#     elif method == "random_sampling":
#         # Generate according to the relative frequency of each rating.
#         return random.choices(
#             keys,
#             weights=[ratings[rating] for rating in keys],
#             k=n
#         )

#     elif method == "third":
#         # Example third method:
#         # generate one-third of the ratings randomly and
#         # two-thirds using the fixed distribution.
#         random_n = n // 3
#         fixed_n = n - random_n

#         generated = (
#             generate_ratings(ratings, fixed_n, "fixed_distribution")
#             + generate_ratings(ratings, random_n, "random")
#         )

#         random.shuffle(generated)
#         return generated

#     else:
#         raise ValueError(
#             f"Unknown method '{method}'. "
#             "Choose 'fixed_distribution', 'random', or 'third'."
#         )

def generate_rating(ratings):
    """
    Generate one random rating based on the historical
    distribution of ratings.

    Args:
        ratings (dict): Rating probabilities (prob distribution) or rating count

    Returns:
        int: A randomly sampled rating.
    """

    if not isinstance(ratings, dict) or not ratings:
        raise ValueError("ratings must be a non-empty dictionary")

    if any(count < 0 for count in ratings.values()):
        raise ValueError("rating counts cannot be negative")

    total = sum(ratings.values())

    if total == 0:
        raise ValueError("total rating count must be greater than zero")

    return random.choices(
        list(ratings.keys()),
        weights=list(ratings.values()),
        k=1
    )[0]

def generate_ratings(ratings, n):
    """
    Generate n random ratings based on the historical
    rating distribution.

    Args:
        ratings (dict): Rating probabilities (prob distribution) or rating count
        n (int): Number of ratings to generate.

    Returns:
        list: List of generated ratings.
    """

    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be a non-negative integer")

    generated = []

    for _ in range(n):
        generated.append(generate_rating(ratings))

    return generated

def count_ratings(ratings):
    """
    Count the number of occurrences of each rating.

    Args:
        ratings (list): Numerical ratings.

    Returns:
        dict: Rating counts in the order 5, 4, 3, 2, 1.
    """
    counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}

    for rating in ratings:
        if rating in counts:
            counts[rating] += 1

    return counts


def average_rating(ratings):
    """
    Calculate the average rating.
    
    Args: 
        ratings (list) - numerical ratings.
    
    Outputs: 
        float - average rating, or 0 if empty.
    """
    total_ratings = sum(ratings.values())
    
    if total_ratings == 0:
        return 0
        
    total_score = 0
    for rating, count in ratings.items():
        total_score += rating * count
    
    return total_score / total_ratings

def print_probability_chart(probabilities, width=25):
    """
    Print a CLI horizontal bar chart for rating probabilities.

    Args:
        probabilities (dict): Mapping of rating -> probability.
        width (int): Maximum bar width.
    """
    print("\nRating probability")

    for rating in [5, 4, 3, 2, 1]:
        probability = probabilities.get(rating, 0)
        bar_length = round(probability * width)
        bar = "█" * bar_length

        print(
            f"{rating} | "
            f"{bar:<{width}} "
            f"{probability * 100:5.1f}%"
        )

if __name__ == "__main__":
       
    """
    Tests.
    """
    
    # C01
    ratings = {
        5: 340,
        4: 34,
        3: 6,
        2: 1,
        1: 3
    }
    print(calculate_probabilities(ratings))
    print_probability_chart(calculate_probabilities(count_ratings(generate_ratings(ratings, 100))))
    
    # artificial rating E
    ratings = {
            5: 300,
            4: 100,
            3: 300,
            2: 100,
            1: 300
        }
    print_probability_chart(calculate_probabilities(count_ratings(generate_ratings(ratings, 100))))
    
    # artificial rating t
    ratings = {
            5: 0,
            4: 100,
            3: 200,
            2: 100,
            1: 300
        }
    print_probability_chart(calculate_probabilities(count_ratings(generate_ratings(ratings, 100))))
    
    ratings = {
        5: 6,
        4: 1,
        3: 1,
        2: 1,
        1: 1
    }
    assert(calculate_probabilities(ratings) == {5: 0.6, 4: 0.1, 3: 0.1, 2: 0.1, 1: 0.1})
    assert(count_ratings([5,5,2,1]) == {5: 2, 4: 0, 3: 0, 2: 1, 1: 1})
    assert(count_ratings([5,None,5,2,1]) == {5: 2, 4: 0, 3: 0, 2: 1, 1: 1})
   
    ratings = {
        5: 340,
        4: 34,
        3: 6,
        2: 1,
        1: 3
    }
    assert(average_rating(ratings) == 4.841145833333333)
    ratings = {
        5: 5,
        4: 0,
        3: 0,
        2: 0,
        1: 0
    }
    assert(average_rating(ratings) == 5.00)
    ratings = {
        5: 0,
        4: 0,
        3: 0,
        2: 0,
        1: 7
    }
    assert(average_rating(ratings) == 1.00)
    ratings = {
        5: 1,
        4: 1,
        3: 1,
        2: 1,
        1: 1
    }
    assert(average_rating(ratings) == 3.00)
    
    print('rating_game.py finished.')