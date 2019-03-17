from moa.ast import MOANodeTypes, Node, SymbolNode
from moa.analysis import metric_flops
from moa.shape import calculate_shapes
from moa.dnf import reduce_to_dnf


def test_metric_flops():
    tree = Node(MOANodeTypes.PSI, None,
                Node(MOANodeTypes.ARRAY, None, '_a1'),
                Node(MOANodeTypes.TRANSPOSE, None,
                     Node(MOANodeTypes.PLUS, None,
                          Node(MOANodeTypes.ARRAY, None, 'A'),
                          Node(MOANodeTypes.ARRAY, None, 'B'))))

    symbol_table = {
        '_a1': SymbolNode(MOANodeTypes.ARRAY, (1,), (0,)),
        'A': SymbolNode(MOANodeTypes.ARRAY, (10, 100), None),
        'B': SymbolNode(MOANodeTypes.ARRAY, (10, 100), None)
    }

    symbol_table, tree = calculate_shapes(symbol_table, tree)
    assert metric_flops(symbol_table, tree) == 1000

    symbol_table, tree = reduce_to_dnf(symbol_table, tree)
    assert metric_flops(symbol_table, tree) == 10
