import pytest

from moa.ast import MOANodeTypes, BinaryNode, UnaryNode, ArrayNode
from moa.reduction import (
    reduce_ast,
    _reduce_psi_psi, _reduce_psi_transpose, _reduce_psi_plus
)

def test_reduce_psi_psi():
    tree = BinaryNode(MOANodeTypes.PSI, (0,),
                      ArrayNode(MOANodeTypes.ARRAY, (1,), None, ('i0',)),
                      BinaryNode(MOANodeTypes.PSI, (4,),
                                 ArrayNode(MOANodeTypes.ARRAY, (3,), None, (1, 2, 3)),
                                 ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), None, None)))

    new_tree = _reduce_psi_psi(tree)
    expected_tree = BinaryNode(MOANodeTypes.PSI, (0,),
                               ArrayNode(MOANodeTypes.ARRAY, (4,), None, (1, 2, 3, 'i0')),
                               ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), None, None))

    assert new_tree == expected_tree


def test_reduce_psi_transpose():
    tree = BinaryNode(MOANodeTypes.PSI, (0,),
                      ArrayNode(MOANodeTypes.ARRAY, (4,), None, (3, 2, 'i0', 'i1')),
                      UnaryNode(MOANodeTypes.TRANSPOSE, (4, 3, 2, 1),
                                ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), None, None)))

    new_tree = _reduce_psi_transpose(tree)
    expected_tree = BinaryNode(MOANodeTypes.PSI, (0,),
                               ArrayNode(MOANodeTypes.ARRAY, (4,), None, ('i1', 'i0', 2, 3)),
                               ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), None, None))
    assert new_tree == expected_tree


def test_reduce_psi_plus():
    tree = BinaryNode(MOANodeTypes.PSI, (0,),
                      ArrayNode(MOANodeTypes.ARRAY, (4,), None, (1, 2, 'i0', 'i1')),
                      BinaryNode(MOANodeTypes.PLUS, (1, 2, 3, 4),
                                 ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), None, None),
                                 ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), None, None)))

    new_tree = _reduce_psi_plus(tree)
    expected_tree = BinaryNode(MOANodeTypes.PLUS, (0,),
                               BinaryNode(MOANodeTypes.PSI, (0,),
                                          ArrayNode(MOANodeTypes.ARRAY, (4,), None, (1, 2, 'i0', 'i1')),
                                          ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), None, None)),
                               BinaryNode(MOANodeTypes.PSI, (0,),
                                          ArrayNode(MOANodeTypes.ARRAY, (4,), None, (1, 2, 'i0', 'i1')),
                                          ArrayNode(MOANodeTypes.ARRAY, (1, 2, 3, 4), None, None)))
    assert new_tree == expected_tree



@pytest.mark.parametrize("tree,result", [
    # Lenore Simple Example #1 06/01/2018
    (BinaryNode(MOANodeTypes.PSI, (3,),
                ArrayNode(MOANodeTypes.ARRAY, (1,), None, (0,)),
                UnaryNode(MOANodeTypes.TRANSPOSE, (4, 3),
                          BinaryNode(MOANodeTypes.PLUS, (3, 4),
                                     ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A', None),
                                     ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B', None)))),
     ({'i0': (0, 3)},
      BinaryNode(MOANodeTypes.PLUS, (3,),
                 BinaryNode(MOANodeTypes.PSI, (3,),
                            ArrayNode(MOANodeTypes.ARRAY, (2,), None, ('i0', 0)),
                            ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A', None)),
                 BinaryNode(MOANodeTypes.PSI, (3,),
                            ArrayNode(MOANodeTypes.ARRAY, (2,), None, ('i0', 0)),
                            ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B', None))))),
])
def test_reduce_integration(tree, result):
    result_symbol_table, result_tree = result
    new_symbol_table, new_tree = reduce_ast(tree)
    assert new_symbol_table == result_symbol_table
    assert new_tree == result_tree
