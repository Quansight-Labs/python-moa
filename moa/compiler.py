from moa.frontend import MOAParser
from moa.shape import calculate_shapes
from moa.reduction import reduce_ast
from moa.backend import generate_python_source


def compiler(source, frontend='moa', backend='python'):
    if frontend == 'moa':
        symbol_table, tree = MOAParser().parse(source)
    else:
        raise ValueError(f'unknown frontend: {frontend}')

    shape_symbol_table, shape_tree = calculate_shapes(symbol_table, tree)
    symbol_table, reduced_ast = reduce_ast(symbol_table, shape_tree)

    if backend == 'python':
        return generate_python_source(symbol_table, reduced_ast)
    else:
        raise ValueError(f'unknown backend {backend}')
