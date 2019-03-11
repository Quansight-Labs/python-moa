Implementation
==============

Every effort has been made to restrict the data structures and
algorithms used in the implementation. For this work only
tuples(namedtuples), dictionaries, and enums have been used. All of
which map to low level data structures.

Symbol Table
------------



Abstract Syntax Tree
--------------------

The abstract syntax tree takes inspiration from lisp where each node
is a tuple with the first node determining the ``node_type`` by an
enum. There are three main types of nodes for the frontend. These
types are ``array``, ``unary operation``, and ``binary
operation``. Originally plain tuples were used to represent the nodes
however this lead to ugly ``node[2][1]`` syntax. Using namedtuples
allowed a similar experience with ``node.right_node.shape``. The
abstract syntax tree is heavily tied to the symbol table.

For example the following moa expression :math:`\vc0 \psi \transpose
(A + B)` can be represented with the following symbol table and ast.

.. doctest::

   >>> {'A': SymbolNode(MOANodeTypes.ARRAY, None, None),
   ...  'B': SymbolNode(MOANodeTypes.ARRAY, None, None),
   ...  '_a0': SymbolNode(MOANodeTypes.ARRAY, (1,), (0,))}
   {'A': SymbolNode(node_type=<MOANodeTypes.ARRAY: 1>, shape=None, value=None), 'B': SymbolNode(node_type=<MOANodeTypes.ARRAY: 1>, shape=None, value=None), '_a0': SymbolNode(node_type=<MOANodeTypes.ARRAY: 1>, shape=(1,), value=(0,))}

.. doctest::

   >>> BinaryNode(MOANodeTypes.PSI, None,
   ...            ArrayNode(MOANodeTypes.ARRAY, None, '_a0'),
   ...                      UnaryNode(MOANodeTypes.TRANSPOSE, None,
   ...                                BinaryNode(MOANodeTypes.PLUS, None,
   ...                                           ArrayNode(MOANodeTypes.ARRAY, None, 'A'),
   ...                                           ArrayNode(MOANodeTypes.ARRAY, None, 'B'))))
   BinaryNode(node_type=<MOANodeTypes.PSI: 205>, shape=None, left_node=ArrayNode(node_type=<MOANodeTypes.ARRAY: 1>, shape=None, symbol_node='_a0'), right_node=UnaryNode(node_type=<MOANodeTypes.TRANSPOSE: 110>, shape=None, right_node=BinaryNode(node_type=<MOANodeTypes.PLUS: 201>, shape=None, left_node=ArrayNode(node_type=<MOANodeTypes.ARRAY: 1>, shape=None, symbol_node='A'), right_node=ArrayNode(node_type=<MOANodeTypes.ARRAY: 1>, shape=None, symbol_node='B'))))


Array
+++++

Tuple representation ``ArrayNode(type, shape, name, value)``

Create array named A with shape (1, 3) values (1, 2, 3)

.. doctest::

   >>> ArrayNode(MOANodeTypes.ARRAY, (1, 3), "A")
   ArrayNode(node_type=<MOANodeTypes.ARRAY: 1>, shape=(1, 3), symbol_node='A')

Create array without name and unknown values

.. doctest::

   >>> ArrayNode(MOANodeTypes.ARRAY, (1, 3), '_a0')
   ArrayNode(node_type=<MOANodeTypes.ARRAY: 1>, shape=(1, 3), symbol_node='_a0')

Unary Operation
+++++++++++++++

Unary representation ``UnaryNode(type, shape, right_node)``

Available unary operations: ``PLUSRED``, ``MINUSRED``, ``TIMESRED``,
``DIVIDERED``, ``IOTA``, ``DIM``, ``TAU``, ``SHAPE``, ``RAV``,
``TRANSPOSE``.

.. doctest::

   >>> UnaryNode(MOANodeTypes.TRANSPOSE, (3, 1),
   ...          ArrayNode(MOANodeTypes.ARRAY, (1, 3), "A"))
   UnaryNode(node_type=<MOANodeTypes.TRANSPOSE: 110>, shape=(3, 1), right_node=ArrayNode(node_type=<MOANodeTypes.ARRAY: 1>, shape=(1, 3), symbol_node='A'))

Binary Operation
++++++++++++++++

Binary representation ``BinaryNode(type, shape, left_node, right_node)``

Available binary operations: ``PLUS``, ``MINUS``, ``TIMES``,
``DIVIDE``, ``PSI``, ``TAKE``, ``DROP``, ``CAT``, ``TRANSPOSEV``.

.. doctest::

   >>> BinaryNode(MOANodeTypes.PLUS, (2, 3),
   ...           ArrayNode(MOANodeTypes.ARRAY, (), "A"),
   ...           ArrayNode(MOANodeTypes.ARRAY, (2, 3), "B"))
   BinaryNode(node_type=<MOANodeTypes.PLUS: 201>, shape=(2, 3), left_node=ArrayNode(node_type=<MOANodeTypes.ARRAY: 1>, shape=(), symbol_node='A'), right_node=ArrayNode(node_type=<MOANodeTypes.ARRAY: 1>, shape=(2, 3), symbol_node='B'))

Symbol Table
------------

More work need to be done on unknown shape fixed dimension before
writing.

Shape Calculation
-----------------

Shape calculation can be done with a single pass post-order traversal
(left, right, root) node.

How shapes are calculated for given types.

Array
+++++

For now the shape of an array is required to be defined on the node
and cannot be computed from another value. Thus the second argument
(shape) cannot be ``None``.

.. code-block:: python

   ArrayNode(MOANodeTypes.ARRAY, (2, 3), None, None))

Transpose
+++++++++

Transpose has two forms a unary and binary definition.

.. math::

   \transpose A = (\reverse \iota \dims A) \transpose A

For the simple case of the unary operator.


Reduction
---------

Reduction can be done with a single pass pre-order traversal with
multiple replacements on each node (root, left, right) node. These
replacements have the Church-Rosser property meaning that when
applying reductions the ordering of the replacements does not change
the final result.
