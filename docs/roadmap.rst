Development Roadmap
===================

Progress (in order)

1. Reduce
2. Modular compiler
3. Broadcasting
4. Psi reduction

...


Reduce (binary operation)
-------------------------

Reduction is at the heart of most linear algebra routines and
computation in general. Thus this feature is extremely important to
implement. So far the frontend, shape, dnf stages have been
completed. Transforming the dnf to the onf is non-trivial with complex
cases. Here I will present features that I believe need to be
implemented in order for this to work.

Suppose the following moa expression with the following shapes.

 - :math:`\shape A = \vcc34`
 - :math:`\shape B = \vc4`

.. code-block:: text

   (B + +red A) + *red (A + A)


.. code-block:: python

   _a1 = numpy.zeros((4,))

   for _i0 in range(0, 4):
       _a2 = numpy.full((), 1)
       for _i1 in range(0, 3):
           _a2  = _a2 * (A[_i1, _i0] + A[_i1, _i0])

       _a3 = numpy.full((), 0)
       for _i2 in range(0, 3):
           _a3  = _a3 + A[_i2, _i0]
       _a1[_i0] = B[_i0] + _a2 + _a3

This is a simple moa expression to python code conversion but still
several difficulties emerge.

1. with the expression ``_a1[i0] = B[i0] + _a2 + _a3`` the ``_a2,
   _a3`` are at different levels in the tree thus simple preorder
   traversal will not work. A custom tree traversal will be required
   (or postorder traversal might work?). **Will custom tree traversal
   be required?**

2. After reading the dragon book would it be advantageous to form a
   data flow graph? **Would data flow constructs be required for
   compiler?**. Already have ast nodes that can represent this block
   structure (multiple statements in one command).


MOA Compiler
------------

Modularity to enable domain specific operations/shape/dnf
reductions/onf optimizations. Why? Because broadcasting, ufuncs,
slices are not within Lenore's thesis and a modular structure would
allow user contributions to the moa engine and allow the core to
be as minimal as possible. I would like to be able to enable/disable
moa "features". This would also enforce good design.

We need to clearly express what the "core" of moa is and express an
easy way to make MOA modular. Thus at least a simple dispatch
mechanism will be required for each stage? Here I am trying to express
how I would expect modules would "plug in".

Frontend
^^^^^^^^

.. code-block:: python

   A = LazyArray(shape=(3, 4), name='A', modules={
     'uarray.linalg', 'uarray.broadcasting', 'uarray.ufunc'
   })
   B = LazyArray(shape=(3, 4), name='B')

   result = A.linalg.dot(B)

   result = A.core.add(B)

   result = A + B # (maps to A.core.add)

Core would be a default required dependency but would be added in a
"plug in" manner. Module extensions would be allowed to have
"dependencies" which would allow "module" declarations to have
multiple dependencies much like a package manager.

These modules would add to each stage frontend, shape, and dnf. For
example "broadcasting" would not affect the frontend but would allow
for more possible compatible operations.

Here I am showing how lazy array could express the modules that a user


AST
^^^

Module system would at least require the ability for moa users to
specify arbitrary node types (unique symbols).

.. code-block:: python

   class MOACoreTypes(enum.Enum):
       PSI = (2, auto())
       TRANSPOSE = (1, auto())
       PLUS = (2, auto())

This would allow several enums to be used. For defining moa frontend,
shape, dnf, onf symbols.

Node(...) would use these modules to create the correct node_type
contructor. Maybe some global state is needed?

Maybe a tighter constraint is needed for nodes.

``(node_type, shape, *node_specific, *node_children)`` needs more
thinking.

Take for example an if statement ``(node_type, shape, condition_node, block)``.

Maybe a block_type could be used and then all there would be no nested blocks! Looks like an important addition that would generalize well.

Shape
^^^^^

.. code-block:: python

   calculate_shapes(symbol_table, tree, modules={'uarray.core'})

These modules would have a standardized way to specifying shape
function mappings. Most likely a dictionary.

Only one shape is allowed for each shape function. Thus one of two things must happen.

 - modules would override the shape function in order? Seems
   complicated but necessary in where multiple users have different
   implementations.
 - would throw an error stating that multiple functions are defined
   for a specific shape.

``(node_type, shape_function)``

DNF Reduction
^^^^^^^^^^^^^

Multiple possible reductions should not be possible for a given tree. Or should it?

Need some type of reduction language for `(pattern, dnf_function)`.

ONF Reduction
^^^^^^^^^^^^^

TODO need to think on this more.

Numpy Broadcasting
------------------

Broadcasting is a technique that allows for mismatching shapes to
apply an n-ary operation.

Suppose the following ternary operation expression ``op`` with the
following shapes.

 - :math:`\shape A = \vccc345`
 - :math:`\shape B = \vccc311`
 - :math:`\shape C = \vcccc2115`

The resulting shape would be :math:`\vcccc2345`.

This leads to the following indexing code.

.. code-block:: python

   result[i, j, k, l] = A[j, k, l] + B[j, 0, 0] + C[i, 0, 0, l]

The following rules define broadcasting.

1. For missing dimensions fill with ``1``s on the left hand side

2. Positional shape elements must all be equal or ``1``s

For symbolic shapes this constraint leads to multiple possible code
paths. Suppose.

Suppose the following ternary operation expression ``op`` with the
following shapes.

 - :math:`\shape A = \vccc345`
 - :math:`\shape B = \vccc3n1`

``n`` can equal either 1 or 4.

.. code-block:: python

   # n = 1
   result[i, j, k] = A[i, j, k] + B[i, 0, 0]

   # n = 4
   result[i, j, k] = A[i, j, k] + B[i, j, 0]

This will need to be solved for symbolic shapes.

Also note that a max function will be required to determine shape.

 - :math:`\shape A = \vccc3m5`
 - :math:`\shape B = \vccc3n1`

The resulting shape is ``k = max(n, m)`` :math:`\vccc3k4`.

Numpy Ufuncs
------------

ufuncs further documented.


Slice MOA Operation
-------------------

Take, drop, and reverse are not general enough.


Conditional Indexing
--------------------

Allowing a selection of elements to be taken from an array. The resulting shape.

.. code-block:: python

   A[A > 5]


Reshape
-------

TODO

PSI Reduction Implementation
----------------------------

Useful for a huge performance increase and reduce the number of
loops.
