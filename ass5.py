import os

from buddy.buddy import BuDDy

directory = 'ass5'

var_order = list(range(1000))
manager = BuDDy(var_order, "buddy/buddy.windows")

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

    x = [manager.var2bdd(i) for i in range(number_of_variables)]

    clauses = manager.true
    curr = manager.false
    for c in code:
        if c == 0:
            clauses = manager.apply_and(clauses, curr)
            curr = manager.false
        else:
            if c > 0:
                curr = manager.apply_or(curr, x[c - 1])
            else:
                curr = manager.apply_or(curr, manager.neg(x[abs(c) - 1]))

    return manager.satcount(clauses)


for filename in os.listdir(directory):
    result = process_file(filename)
    print(f"File {filename} SAT count: {result}")
