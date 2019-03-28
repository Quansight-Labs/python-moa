import pytest

from moa.frontend import LazyArray
from moa import ast
from moa import testing


def test_array_single_array():
    expression = LazyArray(name='A', shape=(2, 3))
    node = ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ())
    symbol_table = {'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, None)}
    context = ast.create_context(ast=node, symbol_table=symbol_table)

    testing.assert_context_equal(context, expression.context)


@pytest.mark.parametrize("function, side, operation", [
    (lambda: LazyArray(name='A', shape=(2, 3)) + 1, 'right', ast.NodeSymbol.PLUS),
    (lambda: 1 + LazyArray(name='A', shape=(2, 3)), 'left', ast.NodeSymbol.PLUS),
    (lambda: LazyArray(name='A', shape=(2, 3)) - 1, 'right', ast.NodeSymbol.MINUS),
    (lambda: 1 - LazyArray(name='A', shape=(2, 3)), 'left', ast.NodeSymbol.MINUS),
    (lambda: LazyArray(name='A', shape=(2, 3)) * 1, 'right', ast.NodeSymbol.TIMES),
    (lambda: 1 * LazyArray(name='A', shape=(2, 3)), 'left', ast.NodeSymbol.TIMES),
    (lambda: LazyArray(name='A', shape=(2, 3)) / 1, 'right', ast.NodeSymbol.DIVIDE),
    (lambda: 1 / LazyArray(name='A', shape=(2, 3)), 'left', ast.NodeSymbol.DIVIDE),
])
def test_array_single_array_binary_operation_cast(function, side, operation):
    expression = function()
    if side == 'right':
        tree = ast.Node((operation,), None, (), (
            ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a1',), ())))
    else:
        tree = ast.Node((operation,), None, (), (
            ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a1',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ())))
    symbol_table = {
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, None),
        '_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, (1,))
    }
    context = ast.create_context(ast=tree, symbol_table=symbol_table)

    testing.assert_context_equal(context, expression.context)


def test_array_addition():
    expression = LazyArray(name='A', shape=(2, 3)) + LazyArray(name='B', shape=(2, 3))
    tree = ast.Node((ast.NodeSymbol.PLUS,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('B',), ())))
    symbol_table = {
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, None),
        'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, None)
    }
    context = ast.create_context(ast=tree, symbol_table=symbol_table)

    testing.assert_context_equal(context, expression.context)



def test_array_transpose_T():
    expression = LazyArray(name='A', shape=(2, 3)).T
    node = ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),))
    symbol_table = {'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, None)}
    context = ast.create_context(ast=node, symbol_table=symbol_table)

    testing.assert_context_equal(context, expression.context)


def test_array_transpose_default():
    expression = LazyArray(name='A', shape=(2, 3)).transpose()
    node = ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),))
    symbol_table = {'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, None)}
    context = ast.create_context(ast=node, symbol_table=symbol_table)

    testing.assert_context_equal(context, expression.context)


def test_array_transpose_with_vector():
    expression = LazyArray(name='A', shape=(2, 3)).transpose([1, 0])
    node = ast.Node((ast.NodeSymbol.TRANSPOSEV,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a1',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),))
    symbol_table = {
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, None),
        '_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2,), None, (1, 0)),
    }
    context = ast.create_context(ast=node, symbol_table=symbol_table)

    testing.assert_context_equal(context, expression.context)


@pytest.mark.parametrize("symbol, operation", [
    ('+', ast.NodeSymbol.PLUS),
    ('-', ast.NodeSymbol.MINUS),
    ('*', ast.NodeSymbol.TIMES),
    ('/', ast.NodeSymbol.DIVIDE),
])
def test_array_outer_product(symbol, operation):
    expression = LazyArray(name='A', shape=(2, 3)).outer(symbol, LazyArray(name='B', shape=(1, 2)))

    expected_tree = ast.Node((ast.NodeSymbol.DOT, operation), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('B',), ())))
    expected_symbol_table = {
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, None),
        'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1, 2), None, None),
    }
    expected_context = ast.create_context(ast=expected_tree, symbol_table=expected_symbol_table)

    testing.assert_context_equal(expected_context, expression.context)


def test_array_index_int():
    expression = LazyArray(name='A', shape=(2, 3))[0]
    node = ast.Node((ast.NodeSymbol.PSI,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a1',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),))
    symbol_table = {
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, None),
        '_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1,), None, (0,)),
    }
    context = ast.create_context(ast=node, symbol_table=symbol_table)

    testing.assert_context_equal(context, expression.context)


def test_array_index_symbol():
    expression = LazyArray(name='A', shape=(2, 3))['n']
    node = ast.Node((ast.NodeSymbol.PSI,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a2',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),))
    symbol_table = {
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, None),
        'n': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, None),
        '_a2': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1,), None, (ast.Node((ast.NodeSymbol.ARRAY,), (), ('n',), ()),)),
    }
    context = ast.create_context(ast=node, symbol_table=symbol_table)

    testing.assert_context_equal(context, expression.context)


@pytest.mark.xfail
def test_array_index_stride():
    expression = LazyArray(name='A', shape=(2, 3))[1:2]
    tree = ast.Node((ast.NodeSymbol.PSI,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a2',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ())))
    symbol_table = {
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, None),
        'n': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, None),
        '_a2': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1,), None, (Node(ast.NodeSymbol.ARRAY, (), 'n'),)),
    }
    context = ast.create_context(ast=tree, symbol_table=symbol_table)

    testing.assert_context_equal(context, expression.context)


@pytest.mark.xfail
def test_array_index_stride_reverse():
    expression = LazyArray(name='A', shape=(2, 3))[1:2:-1]
    tree = ast.Node(ast.NodeSymbol.PSI, None, (), (
                    ast.Node(ast.NodeSymbol.ARRAY, None, ('_a2',), ()),
                    ast.Node(ast.NodeSymbol.ARRAY, None, ('A',), ())))
    symbol_table = {
        'A': SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, None),
        'n': SymbolNode(ast.NodeSymbol.ARRAY, (), None, None),
        '_a2': SymbolNode(ast.NodeSymbol.ARRAY, (1,), None, (Node(ast.NodeSymbol.ARRAY, (), 'n'),)),
    }
    context = ast.create_context(ast=tree, symbol_table=symbol_table)

    testing.assert_context_equal(context, expression.context)


def test_array_index_tuple():
    expression = LazyArray(name='A', shape=(2, 3))[1, 0]
    node = ast.Node((ast.NodeSymbol.PSI,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a1',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),))
    symbol_table = {
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, None),
        '_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2,), None, (1, 0)),
    }
    context = ast.create_context(ast=node, symbol_table=symbol_table)

    testing.assert_context_equal(context, expression.context)
