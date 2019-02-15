import enum
import collections


class MOANodeTypes(enum.Enum):
    ARRAY = 1

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
# recursive for simplicity
def postorder_replacement(node, replacement_function):
    if is_unary_operation(node):
        right_node = postorder_replacement(node.right_node, replacement_function)
        node = UnaryNode(node.node_type, node.shape, right_node)
    elif is_binary_operation(node):
        left_node = postorder_replacement(node.left_node, replacement_function)
        right_node = postorder_replacement(node.right_node, replacement_function)
        node = BinaryNode(node.node_type, node.shape, left_node, right_node)
    return replacement_function(node)


def preorder_replacement(node, replacement_function):
    node = replacement_function(node)
    if is_unary_operation(node):
        right_node = preorder_replacement(node.right_node, replacement_function)
        node = UnaryNode(node.node_type, node.shape, right_node)
    elif is_binary_operation(node):
        left_node = preorder_replacement(node.left_node, replacement_function)
        right_node = preorder_replacement(node.right_node, replacement_function)
        node = BinaryNode(node.node_type, node.shape, left_node, right_node)
    return node
