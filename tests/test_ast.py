import itertools
import copy

import pytest

from moa.ast import (
    MOANodeTypes, Node, SymbolNode,
    is_array, is_unary_operation, is_binary_operation,
    add_symbol,
    generate_unique_array_name, generate_unique_index_name,
    join_symbol_tables,
    postorder_replacement,
    preorder_replacement
)

@pytest.mark.parametrize('node, result', [
    (Node(MOANodeTypes.ARRAY, None, None), (True, False, False)),
    (Node(MOANodeTypes.TRANSPOSE, None, None), (False, True, False)),
    (Node(MOANodeTypes.CAT, None, None, None), (False, False, True)),
    (Node((MOANodeTypes.DOT, MOANodeTypes.TIMES), None, None, None), (False, False, True)),
])
def test_ast_nodes(node, result):
    assert result == (
        is_array(node),
        is_unary_operation(node),
        is_binary_operation(node))


def test_add_symbol_table_idempodent():
    symbol_table = {}
    symbol_table_copy = copy.deepcopy(symbol_table)
    new_symbol_table = add_symbol(symbol_table, 'A', MOANodeTypes.ARRAY, (3, 4), None)
    assert symbol_table == symbol_table_copy
    assert new_symbol_table == {'A': (MOANodeTypes.ARRAY, (3, 4), None)}


def test_symbol_table_unique_array():
    symbol_table = {}
    symbol_table_copy = copy.deepcopy(symbol_table)
    symbol_array_name_1 = generate_unique_array_name(symbol_table)
    new_symbol_table_1 = add_symbol(symbol_table, symbol_array_name_1, MOANodeTypes.ARRAY, (3, 4), None)
    symbol_array_name_2 = generate_unique_array_name(new_symbol_table_1)
    assert symbol_table == symbol_table_copy
    assert symbol_array_name_1 != symbol_array_name_2


def test_symbol_table_unique_array():
    symbol_table = {}
    symbol_table_copy = copy.deepcopy(symbol_table)
    symbol_index_name_1 = generate_unique_index_name(symbol_table)
    new_symbol_table_1 = add_symbol(symbol_table, symbol_index_name_1, MOANodeTypes.INDEX, (3, 4), None)
    symbol_index_name_2 = generate_unique_index_name(new_symbol_table_1)
    assert symbol_table == symbol_table_copy
    assert symbol_index_name_1 != symbol_index_name_2


def test_join_symbol_tables_simple():
    left_tree = Node(MOANodeTypes.PLUS, None,
                     Node(MOANodeTypes.ARRAY, None, 'A'),
                     Node(MOANodeTypes.ARRAY, None, 'B'))
    left_symbol_table = {
        'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
        '_a1': SymbolNode(MOANodeTypes.ARRAY, (1, Node(MOANodeTypes.ARRAY, (), 'm')), None),
        'B': SymbolNode(MOANodeTypes.ARRAY, (2, 4), None)
    }

    right_tree = Node(MOANodeTypes.MINUS, None,
                      Node(MOANodeTypes.ARRAY, None, 'A'),
                      Node(MOANodeTypes.ARRAY, None, '_a3'))
    right_symbol_table = {
        'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
        '_a3': SymbolNode(MOANodeTypes.ARRAY, (Node(MOANodeTypes.ARRAY, (), '_a10'), Node(MOANodeTypes.ARRAY, (), 'm')), None),
        '_a10': SymbolNode(MOANodeTypes.ARRAY, (), (1,)),
        'm': SymbolNode(MOANodeTypes.ARRAY, (), None),
        'B': SymbolNode(MOANodeTypes.ARRAY, (2, 4), None),
        'n': SymbolNode(MOANodeTypes.ARRAY, (), None),
    }

    symbol_table, new_left_tree, new_right_tree = join_symbol_tables(left_symbol_table, left_tree, right_symbol_table, right_tree)

    assert symbol_table == {
        'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
        'B': SymbolNode(MOANodeTypes.ARRAY, (2, 4), None),
        'm': SymbolNode(MOANodeTypes.ARRAY, (), None),
        '_a0': SymbolNode(MOANodeTypes.ARRAY, (), (1,)),
        '_a1': SymbolNode(MOANodeTypes.ARRAY, (Node(MOANodeTypes.ARRAY, (), '_a0'), Node(MOANodeTypes.ARRAY, (), 'm')), None),
    }
    assert new_left_tree == Node(MOANodeTypes.PLUS, None,
                                       Node(MOANodeTypes.ARRAY, None, 'A'),
                                       Node(MOANodeTypes.ARRAY, None, 'B'))
    assert new_right_tree == Node(MOANodeTypes.MINUS, None,
                                  Node(MOANodeTypes.ARRAY, None, 'A'),
                                  Node(MOANodeTypes.ARRAY, None, '_a1'))


def test_postorder_replacement():
    counter = itertools.count()

    def replacement_function(symbol_table, node):
        node_value = (next(counter),)
        if is_unary_operation(node):
            return symbol_table, Node(node.node_type, node_value, node.right_node)
        elif is_binary_operation(node):
            return symbol_table, Node(node.node_type, node_value, node.left_node, node.right_node)
        return symbol_table, Node(node.node_type, node_value, None)

    tree = Node(MOANodeTypes.CAT, None,
                Node(MOANodeTypes.PLUSRED, None,
                     Node(MOANodeTypes.ARRAY, None, None)),
                Node(MOANodeTypes.PLUS, None,
                     Node(MOANodeTypes.SHAPE, None,
                          Node(MOANodeTypes.ARRAY, None, None)),
                     Node(MOANodeTypes.RAV, None,
                          Node(MOANodeTypes.ARRAY, None, None))))
    symbol_table = {} # can get away with not contructing symbol table

    expected_tree = (MOANodeTypes.CAT, (7,),
                     (MOANodeTypes.PLUSRED, (1,),
                      (MOANodeTypes.ARRAY, (0,), None)),
                     (MOANodeTypes.PLUS, (6,),
                      (MOANodeTypes.SHAPE, (3,),
                       (MOANodeTypes.ARRAY, (2,), None)),
                      (MOANodeTypes.RAV, (5,),
                       (MOANodeTypes.ARRAY, (4,), None))))

    new_symbol_table, new_tree = postorder_replacement(symbol_table, tree, replacement_function)
    assert new_symbol_table == symbol_table
    assert new_tree == expected_tree


def test_preorder_replacement():
    counter = itertools.count()

    def replacement_function(symbol_table, node):
        # termination condition we end up visiting each node twice
        if node.shape is not None:
            return None, None

        node_value = (next(counter),)
        if is_unary_operation(node):
            return symbol_table, Node(node.node_type, node_value, node.right_node)
        elif is_binary_operation(node):
            return symbol_table, Node(node.node_type, node_value, node.left_node, node.right_node)
        return symbol_table, Node(node.node_type, node_value, None)

    tree = Node(MOANodeTypes.CAT, None,
                      Node(MOANodeTypes.PLUSRED, None,
                           Node(MOANodeTypes.ARRAY, None, None)),
                Node(MOANodeTypes.PLUS, None,
                     Node(MOANodeTypes.SHAPE, None,
                          Node(MOANodeTypes.ARRAY, None, None)),
                     Node(MOANodeTypes.RAV, None,
                          Node(MOANodeTypes.ARRAY, None, None))))
    symbol_table = {} # can get away with not contructing symbol table

    expected_tree = (MOANodeTypes.CAT, (0,),
                     (MOANodeTypes.PLUSRED, (1,),
                      (MOANodeTypes.ARRAY, (2,), None)),
                     (MOANodeTypes.PLUS, (3,),
                      (MOANodeTypes.SHAPE, (4,),
                       (MOANodeTypes.ARRAY, (5,), None)),
                      (MOANodeTypes.RAV, (6,),
                       (MOANodeTypes.ARRAY, (7,), None))))

    new_symbol_table, new_tree = preorder_replacement(symbol_table, tree, replacement_function)
    assert symbol_table == new_symbol_table
    assert new_tree == expected_tree
