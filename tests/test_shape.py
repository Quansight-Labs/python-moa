import pytest

from moa.ast import MOANodeTypes, ArrayNode, UnaryNode, BinaryNode
from moa.shape import (
    calculate_shapes,
    is_vector, is_scalar
)


def test_is_scalar():
    node = ArrayNode(MOANodeTypes.ARRAY, (), '_1')
    symbol_table = {'_1': (MOANodeTypes.ARRAY, (), (3,))}
    assert is_scalar(node, symbol_table)


def test_is_not_scalar(): # vector
    node = ArrayNode(MOANodeTypes.ARRAY, None, '_1')
    symbol_table = {'_1', (MOANodeTypes.ARRAY, (2,), (1, 2))}
    assert not is_scalar(tree, symbol_table)


def test_is_not_scalar(): # 2D array
    node = ArrayNode(MOANodeTypes.ARRAY, None, '_1')
    symbol_table = {'_1', (MOANodeTypes.ARRAY, (2, 3), (1, 2, 3, 4, 5, 6))}
    assert not is_scalar(node, symbol_table)


def test_is_vector():
    tree = ArrayNode(MOANodeTypes.ARRAY, None, '_1')
    symbol_table = {'_1', (MOANodeTypes.ARRAY, (5,), (1, 2, 3, 4, 5))}
    assert is_vector(node, symbol_table)


def test_is_not_vector(): # 2D array
    tree = ArrayNode(MOANodeTypes.ARRAY, None, 'A')
    symbol_table = {'A', (MOANodeTypes.ARRAY, (5, 1), (1, 2, 3, 4, 5))}
    assert not is_vector(node, symbol_table)


def test_is_not_vector(): # scalar
    node = ArrayNode(MOANodeTypes.ARRAY, None, 'asdf')
    symbol_table = {'asdf': (MOANodeTypes.ARRAY, (), (3,))}
    assert not is_vector(node, symbol_table)


@pytest.mark.parametrize("symbol_table, tree, shape_symbol_table, shape_tree", [
    # ARRAY
    ({'A': (MOANodeTypes.ARRAY, (2,), (3, 5))},
     ArrayNode(MOANodeTypes.ARRAY, None, 'A'),
     ArrayNode(MOANodeTypes.ARRAY, (2,), 'A')),
    # TRANSPOSE
    ({'_1': (MOANodeTypes.ARRAY, (3, 4, 5), None)},
     UnaryNode(MOANodeTypes.TRANSPOSE, None,
               ArrayNode(MOANodeTypes.ARRAY, None, '_1')),
     UnaryNode(MOANodeTypes.TRANSPOSE, (5, 4, 3),
               ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), '_1'))),
    # TRANSPOSE VECTOR
    ({'_1': (MOANodeTypes.ARRAY, (3,), (2, 0, 1)),
      'B': (MOANodeTypes.ARRAY, (3, 4, 5), None)},
     BinaryNode(MOANodeTypes.TRANSPOSEV, None,
               ArrayNode(MOANodeTypes.ARRAY, None, '_1'),
               ArrayNode(MOANodeTypes.ARRAY, None, 'B')),
     BinaryNode(MOANodeTypes.TRANSPOSEV, (4, 5, 3),
               ArrayNode(MOANodeTypes.ARRAY, (3,), '_1'),
               ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), 'B'))),
    # PLUSRED
    ({'A': (MOANodeTypes.ARRAY, (3, 4, 5), None)},
     UnaryNode(MOANodeTypes.PLUSRED, None,
                ArrayNode(MOANodeTypes.ARRAY, None, 'A')),
     UnaryNode(MOANodeTypes.PLUSRED, (4, 5),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), 'A'))),
    # PSI
    ({'_1': (MOANodeTypes.ARRAY, (2,), (3, 5)),
      'A': (MOANodeTypes.ARRAY, (4, 5, 6), None)},
     BinaryNode(MOANodeTypes.PSI, None,
                ArrayNode(MOANodeTypes.ARRAY, None, '_1'),
                ArrayNode(MOANodeTypes.ARRAY, None, 'A')),
     BinaryNode(MOANodeTypes.PSI, (6,),
                ArrayNode(MOANodeTypes.ARRAY, (2,), None, '_1'),
                ArrayNode(MOANodeTypes.ARRAY, (4, 5, 6), 'A'))),
    # PLUS EQUAL
    ({'A': (MOANodeTypes.ARRAY, (3, 4, 5), None),
      'B': (MOANodeTypes.ARRAY, (3, 4, 5), None)},
     BinaryNode(MOANodeTypes.PLUS, None,
                ArrayNode(MOANodeTypes.ARRAY, None, 'A'),
                ArrayNode(MOANodeTypes.ARRAY, None, 'B')),
     BinaryNode(MOANodeTypes.PLUS, (3, 4, 5),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), 'A'),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), 'B'))),
    # MINUS EQUAL
    ({'A': (MOANodeTypes.ARRAY, (3, 4, 5), None),
      'B': (MOANodeTypes.ARRAY, (3, 4, 5), None)},
     BinaryNode(MOANodeTypes.MINUS, None,
                ArrayNode(MOANodeTypes.ARRAY, None, 'A'),
                ArrayNode(MOANodeTypes.ARRAY, None, 'B')),
     BinaryNode(MOANodeTypes.MINUS, (3, 4, 5),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), 'A'),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), 'B'))),
    # DIVIDE EQUAL
    ({'A': (MOANodeTypes.ARRAY, (3, 4, 5), None),
      'B': (MOANodeTypes.ARRAY, (3, 4, 5), None)},
     BinaryNode(MOANodeTypes.DIVIDE, None,
                ArrayNode(MOANodeTypes.ARRAY, None, 'A'),
                ArrayNode(MOANodeTypes.ARRAY, None, 'B')),
     BinaryNode(MOANodeTypes.DIVIDE, (3, 4, 5),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), 'A'),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), 'B'))),
    # TIMES EQUAL
    ({'A': (MOANodeTypes.ARRAY, (3, 4, 5), None),
      'B': (MOANodeTypes.ARRAY, (3, 4, 5), None)},
     BinaryNode(MOANodeTypes.TIMES, None,
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), None, None),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), None, None)),
     BinaryNode(MOANodeTypes.TIMES, (3, 4, 5),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), None, None),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), None, None))),
    # PLUS SCALAR EXTENSION
    ({},
     BinaryNode(MOANodeTypes.PLUS, None,
                ArrayNode(MOANodeTypes.ARRAY, (), None, (4,)),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), None, None)),
     BinaryNode(MOANodeTypes.PLUS, (3, 4, 5),
                ArrayNode(MOANodeTypes.ARRAY, (), None, (4,)),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), None, None))),
    # MINUS SCALAR EXTENSION
    ({},
     BinaryNode(MOANodeTypes.MINUS, None,
                ArrayNode(MOANodeTypes.ARRAY, (), None, (4,)),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), None, None)),
     BinaryNode(MOANodeTypes.MINUS, (3, 4, 5),
                ArrayNode(MOANodeTypes.ARRAY, (), None, (4,)),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), None, None))),
    # TIMES SCALAR EXTENSION
    ({},
     BinaryNode(MOANodeTypes.TIMES, None,
                ArrayNode(MOANodeTypes.ARRAY, (), None, (4,)),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), None, None)),
     BinaryNode(MOANodeTypes.TIMES, (3, 4, 5),
                ArrayNode(MOANodeTypes.ARRAY, (), None, (4,)),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), None, None))),
    # DIVIDE SCALAR EXTENSION
    ({},
     BinaryNode(MOANodeTypes.DIVIDE, None,
                ArrayNode(MOANodeTypes.ARRAY, (), None, (4,)),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), None, None)),
     BinaryNode(MOANodeTypes.DIVIDE, (3, 4, 5),
                ArrayNode(MOANodeTypes.ARRAY, (), None, (4,)),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), None, None))),
])
def test_shape_unit(tree, result):
    new_tree = calculate_shapes(tree)
    assert new_tree == result


@pytest.mark.parametrize("tree,result", [
    # Lenore Simple Example #1 06/01/2018
    (BinaryNode(MOANodeTypes.PSI, None,
                ArrayNode(MOANodeTypes.ARRAY, (1,), None, (0,)),
                UnaryNode(MOANodeTypes.TRANSPOSE, None,
                          BinaryNode(MOANodeTypes.PLUS, None,
                                     ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A', None),
                                     ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B', None)))),
     (MOANodeTypes.PSI, (3,),
      (MOANodeTypes.ARRAY, (1,), None, (0,)),
      (MOANodeTypes.TRANSPOSE, (4, 3),
       (MOANodeTypes.PLUS, (3, 4),
        (MOANodeTypes.ARRAY, (3, 4), 'A', None),
        (MOANodeTypes.ARRAY, (3, 4), 'B', None))))),
])
def test_shape_integration(tree, result):
    new_tree = calculate_shapes(tree)
    assert new_tree == result
