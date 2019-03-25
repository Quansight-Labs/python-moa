Development Roadmap
===================

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

.. code-block::

   (B + +red A) + *red (A + A)

.. code-block:: python

   _a1 = numpy.zeros((4,))

   for i0 in range(0, 4):
       _a2 = numpy.full((), 1)
       for i1 in range(0, 3):
           _a2  = _a2 * (A[i1, i0] + A[i1, i0])

       _a3 = numpy.full((), 0)
       for i2 in range(0, 3):
           _a3  = _a3 + A[i2, i0]
       _a1[i0] = B[i0] + _a2 + _a3

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

Modular to enalbe domain specific reductions/optimizations. Why?
Because broadcasting, ufuncs, slice are not within Lenore's thesis and
a modular structure would allow user contributions to the reduction
engine and allow the core to be as minimal as possible. I would like
to be able to enalbe/disable moa "features".


Numpy Broadcasting
------------------

Broadcasting is a technique that


Numpy Ufuncs
------------

ufuns todo


Slice MOA Operation
-------------------

Take, drop, and reverse are not general enough.


PSI Reduction Implementation
----------------------------

Useful for a huge performance increase and reduce the number of
loops.
