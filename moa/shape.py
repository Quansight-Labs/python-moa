from . import ast
from .exception import MOAException


class MOAShapeError(MOAException):
    pass


# dimension
def dimension(context):
    if ast.is_array(context):
        return len(ast.get_array_node_symbol(context).shape)
    elif node.shape:
        return len(node.shape)
    raise MOAShapeError(f'cannot determine dimension from node {node.node_type} with shape {node.shape}')


def is_scalar(context):
    return ast.is_array(context) and dimension(context) == 0


def is_vector(context):
    return ast.is_array(context) and dimension(context) == 1


# shape calculation
def calculate_shapes(context):
    """Postorder traversal to calculate node shapes

    """
    return node_traversal(context, _shape_replacement, traversal='postorder')


def _shape_replacement(symbol_table, node):
    shape_map = {
        (NodeSymbol.ARRAY,): _shape_array,
        (NodeSymbol.TRANSPOSE,): _shape_transpose,
        (NodeSymbol.TRANSPOSEV,): _shape_transpose_vector,
        (NodeSymbol.ASSIGN,): _shape_assign,
        (NodeSymbol.SHAPE,): _shape_shape,
        (NodeSymbol.PSI,): _shape_psi,
        (NodeSymbol.PLUS,): _shape_plus_minus_divide_times,
        (NodeSymbol.MINUS,): _shape_plus_minus_divide_times,
        (NodeSymbol.TIMES,): _shape_plus_minus_divide_times,
        (NodeSymbol.DIVIDE,): _shape_plus_minus_divide_times,
        (NodeSymbol.DOT, NodeSymbol.PLUS): _shape_outer_plus_minus_divide_times,
        (NodeSymbol.DOT, NodeSymbol.MINUS): _shape_outer_plus_minus_divide_times,
        (NodeSymbol.DOT, NodeSymbol.TIMES): _shape_outer_plus_minus_divide_times,
        (NodeSymbol.DOT, NodeSymbol.DIVIDE): _shape_outer_plus_minus_divide_times,
        (NodeSymbol.REDUCE, NodeSymbol.PLUS): _shape_reduce_plus_minus_divide_times,
        (NodeSymbol.REDUCE, NodeSymbol.MINUS): _shape_reduce_plus_minus_divide_times,
        (NodeSymbol.REDUCE, NodeSymbol.TIMES): _shape_reduce_plus_minus_divide_times,
        (NodeSymbol.REDUCE, NodeSymbol.DIVIDE): _shape_reduce_plus_minus_divide_times,
    }

    # condition_node = None
    # # condition propagation
    # if is_binary_operation(node):
    #     if node.left_node.node_type == MOANodeTypes.CONDITION and node.right_node.node_type == MOANodeTypes.CONDITION:
    #         condition_node = Node(MOANodeTypes.AND, None, node.left_node.condition_node, node.right_node.condition_node)
    #         node = Node(node.node_type, None, node.left_node.right_node, node.right_node.right_node)
    #     if node.left_node.node_type == MOANodeTypes.CONDITION:
    #         condition_node = node.left_node.condition_node
    #         node = Node(node.node_type, None, node.left_node.right_node, node.right_node)
    #     elif node.right_node.node_type == MOANodeTypes.CONDITION:
    #         condition_node = node.right_node.condition_node
    #         node = Node(node.node_type, None, node.left_node, node.right_node.right_node)
    # elif is_unary_operation(node):
    #     if node.right_node.node_type == MOANodeTypes.CONDITION:
    #         condition_node = node.right_node.condition_node
    #         node = Node(node.node_type, None, node.right_node.right_node)

    context = shape_map[node.node_type](context)

    # # combine possible two conditions and set shape
    # if node.node_type == MOANodeTypes.CONDITION and condition_node:
    #    node = Node(MOANodeTypes.CONDITION, node.shape,
    #                Node(MOANodeTypes.AND, (), condition_node, node.condition_node),
    #                node.right_node)
    # elif condition_node:
    #     node = Node(MOANodeTypes.CONDITION, node.shape, condition_node, node)

    return context


# Array Operations
def _shape_array(context):
    shape = ast.get_array_node_symbol(context).shape
    return ast.replace_node_shape(context, shape, ())


# Unary Operations
def _shape_transpose(context):
    shape = context.ast.shape[::-1]
    return ast.replace_node_shape(context, shape, ())


# def _shape_transpose_vector(symbol_table, node):
#     if not is_vector(symbol_table, node.left_node):
#         raise MOAShapeException('TRANSPOSE VECTOR requires left node to be vector')

#     left_symbol_node = symbol_table[node.left_node.symbol_node]
#     if has_symbolic_elements(node.left_node.shape) or has_symbolic_elements(left_symbol_node.value):
#         raise MOAShapeException('TRANSPOSE VECTOR not implemented for left node to be vector with symbolic components')

#     if node.left_node.shape[0] != dimension(symbol_table, node.right_node):
#         raise MOAShapeException('TRANSPOSE VECTOR requires left node vector to have total number of elements equal to dimension of right node')

#     if len(set(left_symbol_node.value)) != len(left_symbol_node.value):
#         raise MOAShapeException('TRANSPOSE VECTOR requires left node vector to have unique elements')

#     # sort two lists according to one list
#     shape = tuple(s for _, s in sorted(zip(left_symbol_node.value, node.right_node.shape), key=lambda pair: pair[0]))
#     return symbol_table, Node(node.node_type, shape, node.left_node, node.right_node)


# def _shape_assign(symbol_table, node):
#     if dimension(symbol_table, node.left_node) and dimension(symbol_table, node.right_node):
#         raise MOAShapeException('ASSIGN requires that the dimension of the left and right nodes to be same')

#     shape = ()
#     for i, (left_element, right_element) in enumerate(zip(node.left_node.shape, node.right_node.shape)):
#         if is_symbolic_element(left_element) and is_symbolic_element(right_element): # both are symbolic
#             conditions.append(Node(MOANodeTypes.EQUAL, (), left_element, right_element))
#             shape = shape + (left_element,)
#         elif is_symbolic_element(left_element): # only left is symbolic
#             array_name = generate_unique_array_name(symbol_table)
#             symbol_table = add_symbol(symbol_table, array_name, MOANodeTypes.ARRAY, (), (right_element,))
#             conditions.append(Node(MOANodeTypes.EQUAL, (), left_element, Node(MOANodeTypes.ARRAY, (), array_name)))
#             shape = shape + (right_element,)
#         elif is_symbolic_element(right_element): # only right is symbolic
#             array_name = generate_unique_array_name(symbol_table)
#             symbol_table = add_symbol(symbol_table, array_name, MOANodeTypes.ARRAY, (), (left_element,))
#             conditions.append(Node(MOANodeTypes.EQUAL, (), Node(MOANodeTypes.ARRAY, (), array_name), right_element))
#             shape = shape + (left_element,)
#         else: # neither symbolic
#             if left_element != right_element:
#                 raise MOAShapeException(f'ASSIGN requires shapes to match elements #{i} left {left_element} != right {right_element}')
#             shape = shape + (left_element,)

#     node = Node(node.node_type, shape, node.left_node, node.right_node)
#     if conditions:
#         condition_node = conditions[0]
#         for condition in conditions[1:]:
#             condition_node = Node(MOANodeTypes.AND, (), condition, condition_node)
#         node = Node(MOANodeTypes.CONDITION, node.shape, condition_node, node)
#     return symbol_table, node


# def _shape_shape(symbol_table, node):
#     return symbol_table, Node(node.node_type, (dimension(symbol_table, node.right_node),), node.right_node)


# # Binary Operations
# def _shape_psi(symbol_table, node):
#     if not is_vector(symbol_table, node.left_node):
#         raise MOAShapeException('PSI requires left node to be vector')

#     left_symbol_node = symbol_table[node.left_node.symbol_node]
#     if has_symbolic_elements(left_symbol_node.shape):
#         raise MOAShapeException('PSI not implemented for left node to be vector with symbolic shape')

#     drop_dimensions = left_symbol_node.shape[0]
#     if drop_dimensions > dimension(symbol_table, node.right_node):
#         raise MOAShapeException('PSI requires that vector length be no greater than dimension of right node')

#     conditions = []
#     for i, (left_element, right_element) in enumerate(zip(left_symbol_node.value, node.right_node.shape)):
#         if is_symbolic_element(left_element) and is_symbolic_element(right_element): # both are symbolic
#             conditions.append(Node(MOANodeTypes.LESSTHAN, (), left_element, right_element))
#         elif is_symbolic_element(left_element): # only left is symbolic
#             array_name = generate_unique_array_name(symbol_table)
#             symbol_table = add_symbol(symbol_table, array_name, MOANodeTypes.ARRAY, (), (right_element,))
#             conditions.append(Node(MOANodeTypes.LESSTHAN, (), left_element, Node(MOANodeTypes.ARRAY, (), array_name)))
#         elif is_symbolic_element(right_element): # only right is symbolic
#             array_name = generate_unique_array_name(symbol_table)
#             symbol_table = add_symbol(symbol_table, array_name, MOANodeTypes.ARRAY, (), (left_element,))
#             conditions.append(Node(MOANodeTypes.LESSTHAN, (), Node(MOANodeTypes.ARRAY, (), array_name), right_element))
#         else: # neither symbolic
#             if left_element >= right_element:
#                 raise MOAShapeException(f'PSI requires elements #{i} left {left_element} < right {right_element}')

#     node = Node(node.node_type, node.right_node.shape[drop_dimensions:], node.left_node, node.right_node)
#     if conditions:
#         condition_node = conditions[0]
#         for condition in conditions[1:]:
#             condition_node = Node(MOANodeTypes.AND, (), condition, condition_node)
#         node = Node(MOANodeTypes.CONDITION, node.shape, condition_node, node)
#     return symbol_table, node


# def _shape_reduce_plus_minus_divide_times(symbol_table, node):
#     if dimension(symbol_table, node.right_node) == 0:
#         return symbol_table, node.right_node
#     return symbol_table, Node(node.node_type, node.right_node.shape[1:], None, node.right_node)


# def _shape_outer_plus_minus_divide_times(symbol_table, node):
#     node_shape = node.left_node.shape + node.right_node.shape
#     return symbol_table, Node(node.node_type, node_shape, node.left_node, node.right_node)


# def _shape_plus_minus_divide_times(symbol_table, node):
#     conditions = []
#     if is_scalar(symbol_table, node.left_node): # scalar extension
#         shape = node.right_node.shape
#     elif is_scalar(symbol_table, node.right_node): # scalar extension
#         shape = node.left_node.shape
#     else: # shapes must match
#         if dimension(symbol_table, node.left_node) != dimension(symbol_table, node.right_node):
#             raise MOAShapeException('(+,-,/,*) requires dimension to match or single argument to be scalar')

#         shape = ()
#         for i, (left_element, right_element) in enumerate(zip(node.left_node.shape, node.right_node.shape)):
#             if is_symbolic_element(left_element) and is_symbolic_element(right_element): # both are symbolic
#                 conditions.append(Node(MOANodeTypes.EQUAL, (), left_element, right_element))
#                 shape = shape + (left_element,)
#             elif is_symbolic_element(left_element): # only left is symbolic
#                 array_name = generate_unique_array_name(symbol_table)
#                 symbol_table = add_symbol(symbol_table, array_name, MOANodeTypes.ARRAY, (), (right_element,))
#                 conditions.append(Node(MOANodeTypes.EQUAL, (), left_element, Node(MOANodeTypes.ARRAY, (), array_name)))
#                 shape = shape + (right_element,)
#             elif is_symbolic_element(right_element): # only right is symbolic
#                 array_name = generate_unique_array_name(symbol_table)
#                 symbol_table = add_symbol(symbol_table, array_name, MOANodeTypes.ARRAY, (), (left_element,))
#                 conditions.append(Node(MOANodeTypes.EQUAL, (), Node(MOANodeTypes.ARRAY, (), array_name), right_element))
#                 shape = shape + (left_element,)
#             else: # neither symbolic
#                 if left_element != right_element:
#                     raise MOAShapeException(f'(+,-,/,*) requires shapes to match elements #{i} left {left_element} != right {right_element}')
#                 shape = shape + (left_element,)

#     node = Node(node.node_type, shape, node.left_node, node.right_node)
#     if conditions:
#         condition_node = conditions[0]
#         for condition in conditions[1:]:
#             condition_node = Node(MOANodeTypes.AND, (), condition, condition_node)
#         node = Node(MOANodeTypes.CONDITION, node.shape, condition_node, node)
#     return symbol_table, node
