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


def is_array(node):
    return node[0] == MOANodeTypes.ARRAY


def is_unary_operation(node):
    return 100 < node[0].value < 200


def is_binary_operation(node):
    return 200 < node[0].value < 300
