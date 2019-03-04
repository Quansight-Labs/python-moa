from .ast import (
    MOANodeTypes, postorder_replacement,
    ArrayNode, BinaryNode, UnaryNode,
    is_array, is_unary_operation, is_binary_operation,
    generate_unique_array_name, add_symbol
)
from .core import MOAException


class MOAShapeException(MOAException):
    pass


# dimension
def dimension(symbol_table, node):
    if is_array(node):
        return len(symbol_table[node.symbol_node].shape)
    elif node.shape:
        return len(node.shape)
    raise MOAShapeException(f'cannot determine dimension from node {node.node_type} with shape {node.shape}')


def is_scalar(symbol_table, node):
    return node.node_type == MOANodeTypes.ARRAY and dimension(symbol_table, node) == 0


def is_vector(symbol_table, node):
    return node.node_type == MOANodeTypes.ARRAY and dimension(symbol_table, node) == 1


# symbolic
def has_symbolic_elements(elements):
    return any(is_symbolic_element(element) for element in elements)


def is_symbolic_element(element):
    return isinstance(element, tuple)


# shape calculation
def calculate_shapes(symbol_table, tree):
    """Postorder traversal to calculate node shapes

    """
    return postorder_replacement(symbol_table, tree, _shape_replacement)


def _shape_replacement(symbol_table, node):
    shape_map = {
        MOANodeTypes.ARRAY: _shape_array,
        MOANodeTypes.TRANSPOSE: _shape_transpose,
        MOANodeTypes.TRANSPOSEV: _shape_transpose_vector,
        MOANodeTypes.PLUSRED: _shape_plus_red,
        MOANodeTypes.PSI: _shape_psi,
        MOANodeTypes.PLUS: _shape_plus_minus_divide_times,
        MOANodeTypes.MINUS: _shape_plus_minus_divide_times,
        MOANodeTypes.TIMES: _shape_plus_minus_divide_times,
        MOANodeTypes.DIVIDE: _shape_plus_minus_divide_times,
    }
    return shape_map[node.node_type](symbol_table, node)


# Array Operations
def _shape_array(symbol_table, node):
    return symbol_table, ArrayNode(node.node_type, symbol_table[node.symbol_node].shape, node.symbol_node)


# Unary Operations
def _shape_transpose(symbol_table, node):
    return symbol_table, UnaryNode(node.node_type, node.right_node.shape[::-1], node.right_node)


def _shape_transpose_vector(symbol_table, node):
    if not is_vector(symbol_table, node.left_node):
        raise MOAShapeException('TRANSPOSE VECTOR requires left node to be vector')

    left_symbol_node = symbol_table[node.left_node.symbol_node]
    if has_symbolic_elements(node.left_node.shape) or has_symbolic_elements(left_symbol_node.value):
        raise MOAShapeException('TRANSPOSE VECTOR not implemented for left node to be vector with symbolic components')

    if node.left_node.shape[0] != dimension(symbol_table, node.right_node):
        raise MOAShapeException('TRANSPOSE VECTOR requires left node vector to have total number of elements equal to dimension of right node')

    if len(set(left_symbol_node.value)) != len(left_symbol_node.value):
        raise MOAShapeException('TRANSPOSE VECTOR requires left node vector to have unique elements')

    # sort two lists according to one list
    shape = tuple(s for _, s in sorted(zip(left_symbol_node.value, node.right_node.shape), key=lambda pair: pair[0]))
    return symbol_table, BinaryNode(node.node_type, shape, node.left_node, node.right_node)


def _shape_plus_red(symbol_table, node):
    # TODO: should reduction be done in the shape analysis?
    if dimension(symbol_table, node.right_node) == 0:
        return symbol_table, node.right_node

    return symbol_table, UnaryNode(node.node_type, node.right_node.shape[1:], node.right_node)


# Binary Operations
def _shape_psi(symbol_table, node):
    if not is_vector(symbol_table, node.left_node):
        raise MOAShapeException('PSI requires left node to be vector')

    left_symbol_node = symbol_table[node.left_node.symbol_node]
    if has_symbolic_elements(left_symbol_node.shape):
        raise MOAShapeException('PSI not implemented for left node to be vector with symbolic shape')

    drop_dimensions = left_symbol_node.shape[0]
    if drop_dimensions > dimension(symbol_table, node.right_node):
        raise MOAShapeException('PSI requires that vector length be no greater than dimension of right node')

    conditions = []
    for i, (left_element, right_element) in enumerate(zip(left_symbol_node.value, node.right_node.shape)):
        if is_symbolic_element(left_element) and is_symbolic_element(right_element): # both are symbolic
            conditions.append(BinaryNode(MOANodeTypes.LESSTHAN, (), left_element, right_element))
        elif is_symbolic_element(left_element): # only left is symbolic
            array_name = generate_unique_array_name(symbol_table)
            symbol_table = add_symbol(symbol_table, array_name, MOANodeTypes.ARRAY, (), (left_element,))
            conditions.append(BinaryNode(MOANodeTypes.LESSTHAN, (), left_element, (MOANodeTypes.ARRAY, (), array_name)))
        elif is_symbolic_element(right_element): # only right is symbolic
            array_name = generate_unique_array_name(symbol_table)
            symbol_table = add_symbol(symbol_table, array_name, MOANodeTypes.ARRAY, (), (left_element,))
            conditions.append(BinaryNode(MOANodeTypes.LESSTHAN, (), (MOANodeTypes.ARRAY, (), array_name), right_element))
        else: # neither symbolic
            if left_element >= right_element:
                raise MOAShapeException(f'PSI requires elements #{i} left {left_element} < right {right_element}')

    node = BinaryNode(node.node_type, node.right_node.shape[drop_dimensions:], node.left_node, node.right_node)
    if conditions:
        condition_node = conditions[0]
        for condition in conditions[1:]:
            condition_node = BinaryNode(MOANodeTypes.AND, (), condition, condition_node)
        node = BinaryNode(MOANodeTypes.CONDITION, node.shape, condition_node, node)
    return symbol_table, node


def _shape_plus_minus_divide_times(symbol_table, node):
    conditions = []
    if is_scalar(symbol_table, node.left_node): # scalar extension
        shape = node.right_node.shape
    elif is_scalar(symbol_table, node.right_node): # scalar extension
        shape = node.left_node.shape
    else: # shapes must match
        if dimension(symbol_table, node.left_node) != dimension(symbol_table, node.right_node):
            raise MOAShapeException('(+,-,/,*) requires dimension to match or single argument to be scalar')

        shape = ()
        for i, (left_element, right_element) in enumerate(zip(node.left_node.shape, node.right_node.shape)):
            if is_symbolic_element(left_element) and is_symbolic_element(right_element): # both are symbolic
                conditions.append(BinaryNode(MOANodeTypes.EQUAL, (), left_element, right_element))
                shape = shape + (left_element,)
            elif is_symbolic_element(left_element): # only left is symbolic
                array_name = generate_unique_array_name(symbol_table)
                symbol_table = add_symbol(symbol_table, array_name, MOANodeTypes.ARRAY, (), (left_element,))
                conditions.append(BinaryNode(MOANodeTypes.EQUAL, (), left_element, (MOANodeTypes.ARRAY, (), array_name)))
                shape = shape + (right_element,)
            elif is_symbolic_element(right_element): # only right is symbolic
                array_name = generate_unique_array_name(symbol_table)
                symbol_table = add_symbol(symbol_table, array_name, MOANodeTypes.ARRAY, (), (left_element,))
                conditions.append(BinaryNode(MOANodeTypes.EQUAL, (), (MOANodeTypes.ARRAY, (), array_name), right_element))
                shape = shape + (left_element,)
            else: # neither symbolic
                if left_element != right_element:
                    raise MOAShapeException(f'(+,-,/,*) requires shapes to match elements #{i} left {left_element} != right {right_element}')
                shape = shape + (left_element,)

    node = BinaryNode(node.node_type, shape, node.left_node, node.right_node)
    if conditions:
        condition_node = conditions[0]
        for condition in conditions[1:]:
            condition_node = BinaryNode(MOANodeTypes.AND, (), condition, condition_node)
        node = BinaryNode(MOANodeTypes.CONDITION, node.shape, condition_node, node)
    return symbol_table, node
