import os
import pickle
import time


# ============================================================
# MDP PARAMETERS
# ============================================================

DAILY_RATING_PROBABILITY = 1 / 7

RATING_PROBABILITIES = {
    5: 0.85,
    4: 0.10,
    3: 0.03,
    2: 0.01,
    1: 0.01,
}


# ============================================================
# POLICY CACHE
# ============================================================

_POLICY_CACHE = {}

_TEMP_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "temp",
)


# ============================================================
# POLICY FILE MANAGEMENT
# ============================================================

def _policy_filename(total_days, threshold, min_ratings):
    """
    Return the path used to store a policy.

    Example:
        temp/policy_days_730_threshold_4_8_minratings_5.pkl
    """

    threshold_string = str(threshold).replace(".", "_")

    return os.path.join(
        _TEMP_DIR,
        (
            f"policy_days_{total_days}"
            f"_threshold_{threshold_string}"
            f"_minratings_{min_ratings}.pkl"
        ),
    )


def _policy_config(total_days, threshold, min_ratings):
    """
    Configuration stored alongside the policy.

    This prevents accidentally loading a policy generated with
    different MDP parameters.
    """

    return {
        "version": 3,
        "total_days": total_days,
        "threshold": threshold,
        "min_ratings": min_ratings,
        "daily_rating_probability": DAILY_RATING_PROBABILITY,
        "rating_probabilities": RATING_PROBABILITIES.copy(),
    }


def save_policy(policy, total_days, threshold, min_ratings):
    """
    Save a generated policy to ./temp.
    """

    os.makedirs(_TEMP_DIR, exist_ok=True)

    filename = _policy_filename(
        total_days,
        threshold,
        min_ratings,
    )

    data = {
        "config": _policy_config(
            total_days,
            threshold,
            min_ratings,
        ),
        "policy": policy,
    }

    with open(filename, "wb") as file:
        pickle.dump(
            data,
            file,
            protocol=pickle.HIGHEST_PROTOCOL,
        )

    print(f"Policy saved to: {filename}")


def load_policy(total_days, threshold, min_ratings):
    """
    Load a previously generated policy.

    Returns None if:
      - the file doesn't exist
      - the file is invalid
      - its configuration doesn't match
    """

    filename = _policy_filename(
        total_days,
        threshold,
        min_ratings,
    )

    if not os.path.exists(filename):
        return None

    try:
        with open(filename, "rb") as file:
            data = pickle.load(file)

        expected_config = _policy_config(
            total_days,
            threshold,
            min_ratings,
        )

        if data.get("config") != expected_config:
            print(
                "Saved policy configuration does not match "
                "the current MDP configuration."
            )
            return None

        policy = data["policy"]

        print(f"Loaded policy from: {filename}")
        print(f"Policy states: {len(policy):,}")

        return policy

    except (
        OSError,
        pickle.PickleError,
        EOFError,
        KeyError,
        TypeError,
    ):
        print("Could not load saved policy.")
        return None


# ============================================================
# STATE FUNCTIONS
# ============================================================

def is_success(
    count,
    deficit,
    threshold,
    min_ratings,
):
    """
    Determine whether the current rating is successful.

    A successful day requires BOTH:

        1. At least min_ratings ratings exist.
        2. The average rating is at or above threshold.

    Rating average is represented as:

        average = (5 * count - deficit) / count

    where:

        deficit = sum(5 - rating)
    """

    # Not enough ratings to receive a rating yet.
    if count < min_ratings:
        return False

    return (
        (5 * count - deficit) / count
        >= threshold
    )


def can_reach_success(
    count,
    deficit,
    threshold,
    min_ratings,
    remaining_days,
):
    """
    EXACT state-pruning test.

    We ask:

        "Could this state possibly reach the threshold
         during the remaining days?"

    Two conditions must be satisfied:

        1. We must be able to obtain at least min_ratings.
        2. The average must be able to reach threshold.

    For the best possible outcome, assume every remaining
    rating is 5 stars.
    """

    # --------------------------------------------------------
    # Already successful.
    # --------------------------------------------------------

    if is_success(
        count,
        deficit,
        threshold,
        min_ratings,
    ):
        return True

    # --------------------------------------------------------
    # We need at least min_ratings ratings.
    #
    # Every remaining day can produce at most one rating.
    # --------------------------------------------------------

    maximum_possible_count = (
        count + remaining_days
    )

    if maximum_possible_count < min_ratings:
        return False

    # --------------------------------------------------------
    # Best possible outcome:
    #
    # Every remaining rating is 5 stars.
    # --------------------------------------------------------

    best_count = maximum_possible_count

    best_average = (
        5 * best_count - deficit
    ) / best_count

    return best_average >= threshold


# ============================================================
# BELLMAN VALUE
# ============================================================

def action_value(
    count,
    deficit,
    threshold,
    min_ratings,
    V_next,
):
    """
    Expected value of KEEPING the current rating history.

    The simulator works in this order:

        1. strategy chooses KEEP/RESET
        2. today's rating may arrive
        3. today's rating is evaluated
        4. score for today is awarded

    V_next contains the optimal future value after today.
    """

    value = 0.0

    # --------------------------------------------------------
    # Case 1:
    # No rating arrives today.
    # --------------------------------------------------------

    probability_no_rating = (
        1 - DAILY_RATING_PROBABILITY
    )

    new_reward = int(
        is_success(
            count,
            deficit,
            threshold,
            min_ratings,
        )
    )

    value += (
        probability_no_rating
        * (
            new_reward
            + V_next.get(
                (count, deficit),
                0.0,
            )
        )
    )

    # --------------------------------------------------------
    # Case 2:
    # A rating arrives today.
    # --------------------------------------------------------

    for rating, probability in RATING_PROBABILITIES.items():

        new_count = count + 1

        new_deficit = (
            deficit + (5 - rating)
        )

        new_reward = int(
            is_success(
                new_count,
                new_deficit,
                threshold,
                min_ratings,
            )
        )

        value += (
            DAILY_RATING_PROBABILITY
            * probability
            * (
                new_reward
                + V_next.get(
                    (
                        new_count,
                        new_deficit,
                    ),
                    0.0,
                )
            )
        )

    return value


# ============================================================
# BUILD OPTIMAL POLICY
# ============================================================

def build_optimal_policy(
    total_days,
    threshold,
    min_ratings,
):
    """
    Build the optimal finite-horizon policy using backward
    dynamic programming.

    State:

        (day, count, deficit)

    Action:

        0 = KEEP
        1 = RESET

    The policy maximizes the expected number of successful
    days over the entire finite horizon.

    A successful day requires:

        count >= min_ratings

    AND

        average >= threshold
    """

    start_time = time.time()

    print()
    print("=" * 60)
    print("BUILDING OPTIMAL MDP POLICY")
    print("=" * 60)
    print(f"Days:         {total_days}")
    print(f"Threshold:    {threshold}")
    print(f"Min ratings:  {min_ratings}")
    print()

    # --------------------------------------------------------
    # V_next represents the optimal future value AFTER the
    # current day.
    #
    # With zero days remaining, there is no future reward.
    # --------------------------------------------------------

    V_next = {}
    policy = {}

    # --------------------------------------------------------
    # The only state possible immediately after a reset is:
    #
    #     count = 0
    #     deficit = 0
    #
    # --------------------------------------------------------

    states = {(0, 0)}

    interval = max(
        1,
        total_days // 20,
    )

    for day in range(total_days, 0, -1):

        V_current = {}

        # Number of days AFTER today's decision.
        remaining_days = day - 1

        # ----------------------------------------------------
        # RESET VALUE
        #
        # Reset happens BEFORE today's rating.
        #
        # Therefore the post-reset state entering today's
        # random transition is (0, 0).
        # ----------------------------------------------------

        reset_value = action_value(
            0,
            0,
            threshold,
            min_ratings,
            V_next,
        )

        # ----------------------------------------------------
        # Evaluate every reachable state.
        # ----------------------------------------------------

        for count, deficit in states:

            keep_value = action_value(
                count,
                deficit,
                threshold,
                min_ratings,
                V_next,
            )

            if reset_value > keep_value:
                action = 1
                best_value = reset_value
            else:
                action = 0
                best_value = keep_value

            policy[
                (
                    day,
                    count,
                    deficit,
                )
            ] = action

            V_current[
                (
                    count,
                    deficit,
                )
            ] = best_value

        V_next = V_current

        # ----------------------------------------------------
        # Generate states that can exist on the next day.
        #
        # A state is retained if it can still possibly achieve
        # the threshold AND obtain enough ratings.
        # ----------------------------------------------------

        next_states = {(0, 0)}

        for count, deficit in states:

            # ------------------------------------------------
            # No rating today.
            # ------------------------------------------------

            if can_reach_success(
                count,
                deficit,
                threshold,
                min_ratings,
                remaining_days,
            ):
                next_states.add(
                    (
                        count,
                        deficit,
                    )
                )

            # ------------------------------------------------
            # Rating arrives today.
            # ------------------------------------------------

            for rating in RATING_PROBABILITIES:

                new_count = count + 1

                new_deficit = (
                    deficit + (5 - rating)
                )

                if can_reach_success(
                    new_count,
                    new_deficit,
                    threshold,
                    min_ratings,
                    remaining_days,
                ):
                    next_states.add(
                        (
                            new_count,
                            new_deficit,
                        )
                    )

        states = next_states

        # ----------------------------------------------------
        # Progress output.
        # ----------------------------------------------------

        if (
            day == total_days
            or day == 1
            or day % interval == 0
        ):
            elapsed = time.time() - start_time

            print(
                f"Day {day:4d}/{total_days} | "
                f"states: {len(V_current):,} | "
                f"next: {len(states):,} | "
                f"time: {elapsed:.1f}s"
            )

    elapsed = time.time() - start_time

    print()
    print("=" * 60)
    print("MDP COMPLETE")
    print("=" * 60)
    print(f"Policy states: {len(policy):,}")
    print(f"Total time:    {elapsed:.2f}s")
    print("=" * 60)
    print()

    return policy


# ============================================================
# GET OPTIMAL ACTION
# ============================================================

def get_optimal_action(
    historical_ratings,
    current_rating,
    day,
    total_days,
    threshold,
    min_ratings,
):
    """
    Return the optimal action for the current simulator state.

    Action:

        0 = KEEP
        1 = RESET

    current_rating is intentionally unused because it is fully
    determined by historical_ratings.

    The actual MDP state is represented by:

        count
        deficit
    """

    key = (
        total_days,
        threshold,
        min_ratings,
    )

    # --------------------------------------------------------
    # Load/build policy only once per configuration.
    # --------------------------------------------------------

    if key not in _POLICY_CACHE:

        print("Checking for saved MDP policy...")

        policy = load_policy(
            total_days=total_days,
            threshold=threshold,
            min_ratings=min_ratings,
        )

        if policy is None:

            print("No valid saved policy found.")
            print("Calculating optimal MDP policy...")

            policy = build_optimal_policy(
                total_days=total_days,
                threshold=threshold,
                min_ratings=min_ratings,
            )

            save_policy(
                policy=policy,
                total_days=total_days,
                threshold=threshold,
                min_ratings=min_ratings,
            )

            print("Optimal policy ready.")

        else:
            print("Optimal policy loaded.")

        _POLICY_CACHE[key] = policy

    # --------------------------------------------------------
    # Convert historical ratings into the sufficient state.
    # --------------------------------------------------------

    count = len(historical_ratings)

    deficit = sum(
        5 - rating
        for rating in historical_ratings
    )

    state = (
        day,
        count,
        deficit,
    )

    # --------------------------------------------------------
    # A state that was pruned cannot possibly recover through
    # KEEP. Therefore RESET is the safe optimal action.
    # --------------------------------------------------------

    return _POLICY_CACHE[key].get(
        state,
        1,
    )


# ============================================================
# STRATEGY FUNCTION USED BY rating_game.py
# ============================================================

def strategy(
    historical_ratings,
    current_rating,
    day,
    total_days,
    threshold,
    min_ratings,
):
    """
    Strategy interface expected by rating_game.simulate().

    Returns:

        0 = KEEP
        1 = RESET
    """

    return get_optimal_action(
        historical_ratings=historical_ratings,
        current_rating=current_rating,
        day=day,
        total_days=total_days,
        threshold=threshold,
        min_ratings=min_ratings,
    )