[![Build Status](https://travis-ci.org/Quansight-Labs/python-moa.svg?branch=master)](https://travis-ci.org/Quansight-Labs/python-moa)
[![Documentation Status](https://readthedocs.org/projects/python-moa/badge/?version=latest)](https://python-moa.readthedocs.io/en/latest/?badge=latest)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Quansight-Labs/python-moa/master)


# Mathematics of Arrays (MOA)

MOA is a mathematically rigorous approach to dealing with arrays that
was developed by [Lenore
Mullins](https://www.albany.edu/ceas/lenore-mullin.php). MOA is guided
by the following principles.

1. Everything is an array and has a shape. Scalars. Vectors. NDArray.

2. What is the shape of the computation at each step of the calculation?

Answering this guarentees no out of bounds indexing and a valid
running program.

3. What are the indicies and operations required to produce a given
   index in the result?

Once we have solved this step we have a minimal representation of the
computation that has the [Church
Rosser](https://en.wikipedia.org/wiki/Church%E2%80%93Rosser_theorem)
property. Allowing us to truely compare algorithms, analyze
algorithms, and finally map to algorithm to a low level
implementation. For further questions see the
[documentation](https://python-moa.readthedocs.io/en/latest/?badge=latest). The
documentation provides the theory, implementation details, and a
guide.

Important questions that will guide development:

 - [X] Is a simple implementation of moa possible with only knowing the dimension?
 - [X] Can we represent complex operations and einsum math: requires `+red, transpose`?
 - [ ] What is the interface for arrays? (shape, indexing function)
 - [ ] How does one wrap pre-existing numerical routines?
 
# Documentation

Documentation is available on
[python-moa.readthedocs.org](https://python-moa.readthedocs.io/en/latest/?badge=latest). The
documentation provides the theory, implementation details, and a
guide for development and usage of `python-moa`.

# Example

A few well maintained jupyter notebooks are available for
experimentation with
[binder](https://mybinder.org/v2/gh/Quansight-Labs/python-moa/master)

## Python Frontend AST Generation

```python
from moa.frontend import LazyArray

A = LazyArray(name='A', shape=(2, 3))
B = LazyArray(name='B', shape=(2, 3))

expression = ((A + B).T)[0]
expression.visualize(as_text=True)
```

```
psi(Ψ)
├── Array _a2: <1> (0)
└── transpose(Ø)
    └── +
        ├── Array A: <2 3>
        └── Array B: <2 3>
```

## Shape Calculation

```python
expression.visualize(stage='shape', as_text=True)
```

```
psi(Ψ): <2>
├── Array _a2: <1> (0)
└── transpose(Ø): <3 2>
    └── +: <2 3>
        ├── Array A: <2 3>
        └── Array B: <2 3>
```

## Reduction to DNF

```python
expression.visualize(stage='dnf', as_text=True)
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

```python
expression.visualize(stage='onf', as_text=True)
```

```
function: <2> (A B) -> _a17
├── if (not ((len(B.shape) == 2) and (len(A.shape) == 2)))
│   └── error arguments have invalid dimension
├── if (not ((3 == B.shape[1]) and ((2 == B.shape[0]) and ((3 == A.shape[1]) and (2 == A.shape[0])))))
│   └── error arguments have invalid shape
├── initialize: <2> _a17
└── loop: <2> _i3
    └── assign: <2>
        ├── psi(Ψ): <2>
        │   ├── Array _a18: <1> (_i3)
        │   └── Array _a17: <2>
        └── +: <2>
            ├── psi(Ψ): <2>
            │   ├── Array _a6: <2> (_i3 0)
            │   └── Array A: <2 3>
            └── psi(Ψ): <2>
                ├── Array _a6: <2> (_i3 0)
                └── Array B: <2 3>
```

## Generate Python Source

```python
print(expression.compile(backend='python', use_numba=True))
```

```python
@numba.jit
def f(A, B):
    
    if (not ((len(B.shape) == 2) and (len(A.shape) == 2))):
        
        raise Exception('arguments have invalid dimension')
    
    if (not ((3 == B.shape[1]) and ((2 == B.shape[0]) and ((3 == A.shape[1]) and (2 == A.shape[0]))))):
        
        raise Exception('arguments have invalid shape')
    
    _a17 = numpy.zeros((2,))
    
    for _i3 in range(0, 2):
        
        _a17[(_i3,)] = (A[(_i3, 0)] + B[(_i3, 0)])
    return _a17
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

To include benchmarks (numba, numpy, pytorch, tensorflow)

```
nix-build dev.nix -A python-moa --arg benchmark true
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

# Development Philosophy

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

# Contributing

Contributions are welcome! For bug reports or requests please submit an issue.

# Authors

The original author is [Christopher
Ostrouchov](https://github.com/costrouc). The funding that made this
project possible came from [Quansight
LLC](https://www.quansight.com/).
