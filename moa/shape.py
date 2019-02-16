from .ast import MOANodeTypes, postorder_replacement, BinaryNode, UnaryNode
from .core import MOAException


class MOAShapeException(MOAException):
    pass


def is_vector(node):
    return node.node_type == MOANodeTypes.ARRAY and len(node.shape) == 1


def is_scalar(node):
    return node.node_type == MOANodeTypes.ARRAY and len(node.shape) == 0


def dimension(node):
    return len(node.shape)


def calculate_shapes(tree):
    """Postorder traversal to calculate node shapes

    """
    return postorder_replacement(tree, _shape_replacement)


def _shape_replacement(node):
    shape_map = {
        MOANodeTypes.ARRAY: lambda node: node,
        MOANodeTypes.TRANSPOSE: _shape_transpose,
        MOANodeTypes.PSI: _shape_psi,
        MOANodeTypes.PLUS: _shape_plus,
    }
    return shape_map[node.node_type](node)


# Unary Operations
def _shape_transpose(node):
    return UnaryNode(node.node_type, node.right_node.shape[::-1], node.right_node)


# Binary Operations
def _shape_psi(node):
    if not is_vector(node.left_node):
        raise MOAShapeException('PSI requires left node to be vector')

    drop_dims = len(node.left_node.value)

    if drop_dims > dimension(node.right_node):
        raise MOAShapeException('PSI requires that vector length be no greater than dimension of right node')

    return BinaryNode(node.node_type, node.right_node.shape[drop_dims:], node.left_node, node.right_node)


def _shape_plus(node):
    if (node.left_node.shape != node.right_node.shape) and not is_scalar(node.left_node) and not is_scalar(node.right_node):
        raise MOAShapeException('(+,-,/,*) requires shapes to match or single argument to be scalar')

    return BinaryNode(node.node_type, node.left_node.shape or node.right_node.shape, node.left_node, node.right_node)
