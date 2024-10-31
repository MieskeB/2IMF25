import os

from buddy.buddy import BuDDy

directory = 'ass7'

manager = BuDDy(list(range(1000)), "buddy.windows")


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
            transitions[from_val] = (transition_val, to_val)
        elif line != lines[0]:
            final_states.append(line.replace('\n', ''))

    return initial_state, final_states, transitions


def create_bdd(initial_state, final_states, transitions):
    var_map = {}

    transition_bdd = manager.true

    for (from_val, (label, to_val)) in transitions.items():
        if from_val not in var_map.keys():
            var_map[from_val] = manager.var2bdd(len(var_map))
        if to_val not in var_map.keys():
            var_map[to_val] = manager.var2bdd(len(var_map))

        if label == '0':
            transition_relation = manager.apply_and(var_map[from_val], var_map[to_val])
        elif label == '1':
            transition_relation = manager.apply_or(var_map[from_val], var_map[to_val])
        else:
            raise ValueError(f"Unexpected label '{label}' in transitions")

        transition_bdd = manager.apply_or(transition_bdd, transition_relation)

    initial_bdd = var_map[initial_state]

    accepting_bdd = manager.true
    for state in final_states:
        if state in var_map:
            accepting_bdd = manager.apply_or(accepting_bdd, var_map[state])

    return initial_bdd, transition_bdd, accepting_bdd


if __name__ == "__main__":
    file_name = "test"
    file_name += ".c.ba"

    initial_state, final_states, transitions = process_ba_file(file_name)

    if initial_state and final_states and transitions:
        initial_bdd, transition_bdd, accepting_bdd = create_bdd(initial_state, final_states, transitions)
        manager.dump(initial_bdd, "ass7/res/test.dot")
        print("BDD created and information reported successfully")
    else:
        print("Failed to process BA file or create BDD")
