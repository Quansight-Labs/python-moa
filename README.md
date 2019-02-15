# Mathematics of Arrays (MOA)

# Philosophy

This is a proof of concept with some assertions on design.

1. Assumes that dimension is each operation is known. 
   - early on it will be required that the shapes are known as well

2. The MOA compiler will always operate as a pipeline with each step
   with clear separation: parsing, shape calculation, index/reduction,
   and code generation.

2. All code is written with the idea that the logic can ported to any
   low level language (C for example). This means no object oriented
   design and using simple data structures. Dictionaries should be the
   highest level data structure used.

3. Performance is not a huge concern instead readability should be
   preferred. The goal of this code is to serve as documentation for
   beginners in moa.

4. This code is meant as an exploration tool and we would like to find
   limitations of the approach.

5. Runtime dependencies should be avoided. Testing (pytest, hypothesis)
   and Visualization (graphviz) are examples of suitable exceptions.

6. Rules are meant to be broken for good reasons.
