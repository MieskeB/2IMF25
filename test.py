from z3 import *

x = Int('x')
y = Int('y')

solver = Solver()

solver.add(x > 0, y > 0)
solver.add(x + y == 10)

if solver.check() == sat:
      model = solver.model()
      print(f"x = {model[x]}, y = {model[y]}")
else:
      print("No solution found")
