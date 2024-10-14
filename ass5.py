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

    return code, number_of_variables, var_order


def run_bdd(manager, clauses_array, variable_count, var_order):
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
    # clauses_array is the list of all possible clauses, while clauses is the manager's BDD
    res_strat_1 = 0
    res_strat_2 = 0
    res_strat_3 = 0
    res_strat_4 = 0
    if sat_count > 0:
        res_strat_1 = permissiveness_strat_1(manager, clauses_array, clauses, var_order)
        res_strat_2 = permissiveness_strat_2(manager, clauses_array, clauses, var_order)
        res_strat_3 = permissiveness_strat_3(manager, clauses_array, clauses, var_order)
        res_strat_4 = permissiveness_strat_4(manager, clauses_array, clauses, var_order)

    print("=-= RESULTS =-=")
    print(f"A) {sat_count}")
    print(f"B)")
    print(f"  i) {res_strat_1}")
    print(f"  ii) {res_strat_2}")
    print(f"  iii) {res_strat_3}")
    print(f"  iv) {res_strat_4}")
    print(f"C) apple")


def permissiveness_strat_1(manager: BuDDy, clauses_array, given_clauses, var_order):
    essential_count = 0
    clauses = manager.apply_and(given_clauses, manager.true)
    print("Choices true: ", end="")
    for var in var_order:
        # If var is not a possible clause, it is not essential and thus doesn't count for the permissiveness length
        if var in clauses_array:
            selected_clause = manager.apply_and(clauses, manager.var2bdd(var))
            deselected_clause = manager.apply_and(clauses, manager.nvar2bdd(var))
            # Do forced assignments also count towards the permissiveness length?
            # Test if it is a choice variable
            if manager.satcount(selected_clause) > 0 and manager.satcount(deselected_clause) > 0:
                clauses = selected_clause
                essential_count += 1
                print(var, end=" ")
    print("")
    return essential_count


def permissiveness_strat_2(manager: BuDDy, clauses_array, given_clauses, var_order):
    essential_count = 0
    clauses = manager.apply_and(given_clauses, manager.true)
    print("Choices false: ", end="")
    for var in var_order:
        if var in clauses_array:
            selected_clause = manager.apply_and(clauses, manager.var2bdd(var))
            deselected_clause = manager.apply_and(clauses, manager.nvar2bdd(var))
            if manager.satcount(selected_clause) > 0 and manager.satcount(deselected_clause) > 0:
                clauses = deselected_clause
                essential_count += 1
                print(var, end=" ")
    print("")
    return essential_count


def permissiveness_strat_3(manager: BuDDy, clauses_array, given_clauses, var_order):
    essential_count = 0
    clauses = manager.apply_and(given_clauses, manager.true)
    print("Choices iff true: ", end="")
    for var in var_order:
        if var in clauses_array:
            selected_clause = manager.apply_and(clauses, manager.var2bdd(var))
            deselected_clause = manager.apply_and(clauses, manager.nvar2bdd(var))
            selected_count = manager.satcount(selected_clause)
            deselected_count = manager.satcount(deselected_clause)
            if selected_count > 0 and deselected_count > 0:
                # Select feature iff selecting it would cover more valid configurations
                if selected_count > deselected_count:
                    essential_count += 1
                    clauses = selected_clause
                    print(var, end=" ")
    print("")
    return essential_count


def permissiveness_strat_4(manager: BuDDy, clauses_array, given_clauses, var_order):
    essential_count = 0
    clauses = manager.apply_and(given_clauses, manager.true)
    print("Choices iff false: ", end="")
    for var in var_order:
        if var in clauses_array:
            selected_clause = manager.apply_and(clauses, manager.var2bdd(var))
            deselected_clause = manager.apply_and(clauses, manager.nvar2bdd(var))
            selected_count = manager.satcount(selected_clause)
            deselected_count = manager.satcount(deselected_clause)
            if selected_count > 0 and deselected_count > 0:
                if deselected_count > selected_count:
                    essential_count += 1
                    clauses = deselected_clause
                    print(var, end=" ")
    print("")
    return essential_count


def find_most_permissive_configuration(manager: BuDDy, clauses_array, given_clauses, var_order):
    essential_count = 0
    clauses = manager.apply_and(given_clauses, manager.true)
    print("Most permissive configuration: ", end="")
    for var in var_order:
        # If the variable isn't in the clauses, it is not essential and we can skip it
        if var not in clauses_array:
            continue

        selected_clause = manager.apply_and(clauses, manager.var2bdd(var))
        deselected_clause = manager.apply_and(clauses, manager.nvar2bdd(var))
        selected_count = manager.satcount(selected_clause)
        deselected_count = manager.satcount(deselected_clause)


if __name__ == "__main__":
    filename = "buildroot"
    # filename = "busybox"
    # filename = "embtoolkit"
    # filename = "toybox"
    # filename = "uClinux"

    filename += ".dimacs"

    print(f"=-=-= {filename} =-=-=")
    clauses_array, number_of_variables, var_order = process_dimacs_file(filename)
    manager = BuDDy(var_order, "buddy/buddy.windows")
    run_bdd(manager, clauses_array, number_of_variables, var_order)
    print(f"=-=-= {filename} =-=-=")
