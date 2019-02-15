import pytest

from moa.ast import MOANodeTypes, ArrayNode, UnaryNode, BinaryNode
from moa.shape import calculate_shapes


@pytest.mark.parametrize("tree, result", [
    # ARRAY
    (ArrayNode(MOANodeTypes.ARRAY, (2,), None, (3, 5)),
     ArrayNode(MOANodeTypes.ARRAY, (2,), None, (3, 5))),
    # TRANSPOSE
    (UnaryNode(MOANodeTypes.TRANSPOSE, None,
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), None, None)),
     UnaryNode(MOANodeTypes.TRANSPOSE, (5, 4, 3),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), None, None))),
    # PSI
    (BinaryNode(MOANodeTypes.PSI, None,
                ArrayNode(MOANodeTypes.ARRAY, (2,), None, (3, 5)),
                ArrayNode(MOANodeTypes.ARRAY, (4, 5, 6), None, None)),
     BinaryNode(MOANodeTypes.PSI, (6,),
                ArrayNode(MOANodeTypes.ARRAY, (2,), None, (3, 5)),
                ArrayNode(MOANodeTypes.ARRAY, (4, 5, 6), None, None))),
    # PLUS
    (BinaryNode(MOANodeTypes.PLUS, None,
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), None, None),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), None, None)),
     BinaryNode(MOANodeTypes.PLUS, (3, 4, 5),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), None, None),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4, 5), None, None))),
])
def test_shape_unit(tree, result):
    new_tree = calculate_shapes(tree)
    print(new_tree)
    assert new_tree == result


@pytest.mark.parametrize("tree,result", [
    # Lenore Simple Example #1 06/01/2018
    (BinaryNode(MOANodeTypes.PSI, None,
                ArrayNode(MOANodeTypes.ARRAY, (1,), None, (0,)),
                UnaryNode(MOANodeTypes.TRANSPOSE, None,
                          BinaryNode(MOANodeTypes.PLUS, None,
                                     ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A', None),
                                     ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B', None)))),
     (MOANodeTypes.PSI, (3,),
      (MOANodeTypes.ARRAY, (1,), None, (0,)),
      (MOANodeTypes.TRANSPOSE, (4, 3),
       (MOANodeTypes.PLUS, (3, 4),
        (MOANodeTypes.ARRAY, (3, 4), 'A', None),
        (MOANodeTypes.ARRAY, (3, 4), 'B', None))))),
])
def test_shape_integration(tree, result):
    new_tree = calculate_shapes(tree)
    print(new_tree)
    assert new_tree == result
