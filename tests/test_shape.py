import copy

import pytest

from moa.ast import (
    MOANodeTypes,
    ArrayNode, UnaryNode, BinaryNode, SymbolNode, ReduceNode
)
from moa.shape import (
    calculate_shapes,
    is_vector, is_scalar
)


def test_is_scalar():
    symbol_table = {'_a1': SymbolNode(MOANodeTypes.ARRAY, (), (3,))}
    node = ArrayNode(MOANodeTypes.ARRAY, (), '_a1')
    assert is_scalar(symbol_table, node)


def test_is_not_scalar_1d(): # vector
    symbol_table = {'_a1': SymbolNode(MOANodeTypes.ARRAY, (2,), (1, 2))}
    node = ArrayNode(MOANodeTypes.ARRAY, None, '_a1')
    assert not is_scalar(symbol_table, node)


def test_is_not_scalar_2d(): # 2D array
    symbol_table = {'_a1': SymbolNode(MOANodeTypes.ARRAY, (2, 3), (1, 2, 3, 4, 5, 6))}
    node = ArrayNode(MOANodeTypes.ARRAY, None, '_a1')
    assert not is_scalar(symbol_table, node)


def test_is_vector():
    symbol_table = {'_a1': SymbolNode(MOANodeTypes.ARRAY, (5,), (1, 2, 3, 4, 5))}
    node = ArrayNode(MOANodeTypes.ARRAY, None, '_a1')
    assert is_vector(symbol_table, node)


def test_is_not_vector_1d(): # scalar
    symbol_table = {'asdf': SymbolNode(MOANodeTypes.ARRAY, (), (3,))}
    node = ArrayNode(MOANodeTypes.ARRAY, None, 'asdf')
    assert not is_vector(symbol_table, node)


def test_is_not_vector_2d(): # 2D array
    symbol_table = {'A': SymbolNode(MOANodeTypes.ARRAY, (5, 1), (1, 2, 3, 4, 5))}
    node = ArrayNode(MOANodeTypes.ARRAY, None, 'A')
    assert not is_vector(symbol_table, node)




@pytest.mark.parametrize("symbol_table, tree, shape_symbol_table, shape_tree", [
    # ARRAY
    ({'A': SymbolNode(MOANodeTypes.ARRAY, (2,), (3, 5))},
     ArrayNode(MOANodeTypes.ARRAY, None, 'A'),
     {'A': SymbolNode(MOANodeTypes.ARRAY, (2,), (3, 5))},
     ArrayNode(MOANodeTypes.ARRAY, (2,), 'A')),
    # TRANSPOSE
    ({'_a0': SymbolNode(MOANodeTypes.ARRAY, (3, 4, 5), None)},
     UnaryNode(MOANodeTypes.TRANSPOSE, None,
               ArrayNode(MOANodeTypes.ARRAY, None, '_a0')),
     {'_a0': SymbolNode(MOANodeTypes.ARRAY, (3, 4, 5), None)},
     UnaryNode(MOANodeTypes.TRANSPOSE, (5, 4, 3),
               ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), '_a0'))),
    # TRANSPOSE VECTOR
    ({'_a1': SymbolNode(MOANodeTypes.ARRAY, (3,), (2, 0, 1)),
      'B': SymbolNode(MOANodeTypes.ARRAY, (3, 4, 5), None)},
     BinaryNode(MOANodeTypes.TRANSPOSEV, None,
               ArrayNode(MOANodeTypes.ARRAY, None, '_a1'),
               ArrayNode(MOANodeTypes.ARRAY, None, 'B')),
     {'_a1': SymbolNode(MOANodeTypes.ARRAY, (3,), (2, 0, 1)),
      'B': SymbolNode(MOANodeTypes.ARRAY, (3, 4, 5), None)},
     BinaryNode(MOANodeTypes.TRANSPOSEV, (4, 5, 3),
               ArrayNode(MOANodeTypes.ARRAY, (3,), '_a1'),
               ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), 'B'))),
    # SHAPE
    ({'_a1': SymbolNode(MOANodeTypes.ARRAY, (3, 2, 1), None)},
     UnaryNode(MOANodeTypes.SHAPE, None,
               ArrayNode(MOANodeTypes.ARRAY, (3, 2, 1), '_a1')),
     {'_a1': SymbolNode(MOANodeTypes.ARRAY, (3, 2, 1), None)},
     UnaryNode(MOANodeTypes.SHAPE, (3,),
               ArrayNode(MOANodeTypes.ARRAY, (3, 2, 1), '_a1'))),
    # PSI
    ({'_a1': SymbolNode(MOANodeTypes.ARRAY, (2,), (3, 4)),
      'A': SymbolNode(MOANodeTypes.ARRAY, (4, 5, 6), None)},
     BinaryNode(MOANodeTypes.PSI, None,
                ArrayNode(MOANodeTypes.ARRAY, None, '_a1'),
                ArrayNode(MOANodeTypes.ARRAY, None, 'A')),
     {'_a1': SymbolNode(MOANodeTypes.ARRAY, (2,), (3, 4)),
      'A': SymbolNode(MOANodeTypes.ARRAY, (4, 5, 6), None)},
     BinaryNode(MOANodeTypes.PSI, (6,),
                ArrayNode(MOANodeTypes.ARRAY, (2,), '_a1'),
                ArrayNode(MOANodeTypes.ARRAY, (4, 5, 6), 'A'))),
])
def test_shape_unit(symbol_table, tree, shape_symbol_table, shape_tree):
    symbol_table_copy = copy.deepcopy(symbol_table)
    new_symbol_table, new_tree = calculate_shapes(symbol_table, tree)
    assert symbol_table == symbol_table_copy
    assert new_tree == shape_tree
    assert new_symbol_table == shape_symbol_table


@pytest.mark.parametrize("operation", [
    MOANodeTypes.PLUS, MOANodeTypes.MINUS,
    MOANodeTypes.DIVIDE, MOANodeTypes.TIMES,
])
def test_shape_unit_outer_plus_minus_multiply_divide_no_symbol(operation):
    symbol_table = {
        'A': SymbolNode(MOANodeTypes.ARRAY, (1, 2, 3), None),
        'B': SymbolNode(MOANodeTypes.ARRAY, (4, 5, 6), None)
    }
    symbol_table_copy = copy.deepcopy(symbol_table)
    tree = BinaryNode((MOANodeTypes.DOT, operation), None,
                          ArrayNode(MOANodeTypes.ARRAY, None, 'A'),
                          ArrayNode(MOANodeTypes.ARRAY, None, 'B'))
    new_symbol_tree, new_tree = calculate_shapes(symbol_table, tree)
    assert symbol_table == symbol_table_copy
    assert new_tree == BinaryNode((MOANodeTypes.DOT, operation), (1, 2, 3, 4, 5, 6),
                                  ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3), 'A'),
                                  ArrayNode(MOANodeTypes.ARRAY, (4, 5, 6), 'B'))
    assert new_symbol_tree == symbol_table


@pytest.mark.parametrize("operation", [
    MOANodeTypes.PLUS, MOANodeTypes.MINUS,
    MOANodeTypes.DIVIDE, MOANodeTypes.TIMES,
])
def test_shape_unit_reduce_plus_minus_multiply_divide_no_symbol(operation):
    symbol_table = {
        'A': SymbolNode(MOANodeTypes.ARRAY, (1, 2, 3), None),
    }
    symbol_table_copy = copy.deepcopy(symbol_table)
    tree = ReduceNode((MOANodeTypes.REDUCE, operation), None, None,
                          ArrayNode(MOANodeTypes.ARRAY, None, 'A'))
    new_symbol_tree, new_tree = calculate_shapes(symbol_table, tree)
    assert symbol_table == symbol_table_copy
    assert new_tree == ReduceNode((MOANodeTypes.REDUCE, operation), (2, 3), None,
                                  ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3), 'A'))

    assert new_symbol_tree == symbol_table


@pytest.mark.parametrize("operation", [
    MOANodeTypes.PLUS, MOANodeTypes.MINUS,
    MOANodeTypes.DIVIDE, MOANodeTypes.TIMES,
])
def test_shape_unit_plus_minus_multiply_divide_no_symbol(operation):
    symbol_table = {
        'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4, 5), None),
        'B': SymbolNode(MOANodeTypes.ARRAY, (3, 4, 5), None)
    }

    def generate_test_ast(operation):
        return BinaryNode(operation, None,
                          ArrayNode(MOANodeTypes.ARRAY, None, 'A'),
                          ArrayNode(MOANodeTypes.ARRAY, None, 'B'))

    def generate_expected_ast(operation):
        return BinaryNode(operation, (3, 4, 5),
                          ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), 'A'),
                          ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), 'B'))

    symbol_table_copy = copy.deepcopy(symbol_table)
    new_symbol_tree, new_tree = calculate_shapes(symbol_table, generate_test_ast(operation))
    assert symbol_table == symbol_table_copy
    assert new_tree == generate_expected_ast(operation)
    assert new_symbol_tree == symbol_table


@pytest.mark.parametrize("operation", [
    MOANodeTypes.PLUS, MOANodeTypes.MINUS,
    MOANodeTypes.DIVIDE, MOANodeTypes.TIMES,
])
def test_shape_scalar_plus_minus_multiply_divide_no_symbol(operation):
    symbol_table = {
        'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4, 5), None),
        'B': SymbolNode(MOANodeTypes.ARRAY, (), (0,))
    }

    def generate_test_ast(operation):
        return BinaryNode(operation, None,
                          ArrayNode(MOANodeTypes.ARRAY, None, 'A'),
                          ArrayNode(MOANodeTypes.ARRAY, None, 'B'))

    def generate_expected_ast(operation):
        return BinaryNode(operation, (3, 4, 5),
                          ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), 'A'),
                          ArrayNode(MOANodeTypes.ARRAY, (), 'B'))

    symbol_table_copy = copy.deepcopy(symbol_table)
    new_symbol_table, new_tree = calculate_shapes(symbol_table, generate_test_ast(operation))
    assert symbol_table == symbol_table_copy
    assert new_tree == generate_expected_ast(operation)
    assert new_symbol_table == symbol_table
