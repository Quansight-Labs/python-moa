import enum
import collections
import copy
import itertools

from .core import MOAException


class MOAReplacementError(MOAException):
    pass


class MOANodeTypes(enum.Enum):
    # storage
    ARRAY = 1 # scalars, vectors, array
    INDEX = 2 # indexing

    # control
    INITIALIZE = 50
    FUNCTION   = 51
    LOOP       = 52
    ASSIGN     = 53
    ERROR      = 54
    CONDITION  = 55
    IF         = 56

    # compound operators
    # examples
    #  - reduce
    #  - outer and inner product
    REDUCE = 75
    DOT = 76

    # unary
    PLUSRED   = 101
    MINUSRED  = 102
    TIMESRED  = 103
    DIVIDERED = 104
    IOTA      = 105
    DIM       = 106
    TAU       = 107
    SHAPE     = 108
    RAV       = 109
    TRANSPOSE = 110

    # unary boolean
    NOT       = 150

    # binary
    PLUS       = 201
    MINUS      = 202
    TIMES      = 203
    DIVIDE     = 204
    PSI        = 205
    TAKE       = 206
    DROP       = 207
    CAT        = 208
    TRANSPOSEV = 209

    # binary boolean (comparison)
    EQUAL            = 250
    NOTEQUAL         = 251
    LESSTHAN         = 252
    LESSTHANEQUAL    = 253
    GREATERTHAN      = 254
    GREATERTHANEQUAL = 255
    AND              = 256
    OR               = 257


# AST Representation
FunctionNode = collections.namedtuple(
    'FunctionNode', ['node_type', 'shape', 'arguments', 'result', 'body'])
LoopNode = collections.namedtuple(
    'LoopNode', ['node_type', 'shape', 'symbol_node', 'body'])
IfNode = collections.namedtuple(
    'IfNode', ['node_type', 'shape', 'condition_node', 'body'])
InitializeNode = collections.namedtuple(
    'InitializeNode', ['node_type', 'shape', 'symbol_node'])
ErrorNode = collections.namedtuple(
    'ErrorNode', ['node_type', 'shape', 'message'])
ConditionNode = collections.namedtuple(
    'ConditionNode', ['node_type', 'shape', 'condition_node', 'right_node'])
ReduceNode = collections.namedtuple(
    'ReduceNode', ['node_type', 'shape', 'symbol_node', 'right_node'])
ArrayNode = collections.namedtuple(
    'ArrayNode', ['node_type', 'shape', 'symbol_node'])
UnaryNode = collections.namedtuple(
    'UnaryNode', ['node_type', 'shape', 'right_node'])
BinaryNode = collections.namedtuple(
    'BinaryNode', ['node_type', 'shape', 'left_node', 'right_node'])

# Symbol Table
SymbolNode = collections.namedtuple(
    'SymbolNode', ['node_type', 'shape', 'value'])


# node methods
def is_array(node):
    return node.node_type == MOANodeTypes.ARRAY


def is_unary_operation(node):
    if isinstance(node.node_type, tuple):
        return False
    return 100 < node.node_type.value < 200


def is_binary_operation(node):
    if isinstance(node.node_type, tuple):
        return node.node_type[0] == MOANodeTypes.DOT
    else:
        return 200 < node.node_type.value < 300


def Node(node_type, *args):
    """node constructor

    """
    if isinstance(node_type, tuple) and node_type[0] == MOANodeTypes.DOT:
        shape, left_node, right_node = args
        return BinaryNode(node_type, shape, left_node, right_node)
    elif isinstance(node_type, tuple) and node_type[0] == MOANodeTypes.REDUCE:
        shape, symbol_node, right_node = args
        return ReduceNode(node_type, shape, symbol_node, right_node)
    elif node_type in {MOANodeTypes.ARRAY, MOANodeTypes.INDEX}:
        shape, symbol_node = args
        return ArrayNode(node_type, shape, symbol_node)
    elif node_type == MOANodeTypes.INITIALIZE:
        shape, symbol_node = args
        return InitializeNode(node_type, shape, symbol_node)
    elif node_type == MOANodeTypes.FUNCTION:
        shape, arguments, result, body = args
        return FunctionNode(node_type, shape, arguments, result, body)
    elif node_type == MOANodeTypes.LOOP:
        shape, symbol_node, body = args
        return LoopNode(node_type, shape, symbol_node, body)
    elif node_type == MOANodeTypes.ASSIGN:
        shape, left_node, right_node = args
        return BinaryNode(node_type, shape, left_node, right_node)
    elif node_type == MOANodeTypes.ERROR:
        shape, message = args
        return ErrorNode(node_type, shape, message)
    elif node_type == MOANodeTypes.CONDITION:
        shape, condition_node, right_node = args
        return ConditionNode(node_type, shape, condition_node, right_node)
    elif node_type == MOANodeTypes.IF:
        shape, condition_node, body = args
        return IfNode(node_type, shape, condition_node, body)
    elif 100 < node_type.value < 200:
        shape, right_node = args
        return UnaryNode(node_type, shape, right_node)
    elif 200 < node_type.value < 300:
        shape, left_node, right_node = args
        return BinaryNode(node_type, shape, left_node, right_node)


# symbol table methods
def add_symbol(symbol_table, name, node_type, shape, value):
    if name in symbol_table and symbol_table[name] != (node_type, shape, value):
        raise MOAException(f'attempted to add to symbol table different symbol with same name "{name}" {symbol_table[name]} != {SymbolNode(node_type, shape, value)}')

    # idempotency makes debugging way easier dict(str: tuple)
    # deep copy not necessary
    symbol_table_copy = copy.copy(symbol_table)
    symbol_table_copy[name] = SymbolNode(node_type, shape, value)
    return symbol_table_copy


def generate_unique_array_name(symbol_table):
    return f'_a{len(symbol_table)}'


def generate_unique_index_name(symbol_table):
    return f'_i{len(symbol_table)}'


# symbolic
def has_symbolic_elements(elements):
    return any(is_symbolic_element(element) for element in elements)


def is_symbolic_element(element):
    return isinstance(element, tuple)


# joining symbolic tables
def join_symbol_tables(left_symbol_table, left_tree, right_symbol_table, right_tree):
    """Join two symbol tables together which requires rewriting both trees

    TODO: This function is ugly and could be simplified/broken into parts. It is needed by the array frontend.

    """
    visited_symbols = set()
    counter = itertools.count()

    def _visit_node(symbol_table, node):
        if node.shape:
            raise ValueError('joining symbol tables currently naively assumes it is performed before shape analysis')

        if node.node_type == MOANodeTypes.ARRAY:
            visited_symbols.add(node.symbol_node)

            symbol_node = symbol_table[node.symbol_node]
            if symbol_node.shape:
                for element in symbol_node.shape:
                    if is_symbolic_element(element):
                        visited_symbols.add(element.symbol_node)

            if symbol_node.value:
                for element in symbol_node.value:
                    if is_symbolic_element(element):
                        visited_symbols.add(element.symbol_node)
        return symbol_table, node

    def _symbol_mapping(symbols):
        symbol_mapping = {}
        for symbol in symbols:
            if symbol.startswith('_i'):
                symbol_mapping[symbol] = f'_i{next(counter)}'
            elif symbol.startswith('_a'):
                symbol_mapping[symbol] = f'_a{next(counter)}'
            else:
                symbol_mapping[symbol] = symbol
        return symbol_mapping

    # discover used symbols and create symbol mapping
    postorder_replacement(left_symbol_table, left_tree, _visit_node)
    left_symbol_mapping = _symbol_mapping(visited_symbols)
    visited_symbols.clear()
    postorder_replacement(right_symbol_table, right_tree, _visit_node)
    right_symbol_mapping = _symbol_mapping(visited_symbols)

    # check that user defined symbols match in both tables
    for symbol in (left_symbol_mapping.keys() & right_symbol_mapping.keys()):
        if not symbol.startswith('_') and left_symbol_table[symbol] != right_symbol_table[symbol]:
            raise ValueError(f'user defined symbols must match "{symbol}" {left_symbol_table[symbol]} != {right_symbol_table[symbol]}')

    # rename symbols in tree
    symbol_mapping = {**left_symbol_mapping, **right_symbol_mapping}

    def _rename_symbols(symbol_table, node):
        if node.node_type == MOANodeTypes.ARRAY:
            node = ArrayNode(MOANodeTypes.ARRAY, None, symbol_mapping[node.symbol_node])
        return symbol_table, node

    new_left_symbol_table, new_left_tree = postorder_replacement(left_symbol_table, left_tree, _rename_symbols)
    new_right_symbol_table, new_right_tree = postorder_replacement(right_symbol_table, right_tree, _rename_symbols)

    # select subset of symbols from both symbol tables and rename
    new_symbol_table = {}
    for old_name, new_name in left_symbol_mapping.items():
        new_symbol_table[new_name] = new_left_symbol_table[old_name]
    for old_name, new_name in right_symbol_mapping.items():
        new_symbol_table[new_name] = new_right_symbol_table[old_name]

    # rename symbols within SymbolNode
    for name, symbol_node in new_symbol_table.items():
        shape = None
        if symbol_node.shape is not None:
            shape = ()
            for element in symbol_node.shape:
                if is_symbolic_element(element):
                    shape = shape + (ArrayNode(element.node_type, element.shape, symbol_mapping[element.symbol_node]),)
                else:
                    shape = shape + (element,)

        value = None
        if symbol_node.value is not None:
            value = ()
            for element in symbol_node.value:
                if is_symbolic_element(element):
                    value = value + (ArrayNode(element.node_type, element.shape, symbol_mapping[element.symbol_node]),)
                else:
                    value = value + (element,)
        new_symbol_table[name] = SymbolNode(MOANodeTypes.ARRAY, shape, value)

    return new_symbol_table, new_left_tree, new_right_tree


## replacement methods
def postorder_replacement(symbol_table, node, replacement_function):
    """Postorder (Left, Right, Root) traversal of AST

    Used for calculating the shape of the ast at each node.

    new_symbol_table, new_node = replacement_function(symbol_table, node)
    """
    if is_unary_operation(node):
        symbol_table, right_node = postorder_replacement(symbol_table, node.right_node, replacement_function)
        node = UnaryNode(node.node_type, node.shape, right_node)

    elif is_binary_operation(node) or node.node_type in {MOANodeTypes.ASSIGN}:
        symbol_table, left_node = postorder_replacement(symbol_table, node.left_node, replacement_function)
        symbol_table, right_node = postorder_replacement(symbol_table, node.right_node, replacement_function)
        node = BinaryNode(node.node_type, node.shape, left_node, right_node)

    elif node.node_type == MOANodeTypes.IF:
        symbol_table, condition_node = postorder_replacement(symbol_table, node.condition_node, replacement_function)

        replacement_nodes = ()
        for child_node in node.body:
            symbol_table, replacement_node = postorder_replacement(symbol_table, child_node, replacement_function)
            replacement_nodes = replacement_nodes + (replacement_node,)
        node = IfNode(node.node_type, node.shape, condition_node, replacement_nodes)

    elif node.node_type == MOANodeTypes.FUNCTION:
        replacement_nodes = ()
        for child_node in node.body:
            symbol_table, replacement_node = postorder_replacement(symbol_table, child_node, replacement_function)
            replacement_nodes = replacement_nodes + (replacement_node,)
        node = FunctionNode(node.node_type, node.shape, node.arguments, node.result, replacement_nodes)

    elif node.node_type == MOANodeTypes.LOOP:
        replacement_nodes = ()
        for child_node in node.body:
            symbol_table, replacement_node = postorder_replacement(symbol_table, child_node, replacement_function)
            replacement_nodes = replacement_nodes + (replacement_node,)
        node = LoopNode(node.node_type, node.shape, node.symbol_node, replacement_nodes)

    elif isinstance(node.node_type, tuple) and node.node_type[0] == MOANodeTypes.REDUCE:
        symbol_table, right_node = postorder_replacement(symbol_table, node.right_node, replacement_function)
        node = ReduceNode(node.node_type, node.shape, node.symbol_node, right_node)

    return replacement_function(symbol_table, node)


def preorder_replacement(symbol_table, node, replacement_function, max_iterations=range(100)):
    """Preorder (Root, Left, Right) traversal of AST

    Used for reducing the ast. Note that "replacement_function" is
    called until it returns "None" indicating that there are no more
    reductions to perform on the root node. This behavior is different
    than the "postorder_replacement" function.

    new_context = replacement_function(context)
    """
    for iteration in max_iterations:
        replacement_symbol_table, replacement_node = replacement_function(symbol_table, node)
        if replacement_symbol_table is None or replacement_node is None:
            break
        symbol_table = replacement_symbol_table
        node = replacement_node
    else:
        raise MOAReplacementError(f'reduction failed to complete in max_iterations')

    if is_unary_operation(node):
        symbol_table, right_node = preorder_replacement(symbol_table, node.right_node, replacement_function, max_iterations)
        node = UnaryNode(node.node_type, node.shape, right_node)

    elif is_binary_operation(node):
        symbol_table, left_node = preorder_replacement(symbol_table, node.left_node, replacement_function, max_iterations)
        symbol_table, right_node = preorder_replacement(symbol_table, node.right_node, replacement_function, max_iterations)
        node = BinaryNode(node.node_type, node.shape, left_node, right_node)

    elif node.node_type == MOANodeTypes.ASSIGN:
        symbol_table, left_node = preorder_replacement(symbol_table, node.left_node, replacement_function, max_iterations)
        symbol_table, right_node = preorder_replacement(symbol_table, node.right_node, replacement_function, max_iterations)
        node = BinaryNode(node.node_type, node.shape, left_node, right_node)

    elif node.node_type == MOANodeTypes.CONDITION:
        symbol_table, right_node = preorder_replacement(symbol_table, node.right_node, replacement_function, max_iterations)
        node = ConditionNode(node.node_type, node.shape, node.condition_node, right_node)

    elif node.node_type == MOANodeTypes.FUNCTION:
        replacement_nodes = ()
        for child_node in node.body:
            symbol_table, replacement_node = preorder_replacement(symbol_table, child_node, replacement_function)
            replacement_nodes = replacement_nodes + (replacement_node,)
        node = FunctionNode(node.node_type, node.shape, node.arguments, replacement_nodes)

    elif isinstance(node.node_type, tuple) and node.node_type[0] == MOANodeTypes.REDUCE:
        symbol_table, right_node = preorder_replacement(symbol_table, node.right_node, replacement_function)
        node = ReduceNode(node.node_type, node.shape, node.symbol_node, right_node)

    return symbol_table, node
