from moa import ast, analysis, shape, dnf, visualize


def test_metric_flops():
    tree = ast.Node((ast.NodeSymbol.PSI,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a1',), ()),
        ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (), (
            ast.Node((ast.NodeSymbol.PLUS,), None, (), (
                ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),
                ast.Node((ast.NodeSymbol.ARRAY,), None, ('B',), ()))),))))

    symbol_table = {
        '_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1,), None, (0,)),
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (10, 100), None, None),
        'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (10, 100), None, None)
    }

    context = ast.create_context(ast=tree, symbol_table=symbol_table)
    context = shape.calculate_shapes(context)

    assert analysis.metric_flops(context) == 1000

    context = dnf.reduce_to_dnf(context)

    assert analysis.metric_flops(context) == 10
