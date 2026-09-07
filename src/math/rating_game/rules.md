## Two-Year Rating Optimization Game

Suppose you are playing a game in which you may receive rating between 1 and 5 points.

Your daily rating is calculated as a **running average** of all ratings received since your most recent reset.

* Ratings range from 1 to 5, integer number only.
* If the running average on the day is or above 4.8 you will be given 1 grade point.
* If the running average on the day is below 4.8 you will be given 0 grade point.
* You receive at most one rating per day or none.
* The game lasts for exactly **2 years (approximately 730 days)**.

### Objective

Your goal is to maximize the total number of grade points collected during the two-year period.

### Reset Option

At any point, you may choose to **reset your rating**.

When you reset:

* Your current running average is immediately discarded.
* Your rating history will be 0 until the first rating is recieved.
* Future ratings are averaged only from the new starting point.
* **The game clock does not reset.** You still have the same fixed two-year period, so a reset does not give you additional days.

Therefore, you must decide **when, if ever, resetting your rating is worth sacrificing the current rating history** in order to give yourself a better chance of maintaining a rating above 4.8 in the remaining days.

### Optimization Question

What strategy should be used to maximize the number of days during the two-year period for which the running average is greater than 4.8?

In particular, determine:

1. When it is optimal to continue with the current rating.
2. When it is optimal to reset the rating.
3. How the optimal decision changes depending on the current running average, the number of ratings accumulated since the last reset, and the number of days remaining.
4. What mathematical or computational model is best suited to finding the optimal strategy.