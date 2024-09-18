import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from z3 import *

canvas_width = 30
canvas_height = 30

distance_cut_from_canvas = 0
perp_cut_line = False

posters = [(4, 5), (4, 6), (5, 21), (6, 9), (6, 8), (6, 10), (6, 11), (7, 12), (8, 9), (10, 11), (10, 20)]
num_posters = len(posters)

solver = Solver()

x = [Int(f'x_{i}') for i in range(num_posters)]
y = [Int(f'y_{i}') for i in range(num_posters)]
rotated = [Bool(f'rotated_{i}') for i in range(num_posters)]

# First the inside of canvas constraint
for i in range(num_posters):
    width, height = posters[i]
    solver.add(If(rotated[i],
                  And(
                      x[i] + height <= canvas_width,
                      y[i] + width <= canvas_height,
                      x[i] >= 0,
                      y[i] >= 0
                  ),
                  And(
                      x[i] + width <= canvas_width,
                      y[i] + height <= canvas_height,
                      x[i] >= 0,
                      y[i] >= 0
                  )))

# Second the overlapping constraint
for i in range(num_posters):
    for j in range(i + 1, num_posters):
        w_i, h_i = posters[i]
        w_j, h_j = posters[j]

        solver.add(
            Or(
                x[i] + If(rotated[i], h_i, w_i) <= x[j],
                x[j] + If(rotated[j], h_j, w_j) <= x[i],
                y[i] + If(rotated[i], w_i, h_i) <= y[j],
                y[j] + If(rotated[j], w_j, h_j) <= y[i]
            ))

# Lastly the cut constraint
cut = Int('c')
cut_over_x = Bool('cut_over_x')
solver.add(And(cut > 0 + distance_cut_from_canvas,
               cut < If(cut_over_x,
                        canvas_height - distance_cut_from_canvas,
                        canvas_width - distance_cut_from_canvas
                        )))
if perp_cut_line:
    cut_perp = Int('cut_perp')
    solver.add(And(cut_perp > 0 + distance_cut_from_canvas,
                   cut_perp < If(Not(cut_over_x),
                                     canvas_height - distance_cut_from_canvas,
                                     canvas_width - distance_cut_from_canvas
                                     )))
for i in range(num_posters):
    width, height = posters[i]
    solver.add(If(cut_over_x,
                  Or(
                      y[i] + If(rotated[i], width, height) <= cut,
                      y[i] >= cut
                  ),
                  Or(
                      x[i] + If(rotated[i], height, width) <= cut,
                      x[i] >= cut
                  )))
    if perp_cut_line:
        solver.add(If(cut_over_x,
                      Or(
                          x[i] + If(rotated[i], height, width) <= cut_perp,
                          x[i] >= cut_perp
                      ),
                      Or(
                          y[i] + If(rotated[i], width, height) <= cut_perp,
                          y[i] >= cut_perp
                      )))

if solver.check() == sat:
    model = solver.model()
    print("Solution:")

    fig, ax = plt.subplots()

    # Set up the canvas
    ax.set_xlim(0, canvas_width)
    ax.set_ylim(0, canvas_height)
    ax.set_aspect('equal')
    plt.gca().invert_yaxis()  # Invert the y-axis to match the coordinate system

    # Plot each poster as a rectangle
    for i in range(num_posters):
        width, height = posters[i]
        x_pos = model[x[i]].as_long()
        y_pos = model[y[i]].as_long()
        is_rotated = model[rotated[i]]

        # If rotated, swap width and height
        if is_rotated:
            width, height = height, width

        print(f"Poster {i + 1} ({width} x {height}): "
              f"x = {x_pos}, y = {y_pos}, rotated = {is_rotated}")

        # Add rectangle (poster) to the plot
        rect = Rectangle((x_pos, y_pos), width, height, linewidth=1, edgecolor='black', facecolor='lightblue')
        ax.add_patch(rect)
        # Label each poster with its number
        ax.text(x_pos + width / 2, y_pos + height / 2, str(i + 1) + "\n(" + str(width) + "x" + str(height) + ")", color='black', ha='center', va='center')

    # Plot the cut line
    cut_pos = model[cut].as_long()
    if model[cut_over_x]:
        print(f"Horizontal cut at y = {cut_pos}")
        ax.axhline(cut_pos, color='red', linestyle='--', label=f'Cut at y = {cut_pos}')
    else:
        print(f"Vertical cut at x = {cut_pos}")
        ax.axvline(cut_pos, color='red', linestyle='--', label=f'Cut at x = {cut_pos}')

    if perp_cut_line:
        cut_perp_pos = model[cut_perp].as_long()
        if not model[cut_over_x]:
            print(f"Horizontal cut at y = {cut_perp_pos}")
            ax.axhline(cut_perp_pos, color='red', linestyle='--', label=f'Cut at y = {cut_perp_pos}')
        else:
            print(f"Vertical cut at x = {cut_perp_pos}")
            ax.axvline(cut_perp_pos, color='red', linestyle='--', label=f'Cut at x = {cut_perp_pos}')


    # Display the plot
    plt.title("Posters")
    plt.legend()
    plt.show()

else:
    print("No solution found")
