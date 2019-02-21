Theory
======

Arrays
^^^^^^

In MOA everything is an array or operations on arrays. To help with
discussion we will be using the following notation. More detailed

Constants are defined as a zero dimensional array :math:`\emptyset` or :math:`< \;\; >`

A **vector** :math:`\vccc123` is a a one dimensional array.

A **multidimensional array** :math:`\aaccIcc1212`. Notice that
brackets are used to designate a two dimensional array. We can build
higher dimensional arrays by composing bracket and angled brackets
together.

.. warning::

   :math:`\accc123` is NOT a vector it is an array of dimension two

Shape :math:`\rho` rho
^^^^^^^^^^^^^^^^^^^^^^

The shape of a multidimensional array is an important concept. It is
similar to thinking of the `shape` in `numpy
<https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.shape.html>`_. In
moa the symbol for shape is :math:`\shape` and it is a unary operator on
arrays. Let's look at the examples of arrays above and inspect their
shapes.

.. math::

   \begin{align}
     \shape \emptyset & = \vc0     \\
     \shape \vccc123 & = \vc3      \\
     \shape \accc123 & = \vcc13    \\
     \shape \avcc12 & = \vccc121   \\
     \shape \aacc12 & = \vcccc1211
   \end{align}

Dimension :math:`delta` delta
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We skipped ahead of ourselves earlier when we talked about the
dimensionality of an array. For example we said that :math:`\vccc123`
is a one dimensional array. How do we define this? Let us formally
define the unary operation dimension :math:`\delta`.

**Definition:** :math:`\delta A = \rho ( \rho A )`

The following definition can rigorously define dimensionality even
though it may appear trivial. For example :math:`\delta \vccc123 =
\rho ( \rho \vccc123 ) = \rho \vc3 = \vc1`.

Pi :math:`\pi`
^^^^^^^^^^^^^^

The following unary operation pi :math:`\pi` only applies to vectors
(otherwise known as arrays of dimension one). This operation will be
needed for future derivations.

1. :math:`\pi \emptyset = 1`

2. :math:`\pi \vcccc1234 = 24`

Total :math:`\tau` tau
^^^^^^^^^^^^^^^^^^^^^^

It is from the following definition that we can define total
:math:`tau` which is the total number of elements in an array. Detailed description can be found on

**Definition:** :math:`\tau A = \pi ( \rho A )`

Using this definition we develop the total number of elements in an
array. For example :math:`\tau \vccc123 = \pi ( \shape \acccc1234 ) =
\pi \vcc14 = 4`.

1. :math:`\dims \emptyset = \pi ( \shape \emptyset ) = \pi \vc0 = 0`

2. :math:`\dims \avcc{}{} = \pi ( \shape \avcc{}{} ) = \pi \vccc120 = 0`

.. note::

   There are an infinite number of empty arrays. This concept may seem
   weird at first.
