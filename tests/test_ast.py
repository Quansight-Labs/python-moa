import itertools
import copy

import pytest

from moa import ast
from moa import testing


# is node type
@pytest.mark.parametrize('node, result', [
    (ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),
     (True, False, False, False)),
    (ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (), (None,)),
     (False, True, True, False)),
    (ast.Node((ast.NodeSymbol.CAT,), None, (), (None, None)),
     (False, True, False, True)),
    (ast.Node((ast.NodeSymbol.DOT, ast.NodeSymbol.TIMES), None, (), (None, None)),
     (False, True, False, True)),
])
def test_ast_nodes(node, result):
    context = ast.create_context(ast=node)
    assert result == (
        ast.is_array(context),
        ast.is_operation(context),
        ast.is_unary_operation(context),
        ast.is_binary_operation(context))


# node selection and replacement
@pytest.mark.parametrize('node, selection, result_node', [
    (ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),
     (),
     ast.Node((ast.NodeSymbol.ARRAY,), None, (), ())),

    (ast.Node(ast.NodeSymbol.PLUS, None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, (0,), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), None, (1,), ()))),
     (0,),
     ast.Node((ast.NodeSymbol.ARRAY,), None, (0,), ())),

    (ast.Node((ast.NodeSymbol.PLUS,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, (0,), ()),
        ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (1,), (
            ast.Node((ast.NodeSymbol.ARRAY,), None, (2,), ()),
        )))),
     (1, 0),
     ast.Node((ast.NodeSymbol.ARRAY,), None, (2,), ())),
])
def test_ast_select_node(node, selection, result_node):
    context = ast.create_context(ast=node)
    result_context = ast.create_context(ast=result_node)
    testing.assert_context_equal(
        ast.select_node(context, selection),
        result_context)


@pytest.mark.parametrize('node, replacement_node, selection, result_node', [
    (ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),
     ast.Node((ast.NodeSymbol.ARRAY,), None, (0,), ()),
     (),
     ast.Node((ast.NodeSymbol.ARRAY,), None, (0,), ())),

    (ast.Node((ast.NodeSymbol.PLUS,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, (0,), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), None, (1,), ()))),
     ast.Node((ast.NodeSymbol.ARRAY,), None, (10,), ()),
     (0,),
     ast.Node((ast.NodeSymbol.PLUS,), None, (), (
         ast.Node((ast.NodeSymbol.ARRAY,), None, (10,), ()),
         ast.Node((ast.NodeSymbol.ARRAY,), None, (1,), ())))),

    (ast.Node((ast.NodeSymbol.PLUS,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, (0,), ()),
        ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (1,), (
            ast.Node((ast.NodeSymbol.ARRAY,), None, (2,), ()),
        )))),
     ast.Node((ast.NodeSymbol.ARRAY,), None, (10,), ()),
     (1, 0),
     ast.Node((ast.NodeSymbol.PLUS,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, (0,), ()),
        ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (1,), (
            ast.Node((ast.NodeSymbol.ARRAY,), None, (10,), ()),
        ))))),
])
def test_ast_replace_node(node, replacement_node, selection, result_node):
    context = ast.create_context(ast=node)
    result_context = ast.create_context(ast=result_node)
    testing.assert_context_equal(
        ast.replace_node(context, replacement_node, selection),
        result_context)


# symbol table tests
def test_add_symbol_table_idempodent():
    context = ast.create_context()
    context_copy = copy.deepcopy(context)
    new_context = ast.add_symbol(context, 'A', ast.NodeSymbol.ARRAY, (3, 4), None, None)
    assert context == context_copy
    assert new_context == ast.Context(ast=None, symbol_table={'A': (ast.NodeSymbol.ARRAY, (3, 4), None, None)})


def test_symbol_table_unique_array():
    context = ast.create_context()
    context_copy = copy.deepcopy(context)
    symbol_array_name_1 = ast.generate_unique_array_name(context)
    new_context = ast.add_symbol(context, symbol_array_name_1, ast.NodeSymbol.ARRAY, (3, 4), None, None)
    symbol_array_name_2 = ast.generate_unique_array_name(new_context)
    assert context == context_copy
    assert symbol_array_name_1 != symbol_array_name_2


def test_symbol_table_unique_index():
    context = ast.create_context()
    context_copy = copy.deepcopy(context)
    symbol_index_name_1 = ast.generate_unique_index_name(context)
    new_context = ast.add_symbol(context, symbol_index_name_1, ast.NodeSymbol.ARRAY, (3, 4), None, None)
    symbol_index_name_2 = ast.generate_unique_index_name(new_context)
    assert context == context_copy
    assert symbol_index_name_1 != symbol_index_name_2


# def test_join_symbol_tables_simple():
#     left_tree = Node(MOANodeTypes.PLUS, None,
#                      Node(MOANodeTypes.ARRAY, None, 'A'),
#                      Node(MOANodeTypes.ARRAY, None, 'B'))
#     left_symbol_table = {
#         'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
#         '_a1': SymbolNode(MOANodeTypes.ARRAY, (1, Node(MOANodeTypes.ARRAY, (), 'm')), None),
#         'B': SymbolNode(MOANodeTypes.ARRAY, (2, 4), None)
#     }

#     right_tree = Node(MOANodeTypes.MINUS, None,
#                       Node(MOANodeTypes.ARRAY, None, 'A'),
#                       Node(MOANodeTypes.ARRAY, None, '_a3'))
#     right_symbol_table = {
#         'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
#         '_a3': SymbolNode(MOANodeTypes.ARRAY, (Node(MOANodeTypes.ARRAY, (), '_a10'), Node(MOANodeTypes.ARRAY, (), 'm')), None),
#         '_a10': SymbolNode(MOANodeTypes.ARRAY, (), (1,)),
#         'm': SymbolNode(MOANodeTypes.ARRAY, (), None),
#         'B': SymbolNode(MOANodeTypes.ARRAY, (2, 4), None),
#         'n': SymbolNode(MOANodeTypes.ARRAY, (), None),
#     }

#     symbol_table, new_left_tree, new_right_tree = join_symbol_tables(left_symbol_table, left_tree, right_symbol_table, right_tree)

#     assert symbol_table == {
#         'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
#         'B': SymbolNode(MOANodeTypes.ARRAY, (2, 4), None),
#         'm': SymbolNode(MOANodeTypes.ARRAY, (), None),
#         '_a0': SymbolNode(MOANodeTypes.ARRAY, (), (1,)),
#         '_a1': SymbolNode(MOANodeTypes.ARRAY, (Node(MOANodeTypes.ARRAY, (), '_a0'), Node(MOANodeTypes.ARRAY, (), 'm')), None),
#     }
#     assert new_left_tree == Node(MOANodeTypes.PLUS, None,
#                                        Node(MOANodeTypes.ARRAY, None, 'A'),
#                                        Node(MOANodeTypes.ARRAY, None, 'B'))
#     assert new_right_tree == Node(MOANodeTypes.MINUS, None,
#                                   Node(MOANodeTypes.ARRAY, None, 'A'),
#                                   Node(MOANodeTypes.ARRAY, None, '_a1'))


def test_postorder_replacement():
    counter = itertools.count()

    def replacement_function(context):
        node_value = (next(counter),)
        return Context()

    tree = ast.Node((ast.NodeSymbol.CAT,), None, (), (
        ast.Node(ast.NodeSymbol.TRASPOSE, None, (), (ast.Node(NodeSymbol.ARRAY, None, (), ()))),
        ast.Node(NodeSymbol.PLUS, None, (), (
            ast.Node(NodeSymbol.SHAPE, None, (), (ast.Node(NodeSymbol.ARRAY, None, (), ()))),
            ast.Node(NodeSymbol.RAV, None, (), (
                ast.Node(ast.NodeSymbol.ARRAY, None, (), ())))))))

    expected_tree = ast.Node((ast.NodeSymbol.CAT,), (7,), (), (
        ast.Node(ast.NodeSymbol.TRASPOSE, (1,), (), (
            ast.Node(NodeSymbol.ARRAY, (0,), (), ()))),
        ast.Node(NodeSymbol.PLUS, (6,), (), (
            ast.Node(NodeSymbol.SHAPE, (3,), (), (
                ast.Node(NodeSymbol.ARRAY, (2,), (), ()))),
            ast.Node(NodeSymbol.RAV, (5,), (), (
                ast.Node(ast.NodeSymbol.ARRAY, (4,), (), ())))))))

    raise NotImplementedError('complete')
    new_symbol_table, new_tree = node_traversal(symbol_table, tree, replacement_function, traversal='post')
    assert new_symbol_table == symbol_table
    assert new_tree == expected_tree


# def test_preorder_replacement():
#     counter = itertools.count()

#     def replacement_function(symbol_table, node):
#         # termination condition we end up visiting each node twice
#         if node.shape is not None:
#             return None, None

#         node_value = (next(counter),)
#         if is_unary_operation(node):
#             return symbol_table, Node(node.node_type, node_value, node.right_node)
#         elif is_binary_operation(node):
#             return symbol_table, Node(node.node_type, node_value, node.left_node, node.right_node)
#         return symbol_table, Node(node.node_type, node_value, None)

#     tree = Node(MOANodeTypes.CAT, None,
#                       Node(MOANodeTypes.PLUSRED, None,
#                            Node(MOANodeTypes.ARRAY, None, None)),
#                 Node(MOANodeTypes.PLUS, None,
#                      Node(MOANodeTypes.SHAPE, None,
#                           Node(MOANodeTypes.ARRAY, None, None)),
#                      Node(MOANodeTypes.RAV, None,
#                           Node(MOANodeTypes.ARRAY, None, None))))
#     symbol_table = {} # can get away with not contructing symbol table

#     expected_tree = (MOANodeTypes.CAT, (0,),
#                      (MOANodeTypes.PLUSRED, (1,),
#                       (MOANodeTypes.ARRAY, (2,), None)),
#                      (MOANodeTypes.PLUS, (3,),
#                       (MOANodeTypes.SHAPE, (4,),
#                        (MOANodeTypes.ARRAY, (5,), None)),
#                       (MOANodeTypes.RAV, (6,),
#                        (MOANodeTypes.ARRAY, (7,), None))))

#     new_symbol_table, new_tree = node_traversal(symbol_table, tree, replacement_function, traversal='pre')
#     assert symbol_table == new_symbol_table
#     assert new_tree == expected_tree
