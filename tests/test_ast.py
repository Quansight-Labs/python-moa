import itertools

import pytest

from moa.ast import (
    MOANodeTypes,
    ArrayNode, UnaryNode, BinaryNode,
    is_array, is_unary_operation, is_binary_operation,
    postorder_replacement,
    preorder_replacement
)

@pytest.mark.parametrize('node, result', [
    (ArrayNode(MOANodeTypes.ARRAY, None, None), (True, False, False)),
    (UnaryNode(MOANodeTypes.PLUSRED, None, None), (False, True, False)),
    (BinaryNode(MOANodeTypes.CAT, None, None, None), (False, False, True)),
])
def test_ast_nodes(node, result):
    assert result == (
        is_array(node),
        is_unary_operation(node),
        is_binary_operation(node))


def test_postorder_replacement():
    counter = itertools.count()

    def replacement_function(node, symbol_table):
        node_value = (next(counter),)
        if is_unary_operation(node):
            return UnaryNode(node.node_type, node_value, node.right_node)
        elif is_binary_operation(node):
            return BinaryNode(node.node_type, node_value, node.left_node, node.right_node)
        return ArrayNode(node.node_type, node_value, None)

    tree = BinaryNode(MOANodeTypes.CAT, None,
                      UnaryNode(MOANodeTypes.PLUSRED, None,
                                ArrayNode(MOANodeTypes.ARRAY, None, None)),
                      BinaryNode(MOANodeTypes.PLUS, None,
                                 UnaryNode(MOANodeTypes.SHAPE, None,
                                           ArrayNode(MOANodeTypes.ARRAY, None, None)),
                                 UnaryNode(MOANodeTypes.RAV, None,
                                           ArrayNode(MOANodeTypes.ARRAY, None, None))))
    symbol_table = {} # can get away with not contructing symbol table

    expected_tree = (MOANodeTypes.CAT, (7,),
                     (MOANodeTypes.PLUSRED, (1,),
                      (MOANodeTypes.ARRAY, (0,), None)),
                     (MOANodeTypes.PLUS, (6,),
                      (MOANodeTypes.SHAPE, (3,),
                       (MOANodeTypes.ARRAY, (2,), None)),
                      (MOANodeTypes.RAV, (5,),
                       (MOANodeTypes.ARRAY, (4,), None))))

    new_tree = postorder_replacement(tree, replacement_function, symbol_table)
    assert new_tree == expected_tree


def test_preorder_replacement():
    counter = itertools.count()

    def replacement_function(node, symbol_table):
        # termination condition we end up visiting each node twice
        if node.shape is not None:
            return None

        node_value = (next(counter),)
        if is_unary_operation(node):
            return UnaryNode(node.node_type, node_value, node.right_node)
        elif is_binary_operation(node):
            return BinaryNode(node.node_type, node_value, node.left_node, node.right_node)
        return ArrayNode(node.node_type, node_value, None)

    tree = BinaryNode(MOANodeTypes.CAT, None,
                      UnaryNode(MOANodeTypes.PLUSRED, None,
                                ArrayNode(MOANodeTypes.ARRAY, None, None)),
                      BinaryNode(MOANodeTypes.PLUS, None,
                                 UnaryNode(MOANodeTypes.SHAPE, None,
                                           ArrayNode(MOANodeTypes.ARRAY, None, None)),
                                 UnaryNode(MOANodeTypes.RAV, None,
                                           ArrayNode(MOANodeTypes.ARRAY, None, None))))
    symbol_table = {} # can get away with not contructing symbol table

    expected_tree = (MOANodeTypes.CAT, (0,),
                     (MOANodeTypes.PLUSRED, (1,),
                      (MOANodeTypes.ARRAY, (2,), None)),
                     (MOANodeTypes.PLUS, (3,),
                      (MOANodeTypes.SHAPE, (4,),
                       (MOANodeTypes.ARRAY, (5,), None)),
                      (MOANodeTypes.RAV, (6,),
                       (MOANodeTypes.ARRAY, (7,), None))))

    new_tree = preorder_replacement(tree, replacement_function, symbol_table)
    assert new_tree == expected_tree
