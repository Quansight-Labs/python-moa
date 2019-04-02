Introduction
============

Python-moa (mathematics of arrays) is an approach to a high level
tensor compiler that is based on the work of `Lenore Mullins
<https://www.albany.edu/ceas/lenore-mullin.php>`_ and her
`dissertation
<https://www.researchgate.net/publication/308893116_A_Mathematics_of_Arrays>`_. It
is trying to solve the same problems as other technologies such as the
`taco compiler <http://tensor-compiler.org/>`_ and the `xla compiler
<https://www.tensorflow.org/xla>`_. However, it takes a much different
approach than others guided by the following principles.

1. What is the shape? Everything has a shape. scalars, vectors, arrays, operations, and functions.

2. What are the given indicies and operations required to produce a given index in the result?

Having a compiler that is guided upon these principles allows for high
level reductions that other compilers will miss and allows for
optimization of algorithms as a whole. Keep in mind that MOA is
**NOT** a compiler. It is a theory that guides compiler development.


Frontend
--------

.. code-block:: python

   from moa.frontend import LazyArray

   A = LazyArray(shape=('n', 'm'), name='A')
   B = LazyArray(shape=('k', 'l'), name='B')

   expression = (A + B).T.reduce('+')[0]
   print(expression.compile(use_numba=True, include_conditions=False))

.. image:: ./images/frontend.svg

.. image:: ./images/shape.svg

.. image:: ./images/dnf.svg

.. code-block:: python

   @numba.jit
   def f(A, B):
       n = A.shape[0]
       m = A.shape[1]
       k = B.shape[0]
       l = B.shape[1]

       _a21 = numpy.zeros(())
       _a19 = numpy.zeros(())

       _a21 = 0
       for _i10 in range(0, m, 1):
           _a21 = (_a21 + (A[(0, _i10)] + B[(0, _i10)]))
       _a19[()] = _a21
       return _a19
