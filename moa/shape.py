from .ast import MOANodeTypes, postorder_replacement
from .core import MOAException


class MOAShapeException(MOAException):
    pass


def calculate_shapes(tree):
    """Postorder Traversal of ast tree to calculate shapes

    """
    return postorder_replacement(tree, _shape_replacement)


def _shape_replacement(node):
    shape_map = {
        MOANodeTypes.ARRAY: lambda node: node,
        MOANodeTypes.TRANSPOSE: _shape_transpose,
        MOANodeTypes.PSI: _shape_psi,
        MOANodeTypes.PLUS: _shape_plus,
    }
    return shape_map[node[0]](node)


# Unary Operations
def _shape_transpose(node):
    return (node[0], node[2][1][::-1], node[2])


# Binary Operations
def _shape_psi(node):
    if len(node[2][1]) != 1:
        raise MOAShapeException('PSI requires left node to be vector')

    drop_dims = len(node[2][3])

    if drop_dims > len(node[3][1]):
        raise MOAShapeException('PSI requires that vector length be no greater than dimension of right node')

    return (node[0], node[3][1][drop_dims:], node[2], node[3])


def _shape_plus(node):
    if node[2][1] != node[3][1]:
        raise MOAShapeException('(+,-,/,*) for now requires shapes to match')

    return (node[0], node[2][1], node[2], node[3])
