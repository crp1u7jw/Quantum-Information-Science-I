import numpy as np
import random

# This function checks whether a specific configuration tensor for a 3SAT instance is solvable. 
# The technique I have used to do so is detailed in the README file and scratch notes.
def check_3SAT(T):
    X = np.ones([2] * n)
    null_vector = np.array([-1, -1, -1])

    for t in T:
        null_input = null_vector @ t.T
        #                       ⌄ This maps {1: 0, -1: 1} {value: index}
        null_slice = tuple(int(-0.5*i+0.5) if i else slice(None) for i in null_input)
        X[null_slice] = False

        if not np.any(X):
            return False
        
    return True

n = 10
m = 50

# Generate random mapping of variables and NOT gates (1 represents identity, -1 represents NOT)
map = np.empty((m, 3), dtype=int)
gates = np.empty((m, 3), dtype=int)

for i in range(m):
    available_variables = list(range(n))
    for j in range(3):
        map[i, j] = random.choice(available_variables)
        available_variables.remove(map[i, j])

        gates[i, j] = random.choice([1, -1])

# Convert mapping into a configuration tensor for processing and a system tensor for display
config_tensor = np.zeros((m, n, 3))
system = np.empty((m, 3), dtype=object)

for num_list, gates_list, floor, equation in zip(map, gates, config_tensor, system):
    for i, (num, gate) in enumerate(zip(num_list, gates_list)):
        floor[num, i] = gate
        equation[i] = str(gate).removesuffix("1") + "x" + str(num)

# Check if tensor configuration is possible
possible = check_3SAT(config_tensor)

# Print result
print(f"Config tensor: {config_tensor}\nSystem:\n{system}\nPossible: {possible}")