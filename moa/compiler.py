from moa.frontend import MOAParser
from moa.shape import calculate_shapes
from moa.dnf import reduce_to_dnf
from moa.onf import reduce_to_onf
from moa.backend import generate_python_source


def compiler(source, frontend='moa', backend='python'):
    if frontend == 'moa':
        symbol_table, tree = MOAParser().parse(source)
    else:
        raise ValueError(f'unknown frontend: {frontend}')

    shape_symbol_table, shape_tree = calculate_shapes(symbol_table, tree)
    dnf_symbol_table, dnf_tree = reduce_to_dnf(shape_symbol_table, shape_tree)
    onf_symbol_table, onf_tree = reduce_to_onf(dnf_symbol_table, dnf_tree)

    if backend == 'python':
        return generate_python_source(onf_symbol_table, onf_tree)
    else:
        raise ValueError(f'unknown backend {backend}')
