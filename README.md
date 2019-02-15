# Mathematics of Arrays (MOA)

Important questions that should guide development:

 - [ ] Is a simple implementation of moa possible?
 - [ ] Can we represent complex operations and einsum math?
 - [ ] How does one wrap pre-existing numerical routines?

# Philosophy

This is a proof of concept with some assertions on design.

1. Assumes that dimension is each operation is known. 
   - early on it will be required that the shapes are known as well

2. The MOA compiler will always operate as a pipeline with each step
   with clear separation: parsing, shape calculation, reduction, and
   code generation.

2. All code is written with the idea that the logic can ported to any
   low level language (C for example). This means no object oriented
   design and using simple data structures. Dictionaries should
   be the highest level data structure used.

3. Performance is not a huge concern instead readability should be
   preferred. The goal of this code is to serve as documentation for
   beginners in MOA. Remember that tests are often great forms of
   documentation as well.

4. This code is meant as an exploration tool and we would like to find
   limitations of the approach.

5. Runtime dependencies should be avoided. Testing (pytest, hypothesis)
   and Visualization (graphviz) are examples of suitable exceptions.

6. Rules are meant to be broken for good reasons.


# AST Representation

Initially I used strictly tuples for representing the ast but using
indexes only lead to unreadable code. I have used `namedtuple` which
easily maps to `C structs`.

 - array `(node_type, shape, name, value)`

 - unary functions `(node_type, shape, right_node)`

 - binary functions `(node_type, shape, left_node, right_node)`
