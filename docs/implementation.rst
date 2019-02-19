Implementation
==============

Every effort has been made to restrict the data structures and
algorithms used in the implementation. For this work only
tuples(namedtuples), dictionaries, and enums have been used. All of
these data structures map to low level data structures.

Abstract Syntax Tree
--------------------

The abstract syntax tree takes inspiration from lisp where each node
is a tuple with the first node determining the ``type`` by an
enum. There are three main types of nodes for the frontend. These
types are ``array``, ``unary operation``, and ``binary
operation``. Originally plain tuples were used to represent the nodes
however this lead to ugly ``node[2][1]`` syntax. Using namedtuples
allowed a similar experience with ``node.right_node.shape``.

For example the following moa expression :math:`\vc0 \psi \transpose (A + B)` can be represented with the following ast.

.. code-block:: python

   BinaryNode(MOANodeTypes.PSI, None,
              ArrayNode(MOANodeTypes.ARRAY, (1,), None, (0,)),
              UnaryNode(MOANodeTypes.TRANSPOSE, None,
                       BinaryNode(MOANodeTypes.PLUS, None,
                                  ArrayNode(MOANodeTypes.ARRAY, None, 'A', None),
                                  ArrayNode(MOANodeTypes.ARRAY, None, 'B', None))))

Array
+++++

Tuple representation ``ArrayNode(type, shape, name, value)``

.. code-block:: python

   # Array named A with shape (1, 3) values (1, 2, 3)
   ArrayNode(MOANodeTypes.ARRAY, (1, 3), "A", (1, 2, 3))

   # Array without name and unknown values
   ArrayNode(MOANodeTypes.ARRAY, (1, 3), None, None)

Unary Operation
+++++++++++++++

Unary representation ``UnaryNode(type, shape, right_node)``

Available unary operations: ``PLUSRED``, ``MINUSRED``, ``TIMESRED``,
``DIVIDERED``, ``IOTA``, ``DIM``, ``TAU``, ``SHAPE``, ``RAV``,
``TRANSPOSE``.

.. code-block:: python

   UnaryNode(MOANodeType.TRANSPOSE, (3, 1),
             ArrayNode(MOANodeTypes.ARRAY, (1, 3), "A", (1, 2, 3)))

Binary Operation
++++++++++++++++

Binary representation ``BinaryNode(type, shape, left_node, right_node)``

Available binary operations: ``PLUS``, ``MINUS``, ``TIMES``,
``DIVIDE``, ``PSI``, ``TAKE``, ``DROP``, ``CAT``.

.. code-block:: python

   BinaryNode(MOANodeType.PLUS, (2, 3),
              ArrayNode(MOANodeTypes.ARRAY, (), "A", (1)),
              ArrayNode(MOANodeTypes.ARRAY, (2, 3), "A", None))

Symbol Table
------------

More work need to be done on unknown shape fixed dimension before
writing.

Shape Calculation
-----------------

Shape calculation can be done with a single pass post-order traversal
(left, right, root) node.
