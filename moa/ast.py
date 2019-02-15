import enum
import collections

from .core import MOAException


class MOAReplacementError(MOAException):
    pass


class MOANodeTypes(enum.Enum):
    ARRAY = 1
    INDEX = 2

    # unary
    PLUSRED   = 101
    MINUSRED  = 102
    TIMESRED  = 103
    DIVIDERED = 104
    IOTA      = 105
    DIM       = 106
    TAU       = 107
    SHAPE     = 108
    RAV       = 109
    TRANSPOSE = 110

    # binary
    PLUS    = 201
    MINUS   = 202
    TIMES   = 203
    DIVIDE  = 204
    PSI     = 205
    TAKE    = 206
    DROP    = 207
    CAT     = 208


# I was hesitant to add this but it makes
# readibility **SO** much better
# and it is rougly equivalent to C struct
ArrayNode = collections.namedtuple(
    'ArrayNode', ['node_type', 'shape', 'name', 'value'])
UnaryNode = collections.namedtuple(
    'UnaryNode', ['node_type', 'shape', 'right_node'])
BinaryNode = collections.namedtuple(
    'BinaryNode', ['node_type', 'shape', 'left_node', 'right_node'])


# node methods
def is_array(node):
    return node.node_type == MOANodeTypes.ARRAY


def is_unary_operation(node):
    return 100 < node.node_type.value < 200


def is_binary_operation(node):
    return 200 < node.node_type.value < 300


## replacement methods
def postorder_replacement(node, replacement_function):
    """Postorder (Left, Right, Root) traversal of AST

    Used for calculating the shape of the ast at each node.
    """
    if is_unary_operation(node):
        right_node = postorder_replacement(node.right_node, replacement_function)
        node = UnaryNode(node.node_type, node.shape, right_node)
    elif is_binary_operation(node):
        left_node = postorder_replacement(node.left_node, replacement_function)
        right_node = postorder_replacement(node.right_node, replacement_function)
        node = BinaryNode(node.node_type, node.shape, left_node, right_node)
    return replacement_function(node)


def preorder_replacement(node, replacement_function, max_iterations=100):
    """Preorder (Root, Left, Right) traversal of AST

    Used for reducing the ast. Note that "replacement_function" is
    called until it returns "None" indicating that there are no more
    reductions to perform on the root node. This behavior is different
    than the "postorder_replacement" function.
    """
    for i in range(max_iterations):
        replacement_node = replacement_function(node)
        if replacement_node is None:
            break
        node = replacement_node
    else:
        raise MOAReplacementError(f'reduction on node {node.node_type} failed to complete in {max_iterations} iterations')

    if is_unary_operation(node):
        right_node = preorder_replacement(node.right_node, replacement_function)
        node = UnaryNode(node.node_type, node.shape, right_node)
    elif is_binary_operation(node):
        left_node = preorder_replacement(node.left_node, replacement_function)
        right_node = preorder_replacement(node.right_node, replacement_function)
        node = BinaryNode(node.node_type, node.shape, left_node, right_node)
    return node
