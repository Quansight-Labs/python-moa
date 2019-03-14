import pytest

from moa.frontend import LazyArray
from moa.ast import (
    MOANodeTypes,
    BinaryNode, UnaryNode, ArrayNode, SymbolNode
)


def test_array_single_array():
    expression = LazyArray(name='A', shape=(2, 3))
    assert expression.tree == ArrayNode(MOANodeTypes.ARRAY, None, 'A')
    assert expression.symbol_table == {
        'A': SymbolNode(MOANodeTypes.ARRAY, (2, 3), None)
    }


@pytest.mark.parametrize("function, side, operation", [
    (lambda: LazyArray(name='A', shape=(2, 3)) + 1, 'right', MOANodeTypes.PLUS),
    (lambda: 1 + LazyArray(name='A', shape=(2, 3)), 'left', MOANodeTypes.PLUS),
    (lambda: LazyArray(name='A', shape=(2, 3)) - 1, 'right', MOANodeTypes.MINUS),
    (lambda: 1 - LazyArray(name='A', shape=(2, 3)), 'left', MOANodeTypes.MINUS),
    (lambda: LazyArray(name='A', shape=(2, 3)) * 1, 'right', MOANodeTypes.TIMES),
    (lambda: 1 * LazyArray(name='A', shape=(2, 3)), 'left', MOANodeTypes.TIMES),
    (lambda: LazyArray(name='A', shape=(2, 3)) / 1, 'right', MOANodeTypes.DIVIDE),
    (lambda: 1 / LazyArray(name='A', shape=(2, 3)), 'left', MOANodeTypes.DIVIDE),
])
def test_array_single_array_binary_operation_cast(function, side, operation):
    expression = function()
    if side == 'right':
        assert expression.tree == BinaryNode(operation, None,
                                             ArrayNode(MOANodeTypes.ARRAY, None, 'A'),
                                             ArrayNode(MOANodeTypes.ARRAY, None, '_a1'))
    else:
        assert expression.tree == BinaryNode(operation, None,
                                             ArrayNode(MOANodeTypes.ARRAY, None, '_a1'),
                                             ArrayNode(MOANodeTypes.ARRAY, None, 'A'))

    assert expression.symbol_table == {
        'A': SymbolNode(MOANodeTypes.ARRAY, (2, 3), None),
        '_a1': SymbolNode(MOANodeTypes.ARRAY, (), (1,))
    }


def test_array_addition():
    expression = LazyArray(name='A', shape=(2, 3)) + LazyArray(name='B', shape=(2, 3))
    assert expression.tree == BinaryNode(MOANodeTypes.PLUS, None,
                                         ArrayNode(MOANodeTypes.ARRAY, None, 'A'),
                                         ArrayNode(MOANodeTypes.ARRAY, None, 'B'))
    assert expression.symbol_table == {
        'A': SymbolNode(MOANodeTypes.ARRAY, (2, 3), None),
        'B': SymbolNode(MOANodeTypes.ARRAY, (2, 3), None)
    }


def test_array_transpose_T():
    expression = LazyArray(name='A', shape=(2, 3)).T
    assert expression.tree == UnaryNode(MOANodeTypes.TRANSPOSE, None,
                                        ArrayNode(MOANodeTypes.ARRAY, None, 'A'))
    assert expression.symbol_table == {
        'A': SymbolNode(MOANodeTypes.ARRAY, (2, 3), None)
    }


def test_array_transpose_default():
    expression = LazyArray(name='A', shape=(2, 3)).transpose()
    assert expression.tree == UnaryNode(MOANodeTypes.TRANSPOSE, None,
                                        ArrayNode(MOANodeTypes.ARRAY, None, 'A'))
    assert expression.symbol_table == {
        'A': SymbolNode(MOANodeTypes.ARRAY, (2, 3), None)
    }


@pytest.mark.xfail
def test_array_transpose_with_vector():
    expression = LazyArray(name='A', shape=(2, 3)).transpose([1, 0])
    assert expression.tree == UnaryNode(MOANodeTypes.TRANSPOSEV, None,
                                        ArrayNode(MOANodeTypes.ARRAY, None, '_a1'),
                                        ArrayNode(MOANodeTypes.ARRAY, None, 'A'))
    assert expression.symbol_table == {
        'A': SymbolNode(MOANodeTypes.ARRAY, (2, 3), None),
        '_a1': SymbolNode(MOANodeTypes.ARRAY, (2,), (1, 0)),
    }


@pytest.mark.parametrize("symbol, operation", [
    ('+', MOANodeTypes.PLUS),
    ('-', MOANodeTypes.MINUS),
    ('*', MOANodeTypes.TIMES),
    ('/', MOANodeTypes.DIVIDE),
])
def test_array_outer_product(symbol, operation):
    expression = LazyArray(name='A', shape=(2, 3)).outer(symbol, LazyArray(name='B', shape=(1, 2)))
    assert expression.tree == BinaryNode((MOANodeTypes.DOT, operation), None,
                                         ArrayNode(MOANodeTypes.ARRAY, None, 'A'),
                                         ArrayNode(MOANodeTypes.ARRAY, None, 'B'))
    assert expression.symbol_table == {
        'A': SymbolNode(MOANodeTypes.ARRAY, (2, 3), None),
        'B': SymbolNode(MOANodeTypes.ARRAY, (1, 2), None),
    }


def test_array_index_int():
    expression = LazyArray(name='A', shape=(2, 3))[0]
    assert expression.tree == BinaryNode(MOANodeTypes.PSI, None,
                                         ArrayNode(MOANodeTypes.ARRAY, None, '_a1'),
                                         ArrayNode(MOANodeTypes.ARRAY, None, 'A'))
    assert expression.symbol_table == {
        'A': SymbolNode(MOANodeTypes.ARRAY, (2, 3), None),
        '_a1': SymbolNode(MOANodeTypes.ARRAY, (1,), (0,)),
    }


def test_array_index_tuple():
    expression = LazyArray(name='A', shape=(2, 3))[1, 0]
    assert expression.tree == BinaryNode(MOANodeTypes.PSI, None,
                                         ArrayNode(MOANodeTypes.ARRAY, None, '_a1'),
                                         ArrayNode(MOANodeTypes.ARRAY, None, 'A'))
    assert expression.symbol_table == {
        'A': SymbolNode(MOANodeTypes.ARRAY, (2, 3), None),
        '_a1': SymbolNode(MOANodeTypes.ARRAY, (2,), (1, 0)),
    }
