Machine Independent Optimization
================================

TODO

Machine Dependent Optimization
==============================

`python-moa` has the ability to have multiple backends. Generally
these optimizations fall under loop optimizations. Wikipedia has a
good overview approaches are `polyhedral and unimodular transformation
<https://en.wikipedia.org/wiki/Polytope_model>`_. These issues of
optimization fall outside of the scope of work of MOA and we need to
learn how to use other's approaches. Some of the optimizations that we
could expect the framework to perform.

 - loop fusion
 - loop ordering
 - loop reduction (psi reduction)
 - reorder expressions (distributive property +-*/)
 - dimension lifting for parallelizing algorithms
 - cache intermediate results (immediately obvious in multiple matrix multiply and fast fourier transform)

Some frameworks claim to handle pieces of this problem so they should be looked into.

 - `loopy <https://github.com/inducer/loopy>`_
 - `mlir <https://github.com/tensorflow/mlir>`_
 - `polly <https://polly.llvm.org/>`_ (looks promising)
