import random
import matplotlib.pyplot as plt
from matplotlib.widgets import Button


def do_flip():
    global total

    flip = random.choice([-1, 1])

    flips.append(flip)
    total += flip

    average = total / len(flips)
    running_average.append(average)

    line.set_data(
        range(1, len(flips) + 1),
        running_average
    )

    current = len(flips)

    # Stretch x-axis
    if current <= 50:
        ax.set_xlim(0, 100)
    else:
        ax.set_xlim(0, current * 2)

    result = "Heads (+1)" if flip == 1 else "Tails (-1)"

    ax.set_title(
        f"Flip #{current}: {result} | Average: {average:.6f}"
    )


def start_fast_mode():
    if holding:
        fast_timer.start()


def fast_flip():
    if holding:
        for _ in range(10):
            do_flip()

        fig.canvas.draw_idle()


def start_holding(event):
    global holding

    # Only react to the coin button
    if event.inaxes != button_ax:
        return

    holding = True

    # Flip immediately
    do_flip()
    fig.canvas.draw_idle()

    # Wait 0.5 seconds before fast mode
    hold_timer.start()


def stop_holding(event):
    global holding

    if event.inaxes != button_ax and not holding:
        return

    holding = False

    hold_timer.stop()
    fast_timer.stop()


if __name__ == "__main__":

    flips = []
    running_average = []
    total = 0

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.subplots_adjust(bottom=0.2)

    line, = ax.plot([], [], linewidth=1)

    ax.set_ylim(-1.1, 1.1)
    ax.set_xlim(0, 100)

    ax.set_xlabel("Number of coin flips")
    ax.set_ylabel("Running average")
    ax.set_title("Coin Flip Experiment")

    ax.axhline(0, linestyle="--", label="Expected average")
    ax.legend()

    # Create button
    button_ax = plt.axes([0.4, 0.05, 0.2, 0.075])
    button = Button(button_ax, "Flip Coin")

    holding = False

    # Timers
    fast_timer = fig.canvas.new_timer(interval=10)
    hold_timer = fig.canvas.new_timer(interval=500)

    hold_timer.add_callback(start_fast_mode)
    fast_timer.add_callback(fast_flip)

    fig.canvas.mpl_connect(
        "button_press_event",
        start_holding
    )

    fig.canvas.mpl_connect(
        "button_release_event",
        stop_holding
    )

    plt.show()