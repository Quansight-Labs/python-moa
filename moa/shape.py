from .ast import (
    MOANodeTypes, postorder_replacement,
    ArrayNode, BinaryNode, UnaryNode,
    is_array, is_unary_operation, is_binary_operation
)
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
        MOANodeTypes.ARRAY: lambda node: node.shape,
        MOANodeTypes.TRANSPOSE: _shape_transpose,
        MOANodeTypes.TRANSPOSEV: _shape_transpose_vector,
        MOANodeTypes.PLUSRED: _shape_plus_red,
        MOANodeTypes.PSI: _shape_psi,
        MOANodeTypes.PLUS: _shape_plus_minus_divide_times,
        MOANodeTypes.MINUS: _shape_plus_minus_divide_times,
        MOANodeTypes.TIMES: _shape_plus_minus_divide_times,
        MOANodeTypes.DIVIDE: _shape_plus_minus_divide_times,
    }
    shape = shape_map[node.node_type](node)
    if is_unary_operation(node):
        return UnaryNode(node.node_type, shape, node.right_node)
    elif is_binary_operation(node):
        return BinaryNode(node.node_type, shape, node.left_node, node.right_node)
    else: # Array
        return ArrayNode(node.node_type, shape, node.name, node.value)


# Unary Operations
def _shape_transpose(node):
    return node.right_node.shape[::-1]


def _shape_transpose_vector(node):
    if not is_vector(node.left_node):
        raise MOAShapeException('TRANSPOSE VECTOR requires left node to be vector')

    if dimension(node.right_node) != len(node.left_node.value):
        raise MOAShapeException('TRANSPOSE VECTOR requires left node vector to have total number of elements equal to dimension of right node')

    if len(set(node.left_node.value)) != len(node.left_node.value):
        raise MOAShapeException('TRANSPOSE VECTOR requires left node vector to have unique elements')

    # sort two lists according to one list
    return tuple(s for _, s in sorted(zip(node.left_node.value, node.right_node.shape), key=lambda pair: pair[0]))


def _shape_plus_red(node):
    return node.right_node.shape[1:]


# Binary Operations
def _shape_psi(node):
    if not is_vector(node.left_node):
        raise MOAShapeException('PSI requires left node to be vector')

    drop_dims = len(node.left_node.value)

    if drop_dims > dimension(node.right_node):
        raise MOAShapeException('PSI requires that vector length be no greater than dimension of right node')

    return node.right_node.shape[drop_dims:]


def _shape_plus_minus_divide_times(node):
    if (node.left_node.shape != node.right_node.shape) and not is_scalar(node.left_node) and not is_scalar(node.right_node):
        raise MOAShapeException('(+,-,/,*) requires shapes to match or single argument to be scalar')

    return node.left_node.shape or node.right_node.shape
