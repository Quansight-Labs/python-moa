import itertools
import copy

import pytest

from moa import ast
from moa import visualize
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
@pytest.mark.parametrize('node, result', [
    (ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()), 0),
    (ast.Node((ast.NodeSymbol.ARRAY,), None, (), (1, 2, 3)), 3),
])
def test_ast_num_node_children(node, result):
    context = ast.create_context(ast=node)
    assert ast.num_node_children(context) == result


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
    # root
    (ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),
     ast.Node((ast.NodeSymbol.ARRAY,), None, (0,), ()),
     (),
     ast.Node((ast.NodeSymbol.ARRAY,), None, (0,), ())),

    # leaf node
    (ast.Node((ast.NodeSymbol.PLUS,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, (0,), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), None, (1,), ()))),
     ast.Node((ast.NodeSymbol.ARRAY,), None, (10,), ()),
     (0,),
     ast.Node((ast.NodeSymbol.PLUS,), None, (), (
         ast.Node((ast.NodeSymbol.ARRAY,), None, (10,), ()),
         ast.Node((ast.NodeSymbol.ARRAY,), None, (1,), ())))),

    # nested leaf node
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

    # selection not fully to leaf node
    (ast.Node((ast.NodeSymbol.PLUS,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),
        ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (), (
            ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),
        )))),
     ast.Node((ast.NodeSymbol.ARRAY,), None, (10,), ()),
     (1,),
     ast.Node((ast.NodeSymbol.PLUS,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),
         ast.Node((ast.NodeSymbol.ARRAY,), None, (10,), ()),
     )))
])
def test_ast_replace_node(node, replacement_node, selection, result_node):
    context = ast.create_context(ast=node)
    result_context = ast.create_context(ast=result_node)
    testing.assert_context_equal(
        ast.replace_node(context, replacement_node, selection),
        result_context)


@pytest.mark.parametrize('node, replacement_shape, selection, result_node', [
    # root
    (ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),
     (1, 2, 3),
     (),
     ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3), (), ())),

    # leaf node
    (ast.Node((ast.NodeSymbol.PLUS,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()))),
     (1, 2, 3),
     (0,),
     ast.Node((ast.NodeSymbol.PLUS,), None, (), (
         ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3), (), ()),
         ast.Node((ast.NodeSymbol.ARRAY,), None, (), ())))),

    # nested leaf node
    (ast.Node((ast.NodeSymbol.PLUS,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),
        ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (), (
            ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),
        )))),
     (1, 2, 3),
     (1, 0),
     ast.Node((ast.NodeSymbol.PLUS,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),
        ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3), (), ()),
        ))))),

    # selection not fully to leaf node
    (ast.Node((ast.NodeSymbol.PLUS,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),
        ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (), (
            ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),
        )))),
     (1, 2, 3),
     (1,),
     ast.Node((ast.NodeSymbol.PLUS,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),
        ast.Node((ast.NodeSymbol.TRANSPOSE,), (1, 2, 3), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),
        ))))),
])
def test_ast_replace_node_shape(node, replacement_shape, selection, result_node):
    context = ast.create_context(ast=node)
    result_context = ast.create_context(ast=result_node)
    testing.assert_context_equal(
        ast.replace_node_shape(context, replacement_shape, selection),
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

# symbolic elements
@pytest.mark.parametrize('elements, result', [
    ((1, 2, 3), False),
    (((ast.NodeSymbol.ARRAY, None, (), ()), 2, 3, 4), True)
])
def test_has_symbolic_elements(elements, result):
    assert ast.has_symbolic_elements(elements) == result


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
        return ast.replace_node_shape(context, (next(counter),), ())

    tree = ast.Node((ast.NodeSymbol.CAT,), None, (), (
        ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (), (
            ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),)),
        ast.Node((ast.NodeSymbol.PLUS,), None, (), (
            ast.Node((ast.NodeSymbol.SHAPE,), None, (), (
                ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),)),
            ast.Node((ast.NodeSymbol.RAV,), None, (), (
                ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),)),)),))
    context = ast.create_context(ast=tree)
    context_copy = copy.deepcopy(context)

    expected_tree = ast.Node((ast.NodeSymbol.CAT,), (7,), (), (
        ast.Node((ast.NodeSymbol.TRANSPOSE,), (1,), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (0,), (), ()),)),
        ast.Node((ast.NodeSymbol.PLUS,), (6,), (), (
            ast.Node((ast.NodeSymbol.SHAPE,), (3,), (), (
                ast.Node((ast.NodeSymbol.ARRAY,), (2,), (), ()),)),
            ast.Node((ast.NodeSymbol.RAV,), (5,), (), (
                ast.Node((ast.NodeSymbol.ARRAY,), (4,), (), ()),)),)),))
    expected_context = ast.create_context(ast=expected_tree)

    new_context = ast.node_traversal(context, replacement_function, traversal='postorder')

    testing.assert_context_equal(context, context_copy)
    testing.assert_context_equal(new_context, expected_context)


def test_preorder_replacement():
    counter = itertools.count()

    def replacement_function(context):
        if context.ast.shape is None:
            return ast.replace_node_shape(context, (next(counter),), ())
        return None

    tree = ast.Node((ast.NodeSymbol.CAT,), None, (), (
        ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (), (
            ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),)),
        ast.Node((ast.NodeSymbol.PLUS,), None, (), (
            ast.Node((ast.NodeSymbol.SHAPE,), None, (), (
                ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),)),
            ast.Node((ast.NodeSymbol.RAV,), None, (), (
                ast.Node((ast.NodeSymbol.ARRAY,), None, (), ()),)),)),))
    context = ast.create_context(ast=tree)
    context_copy = copy.deepcopy(context)

    expected_tree = ast.Node((ast.NodeSymbol.CAT,), (0,), (), (
        ast.Node((ast.NodeSymbol.TRANSPOSE,), (1,), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (2,), (), ()),)),
        ast.Node((ast.NodeSymbol.PLUS,), (3,), (), (
            ast.Node((ast.NodeSymbol.SHAPE,), (4,), (), (
                ast.Node((ast.NodeSymbol.ARRAY,), (5,), (), ()),)),
            ast.Node((ast.NodeSymbol.RAV,), (6,), (), (
                ast.Node((ast.NodeSymbol.ARRAY,), (7,), (), ()),)),)),))
    expected_context = ast.create_context(ast=expected_tree)

    new_context = ast.node_traversal(context, replacement_function, traversal='preorder')

    testing.assert_context_equal(context, context_copy)
    testing.assert_context_equal(new_context, expected_context)
