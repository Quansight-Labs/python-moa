import enum
import collections
import copy
import itertools

from .exception import MOAException


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
def is_array(context, selection=()):
    context = select_node(context, selection)
    return context.ast.symbol == (NodeSymbol.ARRAY,)


def is_operation(context, selection=()):
    context = select_node(context, selection)
    return context.ast.symbol[0] not in {
        NodeSymbol.ARRAY, NodeSymbol.INDEX,
        NodeSymbol.INITIALIZE, NodeSymbol.ERROR,
        NodeSymbol.BLOCK,
        NodeSymbol.FUNCTION, NodeSymbol.LOOP, NodeSymbol.CONDITION}


def is_unary_operation(context, selection=()):
    context = select_node(context, selection)
    return is_operation(context) and len(context.ast.child) == 1


def is_binary_operation(context, selection=()):
    context = select_node(context, selection)
    return is_operation(context) and len(context.ast.child) == 2


def num_node_children(context, selection=()):
    context = select_node(context, selection)
    return len(context.ast.child)


def select_node(context, selection=()):
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


def select_node_shape(context, selection=()):
    """Select a nested child node shape from a context
    """
    return select_node(context, selection).ast.shape


def replace_node_by_function(context, replacement_function, selection=()):
    """Replace a nested node shape with new node determined from replacement_function

    context: Context
      MOA context
    replacement_function: function
      function that takes in node and returns new node
    selection: List[int]
      list of integers to select nested child node
    """
    stack = []

    node = context.ast
    for index in selection:
        stack.append((node, index))
        node = node.child[index]

    node = replacement_function(node)

    for stack_node, index in reversed(stack):
        node = Node(symbol=stack_node.symbol, shape=stack_node.shape, attrib=stack_node.attrib, child=replace_tuple(stack_node.child, node, index))
    return Context(ast=node, symbol_table=context.symbol_table)


def replace_node(context, replacement_node, selection=()):
    """Replace a nested child node from a context with node

    context: Context
      MOA context
    replacement_node: tuple
      replacement node to insert at child node
    selection: List[int]
      list of integers to select nested child node
    """
    def _replace_node(node):
        return replacement_node

    return replace_node_by_function(context, _replace_node, selection)


def replace_node_shape(context, replacement_shape, selection=()):
    """Replace a nested child node shape with new shape

    context: Context
      MOA context
    selection: List[int]
      list of integers to select nested child node
    """
    def _replace_shape(node):
        return Node(symbol=node.symbol, shape=replacement_shape, attrib=node.attrib, child=node.child)

    return replace_node_by_function(context, _replace_shape, selection)


# symbol table methods
def add_symbol(context, name, symbol, shape, type, value):
    symbol_table = context.symbol_table
    if name in symbol_table and symbol_table[name] != (symbol, shape, type, value):
        raise MOAException(f'attempted to add to symbol table different symbol with same name "{name}" {symbol_table[name]} != {SymbolNode(symbol, shape, type, value)}')

    # idempotency makes debugging way easier dict(str: tuple)
    # deep copy not necessary
    symbol_table_copy = copy.copy(symbol_table)
    symbol_table_copy[name] = SymbolNode(symbol, shape, type, value)
    return Context(ast=context.ast, symbol_table=symbol_table_copy)


def select_array_node_symbol(context, selection=()):
    context = select_node(context, selection)
    return context.symbol_table[context.ast.attrib[0]]


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
class MOAReplacementError(MOAException):
    pass


def node_traversal(context, replacement_function, traversal, max_iterations=range(100)):
    if traversal == 'preorder':
        for iteration in max_iterations:
            replacement_context = replacement_function(context)
            if replacement_context is None:
                break
            context = replacement_context
        else:
            raise MOAReplacementError(f'reduction failed to complete in max_iterations')

    for index in range(num_node_children(context)):
        child_context = select_node(context, (index,))
        replacement_child_context = node_traversal(child_context, replacement_function, traversal, max_iterations)
        context = replace_node(context, replacement_child_context.ast, (index,))
        context = Context(ast=context.ast, symbol_table=replacement_child_context.symbol_table)

    if traversal == 'postorder':
        return replacement_function(context)

    return context
