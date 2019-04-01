from functools import reduce

from . import ast


def metric_flops(context):
    def _count_flops(context):
        if context.ast.shape is None:
            raise ValueError('metric "flops" assumes that shape analysis is completed')

        flops = 0

        if context.ast.symbol[-1] in {ast.NodeSymbol.PLUS, ast.NodeSymbol.MINUS, ast.NodeSymbol.TIMES, ast.NodeSymbol.DIVIDE}:
            flops = reduce(lambda x,y: x*y, context.ast.shape)

        return ast.create_context(
            ast=flops + sum([_ for _ in context.ast.child]),
            symbol_table=context.symbol_table)

    context = ast.node_traversal(context, _count_flops, traversal='postorder')
    return context.ast
