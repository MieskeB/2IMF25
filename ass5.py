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
    print(clauses_array)
    for c in clauses_array:
        if c == 0:
            clauses = manager.apply_and(clauses, curr)
            curr = manager.false
        else:
            if c > 0:
                curr = manager.apply_or(curr, manager.var2bdd(c))
            else:
                curr = manager.apply_or(curr, manager.nvar2bdd(abs(c)))

    manager.dump(clauses, filename=f"{directory}/res/{filename.replace('.dimacs', '')}.dot")
    manager.dump(clauses, filename=f"{directory}/res/{filename.replace('.dimacs', '')}.bdd")

    node_count = manager.node_count(clauses)
    print(f"Node count: {node_count}")
    sat_count = manager.satcount_ln(clauses)
    # clauses_array is the list of all possible clauses, while clauses is the manager's BDD
    res_strat_1 = 0
    res_strat_2 = 0
    res_strat_3 = 0
    res_strat_4 = 0
    res_most_permissive_conf = 0
    if sat_count > 0:
        res_strat_1 = permissiveness_strat_1(manager, clauses_array, clauses, var_order)
        res_strat_2 = permissiveness_strat_2(manager, clauses_array, clauses, var_order)
        res_strat_3 = permissiveness_strat_3(manager, clauses_array, clauses, var_order)
        res_strat_4 = permissiveness_strat_4(manager, clauses_array, clauses, var_order)

        res_most_permissive_conf = find_most_permissive_configuration(manager, clauses_array, clauses, var_order)

    print("=-= RESULTS =-=")
    print(f"A) 2^{sat_count}")
    print(f"B)")
    print(f"  i) {res_strat_1}")
    print(f"  ii) {res_strat_2}")
    print(f"  iii) {res_strat_3}")
    print(f"  iv) {res_strat_4}")
    print(f"C) {res_most_permissive_conf}")


def permissiveness_strat_1(manager: BuDDy, clauses_array, given_clauses, var_order):
    essential_count = 0
    clauses = manager.apply_and(given_clauses, manager.true)
    print("Choices true: ", end="")
    for var in var_order:
        # If var is not a possible clause, it is not essential and thus doesn't count for the permissiveness length
        if var in clauses_array:
            selected_clause = manager.high(clauses)
            deselected_clause = manager.low(clauses)
            selected_count = manager.satcount_ln(selected_clause)
            deselected_count = manager.satcount_ln(deselected_clause)
            if selected_count > 0 and deselected_count > 0:
                clauses = selected_clause
                essential_count += 1
                print(f"{var}", end=" ")
            elif selected_count > 0:
                clauses = selected_clause
                print(f"\033[91m{var}\033[0m", end=" ")
            elif deselected_count > 0:
                clauses = deselected_clause
                print(f"\033[91m-{var}\033[0m", end=" ")
            else:
                break
        if manager.node_count(clauses) == 0:
            break
    print("")
    return essential_count


def permissiveness_strat_2(manager: BuDDy, clauses_array, given_clauses, var_order):
    essential_count = 0
    clauses = manager.apply_and(given_clauses, manager.true)
    print("Choices false: ", end="")
    for var in var_order:
        if var in clauses_array:
            selected_clause = manager.high(clauses)
            deselected_clause = manager.low(clauses)
            selected_count = manager.satcount_ln(selected_clause)
            deselected_count = manager.satcount_ln(deselected_clause)
            if selected_count > 0 and deselected_count > 0:
                clauses = deselected_clause
                essential_count += 1
                print(f"-{var}", end=" ")
            elif selected_count > 0:
                clauses = selected_clause
                print(f"\033[91m{var}\033[0m", end=" ")
            elif deselected_count > 0:
                clauses = deselected_clause
                print(f"\033[91m-{var}\033[0m", end=" ")
            else:
                break
        if manager.node_count(clauses) == 0:
            break
    print("")
    return essential_count


def permissiveness_strat_3(manager: BuDDy, clauses_array, given_clauses, var_order):
    essential_count = 0
    clauses = manager.apply_and(given_clauses, manager.true)
    print("Choices iff true: ", end="")
    for var in var_order:
        if var in clauses_array:
            selected_clause = manager.high(clauses)
            deselected_clause = manager.low(clauses)
            selected_count = manager.satcount_ln(selected_clause)
            deselected_count = manager.satcount_ln(deselected_clause)
            # Select feature iff selecting it would cover more valid configurations
            if selected_count > deselected_count:
                essential_count += 1
                clauses = selected_clause
                print(var, end=" ")
            else:
                clauses = deselected_clause
                print(f"\033[91m-{var}\033[0m", end=" ")
        if manager.node_count(clauses) == 0:
            break
    print("")
    return essential_count


def permissiveness_strat_4(manager: BuDDy, clauses_array, given_clauses, var_order):
    essential_count = 0
    clauses = manager.apply_and(given_clauses, manager.true)
    print("Choices iff false: ", end="")
    for var in var_order:
        if var in clauses_array:
            selected_clause = manager.high(clauses)
            deselected_clause = manager.low(clauses)
            selected_count = manager.satcount_ln(selected_clause)
            deselected_count = manager.satcount_ln(deselected_clause)
            if deselected_count > selected_count:
                essential_count += 1
                clauses = deselected_clause
                print(f"-{var}", end=" ")
            else:
                clauses = selected_clause
                print(f"\033[91m{var}\033[0m", end=" ")
        if manager.node_count(clauses) == 0:
            break
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
        selected_count = manager.satcount_ln(selected_clause)
        deselected_count = manager.satcount_ln(deselected_clause)

        if selected_count > 0 and deselected_count > 0:
            if selected_count == deselected_count:
                # This variable doesn't do anything, therefore not counting it
                continue
            elif selected_count > deselected_count:
                clauses = selected_clause
                essential_count += 1
                print(f"{var}", end=" ")
            else:
                clauses = deselected_clause
                essential_count += 1
                print(f"-{var}", end=" ")
    print("0")
    return essential_count


if __name__ == "__main__":
    # filename = "buildroot"
    # filename = "busybox"
    # filename = "embtoolkit"
    # filename = "toybox"
    filename = "uClinux"

    # filename = "testFile"

    filename += ".dimacs"

    print(f"=-=-= {filename} =-=-=")
    clauses_array, number_of_variables, var_order = process_dimacs_file(filename)
    manager = BuDDy(var_order, "buddy/buddy.windows")
    run_bdd(manager, clauses_array, number_of_variables, var_order)
    print(f"=-=-= {filename} =-=-=")
