from moa.visualize import visualize_ast, print_ast
from moa.ast import MOANodeTypes, Node, SymbolNode


def test_graphviz_visualization():
    symbol_table = {'_a1': SymbolNode(MOANodeTypes.ARRAY, (1,), (0,)),
                    'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
                    'B': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None)}
    tree = Node(MOANodeTypes.PSI, None,
                Node(MOANodeTypes.ARRAY, None, '_a1'),
                Node(MOANodeTypes.TRANSPOSE, None,
                     Node(MOANodeTypes.PLUS, None,
                          Node(MOANodeTypes.ARRAY, None, 'A'),
                          Node(MOANodeTypes.ARRAY, None, 'B'))))

    visualize_ast(symbol_table, tree)


def test_print_visualization():
    symbol_table = {'_a1': SymbolNode(MOANodeTypes.ARRAY, (1,), (0,)),
                    'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
                    'B': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None)}
    tree = Node(MOANodeTypes.PSI, None,
                Node(MOANodeTypes.ARRAY, None, '_a1'),
                Node(MOANodeTypes.TRANSPOSE, None,
                     Node(MOANodeTypes.PLUS, None,
                          Node(MOANodeTypes.ARRAY, None, 'A'),
                          Node(MOANodeTypes.ARRAY, None, 'B'))))

    print_ast(symbol_table, tree)
