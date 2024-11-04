import os

from buddy.buddy import BuDDy

directory = 'ass7'

manager = BuDDy(list(range(1000000)), "buddy.windows")


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

            label = split_line[0] + ','
            for i in range(20):
                if label + str(i) not in transitions.keys():
                    transitions[label + str(i)] = (from_val, transition_val, to_val, i)
                    break

        elif line != lines[0]:
            final_states.append(line.replace('\n', ''))

    return initial_state, final_states, transitions


def create_bdd(initial_state, final_states, transitions):
    var_map = {}

    var_map[initial_state] = manager.var2bdd(0)

    result_bdd = manager.true

    for (label_from_val, (from_val, label, to_val, _)) in ((k, v) for k, v in transitions.items() if v[3] == 0):
        print(result_bdd)
        if from_val not in var_map.keys():
            var_map[from_val] = manager.var2bdd(len(var_map))
        if to_val not in var_map.keys():
            var_map[to_val] = manager.var2bdd(len(var_map))

        if label == '0' and '1' + label_from_val[1:] not in transitions.keys():
            print("apple")
            # Case if only 0 exists
            la = label_from_val[:-1] + str(1)
            if la in transitions.keys():
                first_decision_key = from_val + 'D0'
                var_map[first_decision_key] = len(var_map)
                first_bet_bdd = manager.apply_ite(var_map[from_val], manager.false, var_map[first_decision_key])
                result_bdd = manager.apply_and(result_bdd, first_bet_bdd)
                for i in range(20):
                    second_next_item_key = label_from_val[:-1] + str(i + 2)
                    next_item_key = label_from_val[:-1] + str(i + 1)
                    if next_item_key not in var_map:
                        var_map[next_item_key] = len(var_map)
                    decision_key = from_val + 'D' + str(i)
                    if second_next_item_key not in transitions.keys():
                        # Last iteration
                        bet_bdd = manager.apply_ite(var_map[decision_key], var_map[to_val], var_map[next_item_key])
                        result_bdd = manager.apply_and(result_bdd, bet_bdd)
                        break
                    next_decision_key = from_val + 'D' + str(i + 1)
                    var_map[next_decision_key] = len(var_map)
                    (_, _, t0, _) = transitions[next_item_key]
                    if t0 not in var_map.keys():
                        var_map[t0] = manager.var2bdd(len(var_map))
                    bet_bdd = manager.apply_ite(var_map[decision_key], var_map[next_decision_key], var_map[t0])
                    result_bdd = manager.apply_and(result_bdd, bet_bdd)
            else:
                bet_bdd = manager.apply_ite(var_map[from_val], manager.false, var_map[to_val])
                result_bdd = manager.apply_and(result_bdd, bet_bdd)

        elif label == '1' and '0' + label_from_val[1:] not in transitions.keys():
            # Case if only 1 exists
            la = label_from_val[:-1] + str(1)
            if la in transitions.keys():
                first_decision_key = from_val + 'D0'
                var_map[first_decision_key] = len(var_map)
                first_bet_bdd = manager.apply_ite(var_map[from_val], var_map[first_decision_key], manager.false)
                result_bdd = manager.apply_and(result_bdd, first_bet_bdd)
                for i in range(20):
                    second_next_item_key = label_from_val[:-1] + str(i + 2)
                    next_item_key = label_from_val[:-1] + str(i + 1)
                    if next_item_key not in var_map:
                        var_map[next_item_key] = len(var_map)
                    decision_key = from_val + 'D' + str(i)
                    if second_next_item_key not in transitions.keys():
                        # Last iteration
                        bet_bdd = manager.apply_ite(var_map[decision_key], var_map[to_val], var_map[next_item_key])
                        result_bdd = manager.apply_and(result_bdd, bet_bdd)
                        break
                    next_decision_key = from_val + 'D' + str(i + 1)
                    var_map[next_decision_key] = len(var_map)
                    (_, _, t0, _) = transitions[next_item_key]
                    if t0 not in var_map.keys():
                        var_map[t0] = manager.var2bdd(len(var_map))
                    bet_bdd = manager.apply_ite(var_map[decision_key], var_map[next_decision_key], var_map[t0])
                    result_bdd = manager.apply_and(result_bdd, bet_bdd)
            else:
                bet_bdd = manager.apply_ite(var_map[from_val], var_map[to_val], manager.false)
                result_bdd = manager.apply_and(result_bdd, bet_bdd)

        else:
            # General case if both 1 and 0 exist (if they both exist, we only add when we encounter 0)
            if label == '1':
                continue
            label_from_val1 = '1' + label_from_val[1:]
            (from_val1, label1, to_val1, i1) = transitions[label_from_val1]

            if from_val1 not in var_map.keys():
                var_map[from_val1] = manager.var2bdd(len(var_map))
            if to_val1 not in var_map.keys():
                var_map[to_val1] = manager.var2bdd(len(var_map))

            la0 = label_from_val[:-1] + str(1)
            la1 = label_from_val1[:-1] + str(1)
            if la0 in transitions.keys() and la1 in transitions.keys():
                print("TODO there is multiple of both 0s and 1s")
            elif la0 in transitions.keys():
                print("TODO there is multiple of only 0s")
            elif la1 in transitions.keys():
                print("TODO there is multiple of only 1s")
            else:
                bet_bdd = manager.apply_ite(var_map[from_val], var_map[to_val1], var_map[to_val])
                result_bdd = manager.apply_and(result_bdd, bet_bdd)

    final_bdd = manager.false
    for final_state in final_states:
        if final_state not in var_map.keys():
            var_map[final_state] = manager.var2bdd(len(var_map))

        final_bdd = manager.apply_or(final_bdd, var_map[final_state])

    result_bdd = manager.apply_and(result_bdd, final_bdd)

    return result_bdd


if __name__ == "__main__":
    file_name = "bakery.1.c.ba"

    initial_state, final_states, transitions = process_ba_file(file_name)
    print(f"Initial state: {initial_state}")
    print(f"Transitions: {transitions}")
    print(f"Final states: {final_states}")

    if initial_state and final_states and transitions:
        result_bdd = create_bdd(initial_state, final_states, transitions)
        manager.dump(result_bdd, f"ass7/res/{file_name}.dot")
        print("BDD successfully created")
    else:
        print("Failed to create BDD")
