import os
from oxidd.bdd import BDDManager

directory = 'ass5'

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)

    if not os.path.isfile(f):
        print(f"File {f} does not exist")
        exit(-1)

    file = open(f, 'r')
    lines = file.readlines()

    numberOfVariables = 0
    code = []
    for line in lines:
        if line.startswith('p'):
            # 'p cnf ' = 6 characters
            numberOfVariables = int(line.split(' ')[2])
        elif not line.startswith('c'):
            for c in line.split(' '):
                code.append(int(c))

    manager = BDDManager(100_000_000, 1_000_000, 10)
    x = [manager.new_var() for i in range(numberOfVariables)]

    clauses = manager.true()
    curr = manager.false()
    for c in code:
        if c == 0:
            clauses &= curr
            curr = manager.false()
        else:
            if c > 0:
                curr |= x[c - 1]
            else:
                curr |= ~x[abs(c) - 1]

    print(f"File {filename} SAT count: {clauses.sat_count_float(numberOfVariables)}")
