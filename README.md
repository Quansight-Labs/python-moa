[![Build Status](https://travis-ci.org/costrouc/python-moa.svg?branch=master)](https://travis-ci.org/costrouc/python-moa)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/costrouc/python-moa/master)


# Mathematics of Arrays (MOA)

Important questions that should guide development most likely in this order:

 - [X] Is a simple implementation of moa possible with only knowing the dimension?
 - [ ] Can we represent complex operations and einsum math: requires `+red, transpose`?
 - [ ] What is the interface for arrays? (shape, indexing function)
 - [ ] How does one wrap pre-existing numerical routines?
 
# Documentation



# Example

## Python Frontend AST Generation

```python
from moa.frontend import MOAParser
from moa.visualize import print_ast

parser = MOAParser()
symbol_table, tree = parser.parse('<0> psi (tran(A ^ <2 3> + B ^ <2 3>))')
print_ast(symbol_table, tree)
```

```
psi(Ψ)
├── Array _a0: <1> (0)
└── transpose(Ø)
    └── +
        ├── Array A: <2 3>
        └── Array B: <2 3>
```

## Shape Calculation

```
from moa.shape import calculate_shapes

shape_symbol_table, shape_tree = calculate_shapes(symbol_table, tree)
print_ast(shape_symbol_table, shape_tree)
```

```
psi(Ψ): <2>
├── Array _a0: <1> (0)
└── transpose(Ø): <3 2>
    └── +: <2 3>
        ├── Array A: <2 3>
        └── Array B: <2 3>
```

## Reduction to DNF

```
from moa.dnf import reduce_to_dnf

dnf_symbol_table, dnf_tree = reduce_to_dnf(shape_symbol_table, shape_tree)
print_ast(dnf_symbol_table, dnf_tree)
```

```
+: <2>
├── psi(Ψ): <2>
│   ├── Array _a6: <2> (_i3 0)
│   └── Array A: <2 3>
└── psi(Ψ): <2>
    ├── Array _a6: <2> (_i3 0)
    └── Array B: <2 3>
```

## Reduction to ONF

```
from moa.onf import reduce_to_onf

onf_symbol_table, onf_tree = reduce_to_onf(dnf_symbol_table, dnf_tree)
print_ast(onf_symbol_table, onf_tree)
```

```
function: <2> (B A) -> _a7
├── initialize: <2> _a7
└── loop: <2> _i3
    └── assign: <2>
        ├── psi(Ψ): <2>
        │   ├── Array _a8: <1> (_i3)
        │   └── Array _a7: <2>
        └── +: <2>
            ├── psi(Ψ): <2>
            │   ├── Array _a6: <2> (_i3 0)
            │   └── Array A: <2 3>
            └── psi(Ψ): <2>
                ├── Array _a6: <2> (_i3 0)
                └── Array B: <2 3>
```

## Generate Python Source

```
from moa.backend import generate_python_source

print(generate_python_source(onf_symbol_table, onf_tree))
```

```python
def f(B, A):
    _a7 = Array((2,))
    for _i3 in range(0, 2):
        _a7[(_i3,)] = (A[(_i3, 0)] + B[(_i3, 0)])
    return _a7
```

# Development

Download [nix](https://nixos.org/nix/download.html). No other
dependencies and all builds will be identical on Linux and OSX.

## Demoing

`jupyter` environment

```
nix-shell dev.nix -A jupyter-shell
```

`ipython` environment

```
nix-shell dev.nix -A ipython-shell
```

## Testing

```
nix-build dev.nix -A python-moa
```

## Documentation

```
nix-build dev.nix -A docs
firefox result/index.html
```

## Docker

```
nix-build moa.nix -A docker
docker load < result
```

# Philosophy

This is a proof of concept which should be guided by assumptions and
goals.

1. Assumes that dimension is each operation is known. This condition
   with not much work can be relaxed to knowing an upper bound.

2. The MOA compiler is designed to be modular with clear separations:
   parsing, shape calculation, dnf reduction, onf reduction, and code
   generation.

3. All code is written with the idea that the logic can ported to any
   low level language (C for example). This means no object oriented
   design and using simple data structures. Dictionaries should be the
   highest level data structure used.

4. Performance is not a huge concern instead readability should be
   preferred. The goal of this code is to serve as documentation for
   beginners in MOA. Remember that tests are often great forms of
   documentation as well.

5. Runtime dependencies should be avoided. Testing (pytest, hypothesis)
   and Visualization (graphviz) are examples of suitable exceptions.
