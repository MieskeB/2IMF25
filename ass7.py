import os

from buddy.buddy import BuDDy

directory = 'ass7'

manager = BuDDy(list(range(100000)), "buddy.windows")


def process_ba_file(filename):
    print(f"Now processing {filename}")
    f = os.path.join(directory, filename)

    if not os.path.isfile(f):
        print(f"File {f} does not exist")
        return 0

    file = open(f, 'r')
    lines = file.readlines()

    if '->' in lines[0]:
        initial_state = lines[0].split('->')[0].split(',')[1]
    else:
        initial_state = lines[0]

    final_states = []
    transitions = {}
    for line in lines:
        if "->" in line:
            split_line = line.split('->')
            transition_val = split_line[0].split(',')[0]
            from_val = split_line[0].split(',')[1]
            to_val = split_line[1].replace('\n', '')
            transitions[split_line[0]] = (from_val, transition_val, to_val)
        elif line != lines[0]:
            final_states.append(line.replace('\n', ''))

    return initial_state, final_states, transitions


def create_bdd(initial_state, final_states, transitions):
    var_map = {}

    var_map[initial_state] = manager.var2bdd(0)

    result_bdd = manager.true

    for (label_from_val, (from_val, label, to_val)) in transitions.items():
        if from_val not in var_map.keys():
            var_map[from_val] = manager.var2bdd(len(var_map))
        if to_val not in var_map.keys():
            var_map[to_val] = manager.var2bdd(len(var_map))

        if label == '0':
            label_from_val1 = label_from_val.replace('0', '1', 1)
            # Case if only 0 exists
            if label_from_val1 not in transitions.keys():
                bet_bdd = manager.apply_ite(var_map[from_val], manager.false, var_map[to_val])
                result_bdd = manager.apply_and(result_bdd, bet_bdd)
                continue

            # General case if both 1 and 0 exist
            (from_val1, label1, to_val1) = transitions[label_from_val1]

            if from_val1 not in var_map.keys():
                var_map[from_val1] = manager.var2bdd(len(var_map))
            if to_val1 not in var_map.keys():
                var_map[to_val1] = manager.var2bdd(len(var_map))

            bet_bdd = manager.apply_ite(var_map[from_val], var_map[to_val1], var_map[to_val])
            result_bdd = manager.apply_and(result_bdd, bet_bdd)

        elif label == '1' and label_from_val.replace('1', '0', 1) not in transitions.keys():
            # Case if only 1 exists
            bet_bdd = manager.apply_ite(var_map[from_val], var_map[to_val], manager.false)
            result_bdd = manager.apply_and(result_bdd, bet_bdd)

    final_bdd = manager.false
    for final_state in final_states:
        if final_state not in var_map.keys():
            var_map[final_state] = manager.var2bdd(len(var_map))

        final_bdd = manager.apply_or(final_bdd, var_map[final_state])

    result_bdd = manager.apply_and(result_bdd, final_bdd)


    return result_bdd


if __name__ == "__main__":
    file_name = "test.c.ba"

    initial_state, final_states, transitions = process_ba_file(file_name)
    print(initial_state)
    print(transitions)
    print(final_states)

    if initial_state and final_states and transitions:
        result_bdd = create_bdd(initial_state, final_states, transitions)
        manager.dump(result_bdd, f"ass7/res/{file_name}.dot")
        print("BDD successfully created")
    else:
        print("Failed to create BDD")
