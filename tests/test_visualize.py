from moa.visualize import visualize_ast, print_ast
from moa import ast


def test_graphviz_visualization():
    symbol_table = {'_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1,), None, (0,)),
                    'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4), None, None),
                    'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4), None, None)}
    tree = ast.Node((ast.NodeSymbol.PSI,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a1',), ()),
        ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (), (
            ast.Node((ast.NodeSymbol.PLUS,), None, (), (
                ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),
                ast.Node((ast.NodeSymbol.ARRAY,), None, ('B',), ()),)),))))

    context = ast.create_context(ast=tree, symbol_table=symbol_table)
    visualize_ast(context)


def test_print_visualization():
    symbol_table = {'_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1,), None, (0,)),
                    'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4), None, None),
                    'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4), None, None)}
    tree = ast.Node((ast.NodeSymbol.PSI,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a1',), ()),
        ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (), (
            ast.Node((ast.NodeSymbol.PLUS,), None, (), (
                ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),
                ast.Node((ast.NodeSymbol.ARRAY,), None, ('B',), ()),)),))))

    context = ast.create_context(ast=tree, symbol_table=symbol_table)
    print_ast(context)
