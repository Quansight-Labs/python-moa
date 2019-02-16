import itertools

from .core import MOAException
from .ast import (
    MOANodeTypes,
    ArrayNode, BinaryNode,
    preorder_replacement
)
from .shape import is_vector


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


def reduce_ast(tree):
    """Preorder traversal and replacement of ast tree

    In the future the symbol table will have to be constructed earlier
    for arrays and variables for shapes.
    """
    counter = itertools.count()
    symbol_table = {}

    tree = add_indexing_node(tree, symbol_table, counter)
    tree = preorder_replacement(tree, _reduce_replacement)
    return symbol_table, tree


def _reduce_replacement(node):
    reduce_psi_map = {
        MOANodeTypes.PSI: _reduce_psi_psi,
        MOANodeTypes.TRANSPOSE: _reduce_psi_transpose,
        MOANodeTypes.PLUS: _reduce_psi_plus
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


def _reduce_psi_plus(node):
    """<i j> psi (... plus ...) => (<i j> psi ...) plus (<k l> psi ...)"""
    index_node = node.left_node
    return BinaryNode(MOANodeTypes.PLUS, node.shape,
                      BinaryNode(MOANodeTypes.PSI, node.shape,
                                 index_node,
                                 node.right_node.left_node),
                      BinaryNode(MOANodeTypes.PSI, node.shape,
                                 index_node,
                                 node.right_node.right_node))
