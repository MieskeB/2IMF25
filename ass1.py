from z3 import *

# Number of trucks
num_trucks = 6

# Create variables to represent the number of pallets of each type loaded into each truck
# Each truck has variables for nuzzles, prittles, skipples, crottles, and dupples
nuzzles = [Int(f"nuzzles_{i}") for i in range(num_trucks)]
prittles = [Int(f"prittles_{i}") for i in range(num_trucks)]
skipples = [Int(f"skipples_{i}") for i in range(num_trucks)]
crottles = [Int(f"crottles_{i}") for i in range(num_trucks)]
dupples = [Int(f"dupples_{i}") for i in range(num_trucks)]

# Create a solver instance
solver = Optimize()#Solver()

# Total number of pallets of each item
total_nuzzles = 6
total_prittles = 12
total_skipples = 15
total_crottles = 8

# Pallet weights for each type
nuzzles_weight = 800
prittles_weight = 405
skipples_weight = 500
crottles_weight = 2500
dupples_weight = 600

for i in range(num_trucks):
    # Can't have a negative amount of pallets
    solver.add(nuzzles[i] >= 0)
    solver.add(prittles[i] >= 0)
    solver.add(skipples[i] >= 0)
    solver.add(crottles[i] >= 0)
    solver.add(dupples[i] >= 0)
    
    # Can't have more than 10 pallets per truck
    solver.add(nuzzles[i] + prittles[i] + skipples[i] + crottles[i] + dupples[i] <= 10)
    
    # Maximum of 8000kg per truck
    solver.add(nuzzles[i] * nuzzles_weight +
               prittles[i] * prittles_weight +
               skipples[i] * skipples_weight +
               crottles[i] * crottles_weight +
               dupples[i] * dupples_weight <= 8000)


# Sum of amounts per truck must match total amount
solver.add(Sum(nuzzles) == total_nuzzles)
solver.add(Sum(prittles) == total_prittles)
solver.add(Sum(skipples) == total_skipples)
solver.add(Sum(crottles) == total_crottles)

# Prittles must be distributed over at least 5 trucks
solver.add(Sum([If(prittles[i] > 0, 1, 0) for i in range(num_trucks)]) >= 5)

# Only 2 trucks can carry skipples
solver.add(Sum([If(skipples[i] > 0, 1, 0) for i in range(num_trucks)]) == 2)

# part b: enforce at leats 2 dupples if crottles are carried(per truck)
#for i in range(num_trucks):
#    solver.add(If(crottles[i] > 0, dupples[i] >= 2, dupples[i] == 0))

# Goal is to maximize the number of dupples
solver.maximize(Sum(dupples))

# Check for solvability and print solution if found
result = solver.check()
print("done")
if result == sat:
    print("sat")
    model = solver.model()
    for i in range(num_trucks):
        print(f"Truck {i + 1}:")
        print(f"  Nuzzles: {model[nuzzles[i]]}")
        print(f"  Prittles: {model[prittles[i]]}")
        print(f"  Skipples: {model[skipples[i]]}")
        print(f"  Crottles: {model[crottles[i]]}")
        print(f"  Dupples: {model[dupples[i]]}")
else:
    print("No solution found.")
