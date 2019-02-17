import itertools

from .core import MOAException
from .ast import (
    MOANodeTypes,
    ArrayNode, BinaryNode,
    preorder_replacement
)
from .shape import is_vector, is_scalar


class MOAReductionError(MOAException):
    pass


def add_indexing_node(node, symbol_table, counter):
    """Adds indexing into the MOA AST

    For example: <i0 i1> psi (A + B)
    """
    index_symbols = ()
    for i, bound in zip(counter, node.shape):
        symbol_name = f'i{i}'
        symbol_table[symbol_name] = (0, bound)
        index_symbols = index_symbols + (symbol_name,)

    return BinaryNode(MOANodeTypes.PSI, node.shape,
                      ArrayNode(MOANodeTypes.ARRAY, (len(index_symbols),), None, index_symbols),
                      node)


def reduce_ast(tree, max_iterations=100):
    """Preorder traversal and replacement of ast tree

    In the future the symbol table will have to be constructed earlier
    for arrays and variables for shapes.
    """
    counter = itertools.count()
    symbol_table = {}

    tree = add_indexing_node(tree, symbol_table, counter)
    tree = preorder_replacement(tree, _reduce_replacement, range(max_iterations))
    return symbol_table, tree


def _reduce_replacement(node):
    reduce_psi_map = {
        MOANodeTypes.PSI: _reduce_psi_psi,
        MOANodeTypes.TRANSPOSE: _reduce_psi_transpose,
        MOANodeTypes.PLUS: _reduce_psi_plus_minus_times_divide,
        MOANodeTypes.MINUS: _reduce_psi_plus_minus_times_divide,
        MOANodeTypes.TIMES: _reduce_psi_plus_minus_times_divide,
        MOANodeTypes.DIVIDE: _reduce_psi_plus_minus_times_divide,
    }

    # Is reduction as simple as exclusively looking at psi nodes?
    if node.node_type == MOANodeTypes.PSI and node.right_node.node_type in reduce_psi_map:
        if not is_vector(node.left_node) or node.left_node.value is None:
            raise MOAReductionError('PSI replacement assumes that left_node is vector with defined values')
        return reduce_psi_map[node.right_node.node_type](node)
    return None


def _reduce_psi_psi(node):
    """<i j> psi <k l> psi ... => <k l i j> psi ..."""
    if not is_vector(node.right_node.left_node) or node.right_node.left_node.value is None:
        raise MOAReductionError('<...> PSI <...> PSI ... replacement assumes that the inner left_node is vector with defined values')

    index_values = node.right_node.left_node.value + node.left_node.value
    return BinaryNode(MOANodeTypes.PSI, node.shape,
                      ArrayNode(MOANodeTypes.ARRAY, (len(index_values),), None, index_values),
                      node.right_node.right_node)


def _reduce_psi_transpose(node):
    """<i j k> psi transpose ... => <k j i> psi ..."""
    index_values = node.left_node.value[::-1]
    return BinaryNode(MOANodeTypes.PSI, node.shape,
                      ArrayNode(MOANodeTypes.ARRAY, (len(index_values),), None, index_values),
                      node.right_node.right_node)


def _reduce_psi_plus_minus_times_divide(node):
    """<i j> psi (... (+-*/) ...) => (<i j> psi ...) (+-*/) (<k l> psi ...)

    Scalar Extension
      <i j> psi (scalar (+-*/) ...) = scalar (+-*/) <i j> psi ...
    """
    if is_scalar(node.right_node.left_node):
        left_node = node.right_node.left_node
    else:
        left_node = BinaryNode(MOANodeTypes.PSI, node.shape,
                               node.left_node,
                               node.right_node.left_node)

    if is_scalar(node.right_node.right_node):
        right_node = node.right_node.right_node
    else:
        right_node = BinaryNode(MOANodeTypes.PSI, node.shape,
                                node.left_node,
                                node.right_node.right_node)

    return BinaryNode(node.right_node.node_type, node.shape, left_node, right_node)
