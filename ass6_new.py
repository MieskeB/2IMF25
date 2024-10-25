import os
import re

from buddy.buddy import BuDDy

directory = 'ass6'


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
            input_vars.append(re.search(r'\((.*?)\)', line))
        elif line.startswith('OUTPUT'):
            output_vars.append(re.search(r'\((.*?)\)', line))
        elif '=' in line:
            c = line.split('=')
            items[c[0].strip()] = c[1].strip()

    return input_vars, output_vars, items


if __name__ == "__main__":
    print(process_bench_file("circuit01.bench"))
