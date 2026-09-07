import random
import statistics

from rating_game import simulate
from strategy import strategy
from strategy_2 import strategy as strategy_2
from strategy_3 import strategy as strategy_3
from strategy_4 import strategy as strategy_4

def evaluate_strategies(
        strategies,
        n_simulations,
        total_days,
        daily_rating_probability,
        rating_probabilities,
        threshold,
        min_ratings):

    results = {}
    for name in strategies:
        results[name] = []

    for simulation_number in range(n_simulations):

        for name, strategy_function in strategies.items():

            # Reset random generator to the same state
            random.seed(simulation_number)

            result = simulate(
                total_days=total_days,
                daily_rating_probability=daily_rating_probability,
                rating_probabilities=rating_probabilities,
                threshold=threshold,
                strategy_function=strategy_function,
                min_ratings=min_ratings,
            )

            results[name].append(
                result["percentage_above_threshold"]
            )

    return results


def summarize_results(results):

    summaries = {}

    for name, percentages in results.items():

        percentages = sorted(percentages)

        n = len(percentages)

        summaries[name] = {
            "mean": statistics.mean(percentages),
            "median": statistics.median(percentages),
            "stdev": statistics.stdev(percentages),
            "p5": percentages[int(0.05 * n)],
            "p95": percentages[int(0.95 * n)],
        }

    return summaries

def print_results(summaries, n_simulations):
    strategy_width = 15

    print()
    print("=" * 90)
    print("STRATEGY EVALUATION")
    print("=" * 90)
    print(f"Simulations: {n_simulations:,}")
    print()

    print(
        f"{'Strategy':<{strategy_width}}"
        f"{'Mean':>12}"
        f"{'Median':>12}"
        f"{'Std deviation':>16}"
        f"{'5th percentile':>18}"
        f"{'95th percentile':>18}"
    )

    print("-" * 90)

    for name, summary in summaries.items():

        # Truncate long strategy names
        display_name = name
        if len(display_name) > strategy_width:
            display_name = display_name[:strategy_width - 3] + "..."

        print(
            f"{display_name:<{strategy_width}}"
            f"{summary['mean']:>11.2f}%"
            f"{summary['median']:>11.2f}%"
            f"{summary['stdev']:>15.2f}%"
            f"{summary['p5']:>17.2f}%"
            f"{summary['p95']:>17.2f}%"
        )

    print("=" * 90)

if __name__ == "__main__":

    n_simulations = 10000 #10000

    strategies = {
        "Never reset": strategy,
        "Reset if below threshold": strategy_2,
        "finite horizon MDP": strategy_3,
        "finite horizon MDP woth min_ratings": strategy_4,   
    }

    results = evaluate_strategies(
        strategies=strategies,
        n_simulations=n_simulations,
        total_days=730,
        daily_rating_probability=1/7,
        rating_probabilities={
            5: 0.85,
            4: 0.10,
            3: 0.03,
            2: 0.01,
            1: 0.01
        },
        threshold=4.8,
        min_ratings=3,
    )

    summaries = summarize_results(results)

    print_results(summaries, n_simulations)