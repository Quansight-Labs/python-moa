from functools import reduce

from .ast import (
    postorder_replacement,
    MOANodeTypes,
    is_binary_operation, is_unary_operation
)


def metric_flops(symbol_table, tree):
    def _count_flops(symbol_table, node):
        if node.shape is None:
            raise ValueError('metric "flops" assumes that shape analysis is completed')

        if node.node_type == MOANodeTypes.ARRAY:
            return symbol_table, 0
        elif node.node_type in {MOANodeTypes.PLUS, MOANodeTypes.MINUS, MOANodeTypes.TIMES, MOANodeTypes.DIVIDE}:
            node_flops = reduce(lambda x,y: x*y, node.shape)
            return symbol_table, node_flops + node.left_node + node.right_node
        elif isinstance(node.node_type, tuple) and node.node_type[0] == MOANodeTypes.DOT:
            node_flops = reduce(lambda x,y: x*y, node.shape)
            return symbol_table, node_flops + node.left_node + node.right_node
        elif is_unary_operation(node):
            return symbol_table, node.right_node
        elif is_binary_operation(node):
            return symbol_table, node.left_node + node.right_node
        else:
            raise TypeError('flops not counted for type {node.node_type}')

    _, flops = postorder_replacement(symbol_table, tree, _count_flops)
    return flops
