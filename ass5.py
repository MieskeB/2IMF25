import os

from oxidd.bdd import BDDManager

from buddy import buddy

directory = 'ass5'

def process_file(filename):
    f = os.path.join(directory, filename)

    if not os.path.isfile(f):
        print(f"File {f} does not exist")
        return 0

    file = open(f, 'r')
    lines = file.readlines()

    number_of_variables = 0
    code = []
    for line in lines:
        if line.startswith('p'):
            # 'p cnf ' = 6 characters
            number_of_variables = int(line.split(' ')[2])
        elif not line.startswith('c'):
            for c in line.split(' '):
                code.append(int(c))

    manager = BDDManager(100_000_000, 1_000_000, 10)
    x = [manager.new_var() for i in range(number_of_variables)]

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

    return clauses.sat_count_float(number_of_variables)


for filename in os.listdir(directory):
    result = process_file(filename)
    print(f"File {filename} SAT count: {result}")
