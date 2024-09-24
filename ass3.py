from z3 import *

T = 250

initial_food_a = 60
initial_food_b = 60
initial_food_c = 60
food_capacity_a = 90
food_capacity_b = 120
food_capacity_c = 90

truck_food_capacity = 150

truck_at_S = [Bool(f"truck_at_S_{t}") for t in range(T)]
truck_at_A = [Bool(f"truck_at_A_{t}") for t in range(T)]
truck_at_B = [Bool(f"truck_at_B_{t}") for t in range(T)]
truck_at_C = [Bool(f"truck_at_C_{t}") for t in range(T)]

last_location = [Int(f"last_location_{t}") for t in range(T)]

food_remaining_A = [Int(f"food_remaining_A_{t}") for t in range(T)]
food_remaining_B = [Int(f"food_remaining_B_{t}") for t in range(T)]
food_remaining_C = [Int(f"food_remaining_C_{t}") for t in range(T)]

drop_A = [Int(f"drop_A_{t}") for t in range(T)]
drop_B = [Int(f"drop_B_{t}") for t in range(T)]
drop_C = [Int(f"drop_C_{t}") for t in range(T)]

truck_load = [Int(f"truck_load_{t}") for t in range(T)]

solver = Solver()

# Initial values
solver.add(truck_at_S[0])
solver.add(truck_load[0] == truck_food_capacity)
solver.add(food_remaining_A[0] == initial_food_a)
solver.add(food_remaining_B[0] == initial_food_b)
solver.add(food_remaining_C[0] == initial_food_c)

# region Truck movement

# Ensure truck can only be in 1 location at the same time
for t in range(T):
    solver.add(Implies(truck_at_S[t], Not(Or(truck_at_A[t], truck_at_B[t], truck_at_C[t]))))
    solver.add(Implies(truck_at_A[t], Not(Or(truck_at_S[t], truck_at_B[t], truck_at_C[t]))))
    solver.add(Implies(truck_at_B[t], Not(Or(truck_at_A[t], truck_at_S[t], truck_at_C[t]))))
    solver.add(Implies(truck_at_C[t], Not(Or(truck_at_A[t], truck_at_B[t], truck_at_S[t]))))

# Truck movements from all different locations
for t in range(1, T):
    cs = []
    if t >= 15:
        cs.append(And(truck_at_A[t - 15], last_location[t - 1] == 1))
        cs.append(And(truck_at_C[t - 15], last_location[t - 1] == 3))
    solver.add(Implies(truck_at_S[t], Or(*cs, False)))

    ca = []
    if t >= 17:
        ca.append(And(truck_at_B[t - 17], last_location[t - 1] == 2))
    if t >= 12:
        ca.append(And(truck_at_C[t - 12], last_location[t - 1] == 3))
    if t >= 15:
        ca.append(And(truck_at_S[t - 15], last_location[t - 1] == 0))
    solver.add(Implies(truck_at_A[t], Or(*ca, False)))

    cb = []
    if t >= 17:
        cb.append(And(truck_at_A[t - 17], last_location[t - 1] == 1))
    if t >= 9:
        cb.append(And(truck_at_C[t - 9], last_location[t - 1] == 3))
    solver.add(Implies(truck_at_B[t], Or(*cb, False)))

    cc = []
    if t >= 15:
        cc.append(And(truck_at_S[t - 15], last_location[t - 1] == 0))
    if t >= 12:
        cc.append(And(truck_at_A[t - 12], last_location[t - 1] == 1))
    if t >= 13:
        cc.append(And(truck_at_B[t - 13], last_location[t - 1] == 2))
    solver.add(Implies(truck_at_C[t], Or(*cc, False)))

# Maintain last location (needed because a truck can decide to drive to multiple locations)
for t in range(T):
    solver.add(If(truck_at_S[t], last_location[t] == 0,
                  If(truck_at_A[t], last_location[t] == 1,
                     If(truck_at_B[t], last_location[t] == 2,
                        If(truck_at_C[t], last_location[t] == 3, last_location[t] == last_location[t - 1])))))

# endregion

# region Truck (un)loading

# Truck boundaries
for t in range(T):
    solver.add(truck_load[t] <= truck_food_capacity)
    solver.add(truck_load[t] >= 0)

# Truck refill and maintain
for t in range(1, T):
    solver.add(Implies(truck_at_S[t], truck_load[t] == truck_food_capacity))
    solver.add(Implies(Not(Or(truck_at_S[t], truck_at_A[t], truck_at_B[t], truck_at_C[t])),
                       truck_load[t] == truck_load[t - 1]))

# Town capacity
for t in range(T):
    solver.add(food_remaining_A[t] <= food_capacity_a)
    solver.add(food_remaining_B[t] <= food_capacity_b)
    solver.add(food_remaining_C[t] <= food_capacity_c)

# Truck delivery
for t in range(1, T):
    solver.add(And(
        drop_A[t] >= 0,
        drop_A[t] <= If(truck_load[t - 1] < food_capacity_a - food_remaining_A[t - 1],
                        truck_load[t - 1],
                        food_capacity_a - food_remaining_A[t]
                        )))
    solver.add(And(
        drop_B[t] >= 0,
        drop_B[t] <= If(truck_load[t - 1] < food_capacity_b - food_remaining_B[t - 1],
                        truck_load[t - 1],
                        food_capacity_b - food_remaining_B[t]
                        )))
    solver.add(And(
        drop_C[t] >= 0,
        drop_C[t] <= If(truck_load[t - 1] < food_capacity_c - food_remaining_C[t - 1],
                        truck_load[t - 1],
                        food_capacity_c - food_remaining_C[t]
                        )))

    solver.add(Implies(truck_at_A[t], And(
        truck_load[t] == truck_load[t - 1] - drop_A[t],
        food_remaining_A[t] == food_remaining_A[t - 1] + drop_A[t] - 1
    )))
    solver.add(Implies(truck_at_B[t], And(
        truck_load[t] == truck_load[t - 1] - drop_B[t],
        food_remaining_B[t] == food_remaining_B[t - 1] + drop_B[t] - 1
    )))
    solver.add(Implies(truck_at_C[t], And(
        truck_load[t] == truck_load[t - 1] - drop_C[t],
        food_remaining_C[t] == food_remaining_C[t - 1] + drop_C[t] - 1
    )))

# endregion

# region City eating

# Making sure that people eat food every time unit
for t in range(1, T):
    solver.add(Implies(Not(truck_at_A[t]), food_remaining_A[t] == food_remaining_A[t - 1] - 1))
    solver.add(Implies(Not(truck_at_B[t]), food_remaining_B[t] == food_remaining_B[t - 1] - 1))
    solver.add(Implies(Not(truck_at_C[t]), food_remaining_C[t] == food_remaining_C[t - 1] - 1))

# Check for starvation
for t in range(T):
    solver.add(food_remaining_A[t] >= 0)
    solver.add(food_remaining_B[t] >= 0)
    solver.add(food_remaining_C[t] >= 0)

# endregion

# region works indefinitely proof

res1 = Int('t1')
res2 = Int('t2')

# Adding bounds to improve efficiency
solver.add(0 <= res1, res1 <= T)
solver.add(0 <= res2, res2 <= T)

exists_condition = False
for t1 in range(T - 1):
    for t2 in range(t1, T):
        same_state = If(And(Or(
            truck_at_S[t1],
            truck_at_A[t1],
            truck_at_B[t1],
            truck_at_C[t1]
        ), Or(
            truck_at_S[t2],
            truck_at_A[t2],
            truck_at_B[t2],
            truck_at_C[t2]
        )), And(
            Or(
                And(truck_at_S[t1], truck_at_S[t2]),
                And(truck_at_A[t1], truck_at_A[t2]),
                And(truck_at_B[t1], truck_at_B[t2]),
                And(truck_at_C[t1], truck_at_C[t2]),
            ),
            truck_load[t1] == truck_load[t2],
            food_remaining_A[t1] == food_remaining_A[t2],
            food_remaining_B[t1] == food_remaining_B[t2],
            food_remaining_C[t1] == food_remaining_C[t2],
            res1 == t1,
            res2 == t2
        ), False)
        exists_condition = Or(exists_condition, same_state)

solver.add(exists_condition)

# endregion

if solver.check() == sat:
    model = solver.model()
    for i in range(T):
        if model[truck_at_S[i]]:
            print(f"{i}: Now at town S")
        if model[truck_at_A[i]]:
            print(f"{i}: Now at town A, dropping off {model[drop_A[i]]}, current load {model[truck_load[i]]}")
        if model[truck_at_B[i]]:
            print(f"{i}: Now at town B, dropping off {model[drop_B[i]]}, current load {model[truck_load[i]]}")
        if model[truck_at_C[i]]:
            print(f"{i}: Now at town C, dropping off {model[drop_C[i]]}, current load {model[truck_load[i]]}")

        if model[truck_at_S[i]] or model[truck_at_A[i]] or model[truck_at_B[i]] or model[truck_at_C[i]]:
            print(f"Amount of food at town A: {model[food_remaining_A[i]]}")
            print(f"Amount of food at town B: {model[food_remaining_B[i]]}")
            print(f"Amount of food at town C: {model[food_remaining_C[i]]}")

        t1 = model[res1].as_long()
        t2 = model[res2].as_long()
        print(f"There is a matching state at {t1} and {t2}")
        print(
            f"{t1}: Food: {model[food_remaining_A[t1]]}, {model[food_remaining_B[t1]]}, {model[food_remaining_C[t1]]}")
        print(
            f"    Truck load: {model[truck_load[t1]]}, last location: {model[last_location[t1]]}")
        print(
            f"{t2}: Food: {model[food_remaining_A[t2]]}, {model[food_remaining_B[t2]]}, {model[food_remaining_C[t2]]}")
        print(
            f"    Truck load: {model[truck_load[t2]]}, last location: {model[last_location[t2]]}")
else:
    print("No solutions found")
