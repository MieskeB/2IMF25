from buddy.buddy import BuDDy

manager = BuDDy(list(range(100)), "buddy/buddy.windows")

north_south = manager.var2bdd(0)
east_west = manager.var2bdd(1)

a = manager.apply_and(north_south, manager.neg(east_west))
b = manager.apply_and(manager.neg(north_south), east_west)

apple = manager.apply_or(a, b)

manager.dump(apple, "ass8/res.dot")
