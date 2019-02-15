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
    (ArrayNode(MOANodeTypes.ARRAY, None, None, None), (True, False, False)),
    (UnaryNode(MOANodeTypes.PLUSRED, None, None), (False, True, False)),
    (BinaryNode(MOANodeTypes.CAT, None, None, None), (False, False, True)),
])
def test_ast_nodes(node, result):
    assert is_array(node) == result[0]
    assert is_unary_operation(node) == result[1]
    assert is_binary_operation(node) == result[2]


def test_postorder_replacement():
    counter = itertools.count()

    def replacement_function(node):
        if is_unary_operation(node):
            return (next(counter), node[2])
        elif is_binary_operation(node):
            return (next(counter), node[2], node[3])
        return (next(counter),)

    tree = BinaryNode(MOANodeTypes.CAT, None,
                      UnaryNode(MOANodeTypes.PLUSRED, None,
                                ArrayNode(MOANodeTypes.ARRAY, None, None, 1)),
                      BinaryNode(MOANodeTypes.PLUS, None,
                                 UnaryNode(MOANodeTypes.SHAPE, None,
                                           ArrayNode(MOANodeTypes.ARRAY, None, None, 2)),
                                 UnaryNode(MOANodeTypes.RAV, None,
                                           ArrayNode(MOANodeTypes.ARRAY, None, None, 3))))

    new_tree = postorder_replacement(tree, replacement_function)
    print(new_tree)
    assert new_tree == (7, (1, (0,)), (6, (3, (2,)), (5, (4,))))
