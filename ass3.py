from z3 import *
import matplotlib.pyplot as plt

T = 339

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

drop = [Int(f"drop_{t}") for t in range(T)]

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
    solver.add(Implies(truck_at_A[t], And(
        drop[t] >= 0,
        drop[t] <= If(truck_load[t - 1] < food_capacity_a - food_remaining_A[t - 1],
                      truck_load[t - 1],
                      food_capacity_a - food_remaining_A[t - 1]),
        truck_load[t] == truck_load[t - 1] - drop[t],
        food_remaining_A[t] == food_remaining_A[t - 1] + drop[t] - 1
    )))
    solver.add(Implies(truck_at_B[t], And(
        drop[t] >= 0,
        drop[t] <= If(truck_load[t - 1] < food_capacity_b - food_remaining_B[t - 1],
                      truck_load[t - 1],
                      food_capacity_b - food_remaining_B[t - 1]),
        truck_load[t] == truck_load[t - 1] - drop[t],
        food_remaining_B[t] == food_remaining_B[t - 1] + drop[t] - 1
    )))
    solver.add(Implies(truck_at_C[t], And(
        drop[t] >= 0,
        drop[t] <= If(truck_load[t - 1] < food_capacity_c - food_remaining_C[t - 1],
                      truck_load[t - 1],
                      food_capacity_c - food_remaining_C[t - 1]),
        truck_load[t] == truck_load[t - 1] - drop[t],
        food_remaining_C[t] == food_remaining_C[t - 1] + drop[t] - 1
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

print("=-=-=")
print("Testing if there can be a solution found")
res = solver.check()
if res == sat:
    print("There is at least 1 solution possible")

    model = solver.model()

    for i in range(T):
        if model[truck_at_S[i]]:
            print(f"{i}: Now at town S")
        if model[truck_at_A[i]]:
            print(f"{i}: Now at town A, dropping off {model[drop[i]]}, current load {model[truck_load[i]]}")
        if model[truck_at_B[i]]:
            print(f"{i}: Now at town B, dropping off {model[drop[i]]}, current load {model[truck_load[i]]}")
        if model[truck_at_C[i]]:
            print(f"{i}: Now at town C, dropping off {model[drop[i]]}, current load {model[truck_load[i]]}")

        if model[truck_at_S[i]] or model[truck_at_A[i]] or model[truck_at_B[i]] or model[truck_at_C[i]]:
            print(f"Amount of food at town A: {model[food_remaining_A[i]]}")
            print(f"Amount of food at town B: {model[food_remaining_B[i]]}")
            print(f"Amount of food at town C: {model[food_remaining_C[i]]}")
else:
    print("No solutions possible")
    exit(-1)

print("=-=-=")
print("Now testing if there is a loop possible")
for t in range(T):
    solver.push()

    clauses = BoolVal(False)

    succ = Int("Success_var")
    solver.add(succ >= 1)
    solver.add(succ <= T)

    for t1 in range(t - 1):
        clauses = Or(
            clauses,
            If(truck_at_S[t1], And(
                food_remaining_A[t] == food_remaining_A[t1],
                food_remaining_B[t] == food_remaining_B[t1],
                food_remaining_C[t] == food_remaining_C[t1],
                succ == t1
            ), BoolVal(False)))

    solver.add(If(truck_at_S[t], clauses, False))

    if t % 20 == 0:
        print(f"Now at t = {t}")

    if solver.check() == sat:
        model = solver.model()
        success = model[succ].as_long()
        print(f"Found repeating state at time {t} and {success}")
        print(
            f"Food at {success}: A: {model[food_remaining_A[success]]}, B: {model[food_remaining_B[success]]}, C: {model[food_remaining_C[success]]}")
        print(
            f"Food at {t}: A: {model[food_remaining_A[t]]}, B: {model[food_remaining_B[t]]}, C: {model[food_remaining_C[t]]}")

        # region Visualizations

        food_A = [model[food_remaining_A[i]].as_long() for i in range(T)]
        food_B = [model[food_remaining_B[i]].as_long() for i in range(T)]
        food_C = [model[food_remaining_C[i]].as_long() for i in range(T)]
        truck_load_values = [model[truck_load[i]].as_long() for i in range(T)]
        food_A_succ = model[food_remaining_A[success]].as_long()
        food_B_succ = model[food_remaining_B[success]].as_long()
        food_C_succ = model[food_remaining_C[success]].as_long()
        truck_load_succ = model[truck_load[success]].as_long()

        fig, axs = plt.subplots(2, 2, figsize=(12, 10))

        axs[0, 0].plot(range(T), food_A, label='Food at A', marker='_', color='green')
        axs[0, 0].axvline(x=success, color='b', linestyle='--', label=f't1 = {success}')
        axs[0, 0].axvline(x=t, color='b', linestyle='--', label=f't2 = {t}')
        axs[0, 0].axhline(y=food_A_succ, color='black', linestyle=':', label=f'Equal height = {food_A_succ}')
        axs[0, 0].scatter(success, food_A_succ, color='red', zorder=5)
        axs[0, 0].scatter(t, food_A_succ, color='red', zorder=5)
        axs[0, 0].set_xlim(0, T)
        axs[0, 0].set_ylim(0, food_capacity_a + 10)
        axs[0, 0].set_xlabel('Time Unit (t)')
        axs[0, 0].set_ylabel('Food Remaining')
        axs[0, 0].set_title('Food at A')
        axs[0, 0].legend()
        axs[0, 0].grid(True)

        axs[0, 1].plot(range(T), food_B, label='Food at B', marker='_', color='blue')
        axs[0, 1].axvline(x=success, color='b', linestyle='--', label=f't1 = {success}')
        axs[0, 1].axvline(x=t, color='b', linestyle='--', label=f't2 = {t}')
        axs[0, 1].axhline(y=food_B_succ, color='black', linestyle=':', label=f'Equal height = {food_B_succ}')
        axs[0, 1].scatter(success, food_B_succ, color='red', zorder=5)
        axs[0, 1].scatter(t, food_B_succ, color='red', zorder=5)
        axs[0, 1].set_xlim(0, T)
        axs[0, 1].set_ylim(0, food_capacity_b + 10)
        axs[0, 1].set_xlabel('Time Unit (t)')
        axs[0, 1].set_ylabel('Food Remaining')
        axs[0, 1].set_title('Food at B')
        axs[0, 1].legend()
        axs[0, 1].grid(True)

        axs[1, 0].plot(range(T), food_C, label='Food at C', marker='_', color='orange')
        axs[1, 0].axvline(x=success, color='b', linestyle='--', label=f't1 = {success}')
        axs[1, 0].axvline(x=t, color='b', linestyle='--', label=f't2 = {t}')
        axs[1, 0].axhline(y=food_C_succ, color='black', linestyle=':', label=f'Equal height = {food_C_succ}')
        axs[1, 0].scatter(success, food_C_succ, color='red', zorder=5)
        axs[1, 0].scatter(t, food_C_succ, color='red', zorder=5)
        axs[1, 0].set_xlim(0, T)
        axs[1, 0].set_ylim(0, food_capacity_c + 10)
        axs[1, 0].set_xlabel('Time Unit (t)')
        axs[1, 0].set_ylabel('Food Remaining')
        axs[1, 0].set_title('Food at C')
        axs[1, 0].legend()
        axs[1, 0].grid(True)

        axs[1, 1].plot(range(T), truck_load_values, label='Truck Load', marker='_', color='red')
        axs[1, 1].axvline(x=success, color='b', linestyle='--', label=f't1 = {success}')
        axs[1, 1].axvline(x=t, color='b', linestyle='--', label=f't2 = {t}')
        axs[1, 1].axhline(y=truck_load_succ, color='black', linestyle=':', label=f'Equal height = {truck_load_succ}')
        axs[1, 1].scatter(success, truck_load_succ, color='red', zorder=5)
        axs[1, 1].scatter(t, truck_load_succ, color='red', zorder=5)
        axs[1, 1].set_xlim(0, T)
        axs[1, 1].set_ylim(0, max(truck_load_values) + 10)
        axs[1, 1].set_xlabel('Time Unit (t)')
        axs[1, 1].set_ylabel('Truck Load')
        axs[1, 1].set_title('Truck Load')
        axs[1, 1].legend()
        axs[1, 1].grid(True)

        plt.tight_layout()

        plt.show()

        # endregion

        exit(0)
    else:
        solver.pop()

print("No loop could be found")
exit(-1)
