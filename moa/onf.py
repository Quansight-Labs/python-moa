from .exception import MOAException
from . import ast, visualize


class MOAONFReductionError(MOAException):
    pass


def reduce_to_onf(context, include_conditions=True):
    return naive_reduction(context, include_conditions=include_conditions)


def naive_reduction(context, include_conditions=True):
    """Simple backend does not simplify loops and directly converts moa reduced statement to ONF

    ONF AST is a language independent representation
    """
    array_arguments = determine_function_arguments(context.symbol_table)

    function_body = ()

    context, dimension_conditions = determine_dimension_conditions(context, array_arguments)
    if include_conditions and dimension_conditions:
        # dimension constraint
        function_body = function_body + (ast.Node((ast.NodeSymbol.CONDITION,), (), (), (
            ast.Node((ast.NodeSymbol.NOT,), (), (), (dimension_conditions,)),
            ast.Node((ast.NodeSymbol.BLOCK,), (), (), (ast.Node((ast.NodeSymbol.ERROR,), (), ('arguments have invalid dimension',), ()),)))),)

    context, assignments, shape_conditions = determine_shape_conditions(context, array_arguments)
    function_body = function_body + tuple(assignments)

    if include_conditions and shape_conditions:
        function_body = function_body + (ast.Node((ast.NodeSymbol.CONDITION,), (), (), (
            ast.Node((ast.NodeSymbol.NOT,), (), (), (shape_conditions,)),
            ast.Node((ast.NodeSymbol.BLOCK,), (), (), (ast.Node((ast.NodeSymbol.ERROR,), (), ('arguments do not match declared shape',), ()),)))),)

    # check for condition node in expression
    if context.ast.symbol == (ast.NodeSymbol.CONDITION,):
        condition_constraints = ast.select_node(context, (0,)).ast
        if include_conditions and condition_constraints:
            function_body = function_body + (ast.Node((ast.NodeSymbol.CONDITION,), (), (), (
                ast.Node((ast.NodeSymbol.NOT,), (), (), (condition_constraints,)),
                ast.Node((ast.NodeSymbol.BLOCK,), (), (), (ast.Node((ast.NodeSymbol.ERROR,), (), ('arguments have incompatible shape',), ()),)))),)
        context = ast.select_node(context, (1,))

    indicies = tuple(determine_indicies(context))

    # eventually get shapes and match with conditions
    result_array_name = ast.generate_unique_array_name(context)
    context = ast.add_symbol(context, result_array_name, ast.NodeSymbol.ARRAY, context.ast.shape, None, None)
    result_index_name = ast.generate_unique_array_name(context)
    context = ast.add_symbol(context, result_index_name, ast.NodeSymbol.ARRAY, (len(indicies),), None, indicies)
    result_initialization = (ast.Node((ast.NodeSymbol.INITIALIZE,), context.ast.shape, (result_array_name,), ()),)

    # reduce node
    context, initializations = rewrite_expression(ast.create_context(
        ast=ast.Node((ast.NodeSymbol.ASSIGN,), context.ast.shape, (), (
            ast.Node((ast.NodeSymbol.PSI,), context.ast.shape, (), (
                ast.Node((ast.NodeSymbol.ARRAY,), context.ast.shape, (result_index_name,), ()),
                ast.Node((ast.NodeSymbol.ARRAY,), context.ast.shape, (result_array_name,), ()))),
            context.ast)),
        symbol_table=context.symbol_table))

    # add array initializations
    initializations = initializations + result_initialization
    function_body = function_body + initializations

    if context.ast.symbol == (ast.NodeSymbol.BLOCK,):
        loop_block = context.ast.child
    else:
        loop_block = (context.ast,)

    for index in indicies:
        loop_block = (ast.Node((ast.NodeSymbol.LOOP,), context.ast.shape, (index.attrib[0],), (
            ast.Node((ast.NodeSymbol.BLOCK,), context.ast.shape, (), loop_block),)),)

    function_body = function_body + loop_block

    return ast.create_context(
        ast=ast.Node((ast.NodeSymbol.FUNCTION,), context.ast.shape, (tuple(arg.attrib[0] for arg in array_arguments), result_array_name), (
            ast.Node((ast.NodeSymbol.BLOCK,), context.ast.shape, (), function_body),)),
        symbol_table=context.symbol_table)


def rewrite_expression(context):
    initializations = ()

    initialization_map = {
        ast.NodeSymbol.PLUS: 0,
        ast.NodeSymbol.MINUS: 0,
        ast.NodeSymbol.TIMES: 1,
        ast.NodeSymbol.DIVIDE: 1,
    }

    def _apply_operation_on_block(context):
        operations = []
        block = []
        for i in range(ast.num_node_children(context)):
            child_node = ast.select_node(context, (i,))
            if child_node.ast.symbol == (ast.NodeSymbol.BLOCK,):
                block.extend(child_node.ast.child[:-1])
                operations.append(child_node.ast.child[-1])
            else:
                operations.append(child_node.ast)
        return ast.create_context(
            ast=ast.Node((ast.NodeSymbol.BLOCK,), (), (), (
                *block,
                ast.Node(context.ast.symbol, (), (), tuple(operations)))),
            symbol_table=context.symbol_table)

    def _reduce_traversal(context):
        nonlocal initializations

        if context.ast.symbol[0] == ast.NodeSymbol.REDUCE:
            array_name = ast.generate_unique_array_name(context)
            context = ast.add_symbol(context, array_name, ast.NodeSymbol.ARRAY, (), None, None)

            initializations = initializations + (ast.Node((ast.NodeSymbol.INITIALIZE,), (), (array_name,), ()),)
            initial_value_name = ast.generate_unique_array_name(context)
            context = ast.add_symbol(context, initial_value_name, ast.NodeSymbol.ARRAY, (), None, (initialization_map[context.ast.symbol[1]],))

            # a hackish way to handle nested block with operation
            block_children = ()
            if context.ast.child[0].symbol == (ast.NodeSymbol.BLOCK,):
                block_children = block_children + ast.select_node(context, (0,)).ast.child[:-1]
                block_end = ast.select_node(context, (0, -1)).ast
            else:
                block_end = ast.select_node(context, (0,)).ast
            loop_block = ast.Node((ast.NodeSymbol.BLOCK,), context.ast.shape, (),
                block_children + (
                    ast.Node((ast.NodeSymbol.ASSIGN,), (), (), (
                        ast.Node((ast.NodeSymbol.ARRAY,), (), (array_name,), ()),
                        ast.Node((context.ast.symbol[1],), (), (), (
                            ast.Node((ast.NodeSymbol.ARRAY,), (), (array_name,), ()),
                            block_end)))),))

            context = ast.create_context(
                ast=ast.Node((ast.NodeSymbol.BLOCK,), context.ast.shape, (), (
                    ast.Node((ast.NodeSymbol.ASSIGN,), (), (), (
                        ast.Node((ast.NodeSymbol.ARRAY,), (), (array_name,), ()),
                        ast.Node((ast.NodeSymbol.ARRAY,), (), (initial_value_name,), ()),)),
                    ast.Node((ast.NodeSymbol.LOOP,), context.ast.shape, (context.ast.attrib[0],), (loop_block,)),
                    ast.Node((ast.NodeSymbol.ARRAY,), (), (array_name,), ()))),
                symbol_table=context.symbol_table)
        elif ast.is_operation(context):
            context = _apply_operation_on_block(context)
        return context

    context = ast.node_traversal(context, _reduce_traversal, traversal='postorder')
    return context, initializations


def determine_dimension_conditions(context, function_arguments):
    dimension_conditions = []

    for array in function_arguments:
        # dim A == value
        value_name = ast.generate_unique_array_name(context)
        context = ast.add_symbol(context, value_name, ast.NodeSymbol.ARRAY, (), None, (len(array.shape),))

        dimension_conditions.append(ast.Node((ast.NodeSymbol.EQUAL,), (), (), (
            ast.Node((ast.NodeSymbol.DIM,), (), (), (array,)),
            ast.Node((ast.NodeSymbol.ARRAY,), (), (value_name,), ()))))

    node = dimension_conditions[0]
    for dimension_condition in dimension_conditions[1:]:
        node = ast.Node((ast.NodeSymbol.AND,), (), (), (dimension_condition, node))
    return context, node


def determine_shape_conditions(context, function_arguments):
    shape_conditions = []
    assignments = []
    for array in function_arguments:
        for i, element in enumerate(array.shape):
            array_name = ast.generate_unique_array_name(context)
            context = ast.add_symbol(context, array_name, ast.NodeSymbol.ARRAY, (1,), None, (i,))

            if ast.is_symbolic_element(element):
                # <i> psi shape A
                assignments.append(ast.Node((ast.NodeSymbol.ASSIGN,), (), (), (
                    ast.Node((ast.NodeSymbol.ARRAY,), (), (element.attrib[0],), ()),
                    ast.Node((ast.NodeSymbol.PSI,), (), (), (
                        ast.Node((ast.NodeSymbol.ARRAY,), (1,), (array_name,), ()),
                        ast.Node((ast.NodeSymbol.SHAPE,), (len(array.shape),), (), (array,)))))))
            else:
                # <i> psi shape A == value
                value_name = ast.generate_unique_array_name(context)
                context = ast.add_symbol(context, value_name, ast.NodeSymbol.ARRAY, (), None, (element,))

                shape_conditions.append(ast.Node((ast.NodeSymbol.EQUAL,), (), (), (
                    ast.Node((ast.NodeSymbol.ARRAY,), (), (value_name,), ()),
                    ast.Node((ast.NodeSymbol.PSI,), (), (), (
                        ast.Node((ast.NodeSymbol.ARRAY,), (1,), (array_name,), ()),
                        ast.Node((ast.NodeSymbol.SHAPE,), (len(array.shape),), (), (array,)))))))

    node = ()
    if shape_conditions:
        node = shape_conditions[0]
        for shape_condition in shape_conditions[1:]:
            node = ast.Node((ast.NodeSymbol.AND,), (), (), (shape_condition, node))
    return context, tuple(assignments), node


def determine_function_arguments(symbol_table):
    """Determines function arguments to moa statement based on symbol table

    Behavior:
      - user defined named symbols with unknown shape or values are arguments
      - implicit arrays "<1 2 n>" with unknown values are arguments
    """
    dependent_arguments = set()
    array_arguments = set()

    for symbol_name, symbol_node in symbol_table.items():
        if symbol_node.symbol == ast.NodeSymbol.INDEX:
            pass # index nodes are not function arguments
        elif symbol_name.startswith('_'):
            if symbol_node.shape is None or ast.has_symbolic_elements(symbol_node.shape):
                raise NotImplementedError('cannot have implicit array with unknown shape')
            elif ast.has_symbolic_elements(symbol_node.value):
                for element in symbol_node.value:
                    if ast.is_symbolic_element(element) and symbol_table[element.attrib[0]].symbol != ast.NodeSymbol.INDEX:
                        array_arguments.add(element.attrib[0])
        else: # user defined
            if symbol_node.shape is None:
                array_arguments.add(symbol_name)
            elif ast.has_symbolic_elements(symbol_node.shape):
                array_arguments.add(symbol_name)
                for element in symbol_node.shape:
                    if ast.is_symbolic_element(element):
                        dependent_arguments.add(element.attrib[0])

            if symbol_node.value is None:
                array_arguments.add(symbol_name)
            elif ast.has_symbolic_elements(symbol_node.value):
                array_arguments.add(symbol_name)
                for element in symbol_node.value:
                    if ast.is_symbolic_element(element):
                        dependent_arguments.add(element.attrib[0])
    return tuple(ast.Node((ast.NodeSymbol.ARRAY,), symbol_table[array_name].shape, (array_name,), ()) for array_name in sorted(array_arguments - dependent_arguments))


def determine_indicies(context):
    indicies = set()
    for symbol_name, symbol_node in context.symbol_table.items():
        if symbol_node.symbol == ast.NodeSymbol.INDEX:
            indicies.add(symbol_name)

    # find indicies in reductions (they should not be included)
    reduction_indicies = set()
    def _reduce_indicies(context):
        if context.ast.symbol[0] == ast.NodeSymbol.REDUCE:
            reduction_indicies.add(context.ast.attrib[0])
        return context

    ast.node_traversal(context, _reduce_indicies, traversal='postorder')
    return tuple(ast.Node((ast.NodeSymbol.ARRAY,), (), (i,), ()) for i in sorted(indicies - reduction_indicies))
