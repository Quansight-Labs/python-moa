import enum
import collections
import copy

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
    return 100 < node.node_type.value < 200


def is_binary_operation(node):
    return 200 < node.node_type.value < 300


# symbol table methods
def add_symbol(symbol_table, name, node_type, shape, value):
    if name in symbol_table and symbol_table[name] != (node_type, shape, value):
        raise MOAException(f'attempted to add to symbol table different symbol with same name {symbol_table[name]} != {SymbolNode(node_type, shape, value)}')

    # idempotency makes debugging way easier dict(str: tuple)
    # deep copy not necessary
    symbol_table_copy = copy.copy(symbol_table)
    symbol_table_copy[name] = SymbolNode(node_type, shape, value)
    return symbol_table_copy


def generate_unique_array_name(symbol_table):
    return f'_a{len(symbol_table)}'


def generate_unique_index_name(symbol_table):
    return f'_i{len(symbol_table)}'


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

    return symbol_table, node
