import pytest

from moa.ast import MOANodeTypes, is_array, is_unary_operation, is_binary_operation

@pytest.mark.parametrize('node, result', [
    ((MOANodeTypes.ARRAY, None, None, None), (True, False, False)),
    ((MOANodeTypes.PLUSRED, None, None), (False, True, False)),
    ((MOANodeTypes.CAT, None, None, None), (False, False, True)),
])
def test_ast_nodes(node, result):
    assert is_array(node) == result[0]
    assert is_unary_operation(node) == result[1]
    assert is_binary_operation(node) == result[2]
