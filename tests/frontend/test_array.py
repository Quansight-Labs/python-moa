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


@pytest.mark.xfail
def test_array_single_array_addition_cast():
    expression = LazyArray(name='A', shape=(2, 3)) + 1
    assert expression.tree == BinaryNode(MOANodeTypes.ADD, None,
                                         ArrayNode(MOANodeTypes.ARRAY, None, 'A'),
                                         ArrayNode(MOANodeTypes.ARRAY, None, 'B'))
    assert expression.symbol_table == {
        'A': SymbolNode(MOANodeTypes.ARRAY, (2, 3), None),
        '_a1': SymbolNode(MOANodeTypes.ARRAY, (), None)
    }


@pytest.mark.xfail
def test_array_addition():
    expression = LazyArray(name='A', shape=(2, 3)) + LazyArray(name='B', shape=(2, 3))
    assert expression.tree == BinaryNode(MOANodeTypes.ADD, None,
                                         ArrayNode(MOANodeTypes.ARRAY, None, 'A'),
                                         ArrayNode(MOANodeTypes.ARRAY, None, 'B'))
    assert expression.symbol_table == {
        'A': SymbolNode(MOANodeTypes.ARRAY, (2, 3), None),
        'B': SymbolNode(MOANodeTypes.ARRAY, (2, 3), None)
    }


def test_array_transpose():
    expression = LazyArray(name='A', shape=(2, 3)).transpose()
    assert expression.tree == UnaryNode(MOANodeTypes.TRANSPOSE, None,
                                        ArrayNode(MOANodeTypes.ARRAY, None, 'A'))
    assert expression.symbol_table == {
        'A': SymbolNode(MOANodeTypes.ARRAY, (2, 3), None)
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
