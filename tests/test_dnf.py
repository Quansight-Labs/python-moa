import copy

import pytest

from moa.ast import (
    MOANodeTypes,
    BinaryNode, UnaryNode, ArrayNode, SymbolNode, ReduceNode,
)
from moa.dnf import (
    reduce_to_dnf,
    add_indexing_node,
    _reduce_psi_psi,
    _reduce_psi_transpose, _reduce_psi_transposev,
    _reduce_psi_assign,
    _reduce_psi_reduce_plus_minus_times_divide,
    _reduce_psi_outer_plus_minus_times_divide,
    _reduce_psi_plus_minus_times_divide,
)


def test_add_indexing_node():
    symbol_table = {'A': SymbolNode(MOANodeTypes.ARRAY, (2, 3), (1, 2, 3, 4, 5, 6))}
    symbol_table_copy = copy.deepcopy(symbol_table)
    tree = ArrayNode(MOANodeTypes.ARRAY, (2, 3), 'A')
    new_symbol_table, new_tree = add_indexing_node(symbol_table, tree)
    assert symbol_table == symbol_table_copy
    assert new_symbol_table == {
        'A': SymbolNode(MOANodeTypes.ARRAY, (2, 3), (1, 2, 3, 4, 5, 6)),
        '_i1': SymbolNode(MOANodeTypes.INDEX, (), (0, 2)),
        '_i2': SymbolNode(MOANodeTypes.INDEX, (), (0, 3)),
        '_a3': SymbolNode(MOANodeTypes.ARRAY, (2,), (ArrayNode(MOANodeTypes.ARRAY, (), '_i1'), ArrayNode(MOANodeTypes.ARRAY, (), '_i2'))),
    }
    assert new_tree == BinaryNode(MOANodeTypes.PSI, (2, 3),
                                  ArrayNode(MOANodeTypes.ARRAY, (2,), '_a3'),
                                  ArrayNode(MOANodeTypes.ARRAY, (2, 3), 'A'))


def test_reduce_psi_psi():
    symbol_table = {
        '_i0': SymbolNode(MOANodeTypes.INDEX, (), (0, 3)),
        '_a1': SymbolNode(MOANodeTypes.ARRAY, (1,), ('_i0',)),
        '_a2': SymbolNode(MOANodeTypes.ARRAY, (3,), (1, 2, 3)),
        '_a3': SymbolNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), None),
    }
    symbol_table_copy = copy.deepcopy(symbol_table)
    tree = BinaryNode(MOANodeTypes.PSI, (0,),
                      ArrayNode(MOANodeTypes.ARRAY, (1,), '_a1'),
                      BinaryNode(MOANodeTypes.PSI, (4,),
                                 ArrayNode(MOANodeTypes.ARRAY, (3,), '_a2'),
                                 ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), '_a3')))

    new_symbol_table, new_tree = _reduce_psi_psi(symbol_table, tree)
    assert symbol_table_copy == symbol_table
    assert new_symbol_table == {
        '_i0': SymbolNode(MOANodeTypes.INDEX, (), (0, 3)),
        '_a1': SymbolNode(MOANodeTypes.ARRAY, (1,), ('_i0',)),
        '_a2': SymbolNode(MOANodeTypes.ARRAY, (3,), (1, 2, 3)),
        '_a3': SymbolNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), None),
        '_a4': SymbolNode(MOANodeTypes.ARRAY, (4,), (1, 2, 3, '_i0')),
    }
    assert new_tree == BinaryNode(MOANodeTypes.PSI, (0,),
                                  ArrayNode(MOANodeTypes.ARRAY, (4,), '_a4'),
                                  ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), '_a3'))


def test_reduce_psi_assign():
    symbol_table = {
        '_a1': SymbolNode(MOANodeTypes.ARRAY, (1,), (0, 1, 2)),
        '_a2': SymbolNode(MOANodeTypes.ARRAY, (1, 2, 3), None),
        '_a3': SymbolNode(MOANodeTypes.ARRAY, (1, 2, 3), None),
    }
    symbol_table_copy = copy.deepcopy(symbol_table)
    tree = BinaryNode(MOANodeTypes.PSI, (),
                      ArrayNode(MOANodeTypes.ARRAY, (3,), '_a1'),
                      BinaryNode(MOANodeTypes.ASSIGN, (1, 2, 3),
                                 ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3), '_a2'),
                                 ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3), '_a3')))

    new_symbol_table, new_tree = _reduce_psi_assign(symbol_table, tree)
    assert symbol_table_copy == symbol_table
    assert new_symbol_table == symbol_table
    assert new_tree == BinaryNode(MOANodeTypes.ASSIGN, (),
                                  BinaryNode(MOANodeTypes.PSI, (),
                                             ArrayNode(MOANodeTypes.ARRAY, (3,), '_a1'),
                                             ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3), '_a2')),
                                  BinaryNode(MOANodeTypes.PSI, (),
                                             ArrayNode(MOANodeTypes.ARRAY, (3,), '_a1'),
                                             ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3), '_a3')))


def test_reduce_psi_transpose():
    symbol_table = {
        '_i0': SymbolNode(MOANodeTypes.INDEX, (), (0, 3)),
        '_i1': SymbolNode(MOANodeTypes.INDEX, (), (0, 2)),
        '_a2': SymbolNode(MOANodeTypes.ARRAY, (4,), (3, 2, '_i0', '_i1')),
        '_a3': SymbolNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), None),
    }
    symbol_table_copy = copy.deepcopy(symbol_table)
    tree = BinaryNode(MOANodeTypes.PSI, (0,),
                      ArrayNode(MOANodeTypes.ARRAY, (4,), '_a2'),
                      UnaryNode(MOANodeTypes.TRANSPOSE, (4, 3, 2, 1),
                                ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), '_a3')))

    new_symbol_table, new_tree = _reduce_psi_transpose(symbol_table, tree)
    assert symbol_table_copy == symbol_table
    assert new_symbol_table == {
        '_i0': SymbolNode(MOANodeTypes.INDEX, (), (0, 3)),
        '_i1': SymbolNode(MOANodeTypes.INDEX, (), (0, 2)),
        '_a2': SymbolNode(MOANodeTypes.ARRAY, (4,), (3, 2, '_i0', '_i1')),
        '_a3': SymbolNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), None),
        '_a4': SymbolNode(MOANodeTypes.ARRAY, (4,), ('_i1', '_i0', 2, 3)),
    }
    assert new_tree ==  BinaryNode(MOANodeTypes.PSI, (0,),
                                   ArrayNode(MOANodeTypes.ARRAY, (4,), '_a4'),
                                   ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), '_a3'))


def test_reduce_psi_transposev():
    symbol_table = {
        '_a0': SymbolNode(MOANodeTypes.ARRAY, (4,), (3, 2, 1, 1)),
        '_a1': SymbolNode(MOANodeTypes.ARRAY, (4,), (4, 2, 3, 1)),
        '_a2': SymbolNode(MOANodeTypes.ARRAY, (2, 3, 5, 7), None),
    }
    symbol_table_copy = copy.deepcopy(symbol_table)
    tree = BinaryNode(MOANodeTypes.PSI, (),
                      ArrayNode(MOANodeTypes.ARRAY, (4,), '_a0'),
                      BinaryNode(MOANodeTypes.TRANSPOSEV, (7, 3, 5, 2),
                                 ArrayNode(MOANodeTypes.ARRAY, (4,), '_a1'),
                                 ArrayNode(MOANodeTypes.ARRAY, (2, 3, 5, 7), '_a2')))
    new_symbol_table, new_tree = _reduce_psi_transposev(symbol_table, tree)
    assert symbol_table_copy == symbol_table
    assert new_symbol_table == {
        '_a0': SymbolNode(MOANodeTypes.ARRAY, (4,), (3, 2, 1, 1)),
        '_a1': SymbolNode(MOANodeTypes.ARRAY, (4,), (4, 2, 3, 1)),
        '_a2': SymbolNode(MOANodeTypes.ARRAY, (2, 3, 5, 7), None),
        '_a3': SymbolNode(MOANodeTypes.ARRAY, (4,), (1, 2, 1, 3))
    }
    assert new_tree == BinaryNode(MOANodeTypes.PSI, (),
                                  ArrayNode(MOANodeTypes.ARRAY, (4,), '_a3'),
                                  ArrayNode(MOANodeTypes.ARRAY, (2, 3, 5, 7), '_a2'))


@pytest.mark.parametrize("operation", [
    MOANodeTypes.PLUS, MOANodeTypes.MINUS,
    MOANodeTypes.DIVIDE, MOANodeTypes.TIMES,
])
def test_reduce_psi_outer_plus_minus_times_divide_equal_shape(operation):
    symbol_table = {
        '_i0': SymbolNode(MOANodeTypes.INDEX, (), (0, 3)),
        '_i1': SymbolNode(MOANodeTypes.INDEX, (), (0, 4)),
        '_i2': SymbolNode(MOANodeTypes.INDEX, (), (0, 5)),
        '_a2': SymbolNode(MOANodeTypes.ARRAY, (4,), ('_i0', '_i1', '_i2')),
        '_a3': SymbolNode(MOANodeTypes.ARRAY, (3,), None),
        '_a4': SymbolNode(MOANodeTypes.ARRAY, (4, 5), None),
    }
    symbol_table_copy = copy.deepcopy(symbol_table)

    tree = BinaryNode(MOANodeTypes.PSI, (0,),
                      ArrayNode(MOANodeTypes.ARRAY, (4,), '_a2'),
                      BinaryNode((MOANodeTypes.DOT, operation), (3, 4, 5),
                                 ArrayNode(MOANodeTypes.ARRAY, (3,), '_a3'),
                                 ArrayNode(MOANodeTypes.ARRAY, (4, 5), '_a4')))

    expected_tree = BinaryNode(operation, (0,),
                               BinaryNode(MOANodeTypes.PSI, (0,),
                                          ArrayNode(MOANodeTypes.ARRAY, (1,), '_a6'),
                                          ArrayNode(MOANodeTypes.ARRAY, (3,), '_a3')),
                               BinaryNode(MOANodeTypes.PSI, (0,),
                                          ArrayNode(MOANodeTypes.ARRAY, (2,), '_a7'),
                                          ArrayNode(MOANodeTypes.ARRAY, (4, 5), '_a4')))

    new_symbol_table, new_tree = _reduce_psi_outer_plus_minus_times_divide(symbol_table, tree)
    assert symbol_table_copy == symbol_table
    assert new_tree == expected_tree
    assert new_symbol_table == {
        '_i0': SymbolNode(MOANodeTypes.INDEX, (), (0, 3)),
        '_i1': SymbolNode(MOANodeTypes.INDEX, (), (0, 4)),
        '_i2': SymbolNode(MOANodeTypes.INDEX, (), (0, 5)),
        '_a2': SymbolNode(MOANodeTypes.ARRAY, (4,), ('_i0', '_i1', '_i2')),
        '_a3': SymbolNode(MOANodeTypes.ARRAY, (3,), None),
        '_a4': SymbolNode(MOANodeTypes.ARRAY, (4, 5), None),
        '_a6': SymbolNode(MOANodeTypes.ARRAY, (1,), ('_i0',)),
        '_a7': SymbolNode(MOANodeTypes.ARRAY, (2,), ('_i1', '_i2')),
    }


@pytest.mark.parametrize("operation", [
    MOANodeTypes.PLUS, MOANodeTypes.MINUS,
    MOANodeTypes.DIVIDE, MOANodeTypes.TIMES,
])
def test_reduce_psi_reduce_plus_minus_times_divide_equal_shape(operation):
    symbol_table = {
        '_i0': SymbolNode(MOANodeTypes.INDEX, (), (0, 4)),
        '_i1': SymbolNode(MOANodeTypes.INDEX, (), (0, 5)),
        '_a2': SymbolNode(MOANodeTypes.ARRAY, (2,), (ArrayNode(MOANodeTypes.ARRAY, (), '_i0'), ArrayNode(MOANodeTypes.ARRAY, (), '_i1'))),
        '_a3': SymbolNode(MOANodeTypes.ARRAY, (3, 4, 5), None),
    }
    symbol_table_copy = copy.deepcopy(symbol_table)

    tree = BinaryNode(MOANodeTypes.PSI, (0,),
                      ArrayNode(MOANodeTypes.ARRAY, (2,), '_a2'),
                      ReduceNode((MOANodeTypes.REDUCE, operation), (4, 5), None,
                                 ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), '_a3')))

    expected_tree = ReduceNode((MOANodeTypes.REDUCE, operation), (0,), '_i4',
                               BinaryNode(MOANodeTypes.PSI, (0,),
                                          ArrayNode(MOANodeTypes.ARRAY, (3,), '_a5'),
                                          ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), '_a3')))

    new_symbol_table, new_tree = _reduce_psi_reduce_plus_minus_times_divide(symbol_table, tree)
    assert symbol_table_copy == symbol_table
    assert new_tree == expected_tree
    assert new_symbol_table == {
        '_i0': SymbolNode(MOANodeTypes.INDEX, (), (0, 4)),
        '_i1': SymbolNode(MOANodeTypes.INDEX, (), (0, 5)),
        '_a2': SymbolNode(MOANodeTypes.ARRAY, (2,), (ArrayNode(MOANodeTypes.ARRAY, (), '_i0'), ArrayNode(MOANodeTypes.ARRAY, (), '_i1'))),
        '_a3': SymbolNode(MOANodeTypes.ARRAY, (3, 4, 5), None),
        '_i4': SymbolNode(MOANodeTypes.INDEX, (), (0, 3)),
        '_a5': SymbolNode(MOANodeTypes.ARRAY, (3,), (ArrayNode(MOANodeTypes.ARRAY, (), '_i4'), ArrayNode(MOANodeTypes.ARRAY, (), '_i0'), ArrayNode(MOANodeTypes.ARRAY, (), '_i1'))),
    }


@pytest.mark.parametrize("operation", [
    MOANodeTypes.PLUS, MOANodeTypes.MINUS,
    MOANodeTypes.DIVIDE, MOANodeTypes.TIMES,
])
def test_reduce_psi_plus_minus_times_divide_equal_shape(operation):
    symbol_table = {
        '_i0': SymbolNode(MOANodeTypes.INDEX, (), (0, 3)),
        '_i1': SymbolNode(MOANodeTypes.INDEX, (), (0, 4)),
        '_a2': SymbolNode(MOANodeTypes.ARRAY, (4,), (1, 2, '_i0', '_i1')),
        '_a3': SymbolNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), None),
        '_a4': SymbolNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), None),
    }
    symbol_table_copy = copy.deepcopy(symbol_table)

    tree = BinaryNode(MOANodeTypes.PSI, (0,),
                      ArrayNode(MOANodeTypes.ARRAY, (4,), '_a2'),
                      BinaryNode(operation, (1, 2, 3, 4),
                                 ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), '_a3'),
                                 ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), '_a4')))

    expected_tree = BinaryNode(operation, (0,),
                               BinaryNode(MOANodeTypes.PSI, (0,),
                                          ArrayNode(MOANodeTypes.ARRAY, (4,), '_a2'),
                                          ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), '_a3')),
                               BinaryNode(MOANodeTypes.PSI, (0,),
                                          ArrayNode(MOANodeTypes.ARRAY, (4,), '_a2'),
                                          ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), '_a4')))

    new_symbol_table, new_tree = _reduce_psi_plus_minus_times_divide(symbol_table, tree)
    assert symbol_table_copy == symbol_table
    assert new_tree == expected_tree
    assert new_symbol_table == symbol_table


@pytest.mark.parametrize("operation", [
    MOANodeTypes.PLUS, MOANodeTypes.MINUS,
    MOANodeTypes.DIVIDE, MOANodeTypes.TIMES,
])
def test_reduce_psi_plus_minus_times_divide_scalar(operation):
    symbol_table = {
        '_i0': SymbolNode(MOANodeTypes.INDEX, (), (0, 3)),
        '_i1': SymbolNode(MOANodeTypes.INDEX, (), (0, 4)),
        '_a2': SymbolNode(MOANodeTypes.ARRAY, (4,), (1, 2, '_i0', '_i1')),
        '_a3': SymbolNode(MOANodeTypes.ARRAY, (), None),
        '_a4': SymbolNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), None),
    }
    symbol_table_copy = copy.deepcopy(symbol_table)

    tree = BinaryNode(MOANodeTypes.PSI, (0,),
                      ArrayNode(MOANodeTypes.ARRAY, (4,), '_a2'),
                      BinaryNode(operation, (1, 2, 3, 4),
                                 ArrayNode(MOANodeTypes.ARRAY, (), '_a3'),
                                 ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), '_a4')))

    expected_tree = BinaryNode(operation, (0,),
                               ArrayNode(MOANodeTypes.ARRAY, (), '_a3'),
                               BinaryNode(MOANodeTypes.PSI, (0,),
                                          ArrayNode(MOANodeTypes.ARRAY, (4,), '_a2'),
                                          ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), '_a4')))

    new_symbol_table, new_tree = _reduce_psi_plus_minus_times_divide(symbol_table, tree)
    assert symbol_table_copy == symbol_table
    assert new_tree == expected_tree
    assert new_symbol_table == symbol_table
