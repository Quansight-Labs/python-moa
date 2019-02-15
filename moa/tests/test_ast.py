import itertools

import pytest

from moa.ast import (
    MOANodeTypes,
    is_array, is_unary_operation, is_binary_operation,
    postorder_replacement,
    preorder_replacement
)

@pytest.mark.parametrize('node, result', [
    ((MOANodeTypes.ARRAY, None, None, None), (True, False, False)),
    ((MOANodeTypes.PLUSRED, None, None), (False, True, False)),
    ((MOANodeTypes.CAT, None, None, None), (False, False, True)),
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

    tree = (MOANodeTypes.CAT, None,
            (MOANodeTypes.PLUSRED, None,
             (MOANodeTypes.ARRAY, None, None, 1)),
            (MOANodeTypes.PLUS, None,
             (MOANodeTypes.SHAPE, None,
              (MOANodeTypes.ARRAY, None, None, 2)),
             (MOANodeTypes.RAV, None,
              (MOANodeTypes.ARRAY, None, None, 3))))

    new_tree = postorder_replacement(tree, replacement_function)
    print(new_tree)
    assert new_tree == (7, (1, (0,)), (6, (3, (2,)), (5, (4,))))
