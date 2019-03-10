from ..core import MOAException
from ..ast import (
    MOANodeTypes, ArrayNode, BinaryNode, ConditionNode, FunctionNode, LoopNode, ErrorNode, InitializeNode, IfNode,
    generate_unique_array_name, add_symbol
)
from ..shape import (
    has_symbolic_elements, is_symbolic_element
)


class MOABackendError(MOAException):
    pass


def determine_function_arguments(symbol_table):
    """Determines function arguments to moa statement based on symbol table

    Behavior:
      - user defined named symbols with unknown shape or values are arguments
      - implicit arrays "<1 2 n>" with unknown values are arguments
    """
    dependent_arguments = set()
    array_arguments = set()

    for symbol_name, symbol_node in symbol_table.items():
        if symbol_name.startswith('_'):
            if symbol_node.shape is None or has_symbolic_elements(symbol_node.shape):
                raise NotImplementedError('cannot have implicit array with unknown shape')
            elif has_symbolic_elements(symbol_node.value):
                for element in symbol_node.value:
                    if is_symbolic_element(element):
                        array_arguments.add(element.symbol_node)
        else: # user defined
            if symbol_node.shape is None:
                array_arguments.add(symbol_name)
            elif has_symbolic_elements(symbol_node.shape):
                array_arguments.add(symbol_name)
                for element in symbol_node.shape:
                    if is_symbolic_element(element):
                        dependent_arguments.add(element.symbol_node)

            if symbol_node.value is None:
                array_arguments.add(symbol_name)
            elif has_symbolic_elements(symbol_node.value):
                array_arguments.add(symbol_name)
                for element in symbol_node.value:
                    if is_symbolic_element(element):
                        dependent_arguments.add(element.symbol_node)
    return array_arguments - dependent_arguments


def determine_indicies(symbol_table):
    indicies = set()
    for symbol_name, symbol_node in symbol_table.items():
        if symbol_node.node_type == MOANodeTypes.INDEX:
            indicies.add(symbol_name)
    return tuple(sorted(indicies))


def add_function_node(symbol_table, node):
    symbols = determine_function_arguments(symbol_table)

    function_body = ()

    # grab condition node
    if node.node_type == MOANodeTypes.CONDITION:
        function_body = (IfNode(MOANodeTypes.IF, (), node.condition_node, (ErrorNode(MOANodeTypes.ERROR, (), 'arguments have invalid shape'),)),)
        node = node.right_node

    indicies = determine_indicies(symbol_table)

    # eventually get shapes and match with conditions
    result_array_name = generate_unique_array_name(symbol_table)
    symbol_table = add_symbol(symbol_table, result_array_name, MOANodeTypes.ARRAY, node.shape, None)
    result_index_name = generate_unique_array_name(symbol_table)
    symbol_table = add_symbol(symbol_table, result_index_name, MOANodeTypes.ARRAY, (len(indicies),), indicies)

    function_body = function_body + (InitializeNode(MOANodeTypes.INITIALIZE, node.shape, result_array_name),)

    loop_node =  BinaryNode(MOANodeTypes.ASSIGN, node.shape,
                            BinaryNode(MOANodeTypes.PSI, node.shape,
                                       ArrayNode(MOANodeTypes.ARRAY, node.shape, result_index_name),
                                       ArrayNode(MOANodeTypes.ARRAY, node.shape, result_array_name)),
                             node)

    for index in indicies:
        loop_node = LoopNode(MOANodeTypes.LOOP, node.shape, index, (loop_node,))

    function_body = function_body + (loop_node,)

    return symbol_table, FunctionNode(MOANodeTypes.FUNCTION, node.shape, tuple(symbols), result_array_name, function_body)



def simple_backend(symbol_table, node):
    """Simple backend does not simplify loops and directly converts moa reduced statement to ONF

    """
    pass
