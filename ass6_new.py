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
        bdd_vars[var] = manager.var2bdd(pos)

    def eval(key):
        if key in bdd_vars:
            return bdd_vars[key]

        value = items[key]

        operation = value.split('(')[0]
        operands = re.search(r'\((.*?)\)', value).group(1).split(', ')

        operand_bdds = [eval(op.strip()) for op in operands]

        if operation == 'NOT':
            result = manager.apply("NOT", operand_bdds[0])
        elif operation == 'AND':
            result = operand_bdds[0]
            for operand in operand_bdds[1:]:
                result = manager.apply_and(result, operand)
        elif operation == 'OR':
            result = operand_bdds[0]
            for operand in operand_bdds[1:]:
                result = manager.apply_or(result, operand)
        elif operation == 'NAND':
            result = operand_bdds[0]
            for operand in operand_bdds[1:]:
                result = manager.apply("and", result, operand)
            result = manager.apply("not", result)
        elif operation == 'NOR':
            result = operand_bdds[0]
            for operand in operand_bdds[1:]:
                result = manager.apply("or", result, operand)
            result = manager.apply("not", result)
        elif operation == 'XOR':
            result = operand_bdds[0]
            for operand in operand_bdds[1:]:
                result = manager.apply("xor", result, operand)
        else:
            print(f"No operation {operation} defined")

        bdd_vars[key] = result
        return result

    return {out_var: eval(out_var) for out_var in output_vars}


if __name__ == "__main__":
    circuit = "00"
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

    all_equal = True
    for i in range(len(bdd_result_items)):
        res = manager.apply("equiv", bdd_result_items[i], bdd_result2_items[i])
        if res == manager.true:
            print(f"\033[92mCircuit{circuit}.bench variable {list(bdd_result.keys())[i]} is equivalent to Circuit{circuit}_opt.bench variable {list(bdd_result2.keys())[i]}!\033[0m")
        else:
            print(f"\033[91mCircuit{circuit}.bench variable {list(bdd_result.keys())[i]} is NOT equivalent to Circuit{circuit}_opt.bench variable {list(bdd_result2.keys())[i]}!\033[0m")
            all_equal = False

    print(f"=-=-=-=-=-=-=  Circuit{circuit}  =-=-=-=-=-=-=-=-=-=")
    if all_equal:
        print(f"\033[92mThe circuits are equivalent!\033[0m")
    else:
        print(f"\033[91mThe circuits are NOT equivalent!\033[0m")
