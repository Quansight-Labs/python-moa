import itertools

from .core import MOAException
from .visualize import print_ast
from .ast import (
    MOANodeTypes,
    ArrayNode, BinaryNode,
    preorder_replacement
)
from .shape import is_vector


class MOAReductionError(MOAException):
    pass


def reduce_ast(tree):
    """Preorder traversal and replacement of ast tree

    In the future the symbol table will have to be constructed earlier
    for arrays and variables for shapes.
    """
    counter = itertools.count()
    symbol_table = {}
    index_symbols = ()
    for i, bound in zip(counter, tree.shape):
        symbol_name = f'i{i}'
        symbol_table[symbol_name] = (0, bound)
        index_symbols = index_symbols + (symbol_name,)

    root_node = BinaryNode(MOANodeTypes.PSI, tree.shape,
                           ArrayNode(MOANodeTypes.ARRAY, (1,), None, index_symbols),
                           tree)
    tree = preorder_replacement(root_node, _reduce_replacement)
    return symbol_table, tree


def _reduce_replacement(node):
    reduce_psi_map = {
        MOANodeTypes.PSI: _reduce_psi_psi,
        MOANodeTypes.TRANSPOSE: _reduce_psi_transpose,
        MOANodeTypes.PLUS: _reduce_psi_plus
    }

    # Is reduction as simple as exclusively looking at psi nodes?
    if node == MOANodeTypes.PSI and reduce_psi_map.get(node.right_node):
        if not is_vector(node.left_node) or node.left_node.value is None:
            raise MOAReductionError('PSI replacement assumes that left_node is vector with defined values')
        return reduce_psi_map[node.right_node](node)
    return None


def _reduce_psi_psi(node):
    return None


def _reduce_psi_transpose(node):
    return None


def _reduce_psi_plus(node):
    return None
