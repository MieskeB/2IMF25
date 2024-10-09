from buddy import BuDDy

var_order = ['x1', 'x2', 'x3']

# please change the library matching your operating system
manager = BuDDy(var_order, "buddy.macos")
x1 = manager.var2bdd('x1')
x2 = manager.var2bdd('x2')
x3 = manager.var2bdd('x3')
nx2 = manager.neg(x2)
x1_a_nx2 = manager.apply_and(x1, nx2)
root = manager.apply('=>', x1_a_nx2, x3)

print(f"Satisfying assignments: {manager.satcount(root)}")