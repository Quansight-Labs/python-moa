import enum
import collections
import copy
import itertools


NodeSymbol = enum.Enum('NodeSymbol', [
    # storage
    'ARRAY', 'INDEX',
    # control
    'FUNCTION', 'INITIALIZE', 'LOOP', 'CONDITION', 'ERROR', 'BLOCK',
    # compound operators
    'REDUCE', 'DOT',
    # unary operators
    'IOTA', 'DIM', 'TAU', 'SHAPE', 'RAV', 'TRANSPOSE',
    # unary boolean operators
    'NOT',
    # binary operators
    'ASSIGN', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'PSI', 'TAKE', 'DROP', 'CAT', 'TRANSPOSEV',
    # binary boolean operators
    'EQUAL', 'NOTEQUAL',
    'LESSTHAN', 'LESSTHANEQUAL',
    'GREATERTHAN', 'GREATERTHANEQUAL',
    'AND', 'OR',
])


Node = collections.namedtuple(
    'Node', ['symbol', 'shape', 'attrib', 'child'])

SymbolNode = collections.namedtuple(
    'SymbolNode', ['symbol', 'shape', 'type', 'value'])

Context = collections.namedtuple(
    'Context', ['ast', 'symbol_table'])


# context methods
def create_context(ast=None, symbol_table=None):
    """Initialize context

    eventually will be more complex method that takes in
    features/modules to enable/disable.
    """
    symbol_table = symbol_table or {}
    return Context(ast=ast, symbol_table=symbol_table)


# context node methods
def is_array(context):
    return context.ast.symbol == (NodeSymbol.ARRAY,)


def is_operation(context):
    return context.ast.symbol[0] not in {
        NodeSymbol.ARRAY, NodeSymbol.INDEX,
        NodeSymbol.INITIALIZE, NodeSymbol.ERROR,
        NodeSymbol.BLOCK,
        NodeSymbol.FUNCTION, NodeSymbol.LOOP, NodeSymbol.CONDITION}


def is_unary_operation(context):
    return is_operation(context) and len(context.ast.child) == 1


def is_binary_operation(context):
    return is_operation(context) and len(context.ast.child) == 2


def select_node(context, selection):
    """Select a nested child node from a context

    context: Context
      MOA context
    selection: List[int]
      list of integers to select nested child node
    """
    node = context.ast
    for index in selection:
        node = node.child[index]

    return Context(ast=node, symbol_table=context.symbol_table)


def replace_node(context, replacement_node, selection):
    """Replace a nested child node from a context with node

    context: Context
      MOA context
    selection: List[int]
      list of integers to select nested child node
    """
    stack = []

    node = context.ast
    for index in selection:
        stack.append((node, index))
        node = node.child[index]

    node = replacement_node
    for stack_node, index in reversed(stack):
        node = Node(symbol=stack_node.symbol, shape=stack_node.shape, attrib=stack_node.attrib, child=replace_tuple(stack_node.child, node, index))
    return Context(ast=node, symbol_table=context.symbol_table)


# symbol table methods
def add_symbol(context, name, symbol, shape, type, value):
    symbol_table = context.symbol_table
    if name in symbol_table and symbol_table[name] != (symbol, shape, type, value):
        raise MOAException(f'attempted to add to symbol table different symbol with same name "{name}" {symbol_table[name]} != {SymbolNode(symbol, shape, value)}')

    # idempotency makes debugging way easier dict(str: tuple)
    # deep copy not necessary
    symbol_table_copy = copy.copy(symbol_table)
    symbol_table_copy[name] = SymbolNode(symbol, shape, type, value)
    return Context(ast=context.ast, symbol_table=symbol_table_copy)


def generate_unique_array_name(context):
    return f'_a{len(context.symbol_table)}'


def generate_unique_index_name(context):
    return f'_i{len(context.symbol_table)}'


# tuple methods
def replace_tuple(value, replacement_element, index):
    return value[:index] + (replacement_element,) + value[index+1:]


def has_symbolic_elements(elements):
    return any(is_symbolic_element(element) for element in elements)


def is_symbolic_element(element):
    return isinstance(element, tuple)


## replacement methods
def node_traversal(context, replacement_function, traversal, max_iterations=100):
    if traversal == 'pre':
        for iteration in max_iterations:
            replacement_context = replacement_function(context)
            if replacement_context is None:
                break
            context = replacement_context
        else:
            raise MOAReplacementError(f'reduction failed to complete in max_iterations')

    for index in range(len(context.ast.child)):
        child_context = select_context_node(context, (index,))
        replacement_child_context = node_traversal(child_context, replacement_function, traversal)
        context = replace_context_node(context, replacement_child_context, (index,))

    if traversal == 'post':
        return replacement_function(context)

    return context
