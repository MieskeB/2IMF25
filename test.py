# from z3 import *
#
# x = Int('x')
# y = Int('y')
#
# solver = Solver()
#
# solver.add(x > 0, y > 0)
# solver.add(x + y == 10)
#
# if solver.check() == sat:
#       model = solver.model()
#       print(f"x = {model[x]}, y = {model[y]}")
# else:
#       print("No solution found")


# from oxidd.bdd import BDDManager
#
# manager = BDDManager(100_000_000, 100_000_000, 3)
#
# x1 = manager.new_var()
# x2 = manager.new_var()
# x3 = manager.new_var()
#
# bdd_f = (x1 & ~x2) | x3
#
# for x1_val in [False, True]:
#     for x2_val in [False, True]:
#         for x3_val in [False, True]:
#             result = bdd_f.eval([(x1, x1_val), (x2, x2_val), (x3, x3_val)])
#             print(f"x1: {x1_val}, x2: {x2_val}, x3: {x3_val} => f: {result}")


from buddy.buddy import BuDDy

var_order = ['x1', 'x2', 'x3']
manager = BuDDy(var_order, "buddy/buddy.windows")
x1 = manager.var2bdd('x1')
x2 = manager.var2bdd('x2')
x3 = manager.var2bdd('x3')
nx2 = manager.neg(x2)
x1_a_nx2 = manager.apply_and(x1, nx2)
root = manager.apply('=>', x1_a_nx2, x3)

print(f"Satisfying assignments: {manager.satcount(root)}")
