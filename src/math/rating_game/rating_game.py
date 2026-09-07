import random
import os
import csv
import matplotlib.pyplot as plt

from rating_utils import generate_rating
from strategy import strategy
from strategy_2 import strategy as strategy_2
from strategy_3 import strategy as strategy_3
from strategy_4 import strategy as strategy_4

def plot_running_rating(daily_history):
    days = [row["day"] for row in daily_history]
    ratings = [row["current_rating"] for row in daily_history]

    plt.figure()
    plt.plot(days, ratings)

    plt.xlabel("Day")
    plt.ylabel("Current Rating")
    plt.title("Running Rating")
    plt.ylim(4, 5.02)
    plt.grid(True)
    plt.show()

def save_daily_history_csv(daily_history):
    if not daily_history:
        return

    temp_dir = os.path.join(os.path.dirname(__file__), "temp")
    os.makedirs(temp_dir, exist_ok=True)

    output_file = os.path.join(temp_dir, "result.csv")

    with open(output_file, "w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=daily_history[0].keys()
        )
        writer.writeheader()

        for row in daily_history:
            row = row.copy()
            row["current_rating"] = f"{row['current_rating']:.2f}"
            writer.writerow(row)

def print_simulation_result(result):
    print()
    print("=" * 50)
    print("SIMULATION RESULT")
    print("=" * 50)

    print(f"Score:                {result['score']}")
    print(f"Total days:           {result['total_days']}")

    print(
        f"Days above 4.8:       "
        f"{result['percentage_above_threshold']:.2f}%"
    )

    print(f"Ratings received:     {result['ratings_received']}")
    print(f"Resets:               {result['resets']}")

    print("=" * 50)

def simulate(
        total_days,  
        daily_rating_probability,
        rating_probabilities,
        threshold,
        strategy_function,
        min_ratings=1):

    # Validate arguments
    if total_days < 1:
        raise ValueError(
            f"total_days must be at least 1."
        )
        
    if not 0 <= daily_rating_probability <= 1:
            raise ValueError(
                "daily_rating_probability must be between 0 and 1."
            )
            
    if not isinstance(rating_probabilities, dict) or not rating_probabilities:
        raise ValueError(
            "rating_probabilities must be a non-empty dictionary."
        )

    for probability in rating_probabilities.values():
        if probability < 0 or probability > 1:
            raise ValueError(
                "Rating probabilities must be between 0 and 1."
            )

    if abs(sum(rating_probabilities.values()) - 1.0) > 1e-9:
        raise ValueError(
            f"rating_probabilities must sum to 1.0. "
            f"Current sum: {sum(rating_probabilities.values())}"
        )
    
    if not 0 <= threshold <= 5:
            raise ValueError(
                "threshold must be between 0 and 5."
            )

    # Initial state
    historical_ratings = []
    current_rating = 0.0
    successful_days = 0
    ratings_received = 0
    resets = 0
    daily_history = []

    # Simulation
    for day in range(1, total_days + 1):
        
        # Get decision from participant
        decision = strategy_function(
            historical_ratings=historical_ratings.copy(),
            current_rating=current_rating,
            day=day,
            total_days=total_days,
            threshold=threshold,
            min_ratings=min_ratings
        )

        # Validate decision
        if decision not in (0, 1):
            raise ValueError(
                f"Strategy must return 0 or 1. "
                f"Got {decision} on day {day}."
            )

        # Reset rating if requested
        did_reset = decision
        if did_reset:
            historical_ratings = []
            current_rating = 0.0
            resets += 1

        # Get today's rating
        received_rating = None
        if random.random() < daily_rating_probability:
            received_rating = generate_rating(rating_probabilities)
            historical_ratings.append(received_rating)
            ratings_received += 1

        # Only have a current rating once we have enough ratings
        if len(historical_ratings) >= min_ratings:
            current_rating = (
                sum(historical_ratings)
                / len(historical_ratings)
            )
        else:
            current_rating = 0.0

        # Calculate today's score
        above_threshold = current_rating >= threshold
        if above_threshold:
            successful_days += 1

        # Save today's information
        daily_history.append({
            "day": day,
            "reset": did_reset,
            "rating_received": received_rating,
            "current_rating": current_rating,
            "ratings_since_reset": len(historical_ratings),
            "above_threshold": above_threshold,
        })

    return {
        "score": successful_days,
        "total_days": total_days,
        "percentage_above_threshold": (
            successful_days / total_days * 100
        ),
        "ratings_received": ratings_received,
        "resets": resets,
        "daily_history": daily_history,
    }

if __name__ == "__main__":
    
    # random.seed(1337)
    
    result = simulate(
        total_days = 730,
        daily_rating_probability = 1/7,
        rating_probabilities={
            5: 0.8854166666666666,
            4: 0.08854166666666667,
            3: 0.015625, 
            2: 0.0026041666666666665, 
            1: 0.0078125},
        threshold = 4.8,
        strategy_function=strategy_2,
        min_ratings = 1,
        )

    # print in cli
    print_simulation_result(result)
    
    # save data to CSV
    save_daily_history_csv(result["daily_history"])
    
    # print simulation result
    plot_running_rating(result["daily_history"])