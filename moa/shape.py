from . import ast
from .exception import MOAException


class MOAShapeError(MOAException):
    pass


# dimension
def dimension(context, selection=()):
    context = ast.select_node(context, selection)

    if ast.is_array(context):
        return len(ast.select_array_node_symbol(context).shape)
    elif context.ast.shape is not None:
        return len(context.ast.shape)
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
        element_message = message + f' requires shapes to match elements #{i} left {left_element} != right {right_element}'

        if ast.is_symbolic_element(left_element) and ast.is_symbolic_element(right_element): # both are symbolic
            conditions = conditions + (ast.Node((comparison,), (), (), (left_element, right_element)),)
            shape = shape + (left_element,)
        elif ast.is_symbolic_element(left_element): # only left is symbolic
            array_name = ast.generate_unique_array_name(context)
            context = ast.add_symbol(context, array_name, ast.NodeSymbol.ARRAY, (), None, (right_element,))
            conditions = conditions + (ast.Node((comparison,), (), (), (left_element, ast.Node((ast.NodeSymbol.ARRAY,), (), (array_name,), ()))),)
            shape = shape + (right_element,)
        elif ast.is_symbolic_element(right_element): # only right is symbolic
            array_name = ast.generate_unique_array_name(context)
            context = ast.add_symbol(context, array_name, ast.NodeSymbol.ARRAY, (), None, (left_element,))
            conditions = conditions + (ast.Node((comparison,), (), (), (ast.Node((ast.NodeSymbol.ARRAY,), (), (array_name,), ()), right_element)),)
            shape = shape + (left_element,)
        else: # neither symbolic
            if not comparison_map[comparison](left_element, right_element):
                raise MOAShapeError(element_message)
            shape = shape + (left_element,)
    return context, conditions, shape


def apply_node_conditions(context, conditions):
    if conditions:
        condition_node = conditions[0]
        for condition in conditions[1:]:
            condition_node = ast.Node((ast.NodeSymbol.AND,), (), (), (condition, condition_node))

        context = ast.create_context(
            ast=ast.Node((ast.NodeSymbol.CONDITION,), context.ast.shape, (), (condition_node, context.ast)),
            symbol_table=context.symbol_table)
    return context


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
        (ast.NodeSymbol.PLUS,): _shape_plus_minus_divide_times,
        (ast.NodeSymbol.MINUS,): _shape_plus_minus_divide_times,
        (ast.NodeSymbol.TIMES,): _shape_plus_minus_divide_times,
        (ast.NodeSymbol.DIVIDE,): _shape_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.PLUS): _shape_outer_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.MINUS): _shape_outer_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.TIMES): _shape_outer_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.DIVIDE): _shape_outer_plus_minus_divide_times,
        (ast.NodeSymbol.REDUCE, ast.NodeSymbol.PLUS): _shape_reduce_plus_minus_divide_times,
        (ast.NodeSymbol.REDUCE, ast.NodeSymbol.MINUS): _shape_reduce_plus_minus_divide_times,
        (ast.NodeSymbol.REDUCE, ast.NodeSymbol.TIMES): _shape_reduce_plus_minus_divide_times,
        (ast.NodeSymbol.REDUCE, ast.NodeSymbol.DIVIDE): _shape_reduce_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.PLUS  , ast.NodeSymbol.PLUS):   _shape_inner_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.MINUS , ast.NodeSymbol.PLUS):   _shape_inner_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.TIMES , ast.NodeSymbol.PLUS):   _shape_inner_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.DIVIDE, ast.NodeSymbol.PLUS):   _shape_inner_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.PLUS  , ast.NodeSymbol.MINUS):  _shape_inner_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.MINUS , ast.NodeSymbol.MINUS):  _shape_inner_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.TIMES , ast.NodeSymbol.MINUS):  _shape_inner_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.DIVIDE, ast.NodeSymbol.MINUS):  _shape_inner_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.PLUS  , ast.NodeSymbol.TIMES):  _shape_inner_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.MINUS , ast.NodeSymbol.TIMES):  _shape_inner_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.TIMES , ast.NodeSymbol.TIMES):  _shape_inner_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.DIVIDE, ast.NodeSymbol.TIMES):  _shape_inner_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.PLUS  , ast.NodeSymbol.DIVIDE): _shape_inner_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.MINUS , ast.NodeSymbol.DIVIDE): _shape_inner_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.TIMES , ast.NodeSymbol.DIVIDE): _shape_inner_plus_minus_divide_times,
        (ast.NodeSymbol.DOT, ast.NodeSymbol.DIVIDE, ast.NodeSymbol.DIVIDE): _shape_inner_plus_minus_divide_times,
    }

    conditions = ()
    for i in range(ast.num_node_children(context)):
        node = ast.select_node(context, (i,)).ast
        if node.symbol == (ast.NodeSymbol.CONDITION,):
            conditions = conditions + (node.child[0],)
            context = ast.replace_node(context, node.child[1], (i,))

    context = shape_map[context.ast.symbol](context)

    if context.ast.symbol == (ast.NodeSymbol.CONDITION,):
        conditions = conditions + (context.ast.child[0],)
        context = ast.select_node(context, (1,))

    context = apply_node_conditions(context, conditions)
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
    return apply_node_conditions(context, conditions)


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

    shape = ast.select_node_shape(context, (1,))[drop_dimensions:]
    context = ast.replace_node_shape(context, shape)
    return apply_node_conditions(context, conditions)


def _shape_reduce_plus_minus_divide_times(context):
    if dimension(context, (0,)) == 0:
        return ast.select_node(context, (0,))
    shape = ast.select_node_shape(context, (0,))[1:]
    return ast.replace_node_shape(context, shape)


def _shape_outer_plus_minus_divide_times(context):
    shape = ast.select_node_shape(context, (0,)) + ast.select_node_shape(context, (1,))
    return ast.replace_node_shape(context, shape)


def _shape_inner_plus_minus_divide_times(context):
    left_shape = ast.select_node_shape(context, (0,))
    right_shape = ast.select_node_shape(context, (1,))

    context, conditions, shape = compare_tuples(ast.NodeSymbol.EQUAL, context,
                                                left_shape[-1:], right_shape[:1], 'INNER PRODUCT')
    shape = left_shape[:-1] + right_shape[1:]
    context = ast.replace_node_shape(context, shape)
    return apply_node_conditions(context, conditions)


def _shape_plus_minus_divide_times(context):
    conditions = ()
    if is_scalar(context, (0,)): # scalar extension
        shape = ast.select_node_shape(context, (1,))
    elif is_scalar(context, (1,)): # scalar extension
        shape = ast.select_node_shape(context, (0,))
    else: # shapes must match
        if dimension(context, (0,)) != dimension(context, (1,)):
            raise MOAShapeError('(+,-,/,*) requires dimension to match or single argument to be scalar')

        context, conditions, shape = compare_tuples(ast.NodeSymbol.EQUAL, context,
                                                    ast.select_node_shape(context, (0,)),
                                                    ast.select_node_shape(context, (1,)), '(+-*/)')

    context = ast.replace_node_shape(context, shape)
    return apply_node_conditions(context, conditions)
