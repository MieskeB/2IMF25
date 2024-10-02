from oxidd.bdd import BDDManager
import re
import z3



circuit_number = 1
if circuit_number < 10:
	circuit_path = "ass6/circuit0" + str(circuit_number) + ".bench"
	circuit_opt_path = "ass6/circuit0" + str(circuit_number) + "_opt.bench"
else:
	circuit_path = "ass6/circuit" + str(circuit_number) + ".bench"
	circuit_opt_path = "ass6/circuit" + str(circuit_number) + "_opt.bench"

with open(circuit_path, 'r') as file:
	circuit = file.read()
with open(circuit_opt_path, 'r') as file_opt:
	circuit_opt = file_opt.read()
	
manager = BDDManager(100_000_000, 1_000_000, 1)

#returns for gates a dictionary with output, type, list[inputs]
def parse_iscas_bench(file_path):
    inputs = []
    outputs = []
    gates = {}
    
    # Regex patterns to match input, output, and gate definitions
    input_pattern = re.compile(r'INPUT\((\w+)\)')
    output_pattern = re.compile(r'OUTPUT\((\w+)\)')
    gate_pattern = re.compile(r'(\w+)\s*=\s*(\w+)\(([\w, ]+)\)')
    
    # Open and read the file line by line
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Match and extract inputs
            input_match = input_pattern.match(line)
            if input_match:
                inputs.append(input_match.group(1))
                continue
            
            # Match and extract outputs
            output_match = output_pattern.match(line)
            if output_match:
                outputs.append(output_match.group(1))
                continue
            
            # Match and extract gates
            gate_match = gate_pattern.match(line)
            if gate_match:
                gate_name = gate_match.group(1)
                gate_type = gate_match.group(2)
                gate_inputs = [x.strip() for x in gate_match.group(3).split(',')]
                gates[gate_name] = (gate_type, gate_inputs)
    
    return inputs, outputs, gates

# Example usage
inputs, outputs, gates = parse_iscas_bench(circuit_path)

for item in inputs:
	print("Inputs:", item)
for item in outputs:
	print("Outputs:", item)
for item in gates.items():
	print("Gates:", item)
