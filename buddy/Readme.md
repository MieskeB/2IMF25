# BuDDy wrapper for Python
## Course 2IMF25 - Automated Reasoning

This folder contains a simple Python wrapper for the BuDDy library (https://github.com/jgcoded/BuDDy) as well as precompiled libraries for Linux, macOS, and Windows.

### Files
- `buddy.py`: the BuDDy class for Python
- `buddy.linux`: binary library for Linux (x64)
- `buddy.macos`: binary library for macOS (arm64)
- `buddy.windows`: binary library for Windows (x64)

### Example
An example use case to construct the BDD for the boolean function represented by `(x1 & !x2) => x3` and count the satisfying assignments:
```
from buddy import BuDDy

var_order = ['x1', 'x2', 'x3']
manager = BuDDy(var_order, "buddy.macos")
x1 = manager.var2bdd('x1')
x2 = manager.var2bdd('x2')
x3 = manager.var2bdd('x3')
nx2 = manager.neg(x2)
x1_a_nx2 = manager.apply_and(x1, nx2)
root = manager.apply('=>', x1_a_nx2, x3)

print(f"Satisfying assignments: {manager.satcount(root)}")
```
Note: you have to replace the ``buddy.macos`` with the name of the binary of your operating system.