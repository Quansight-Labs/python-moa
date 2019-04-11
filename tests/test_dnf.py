import copy

import pytest

from moa import ast, dnf, testing


def test_add_indexing_node():
    tree = ast.Node((ast.NodeSymbol.ARRAY,), (2, 3), ('A',), ())
    symbol_table = {'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, (1, 2, 3, 4, 5, 6))}

    expected_tree = ast.Node((ast.NodeSymbol.PSI,), (2, 3), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (2,), ('_a3',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), (2, 3), ('A',), ())))
    expected_symbol_table = {
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, (1, 2, 3, 4, 5, 6)),
        '_i1': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 2, 1)),
        '_i2': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 3, 1)),
        '_a3': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2,), None, (ast.Node((ast.NodeSymbol.ARRAY,), (), ('_i1',), ()), ast.Node((ast.NodeSymbol.ARRAY,), (), ('_i2',), ()))),
    }

    testing.assert_transformation(tree, symbol_table, expected_tree, expected_symbol_table, dnf.add_indexing_node)


def test_matches_rule_simple():
    tree = ast.Node((ast.NodeSymbol.ARRAY,), (2, 3), ('A',), ())
    symbol_table = {'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, (1, 2, 3, 4, 5, 6))}
    context = ast.create_context(ast=tree, symbol_table=symbol_table)

    rule = ((ast.NodeSymbol.ARRAY,),)
    assert dnf.matches_rule(rule, context)


def test_not_matches_rule_simple():
    tree = ast.Node((ast.NodeSymbol.ARRAY,), (2, 3), ('A',), ())
    symbol_table = {'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, (1, 2, 3, 4, 5, 6))}
    context = ast.create_context(ast=tree, symbol_table=symbol_table)

    rule = ((ast.NodeSymbol.PSI,),)
    assert not dnf.matches_rule(rule, context)


def test_matches_rule_nested():
    tree = ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (2, 3), ('A',), ()),))
    symbol_table = {'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, (1, 2, 3, 4, 5, 6))}
    context = ast.create_context(ast=tree, symbol_table=symbol_table)

    rule = ((ast.NodeSymbol.TRANSPOSE,), (((ast.NodeSymbol.ARRAY,),),))
    assert dnf.matches_rule(rule, context)


def test_not_matches_rule_nested():
    tree = ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (2, 3), ('A',), ()),))
    symbol_table = {'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, (1, 2, 3, 4, 5, 6))}
    context = ast.create_context(ast=tree, symbol_table=symbol_table)

    rule = ((ast.NodeSymbol.TRANSPOSE,), (((ast.NodeSymbol.TRANSPOSE,),),))
    assert not dnf.matches_rule(rule, context)


def test_reduce_psi_psi():
    symbol_table = {
        '_i0': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 3, 1)),
        '_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1,), None, (ast.Node((ast.NodeSymbol.INDEX,), (), ('_i0',), ()),)),
        '_a2': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3,), None, (1, 2, 3)),
        '_a3': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), None, None),
    }
    tree = ast.Node((ast.NodeSymbol.PSI,), (0,), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (1,), ('_a1',), ()),
        ast.Node((ast.NodeSymbol.PSI,), (4,), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (3,), ('_a2',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3, 4), ('_a3',), ())))))

    expected_symbol_table = {
        **symbol_table,
        '_a4': ast.SymbolNode(ast.NodeSymbol.ARRAY, (4,), None, (1, 2, 3, ast.Node((ast.NodeSymbol.INDEX,), (), ('_i0',), ())))
    }
    expected_tree = ast.Node((ast.NodeSymbol.PSI,), (0,), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (4,), ('_a4',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3, 4), ('_a3',), ())))

    testing.assert_transformation(tree, symbol_table, expected_tree, expected_symbol_table, dnf._reduce_psi_psi)


def test_reduce_psi_assign():
    symbol_table = {
        '_a1': ast.SymbolNode((ast.NodeSymbol.ARRAY,), (1,), None, (0, 1, 2)),
        '_a2': ast.SymbolNode((ast.NodeSymbol.ARRAY,), (1, 2, 3), None, None),
        '_a3': ast.SymbolNode((ast.NodeSymbol.ARRAY,), (1, 2, 3), None, None),
    }
    tree = ast.Node((ast.NodeSymbol.PSI,), (), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (3,), ('_a1',), ()),
        ast.Node((ast.NodeSymbol.ASSIGN,), (1, 2, 3), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3), ('_a2',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3), ('_a3',), ())))))

    expected_tree = ast.Node((ast.NodeSymbol.ASSIGN,), (), (), (
        ast.Node((ast.NodeSymbol.PSI,), (), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (3,), ('_a1',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3), ('_a2',), ()))),
        ast.Node((ast.NodeSymbol.PSI,), (), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (3,), ('_a1',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3), ('_a3',), ())))))

    testing.assert_transformation(tree, symbol_table, expected_tree, symbol_table, dnf._reduce_psi_assign)


def test_reduce_psi_transpose():
    symbol_table = {
        '_i0': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 3, 1)),
        '_i1': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 2, 1)),
        '_a2': ast.SymbolNode(ast.NodeSymbol.ARRAY, (4,), None, (
            ast.Node((ast.NodeSymbol.ARRAY,), (), ('_i0',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), (), ('_i1',), ()), 1, 0)),
        '_a3': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), None, None),
    }
    tree = ast.Node((ast.NodeSymbol.PSI,), (0,), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (4,), ('_a2',), ()),
        ast.Node((ast.NodeSymbol.TRANSPOSE,), (4, 3, 2, 1), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3, 4), ('_a3',), ()),))))

    expected_symbol_table = {
        **symbol_table,
        '_a4': ast.SymbolNode(ast.NodeSymbol.ARRAY, (4,), None, (0, 1, ast.Node((ast.NodeSymbol.ARRAY,), (), ('_i1',), ()), ast.Node((ast.NodeSymbol.ARRAY,), (), ('_i0',), ()))),
    }
    expected_tree = ast.Node((ast.NodeSymbol.PSI,), (0,), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (4,), ('_a4',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3, 4), ('_a3',), ())))

    testing.assert_transformation(tree, symbol_table, expected_tree, expected_symbol_table, dnf._reduce_psi_transpose)


def test_reduce_psi_transposev():
    symbol_table = {
        '_a0': ast.SymbolNode(ast.NodeSymbol.ARRAY, (4,), None, (3, 2, 1, 1)),
        '_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (4,), None, (4, 2, 3, 1)),
        '_a2': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3, 5, 7), None, None),
    }
    tree = ast.Node((ast.NodeSymbol.PSI,), (), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (4,), ('_a0',), ()),
        ast.Node((ast.NodeSymbol.TRANSPOSEV,), (7, 3, 5, 2), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (4,), ('_a1',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), (2, 3, 5, 7), ('_a2',), ())))))

    expected_symbol_table = {
        **symbol_table,
        '_a3': ast.SymbolNode(ast.NodeSymbol.ARRAY, (4,), None, (1, 2, 1, 3))
    }
    expected_tree = ast.Node((ast.NodeSymbol.PSI,), (), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (4,), ('_a3',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), (2, 3, 5, 7), ('_a2',), ())))

    testing.assert_transformation(tree, symbol_table, expected_tree, expected_symbol_table, dnf._reduce_psi_transposev)


@pytest.mark.parametrize("operation", [
    ast.NodeSymbol.PLUS, ast.NodeSymbol.MINUS,
    ast.NodeSymbol.DIVIDE, ast.NodeSymbol.TIMES,
])
def test_reduce_psi_outer_plus_minus_times_divide_equal_shape(operation):
    symbol_table = {
        '_i0': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 3, 1)),
        '_i1': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 4, 1)),
        '_i2': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 5, 1)),
        '_a2': ast.SymbolNode(ast.NodeSymbol.ARRAY, (4,), None, (
            ast.Node((ast.NodeSymbol.INDEX,), (), ('_i0',), ()),
            ast.Node((ast.NodeSymbol.INDEX,), (), ('_i1',), ()),
            ast.Node((ast.NodeSymbol.INDEX,), (), ('_i2',), ()))),
        '_a3': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3,), None, None),
        '_a4': ast.SymbolNode(ast.NodeSymbol.ARRAY, (4, 5), None, None),
    }
    tree = ast.Node((ast.NodeSymbol.PSI,), (0,), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (4,), ('_a2',), ()),
        ast.Node((ast.NodeSymbol.DOT, operation), (3, 4, 5), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (3,), ('_a3',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), (4, 5), ('_a4',), ())))))

    expected_symbol_table = {
        **symbol_table,
        '_a6': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1,), None, (ast.Node((ast.NodeSymbol.INDEX,), (), ('_i0',), ()),)),
        '_a7': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2,), None, (
            ast.Node((ast.NodeSymbol.INDEX,), (), ('_i1',), ()),
            ast.Node((ast.NodeSymbol.INDEX,), (), ('_i2',), ()),
        )),
    }
    expected_tree = ast.Node((operation,), (0,), (), (
        ast.Node((ast.NodeSymbol.PSI,), (0,), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (1,), ('_a6',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), (3,), ('_a3',), ()))),
        ast.Node((ast.NodeSymbol.PSI,), (0,), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (2,), ('_a7',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), (4, 5), ('_a4',), ())))))

    testing.assert_transformation(tree, symbol_table, expected_tree, expected_symbol_table, dnf._reduce_psi_outer_plus_minus_times_divide)


@pytest.mark.parametrize("operation", [
    (ast.NodeSymbol.PLUS,  ast.NodeSymbol.PLUS),
    (ast.NodeSymbol.MINUS, ast.NodeSymbol.PLUS),
    (ast.NodeSymbol.DIVIDE,ast.NodeSymbol.PLUS),
    (ast.NodeSymbol.TIMES, ast.NodeSymbol.PLUS),
    (ast.NodeSymbol.PLUS,  ast.NodeSymbol.MINUS),
    (ast.NodeSymbol.MINUS, ast.NodeSymbol.MINUS),
    (ast.NodeSymbol.DIVIDE,ast.NodeSymbol.MINUS),
    (ast.NodeSymbol.TIMES, ast.NodeSymbol.MINUS),
    (ast.NodeSymbol.PLUS,  ast.NodeSymbol.TIMES),
    (ast.NodeSymbol.MINUS, ast.NodeSymbol.TIMES),
    (ast.NodeSymbol.DIVIDE,ast.NodeSymbol.TIMES),
    (ast.NodeSymbol.TIMES, ast.NodeSymbol.TIMES),
    (ast.NodeSymbol.PLUS,  ast.NodeSymbol.DIVIDE),
    (ast.NodeSymbol.MINUS, ast.NodeSymbol.DIVIDE),
    (ast.NodeSymbol.DIVIDE,ast.NodeSymbol.DIVIDE),
    (ast.NodeSymbol.TIMES, ast.NodeSymbol.DIVIDE),
])
def test_reduce_psi_inner_plus_minus_times_divide_equal_shape(operation):
    symbol_table = {
        '_i0': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 3, 1)),
        '_i1': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 5, 1)),
        '_a2': ast.SymbolNode(ast.NodeSymbol.ARRAY, (4,), None, (
            ast.Node((ast.NodeSymbol.INDEX,), (), ('_i0',), ()),
            ast.Node((ast.NodeSymbol.INDEX,), (), ('_i1',), ()))),
        '_a3': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4), None, None),
        '_a4': ast.SymbolNode(ast.NodeSymbol.ARRAY, (4, 5), None, None),
    }
    tree = ast.Node((ast.NodeSymbol.PSI,), (0,), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (2,), ('_a2',), ()),
        ast.Node((ast.NodeSymbol.DOT, *operation), (3, 5), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (3, 4), ('_a3',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), (4, 5), ('_a4',), ())))))

    expected_symbol_table = {
        **symbol_table,
        '_i5': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 4, 1)),
        '_a6': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2,), None, (ast.Node((ast.NodeSymbol.INDEX,), (), ('_i0',), ()), ast.Node((ast.NodeSymbol.INDEX,), (), ('_i5',), ()))),
        '_a7': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2,), None, (ast.Node((ast.NodeSymbol.INDEX,), (), ('_i5',), ()), ast.Node((ast.NodeSymbol.INDEX,), (), ('_i1',), ()))),
    }
    expected_tree = ast.Node((ast.NodeSymbol.REDUCE, operation[0]), (0,), ('_i5',), (
        ast.Node((operation[1],), (0,), (), (
            ast.Node((ast.NodeSymbol.PSI,), (0,), (), (
                ast.Node((ast.NodeSymbol.ARRAY,), (2,), ('_a6',), ()),
                ast.Node((ast.NodeSymbol.ARRAY,), (3, 4), ('_a3',), ()))),
            ast.Node((ast.NodeSymbol.PSI,), (0,), (), (
                ast.Node((ast.NodeSymbol.ARRAY,), (2,), ('_a7',), ()),
                ast.Node((ast.NodeSymbol.ARRAY,), (4, 5), ('_a4',), ()))))),))

    testing.assert_transformation(tree, symbol_table, expected_tree, expected_symbol_table, dnf._reduce_psi_inner_plus_minus_times_divide)


@pytest.mark.parametrize("operation", [
    ast.NodeSymbol.PLUS, ast.NodeSymbol.MINUS,
    ast.NodeSymbol.DIVIDE, ast.NodeSymbol.TIMES,
])
def test_reduce_psi_reduce_plus_minus_times_divide_equal_shape(operation):
    symbol_table = {
        '_i0': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 4, 1)),
        '_i1': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 5, 1)),
        '_a2': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2,), None, (ast.Node((ast.NodeSymbol.ARRAY,), (), ('_i0',), ()), ast.Node((ast.NodeSymbol.ARRAY,), (), ('_i1',), ()))),
        '_a3': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4, 5), None, None),
    }
    tree = ast.Node((ast.NodeSymbol.PSI,), (0,), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (2,), ('_a2',), ()),
        ast.Node((ast.NodeSymbol.REDUCE, operation), (4, 5), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (3, 4, 5), ('_a3',), ()),))))

    expected_tree = ast.Node((ast.NodeSymbol.REDUCE, operation), (0,), ('_i4',), (
        ast.Node((ast.NodeSymbol.PSI,), (0,), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (3,), ('_a5',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), (3, 4, 5), ('_a3',), ()))),))
    expected_symbol_table = {
        **symbol_table,
        '_i4': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 3, 1)),
        '_a5': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3,), None, (ast.Node((ast.NodeSymbol.ARRAY,), (), ('_i4',), ()), ast.Node((ast.NodeSymbol.ARRAY,), (), ('_i0',), ()), ast.Node((ast.NodeSymbol.ARRAY,), (), ('_i1',), ()))),
    }

    testing.assert_transformation(tree, symbol_table, expected_tree, expected_symbol_table, dnf._reduce_psi_reduce_plus_minus_times_divide)


@pytest.mark.parametrize("operation", [
    ast.NodeSymbol.PLUS, ast.NodeSymbol.MINUS,
    ast.NodeSymbol.DIVIDE, ast.NodeSymbol.TIMES,
])
def test_reduce_psi_plus_minus_times_divide_equal_shape(operation):
    symbol_table = {
        '_i0': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 3)),
        '_i1': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 4)),
        '_a2': ast.SymbolNode(ast.NodeSymbol.ARRAY, (4,), None, (1, 2, ast.Node(ast.NodeSymbol.INDEX, (), ('_i0',), ()), ast.Node((ast.NodeSymbol.INDEX,), (), ('_i1',), ()))),
        '_a3': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), None, None),
        '_a4': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), None, None),
    }
    tree = ast.Node((ast.NodeSymbol.PSI,), (0,), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (4,), ('_a2',), ()),
        ast.Node((operation,), (1, 2, 3, 4), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3, 4), ('_a3',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3, 4), ('_a4',), ())))))

    expected_tree = ast.Node((operation,), (0,), (), (
        ast.Node((ast.NodeSymbol.PSI,), (0,), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (4,), ('_a2',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3, 4), ('_a3',), ()))),
        ast.Node((ast.NodeSymbol.PSI,), (0,), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (4,), ('_a2',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3, 4), ('_a4',), ())))))

    testing.assert_transformation(tree, symbol_table, expected_tree, symbol_table, dnf._reduce_psi_plus_minus_times_divide)


@pytest.mark.parametrize("operation", [
    ast.NodeSymbol.PLUS, ast.NodeSymbol.MINUS,
    ast.NodeSymbol.DIVIDE, ast.NodeSymbol.TIMES,
])
def test_reduce_psi_plus_minus_times_divide_scalar(operation):
    symbol_table = {
        '_i0': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 3)),
        '_i1': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 4)),
        '_a2': ast.SymbolNode(ast.NodeSymbol.ARRAY, (4,), None, (1, 2, ast.Node(ast.NodeSymbol.INDEX, (), ('_i0',), ()), ast.Node((ast.NodeSymbol.INDEX,), (), ('_i1',), ()))),
        '_a3': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, None),
        '_a4': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), None, None),
    }
    tree = ast.Node((ast.NodeSymbol.PSI,), (0,), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (4,), ('_a2',), ()),
        ast.Node((operation,), (1, 2, 3, 4), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (), ('_a3',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3, 4), ('_a4',), ())))))

    expected_tree = ast.Node((operation,), (0,), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (), ('_a3',), ()),
        ast.Node((ast.NodeSymbol.PSI,), (0,), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (4,), ('_a2',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3, 4), ('_a4',), ())))))

    testing.assert_transformation(tree, symbol_table, expected_tree, symbol_table, dnf._reduce_psi_plus_minus_times_divide)


# @pytest.mark.parametrize("operation", [
#     ast.NodeSymbol.PLUS, ast.NodeSymbol.MINUS,
#     ast.NodeSymbol.DIVIDE, ast.NodeSymbol.TIMES,
# ])
# def test_reduce_psi_plus_minus_times_divide_scalar(operation):
#     symbol_table = {
#         '_i0': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 3)),
#         '_i1': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 4)),
#         '_a2': SymbolNode(ast.NodeSymbol.ARRAY, (4,), (1, 2, '_i0', '_i1')),
#         '_a3': SymbolNode(ast.NodeSymbol.ARRAY, (), None),
#         '_a4': SymbolNode(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), None),
#     }
#     symbol_table_copy = copy.deepcopy(symbol_table)

#     tree = Node(ast.NodeSymbol.PSI, (0,),
#                 Node(ast.NodeSymbol.ARRAY, (4,), '_a2'),
#                 Node(operation, (1, 2, 3, 4),
#                      Node(ast.NodeSymbol.ARRAY, (), '_a3'),
#                      Node(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), '_a4')))

#     expected_tree = Node(operation, (0,),
#                          Node(ast.NodeSymbol.ARRAY, (), '_a3'),
#                          Node(ast.NodeSymbol.PSI, (0,),
#                               Node(ast.NodeSymbol.ARRAY, (4,), '_a2'),
#                               Node(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), '_a4')))

#     new_symbol_table, new_tree = _reduce_psi_plus_minus_times_divide(symbol_table, tree)
#     assert symbol_table_copy == symbol_table
#     assert new_tree == expected_tree
#     assert new_symbol_table == symbol_table
