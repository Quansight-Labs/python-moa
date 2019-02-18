[![Build Status](https://travis-ci.org/costrouc/python-moa.svg?branch=master)](https://travis-ci.org/costrouc/python-moa)

# Mathematics of Arrays (MOA)

Important questions that should guide development most likely in this order:

 - [ ] Is a simple implementation of moa possible with only knowing the dimension?
 - [ ] Can we represent complex operations and einsum math: requires `+red, omega`?
 - [ ] What is the interface for arrays? (shape, indexing function)
 - [ ] How does one wrap pre-existing numerical routines?

# Example

## Python Frontend AST Generation

```python
from moa.frontend import MOAParser
from moa.visualize import print_ast

parser = MOAParser()
ast = parser.parse('<0> psi (tran(A ^ <2 3> + B ^ <2 3>))')
print_ast(ast)
```

```
psi(Ψ)
├── Array <1>:  (0)
└── transpose(Ø)
    └── +
        ├── Array <2 3>
        └── Array <2 3>
```

## Shape Calculation

```
from moa.shape import calculate_shapes

shape_ast = calculate_shapes(ast)
print_ast(shape_ast)
```

```
psi(Ψ) <2>
├── Array <1>:  (0)
└── transpose(Ø) <3 2>
    └── + <2 3>
        ├── Array <2 3>
        └── Array <2 3>
```

## AST Reduction

```
from moa.reduction import reduce_ast

symbol_table, reduced_ast = reduce_ast(shape_ast)
print_ast(reduced_ast)
```

```
+ <2>
├── psi(Ψ) <2>
│   ├── Array <2>:  (i0 0)
│   └── Array <2 3>
└── psi(Ψ) <2>
    ├── Array <2>:  (i0 0)
    └── Array <2 3>
```

## Python Backend Code Generation

```
import astunparse

from moa.backend import python_backend

ast = python_backend(reduced_ast)
print(astunparse.unparse(ast))
```

```python
(A[('i0', 0)] + B[('i0', 0)])
```

# AST Representation

Initially I used strictly tuples for representing the ast but using
indexes only lead to unreadable code. I have used `namedtuple` which
easily maps to `C structs`. `node_type` is a python enum which
determines the node type an easily maps to c enums. This will need
some work when dealing with operations of operations like `omega` and
`+red`.

 - array `(node_type, shape, name, value)`

 - unary functions `(node_type, shape, right_node)`

 - binary functions `(node_type, shape, left_node, right_node)`

## Symbol Table

For now a symbol table is used to generate the index variables once
the resulting shape is known. However, more work will be done soon to
include named arrays and allowing for known dimension variable shape
arrays.

# Development

Maybe this is a neat project to show off my favorite build/development
tool of all time!? Please just try. Download
[nix](https://nixos.org/nix/download.html) and you will see. Nope no
other dependencies and all our builds will be identical on Linux and
OSX.

## Demoing / Jupyter Lab

```
nix-shell -A shell
```

## Testing

```
nix-build -A python-moa
```

## Documentation

```
nix-build -A docs
firefox result/index.html
```

## Docker

```
nix-build -A docker
docker load < result
```

# Philosophy

This is a proof of concept which should be guided by assumptions and
goals.

1. Assumes that dimension is each operation is known. 
   - early on it will be required that the shapes are known as well

2. The MOA compiler is designed to be modular with clear separations:
   parsing, shape calculation, reduction, and code generation.

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
