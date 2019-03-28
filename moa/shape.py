from . import ast
from .exception import MOAException


class MOAShapeError(MOAException):
    pass


# dimension
def dimension(context, selection=()):
    context = ast.select_node(context, selection)

    if ast.is_array(context):
        return len(ast.select_array_node_symbol(context).shape)
    elif node.shape:
        return len(node.shape)
    raise MOAShapeError(f'cannot determine dimension from node {node.node_type} with shape {node.shape}')


def is_scalar(context, selection=()):
    context = ast.select_node(context, selection)
    return ast.is_array(context) and dimension(context) == 0


def is_vector(context, selection=()):
    context = ast.select_node(context, selection)
    return ast.is_array(context) and dimension(context) == 1


# compare tuples
def compare_tuples(comparison, context, left_tuple, right_tuple, message):
    comparison_map = {
        ast.NodeSymbol.EQUAL: lambda e1, e2: e1 == e2,
        ast.NodeSymbol.NOTEQUAL: lambda e1, e2: e1 != e2,
        ast.NodeSymbol.LESSTHAN: lambda e1, e2: e1 < e2,
        ast.NodeSymbol.LESSTHANEQUAL: lambda e1, e2: e1 <= e2,
        ast.NodeSymbol.GREATERTHAN: lambda e1, e2: e1 > e2,
        ast.NodeSymbol.GREATERTHANEQUAL: lambda e1, e2: e1 >= e2,
    }

    conditions = ()
    shape = ()
    for i, (left_element, right_element) in enumerate(zip(left_tuple, right_tuple)):
        element_message = message + f'requires shapes to match elements #{i} left {left_element} != right {right_element}'

        if ast.is_symbolic_element(left_element) and ast.is_symbolic_element(right_element): # both are symbolic
            conditions = conditions + (ast.Node((MOANodeTypes.EQUAL,), (), (), (left_element, right_element)),)
            shape = shape + (left_element,)
        elif ast.is_symbolic_element(left_element): # only left is symbolic
            array_name = ast.generate_unique_array_name(symbol_table)
            context = ast.add_symbol(context, array_name, MOANodeTypes.ARRAY, (), None, (right_element,))
            conditions = conditions + (ast.Node((MOANodeTypes.EQUAL,), (), (), (left_element, ast.Node((ast.NodeSymbol.ARRAY,), (), (), (array_name,)))),)
            shape = shape + (right_element,)
        elif ast.is_symbolic_element(right_element): # only right is symbolic
            array_name = generate_unique_array_name(symbol_table)
            context = add_symbol(symbol_table, array_name, MOANodeTypes.ARRAY, (), None, (left_element,))
            conditions = conditions + (ast.Node((comparison,), (), (), (ast.Node((ast.NodeSymbol.ARRAY,), (), (), (array_name,)), right_element)),)
            shape = shape + (left_element,)
        else: # neither symbolic
            if not comparison_map[comparison](left_element, right_element):
                raise MOAShapeError(element_message)
            shape = shape + (left_element,)
    return context, conditions, shape


# shape calculation
def calculate_shapes(context):
    """Postorder traversal to calculate node shapes

    """
    return ast.node_traversal(context, _shape_replacement, traversal='postorder')


def _shape_replacement(context):
    shape_map = {
        (ast.NodeSymbol.ARRAY,): _shape_array,
        (ast.NodeSymbol.TRANSPOSE,): _shape_transpose,
        (ast.NodeSymbol.TRANSPOSEV,): _shape_transpose_vector,
        (ast.NodeSymbol.ASSIGN,): _shape_assign,
        (ast.NodeSymbol.SHAPE,): _shape_shape,
        (ast.NodeSymbol.PSI,): _shape_psi,
        # (ast.NodeSymbol.PLUS,): _shape_plus_minus_divide_times,
        # (ast.NodeSymbol.MINUS,): _shape_plus_minus_divide_times,
        # (ast.NodeSymbol.TIMES,): _shape_plus_minus_divide_times,
        # (ast.NodeSymbol.DIVIDE,): _shape_plus_minus_divide_times,
        # (ast.NodeSymbol.DOT, ast.NodeSymbol.PLUS): _shape_outer_plus_minus_divide_times,
        # (ast.NodeSymbol.DOT, ast.NodeSymbol.MINUS): _shape_outer_plus_minus_divide_times,
        # (ast.NodeSymbol.DOT, ast.NodeSymbol.TIMES): _shape_outer_plus_minus_divide_times,
        # (ast.NodeSymbol.DOT, ast.NodeSymbol.DIVIDE): _shape_outer_plus_minus_divide_times,
        # (ast.NodeSymbol.REDUCE, ast.NodeSymbol.PLUS): _shape_reduce_plus_minus_divide_times,
        # (ast.NodeSymbol.REDUCE, ast.NodeSymbol.MINUS): _shape_reduce_plus_minus_divide_times,
        # (ast.NodeSymbol.REDUCE, ast.NodeSymbol.TIMES): _shape_reduce_plus_minus_divide_times,
        # (ast.NodeSymbol.REDUCE, ast.NodeSymbol.DIVIDE): _shape_reduce_plus_minus_divide_times,
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

    context = shape_map[context.ast.symbol](context)

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
    shape = ast.select_array_node_symbol(context).shape
    return ast.replace_node_shape(context, shape)


# Unary Operations
def _shape_transpose(context):
    shape = ast.select_node_shape(context, (0,))[::-1]
    return ast.replace_node_shape(context, shape)


def _shape_transpose_vector(context):
    if not is_vector(context, (0,)):
        raise MOAShapeError('TRANSPOSE VECTOR requires left node to be vector')

    left_node_symbol = ast.select_array_node_symbol(context, (0,))
    if ast.has_symbolic_elements(left_node_symbol.shape) or ast.has_symbolic_elements(left_node_symbol.value):
        raise MOAShapeError('TRANSPOSE VECTOR not implemented for left node to be vector with symbolic components')

    if ast.select_node_shape(context, (0,))[0] != dimension(context, (1,)):
        raise MOAShapeError('TRANSPOSE VECTOR requires left node vector to have total number of elements equal to dimension of right node')

    if len(set(left_node_symbol.value)) != len(left_node_symbol.value):
        raise MOAShapeError('TRANSPOSE VECTOR requires left node vector to have unique elements')

    # sort two lists according to one list
    shape = tuple(s for _, s in sorted(zip(left_node_symbol.value, ast.select_node_shape(context, (1,))), key=lambda pair: pair[0]))
    return ast.replace_node_shape(context, shape)


def _shape_assign(context):
    if dimension(context, (0,)) != dimension(context, (1,)):
        raise MOAShapeError('ASSIGN requires that the dimension of the left and right nodes to be same')

    context, conditions, shape = compare_tuples(ast.NodeSymbol.EQUAL, context,
                                                ast.select_node_shape(context, (0,)),
                                                ast.select_node_shape(context, (1,)), 'ASSIGN')

    context = ast.replace_node_shape(context, shape)
    if conditions:
        condition_node = conditions[0]
        for condition in conditions[1:]:
            condition_node = ast.Node(ast.NodeSymbol.AND, (), (), (condition, condition_node))
        node = ast.Node(ast.NodeSymbol.CONDITION, shape, (), (condition_node, node))
        context = ast.create_context(ast=node, symbol_table=context.symbol_table)
    return context


def _shape_shape(context):
    shape = (dimension(ast.select_node(context, (0,))),)
    return ast.replace_node_shape(context, shape, ())


# Binary Operations
def _shape_psi(context):
    if not is_vector(context, (0,)):
        raise MOAShapeError('PSI requires left node to be vector')

    left_node_symbol = ast.select_array_node_symbol(context, (0,))
    if ast.has_symbolic_elements(left_node_symbol.shape):
        raise MOAShapeError('PSI not implemented for left node to be vector with symbolic shape')

    drop_dimensions = left_node_symbol.shape[0]
    if drop_dimensions > dimension(context, (1,)):
        raise MOAShapeError('PSI requires that vector length be no greater than dimension of right node')

    context, conditions, shape = compare_tuples(ast.NodeSymbol.LESSTHANEQUAL, context,
                                                left_node_symbol.value,
                                                ast.select_node_shape(context, (1,)), 'PSI')

    context = ast.replace_node_shape(context, ast.select_node_shape(context, (1,))[drop_dimensions:])
    if conditions:
        condition_node = conditions[0]
        for condition in conditions[1:]:
            condition_node = ast.Node(ast.NodeSymbol.AND, (), (), (condition, condition_node))
        node = ast.Node(ast.NodeSymbol.CONDITION, shape, (), (condition_node, node))
        context = ast.create_context(ast=node, symbol_table=context.symbol_table)
    return context


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
