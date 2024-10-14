import os

from buddy.buddy import BuDDy

directory = 'ass5'


def process_dimacs_file(filename):
    print(f"Now processing {filename}")
    f = os.path.join(directory, filename)

    if not os.path.isfile(f):
        print(f"File {f} does not exist")
        return 0

    file = open(f, 'r')
    lines = file.readlines()

    number_of_variables = 0
    var_order = []
    code = []
    for line in lines:
        if line.startswith('p'):
            number_of_variables = int(line.split(' ')[2])
        elif line.startswith('c vo'):
            var_order = [int(x) for x in line.split()[2:]]
        elif not line.startswith('c'):
            for c in line.split(' '):
                code.append(int(c))

    if not var_order:
        var_order = list(range(1, number_of_variables + 1))

    return code, var_order


def run_bdd(clauses_array, variable_count, var_order):
    clauses = manager.true
    curr = manager.false
    print(f"Processing {len(clauses_array)} clauses")
    for c in clauses_array:
        if c == 0:
            clauses = manager.apply_and(clauses, curr)
            curr = manager.false
        else:
            if c > 0:
                curr = manager.apply_or(curr, manager.var2bdd(c))
            else:
                curr = manager.apply_or(curr, manager.nvar2bdd(abs(c)))

    node_count = manager.node_count(clauses)
    print(f"Node count: {node_count}")
    sat_count = manager.satcount(clauses)
    print(f"Possible configurations: {sat_count}")

    print("=-= RESULTS =-=")
    print(f"A) {sat_count}")
    print(f"B) apple")
    print(f"  i) apple")
    print(f"  ii) apple")
    print(f"  iii) apple")
    print(f"  iv) apple")
    print(f"C) apple")


if __name__ == "__main__":
    # filename = "buildroot"
    # filename = "busybox"
    filename = "embtoolkit"
    # filename = "toybox"
    # filename = "uClinux"

    filename += ".dimacs"

    print(f"=-=-= {filename} =-=-=")
    clauses_array, var_order = process_dimacs_file(filename)
    manager = BuDDy(var_order, "buddy/buddy.windows")

    print(f"=-=-= {filename} =-=-=")
