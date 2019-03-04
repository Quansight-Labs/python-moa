import itertools

from .core import MOAException
from .ast import (
    MOANodeTypes,
    ArrayNode, BinaryNode, SymbolNode,
    add_symbol,
    generate_unique_index_name, generate_unique_array_name,
    preorder_replacement
)
from .shape import is_vector, is_scalar


class MOAReductionError(MOAException):
    pass


def add_indexing_node(symbol_table, node):
    """Adds indexing into the MOA AST

    For example: <i0 i1> psi (A + B)
    """
    index_symbols = ()
    for bound in node.shape:
        index_name = generate_unique_index_name(symbol_table)
        symbol_table = add_symbol(symbol_table, index_name, MOANodeTypes.INDEX, (), (0, bound))
        index_symbols = index_symbols + (index_name,)

    array_name = generate_unique_array_name(symbol_table)
    symbol_table = add_symbol(symbol_table, array_name, MOANodeTypes.ARRAY, (len(index_symbols),), index_symbols)
    vector_node = ArrayNode(MOANodeTypes.ARRAY, (len(index_symbols),), array_name)
    return symbol_table, BinaryNode(MOANodeTypes.PSI, node.shape, vector_node, node)


def reduce_ast(symbol_table, tree, max_iterations=100):
    """Preorder traversal and replacement of ast tree

    In the future the symbol table will have to be constructed earlier
    for arrays and variables for shapes.

    TODO: change exception to warning to allow for partial replacement
    """
    symbol_table, tree = add_indexing_node(symbol_table, tree)
    symbol_table, tree = preorder_replacement(symbol_table, tree, _reduce_replacement, range(max_iterations))
    return symbol_table, tree


def _reduce_replacement(symbol_table, node):
    reduce_psi_map = {
        MOANodeTypes.PSI: _reduce_psi_psi,
        MOANodeTypes.TRANSPOSE: _reduce_psi_transpose,
        MOANodeTypes.TRANSPOSEV: _reduce_psi_transposev,
        MOANodeTypes.PLUSRED: _reduce_psi_plus_red,
        MOANodeTypes.PLUS: _reduce_psi_plus_minus_times_divide,
        MOANodeTypes.MINUS: _reduce_psi_plus_minus_times_divide,
        MOANodeTypes.TIMES: _reduce_psi_plus_minus_times_divide,
        MOANodeTypes.DIVIDE: _reduce_psi_plus_minus_times_divide,
    }

    # Is reduction as simple as exclusively looking at psi nodes?
    if node.node_type == MOANodeTypes.PSI and node.right_node.node_type in reduce_psi_map:
        if not is_vector(symbol_table, node.left_node) or symbol_table[node.left_node.symbol_node].value is None:
            raise MOAReductionError('PSI replacement assumes that left_node is vector with defined values')
        return reduce_psi_map[node.right_node.node_type](symbol_table, node)
    return None, None


def _reduce_psi_psi(symbol_table, node):
    """<i j> psi <k l> psi ... => <k l i j> psi ..."""
    if not is_vector(symbol_table, node.right_node.left_node) or symbol_table[node.right_node.left_node.symbol_node].value is None:
        raise MOAReductionError('<...> PSI <...> PSI ... replacement assumes that the inner left_node is vector with defined values')

    array_name = generate_unique_array_name(symbol_table)
    array_values = symbol_table[node.right_node.left_node.symbol_node].value + symbol_table[node.left_node.symbol_node].value
    symbol_table = add_symbol(symbol_table, array_name, MOANodeTypes.ARRAY, (len(array_values),), array_values)

    return symbol_table, BinaryNode(MOANodeTypes.PSI, node.shape,
                                    ArrayNode(MOANodeTypes.ARRAY, (len(array_values),), array_name),
                                    node.right_node.right_node)


def _reduce_psi_transpose(symbol_table, node):
    """<i j k> psi transpose ... => <k j i> psi ..."""
    array_name = generate_unique_array_name(symbol_table)
    array_values = symbol_table[node.left_node.symbol_node].value[::-1]
    symbol_table = add_symbol(symbol_table, array_name, MOANodeTypes.ARRAY, (len(array_values),), array_values)

    return symbol_table, BinaryNode(MOANodeTypes.PSI, node.shape,
                                    ArrayNode(MOANodeTypes.ARRAY, (len(array_values),), array_name),
                                    node.right_node.right_node)


def _reduce_psi_transposev(symbol_table, node):
    """<i j k> psi <2 0 1> transpose ... => <k i j> psi ..."""
    array_values = tuple(s for _, s in sorted(zip(node.right_node.left_node.value, node.left_node.value), key=lambda pair: pair[0]))
    return BinaryNode(MOANodeTypes.PSI, node.shape,
                      ArrayNode(MOANodeTypes.ARRAY, (len(index_values),), None, index_values),
                      node.right_node.right_node)


def _reduce_psi_plus_red(node):
    raise NotImplemenetedError('PSI +RED')


def _reduce_psi_plus_minus_times_divide(symbol_table, node):
    """<i j> psi (... (+-*/) ...) => (<i j> psi ...) (+-*/) (<k l> psi ...)

    Scalar Extension
      <i j> psi (scalar (+-*/) ...) = scalar (+-*/) <i j> psi ...
    """
    if is_scalar(symbol_table, node.right_node.left_node):
        left_node = node.right_node.left_node
    else:
        left_node = BinaryNode(MOANodeTypes.PSI, node.shape,
                               node.left_node,
                               node.right_node.left_node)

    if is_scalar(symbol_table, node.right_node.right_node):
        right_node = node.right_node.right_node
    else:
        right_node = BinaryNode(MOANodeTypes.PSI, node.shape,
                                node.left_node,
                                node.right_node.right_node)

    return symbol_table, BinaryNode(node.right_node.node_type, node.shape, left_node, right_node)
