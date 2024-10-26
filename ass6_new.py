import os
import re

from buddy.buddy import BuDDy

directory = 'ass6'

manager = BuDDy(list(range(100)), "buddy.windows")


def process_bench_file(filename):
    print(f"Now processing {filename}")
    f = os.path.join(directory, filename)

    if not os.path.isfile(f):
        print(f"File {f} does not exist")
        return 0

    file = open(f, 'r')
    lines = file.readlines()

    input_vars = []
    output_vars = []
    items = {}
    for line in lines:
        if line.startswith('INPUT'):
            input_vars.append(re.search(r'\((.*?)\)', line).group(1))
        elif line.startswith('OUTPUT'):
            output_vars.append(re.search(r'\((.*?)\)', line).group(1))
        elif '=' in line:
            c = line.split('=')
            items[c[0].strip()] = c[1].strip()

    return input_vars, output_vars, items


def create_bdd(input_vars, output_vars, items):
    bdd_vars = {}

    for pos, var in enumerate(input_vars):
        bdd_vars[pos] = manager.var2bdd(pos)
    for pos, var in enumerate(output_vars):
        bdd_vars[pos + len(input_vars)] = manager.var2bdd(pos + len(input_vars))

    print(bdd_vars)

    for pos, (key, value) in enumerate(items.items()):
        operands = re.search(r'\((.*?)\)', value).group(1).split(', ')

        index = []
        for operand in operands:
            if operand in output_vars:
                index.append(output_vars.index(operand) + len(input_vars))
            elif operand in input_vars:
                index.append(input_vars.index(operand))
            else:
                index.append(list(items.keys()).index(operand) + len(input_vars) + len(output_vars))

            if index[len(index) - 1] not in bdd_vars:
                bdd_vars[index[len(index) - 1]] = manager.var2bdd(index[len(index) - 1])

        if len(index) == 1:
            if 'NOT' in value:
                bdd_vars[pos + len(input_vars) + len(output_vars)] = manager.apply(value.split('(')[0], bdd_vars[index[0]])
            else:
                print(f"Operation {value.split('(')[0]} not defined for 1 parameter")
        elif len(index) == 2:
            bdd_vars[pos + len(input_vars) + len(output_vars)] = manager.apply(value.split('(')[0], bdd_vars[index[0]], bdd_vars[index[1]])
        else:
            if 'NAND' in value:
                res_i = bdd_vars[index[0]]
                for i_i in range(1, len(index)):
                    res_i = manager.apply_and(res_i, bdd_vars[index[i_i]])
                bdd_vars[pos + len(input_vars) + len(output_vars)] = manager.apply("NOT", res_i)
            elif 'AND' in value:
                res_i = bdd_vars[index[0]]
                for i_i in range(1, len(index)):
                    res_i = manager.apply_and(res_i, bdd_vars[index[i_i]])
                bdd_vars[pos + len(input_vars) + len(output_vars)] = res_i
            else:
                print(f"Operation {value.split('(')[0]} not defined for >=3 parameters")

    print(bdd_vars)
    return {out_var: bdd_vars[pos + len(input_vars)] for pos, out_var in enumerate(output_vars)}


if __name__ == "__main__":
    circuit = "20"
    input_v, output_v, items_v = process_bench_file(f"circuit{circuit}.bench")
    bdd_result = create_bdd(input_v, output_v, items_v)
    input_v2, output_v2, items_v2 = process_bench_file(f"circuit{circuit}_opt.bench")
    bdd_result2 = create_bdd(input_v2, output_v2, items_v2)

    for i, (out_var, bdd_node) in enumerate(bdd_result.items()):
        filename = os.path.join(directory, "res", f"circuit{circuit}", f"{output_v[i]}.dot")
        manager.dump(bdd_node, filename)

    for i, (out_var, bdd_node) in enumerate(bdd_result2.items()):
        filename = os.path.join(directory, "res", f"circuit{circuit}", f"{output_v2[i]}_opt.dot")
        manager.dump(bdd_node, filename)

    bdd_result_items = list(bdd_result.values())
    bdd_result2_items = list(bdd_result2.values())

    res = True
    for i in range(len(bdd_result_items)):
        res = manager.apply("equiv", bdd_result_items[i], bdd_result2_items[i])
        if res == manager.true:
            print(f"\033[92mCircuit{circuit}.bench variable {list(bdd_result.keys())[i]} is equivalent to Circuit{circuit}_opt.bench variable {list(bdd_result2.keys())[i]}!\033[0m")
        else:
            print(f"\033[91mCircuit{circuit}.bench variable {list(bdd_result.keys())[i]} is NOT equivalent to Circuit{circuit}_opt.bench variable {list(bdd_result2.keys())[i]}!\033[0m")
            res = False

    print(f"=-=-=-=-=-=-=  Circuit{circuit}  =-=-=-=-=-=-=-=-=-=")
    if res:
        print(f"\033[92mThe circuits are equivalent!\033[0m")
    else:
        print(f"\033[91mThe circuits are NOT equivalent!\033[0m")
