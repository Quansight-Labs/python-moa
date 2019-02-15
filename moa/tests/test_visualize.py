from moa.visualize import visualize_ast
from moa.ast import MOANodeTypes, ArrayNode, UnaryNode, BinaryNode


def test_visualization():
    tree = BinaryNode(MOANodeTypes.PSI, None,
                      ArrayNode(MOANodeTypes.ARRAY, (1,), None, (0,)),
                      UnaryNode(MOANodeTypes.TRANSPOSE, None,
                                BinaryNode(MOANodeTypes.PLUS, None,
                                           ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A', None),
                                           ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B', None))))

    visualize_ast(tree)
