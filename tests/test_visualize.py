from moa.visualize import visualize_ast, print_ast
from moa.ast import MOANodeTypes, ArrayNode, UnaryNode, BinaryNode, SymbolNode


def test_graphviz_visualization():
    symbol_table = {'_a1': SymbolNode(MOANodeTypes.ARRAY, (1,), (0,)),
                    'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
                    'B': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None)}
    tree = BinaryNode(MOANodeTypes.PSI, None,
                      ArrayNode(MOANodeTypes.ARRAY, None, '_a1'),
                      UnaryNode(MOANodeTypes.TRANSPOSE, None,
                                BinaryNode(MOANodeTypes.PLUS, None,
                                           ArrayNode(MOANodeTypes.ARRAY, None, 'A'),
                                           ArrayNode(MOANodeTypes.ARRAY, None, 'B'))))

    visualize_ast(symbol_table, tree)


def test_print_visualization():
    symbol_table = {'_a1': SymbolNode(MOANodeTypes.ARRAY, (1,), (0,)),
                    'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
                    'B': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None)}
    tree = BinaryNode(MOANodeTypes.PSI, None,
                      ArrayNode(MOANodeTypes.ARRAY, None, '_a1'),
                      UnaryNode(MOANodeTypes.TRANSPOSE, None,
                                BinaryNode(MOANodeTypes.PLUS, None,
                                           ArrayNode(MOANodeTypes.ARRAY, None, 'A'),
                                           ArrayNode(MOANodeTypes.ARRAY, None, 'B'))))

    print_ast(symbol_table, tree)
