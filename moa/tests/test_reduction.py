import pytest

from moa.ast import MOANodeTypes, BinaryNode, UnaryNode, ArrayNode
from moa.reduction import reduce_ast


@pytest.mark.parametrize("tree,result", [
    # Lenore Simple Example #1 06/01/2018
    (BinaryNode(MOANodeTypes.PSI, (3,),
                ArrayNode(MOANodeTypes.ARRAY, (1,), None, (0,)),
                UnaryNode(MOANodeTypes.TRANSPOSE, (4, 3),
                          BinaryNode(MOANodeTypes.PLUS, (3, 4),
                                     ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A', None),
                                     ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B', None)))),
     ({'i1': (0, 2)},
      BinaryNode(MOANodeTypes.PLUS, (3,),
                 BinaryNode(MOANodeTypes.PSI, (3,),
                            ArrayNode(MOANodeTypes.ARRAY, (1,), None, ('i1', 0)),
                            ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A', None)),
                 BinaryNode(MOANodeTypes.PSI, (3,),
                            ArrayNode(MOANodeTypes.ARRAY, (1,), None, ('i1', 0)),
                            ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B', None))))),
])
def test_reduce_integration(tree, result):
    result_symbol_table, result_tree = result
    new_symbol_table, new_tree = reduce_ast(tree)
    print(new_tree)
    assert new_symbol_table == result_symbol_table
    assert new_tree == result_tree
