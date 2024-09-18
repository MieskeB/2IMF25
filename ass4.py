from z3 import *

solver = Solver()

a = Int('a')
b = Int('b')

solver.add(a == 1)
solver.add(b == 1)

for i in range(1, 11):
    condition = Bool(f"condition_{i}")

    new_a = Int(f"a_{i}")
    new_b = Int(f"b_{i}")

    solver.add(If(condition,
                  And(
                      new_a == a + 2 * b,
                      new_b == b + 3
                  ),
                  And(
                      new_a == a + i,
                      new_b == b - a,
                  )))

    a = new_a
    b = new_b

for n in range(1, 11):
    solver_c = Solver()
    solver_c.add(solver.assertions())

    solver_c.add(b == 210 + n)

    print("")
    print(f"=-=-=   {n}   =-=-=")

    if solver_c.check() == sat:
        print(f"Program crashes at n = {n}")
        model = solver_c.model()
        print(model)
    else:
        print(f"Program does not crash at n = {n}")

    print(f"=-=-=   {n}   =-=-=")
    print("")
