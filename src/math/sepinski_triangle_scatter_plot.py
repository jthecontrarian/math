import random
import matplotlib.pyplot as plt

# Triangle vertices
vertices = [
    (0, 0),
    (1, 0),
    (0.5, 3**0.5 / 2)
]

# Starting point
x, y = 0.5, 0.25

points_x = []
points_y = []

# Generate fractal
for _ in range(100_000):
    vx, vy = random.choice(vertices)

    # Move halfway toward chosen vertex
    x = (x + vx) / 2
    y = (y + vy) / 2

    points_x.append(x)
    points_y.append(y)

# Render
plt.figure(figsize=(8, 8))
plt.scatter(points_x, points_y, s=0.1)
plt.axis("equal")
plt.axis("off")
plt.show()