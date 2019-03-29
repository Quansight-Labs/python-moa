import copy

import pytest

from moa import ast, dnf, testing


def test_add_indexing_node():
    tree = ast.Node((ast.NodeSymbol.ARRAY,), (2, 3), ('A',), ())
    symbol_table = {'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, (1, 2, 3, 4, 5, 6))}
    context = ast.create_context(ast=tree, symbol_table=symbol_table)
    context_copy = copy.deepcopy(context)

    expected_tree = ast.Node((ast.NodeSymbol.PSI,), (2, 3), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (2,), ('_a3',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), (2, 3), ('A',), ())))
    expected_symbol_table = {
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, (1, 2, 3, 4, 5, 6)),
        '_i1': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 2)),
        '_i2': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 3)),
        '_a3': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2,), None, (ast.Node((ast.NodeSymbol.ARRAY,), (), ('_i1',), ()), ast.Node((ast.NodeSymbol.ARRAY,), (), ('_i2',), ()))),
    }
    exptected_context = ast.create_context(ast=expected_tree, symbol_table=expected_symbol_table)

    new_context = dnf.add_indexing_node(context)
    testing.assert_context_equal(context, context_copy)


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



# def test_reduce_psi_psi():
#     symbol_table = {
#         '_i0': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 3)),
#         '_a1': SymbolNode(ast.NodeSymbol.ARRAY, (1,), ('_i0',)),
#         '_a2': SymbolNode(ast.NodeSymbol.ARRAY, (3,), (1, 2, 3)),
#         '_a3': SymbolNode(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), None),
#     }
#     symbol_table_copy = copy.deepcopy(symbol_table)
#     tree = Node(ast.NodeSymbol.PSI, (0,),
#                 Node(ast.NodeSymbol.ARRAY, (1,), '_a1'),
#                 Node(ast.NodeSymbol.PSI, (4,),
#                      Node(ast.NodeSymbol.ARRAY, (3,), '_a2'),
#                      Node(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), '_a3')))

#     new_symbol_table, new_tree = _reduce_psi_psi(symbol_table, tree)
#     assert symbol_table_copy == symbol_table
#     assert new_symbol_table == {
#         '_i0': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 3)),
#         '_a1': SymbolNode(ast.NodeSymbol.ARRAY, (1,), ('_i0',)),
#         '_a2': SymbolNode(ast.NodeSymbol.ARRAY, (3,), (1, 2, 3)),
#         '_a3': SymbolNode(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), None),
#         '_a4': SymbolNode(ast.NodeSymbol.ARRAY, (4,), (1, 2, 3, '_i0')),
#     }
#     assert new_tree == Node(ast.NodeSymbol.PSI, (0,),
#                             Node(ast.NodeSymbol.ARRAY, (4,), '_a4'),
#                             Node(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), '_a3'))


# def test_reduce_psi_assign():
#     symbol_table = {
#         '_a1': SymbolNode(ast.NodeSymbol.ARRAY, (1,), (0, 1, 2)),
#         '_a2': SymbolNode(ast.NodeSymbol.ARRAY, (1, 2, 3), None),
#         '_a3': SymbolNode(ast.NodeSymbol.ARRAY, (1, 2, 3), None),
#     }
#     symbol_table_copy = copy.deepcopy(symbol_table)
#     tree = Node(ast.NodeSymbol.PSI, (),
#                 Node(ast.NodeSymbol.ARRAY, (3,), '_a1'),
#                 Node(ast.NodeSymbol.ASSIGN, (1, 2, 3),
#                      Node(ast.NodeSymbol.ARRAY, (1, 2, 3), '_a2'),
#                      Node(ast.NodeSymbol.ARRAY, (1, 2, 3), '_a3')))

#     new_symbol_table, new_tree = _reduce_psi_assign(symbol_table, tree)
#     assert symbol_table_copy == symbol_table
#     assert new_symbol_table == symbol_table
#     assert new_tree == Node(ast.NodeSymbol.ASSIGN, (),
#                             Node(ast.NodeSymbol.PSI, (),
#                                  Node(ast.NodeSymbol.ARRAY, (3,), '_a1'),
#                                  Node(ast.NodeSymbol.ARRAY, (1, 2, 3), '_a2')),
#                             Node(ast.NodeSymbol.PSI, (),
#                                  Node(ast.NodeSymbol.ARRAY, (3,), '_a1'),
#                                  Node(ast.NodeSymbol.ARRAY, (1, 2, 3), '_a3')))


# def test_reduce_psi_transpose():
#     symbol_table = {
#         '_i0': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 3)),
#         '_i1': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 2)),
#         '_a2': SymbolNode(ast.NodeSymbol.ARRAY, (4,), (3, 2, '_i0', '_i1')),
#         '_a3': SymbolNode(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), None),
#     }
#     symbol_table_copy = copy.deepcopy(symbol_table)
#     tree = Node(ast.NodeSymbol.PSI, (0,),
#                 Node(ast.NodeSymbol.ARRAY, (4,), '_a2'),
#                 Node(ast.NodeSymbol.TRANSPOSE, (4, 3, 2, 1),
#                      Node(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), '_a3')))

#     new_symbol_table, new_tree = _reduce_psi_transpose(symbol_table, tree)
#     assert symbol_table_copy == symbol_table
#     assert new_symbol_table == {
#         '_i0': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 3)),
#         '_i1': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 2)),
#         '_a2': SymbolNode(ast.NodeSymbol.ARRAY, (4,), (3, 2, '_i0', '_i1')),
#         '_a3': SymbolNode(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), None),
#         '_a4': SymbolNode(ast.NodeSymbol.ARRAY, (4,), ('_i1', '_i0', 2, 3)),
#     }
#     assert new_tree ==  Node(ast.NodeSymbol.PSI, (0,),
#                              Node(ast.NodeSymbol.ARRAY, (4,), '_a4'),
#                              Node(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), '_a3'))


# def test_reduce_psi_transposev():
#     symbol_table = {
#         '_a0': SymbolNode(ast.NodeSymbol.ARRAY, (4,), (3, 2, 1, 1)),
#         '_a1': SymbolNode(ast.NodeSymbol.ARRAY, (4,), (4, 2, 3, 1)),
#         '_a2': SymbolNode(ast.NodeSymbol.ARRAY, (2, 3, 5, 7), None),
#     }
#     symbol_table_copy = copy.deepcopy(symbol_table)
#     tree = Node(ast.NodeSymbol.PSI, (),
#                 Node(ast.NodeSymbol.ARRAY, (4,), '_a0'),
#                 Node(ast.NodeSymbol.TRANSPOSEV, (7, 3, 5, 2),
#                      Node(ast.NodeSymbol.ARRAY, (4,), '_a1'),
#                      Node(ast.NodeSymbol.ARRAY, (2, 3, 5, 7), '_a2')))
#     new_symbol_table, new_tree = _reduce_psi_transposev(symbol_table, tree)
#     assert symbol_table_copy == symbol_table
#     assert new_symbol_table == {
#         '_a0': SymbolNode(ast.NodeSymbol.ARRAY, (4,), (3, 2, 1, 1)),
#         '_a1': SymbolNode(ast.NodeSymbol.ARRAY, (4,), (4, 2, 3, 1)),
#         '_a2': SymbolNode(ast.NodeSymbol.ARRAY, (2, 3, 5, 7), None),
#         '_a3': SymbolNode(ast.NodeSymbol.ARRAY, (4,), (1, 2, 1, 3))
#     }
#     assert new_tree == Node(ast.NodeSymbol.PSI, (),
#                             Node(ast.NodeSymbol.ARRAY, (4,), '_a3'),
#                             Node(ast.NodeSymbol.ARRAY, (2, 3, 5, 7), '_a2'))


# @pytest.mark.parametrize("operation", [
#     ast.NodeSymbol.PLUS, ast.NodeSymbol.MINUS,
#     ast.NodeSymbol.DIVIDE, ast.NodeSymbol.TIMES,
# ])
# def test_reduce_psi_outer_plus_minus_times_divide_equal_shape(operation):
#     symbol_table = {
#         '_i0': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 3)),
#         '_i1': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 4)),
#         '_i2': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 5)),
#         '_a2': SymbolNode(ast.NodeSymbol.ARRAY, (4,), ('_i0', '_i1', '_i2')),
#         '_a3': SymbolNode(ast.NodeSymbol.ARRAY, (3,), None),
#         '_a4': SymbolNode(ast.NodeSymbol.ARRAY, (4, 5), None),
#     }
#     symbol_table_copy = copy.deepcopy(symbol_table)

#     tree = Node(ast.NodeSymbol.PSI, (0,),
#                 Node(ast.NodeSymbol.ARRAY, (4,), '_a2'),
#                 Node((ast.NodeSymbol.DOT, operation), (3, 4, 5),
#                      Node(ast.NodeSymbol.ARRAY, (3,), '_a3'),
#                      Node(ast.NodeSymbol.ARRAY, (4, 5), '_a4')))

#     expected_tree = Node(operation, (0,),
#                          Node(ast.NodeSymbol.PSI, (0,),
#                               Node(ast.NodeSymbol.ARRAY, (1,), '_a6'),
#                               Node(ast.NodeSymbol.ARRAY, (3,), '_a3')),
#                          Node(ast.NodeSymbol.PSI, (0,),
#                               Node(ast.NodeSymbol.ARRAY, (2,), '_a7'),
#                               Node(ast.NodeSymbol.ARRAY, (4, 5), '_a4')))

#     new_symbol_table, new_tree = _reduce_psi_outer_plus_minus_times_divide(symbol_table, tree)
#     assert symbol_table_copy == symbol_table
#     assert new_tree == expected_tree
#     assert new_symbol_table == {
#         '_i0': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 3)),
#         '_i1': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 4)),
#         '_i2': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 5)),
#         '_a2': SymbolNode(ast.NodeSymbol.ARRAY, (4,), ('_i0', '_i1', '_i2')),
#         '_a3': SymbolNode(ast.NodeSymbol.ARRAY, (3,), None),
#         '_a4': SymbolNode(ast.NodeSymbol.ARRAY, (4, 5), None),
#         '_a6': SymbolNode(ast.NodeSymbol.ARRAY, (1,), ('_i0',)),
#         '_a7': SymbolNode(ast.NodeSymbol.ARRAY, (2,), ('_i1', '_i2')),
#     }


# @pytest.mark.parametrize("operation", [
#     ast.NodeSymbol.PLUS, ast.NodeSymbol.MINUS,
#     ast.NodeSymbol.DIVIDE, ast.NodeSymbol.TIMES,
# ])
# def test_reduce_psi_reduce_plus_minus_times_divide_equal_shape(operation):
#     symbol_table = {
#         '_i0': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 4)),
#         '_i1': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 5)),
#         '_a2': SymbolNode(ast.NodeSymbol.ARRAY, (2,), (Node(ast.NodeSymbol.ARRAY, (), '_i0'), Node(ast.NodeSymbol.ARRAY, (), '_i1'))),
#         '_a3': SymbolNode(ast.NodeSymbol.ARRAY, (3, 4, 5), None),
#     }
#     symbol_table_copy = copy.deepcopy(symbol_table)

#     tree = Node(ast.NodeSymbol.PSI, (0,),
#                 Node(ast.NodeSymbol.ARRAY, (2,), '_a2'),
#                 Node((ast.NodeSymbol.REDUCE, operation), (4, 5), None,
#                      Node(ast.NodeSymbol.ARRAY, (3, 4, 5), '_a3')))

#     expected_tree = Node((ast.NodeSymbol.REDUCE, operation), (0,), '_i4',
#                          Node(ast.NodeSymbol.PSI, (0,),
#                               Node(ast.NodeSymbol.ARRAY, (3,), '_a5'),
#                               Node(ast.NodeSymbol.ARRAY, (3, 4, 5), '_a3')))

#     new_symbol_table, new_tree = _reduce_psi_reduce_plus_minus_times_divide(symbol_table, tree)
#     assert symbol_table_copy == symbol_table
#     assert new_tree == expected_tree
#     assert new_symbol_table == {
#         '_i0': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 4)),
#         '_i1': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 5)),
#         '_a2': SymbolNode(ast.NodeSymbol.ARRAY, (2,), (Node(ast.NodeSymbol.ARRAY, (), '_i0'), Node(ast.NodeSymbol.ARRAY, (), '_i1'))),
#         '_a3': SymbolNode(ast.NodeSymbol.ARRAY, (3, 4, 5), None),
#         '_i4': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 3)),
#         '_a5': SymbolNode(ast.NodeSymbol.ARRAY, (3,), (Node(ast.NodeSymbol.ARRAY, (), '_i4'), Node(ast.NodeSymbol.ARRAY, (), '_i0'), Node(ast.NodeSymbol.ARRAY, (), '_i1'))),
#     }


# @pytest.mark.parametrize("operation", [
#     ast.NodeSymbol.PLUS, ast.NodeSymbol.MINUS,
#     ast.NodeSymbol.DIVIDE, ast.NodeSymbol.TIMES,
# ])
# def test_reduce_psi_plus_minus_times_divide_equal_shape(operation):
#     symbol_table = {
#         '_i0': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 3)),
#         '_i1': SymbolNode(ast.NodeSymbol.INDEX, (), (0, 4)),
#         '_a2': SymbolNode(ast.NodeSymbol.ARRAY, (4,), (1, 2, '_i0', '_i1')),
#         '_a3': SymbolNode(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), None),
#         '_a4': SymbolNode(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), None),
#     }
#     symbol_table_copy = copy.deepcopy(symbol_table)

#     tree = Node(ast.NodeSymbol.PSI, (0,),
#                       Node(ast.NodeSymbol.ARRAY, (4,), '_a2'),
#                       Node(operation, (1, 2, 3, 4),
#                            Node(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), '_a3'),
#                            Node(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), '_a4')))

#     expected_tree = Node(operation, (0,),
#                          Node(ast.NodeSymbol.PSI, (0,),
#                               Node(ast.NodeSymbol.ARRAY, (4,), '_a2'),
#                               Node(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), '_a3')),
#                          Node(ast.NodeSymbol.PSI, (0,),
#                               Node(ast.NodeSymbol.ARRAY, (4,), '_a2'),
#                               Node(ast.NodeSymbol.ARRAY, (1, 2, 3, 4), '_a4')))

#     new_symbol_table, new_tree = _reduce_psi_plus_minus_times_divide(symbol_table, tree)
#     assert symbol_table_copy == symbol_table
#     assert new_tree == expected_tree
#     assert new_symbol_table == symbol_table


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
