import itertools

from .exception import MOAException
from . import ast, shape


class MOAReductionError(MOAException):
    pass


def add_indexing_node(context):
    """Adds indexing into the MOA AST

    For example: <i0 i1> psi (A + B)
    """
    condition_node = None
    if context.ast.symbol == (ast.NodeSymbol.CONDITION,):
        condition_node = ast.select_node(context, (0,)).ast
        context = ast.select_node(context, (1,))

    index_symbols = ()
    for bound in context.ast.shape:
        index_name = ast.generate_unique_index_name(context)
        context = ast.add_symbol(context, index_name, ast.NodeSymbol.INDEX, (), None, (0, bound, 1))
        index_symbols = index_symbols + (ast.Node((ast.NodeSymbol.ARRAY,), (), (index_name,), ()),)

    array_name = ast.generate_unique_array_name(context)
    context = ast.add_symbol(context, array_name, ast.NodeSymbol.ARRAY, (len(index_symbols),), None, index_symbols)
    vector_node = ast.Node((ast.NodeSymbol.ARRAY,), (len(index_symbols),), (array_name,), ())
    node = ast.Node((ast.NodeSymbol.PSI,), context.ast.shape, (), (vector_node, context.ast))

    if condition_node:
        node = ast.Node(ast.NodeSymbol.CONDITION, node.shape, (), (condition_node, node))

    return ast.create_context(ast=node, symbol_table=context.symbol_table)


def reduce_to_dnf(context):
    """Preorder traversal and replacement of ast tree

    """
    context = add_indexing_node(context)
    context = node_traversal(context, _reduce_replacement, traversal='preorder')
    return context


def matches_rule(rule, context):
    if rule[0] is not None and (rule[0] != context.ast.symbol):
        return False

    if len(rule) == 2:
        if ast.num_node_children(context) != len(rule[1]):
            return False

        for i in range(ast.num_node_children(context)):
            if rule[1][i] is None:
                continue

            sub_context = ast.select_node(context, (i,))
            if not matches_rule(rule[1][i], sub_context):
                return False
    return True


def _reduce_replacement(context):
    reduction_rules = {
        ((ast.NodeSymbol.PSI,), (None, (((ast.NodeSymbol.ASSIGN,),),),)): _reduce_psi_assign,
        ((ast.NodeSymbol.PSI,), (None, (((ast.NodeSymbol.PSI,),),),)): _reduce_psi_psi,
        ((ast.NodeSymbol.PSI,), (None, (((ast.NodeSymbol.TRANSPOSE,),),),)): _reduce_psi_transpose,
        ((ast.NodeSymbol.PSI,), (None, (((ast.NodeSymbol.TRANSPOSEV,),),),)): _reduce_psi_transposev,
        ((ast.NodeSymbol.PSI,), (None, (((ast.NodeSymbol.PLUS,),),),)): _reduce_psi_plus_minus_times_divide,
        ((ast.NodeSymbol.PSI,), (None, (((ast.NodeSymbol.MINUS,),),),)): _reduce_psi_plus_minus_times_divide,
        ((ast.NodeSymbol.PSI,), (None, (((ast.NodeSymbol.TIMES,),),),)): _reduce_psi_plus_minus_times_divide,
        ((ast.NodeSymbol.PSI,), (None, (((ast.NodeSymbol.DIVIDE,),),),)): _reduce_psi_plus_minus_times_divide,
        ((ast.NodeSymbol.PSI,), (None, (((ast.NodeSymbol.DOT, ast.NodeSymbol.PLUS),),),)): _reduce_psi_outer_plus_minus_times_divide,
        ((ast.NodeSymbol.PSI,), (None, (((ast.NodeSymbol.DOT, ast.NodeSymbol.MINUS),),),)): _reduce_psi_outer_plus_minus_times_divide,
        ((ast.NodeSymbol.PSI,), (None, (((ast.NodeSymbol.DOT, ast.NodeSymbol.TIMES),),),)): _reduce_psi_outer_plus_minus_times_divide,
        ((ast.NodeSymbol.PSI,), (None, (((ast.NodeSymbol.DOT, ast.NodeSymbol.DIVIDE),),),)): _reduce_psi_outer_plus_minus_times_divide,
        ((ast.NodeSymbol.PSI,), (None, (((ast.NodeSymbol.REDUCE, ast.NodeSymbol.PLUS),),),)): _reduce_psi_reduce_plus_minus_times_divide,
        ((ast.NodeSymbol.PSI,), (None, (((ast.NodeSymbol.REDUCE, ast.NodeSymbol.MINUS),),),)): _reduce_psi_reduce_plus_minus_times_divide,
        ((ast.NodeSymbol.PSI,), (None, (((ast.NodeSymbol.REDUCE, ast.NodeSymbol.TIMES),),),)): _reduce_psi_reduce_plus_minus_times_divide,
        ((ast.NodeSymbol.PSI,), (None, (((ast.NodeSymbol.REDUCE, ast.NodeSymbol.DIVIDE),),),)): _reduce_psi_reduce_plus_minus_times_divide,
    }

    for rule, replacement_function in reduction_rules.items():
        if matches_rule(rule, context):
            return replacement_function(context)
    return None, None


def _reduce_psi_assign(context):
    """<i j> psi ... assign ... => <i j> psi ... assign <i j> psi ..."""
    return ast.create_context(
        ast=ast.Node((ast.NodeSymbol.ASSIGN,), context.ast.shape, (), (
            ast.Node((ast.NodeSymbol.PSI,), context.ast.shape, (), (ast.select_node(context, (0,)).ast, ast.select_node(context, (1, 0)).ast)),
            ast.Node((ast.NodeSymbol.PSI,), context.ast.shape, (), (ast.select_node(context, (0,)).ast, ast.select_node(context, (1, 1)).ast)))),
        symbol_table=context.symbol_table)


def _reduce_psi_psi(context):
    """<i j> psi <k l> psi ... => <k l i j> psi ..."""
    # shape check implies that left_nodes are vectors
    left_node_symbol = ast.select_array_node_symbol(context, (0,))
    left_left_node_symbol = ast.select_array_node_symbol(context, (1, 0))

    if left_node_symbol.value is None or left_left_node_symbol is None:
        raise MOAReductionError('<...> PSI <...> PSI ... replacement assumes that the inner psi left_nodes have defined values')

    array_name = ast.generate_unique_array_name(context)
    array_values = left_left_node_symbol.value + left_node_symbol.value
    context = ast.add_symbol(context, array_name, ast.NodeSymbol.ARRAY, (len(array_values),), None, array_values)

    return ast.create_context(
        ast=ast.Node((ast.NodeSymbol.PSI,), context.ast.shape, (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (len(array_values),), (array_name,), ()),
            ast.select_node(context, (1, 1)).ast)),
        symbol_table=context.symbol_table)


def _reduce_psi_transpose(context):
    """<i j k> psi transpose ... => <k j i> psi ..."""
    array_name = ast.generate_unique_array_name(context)
    array_values = ast.select_array_node_symbol(context, (0,)).value[::-1]
    context = ast.add_symbol(context, array_name, ast.NodeSymbol.ARRAY, (len(array_values),), None, array_values)

    return ast.create_context(
        ast=ast.Node((ast.NodeSymbol.PSI,), context.ast.shape, (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (len(array_values),), (array_name,), ()),
            ast.select_node(context, (1, 0)).ast)),
        symbol_table=context.symbol_table)


def _reduce_psi_transposev(symbol_table, node):
    """<i j k> psi <2 0 1> transpose ... => <k i j> psi ..."""
    array_name = ast.generate_unique_array_name(symbol_table)
    array_values = tuple(s for _, s in sorted(zip(symbol_table[node.right_node.left_node.symbol_node].value, symbol_table[node.left_node.symbol_node].value), key=lambda pair: pair[0]))
    symbol_table = add_symbol(symbol_table, array_name, ast.NodeSymbol.ARRAY, (len(array_values),), array_values)
    return symbol_table, Node(ast.NodeSymbol.PSI, node.shape,
                                    Node(ast.NodeSymbol.ARRAY, (len(array_values),), array_name),
                                    node.right_node.right_node)


def _reduce_psi_reduce_plus_minus_times_divide(symbol_table, node):
    index_name = generate_unique_index_name(symbol_table)
    symbol_table = add_symbol(symbol_table, index_name, ast.NodeSymbol.INDEX, (), (0, node.right_node.right_node.shape[0]))

    index_vector = (Node(ast.NodeSymbol.ARRAY, (), index_name),) + symbol_table[node.left_node.symbol_node].value
    array_name = generate_unique_array_name(symbol_table)
    symbol_table = add_symbol(symbol_table, array_name, ast.NodeSymbol.ARRAY, (len(index_vector),), index_vector)

    return symbol_table, Node(node.right_node.node_type, node.shape, index_name,
                                    Node(ast.NodeSymbol.PSI, node.shape,
                                               Node(ast.NodeSymbol.ARRAY, (len(index_vector),), array_name),
                                               node.right_node.right_node))






def _reduce_psi_outer_plus_minus_times_divide(symbol_table, node):
    left_array_name = generate_unique_array_name(symbol_table)
    left_dimension = dimension(symbol_table, node.right_node.left_node)
    symbol_table = add_symbol(symbol_table, left_array_name, ast.NodeSymbol.ARRAY, (left_dimension,), symbol_table[node.left_node.symbol_node].value[:left_dimension])

    right_array_name = generate_unique_array_name(symbol_table)
    right_dimension = dimension(symbol_table, node.right_node.right_node)
    symbol_table = add_symbol(symbol_table, right_array_name, ast.NodeSymbol.ARRAY, (right_dimension,), symbol_table[node.left_node.symbol_node].value[-right_dimension:])

    return symbol_table, Node(node.right_node.node_type[1], node.shape,
                                    Node(ast.NodeSymbol.PSI, node.shape,
                                               Node(ast.NodeSymbol.ARRAY, (left_dimension,), left_array_name),
                                               node.right_node.left_node),
                                    Node(ast.NodeSymbol.PSI, node.shape,
                                               Node(ast.NodeSymbol.ARRAY, (right_dimension,), right_array_name),
                                               node.right_node.right_node))


def _reduce_psi_plus_minus_times_divide(symbol_table, node):
    """<i j> psi (... (+-*/) ...) => (<i j> psi ...) (+-*/) (<k l> psi ...)

    Scalar Extension
      <i j> psi (scalar (+-*/) ...) = scalar (+-*/) <i j> psi ...
    """
    if is_scalar(symbol_table, node.right_node.left_node):
        left_node = node.right_node.left_node
    else:
        left_node = Node(ast.NodeSymbol.PSI, node.shape,
                               node.left_node,
                               node.right_node.left_node)

    if is_scalar(symbol_table, node.right_node.right_node):
        right_node = node.right_node.right_node
    else:
        right_node = Node(ast.NodeSymbol.PSI, node.shape,
                                node.left_node,
                                node.right_node.right_node)

    return symbol_table, Node(node.right_node.node_type, node.shape, left_node, right_node)
