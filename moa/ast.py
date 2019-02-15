import enum


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


# node methods
def is_array(node):
    return node[0] == MOANodeTypes.ARRAY


def is_unary_operation(node):
    return 100 < node[0].value < 200


def is_binary_operation(node):
    return 200 < node[0].value < 300


## replacement methods
# recursive for simplicity
def postorder_replacement(node, replacement_function):
    if is_unary_operation(node):
        right_node = postorder_replacement(node[2], replacement_function)
        node = node[:2] + (right_node,)
    elif is_binary_operation(node):
        left_node = postorder_replacement(node[2], replacement_function)
        right_node = postorder_replacement(node[3], replacement_function)
        node = node[:2] + (left_node, right_node)
    return replacement_function(node)

def preorder_replacement(node):
    pass
