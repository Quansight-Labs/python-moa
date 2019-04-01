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
    replacement_shape:
      new shape to give for nested node
    selection: List[int]
      list of integers to select nested child node
    """
    def _replace_shape(node):
        return Node(symbol=node.symbol, shape=replacement_shape, attrib=node.attrib, child=node.child)

    return replace_node_by_function(context, _replace_shape, selection)


def replace_node_attributes(context, replacement_attributes, selection=()):
    """Replace a nested child node attributes with new attributes

    context: Context
      MOA context
    replacement_attributes:
      new attributes to give for nested node
    selection: List[int]
      list of integers to select nested child node
    """
    def _replace_attributes(node):
        return Node(symbol=node.symbol, shape=node.shape, attrib=replacement_attributes, child=node.child)

    return replace_node_by_function(context, _replace_attributes, selection)


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


def referenced_node_symbols(context):
    visited_symbols = set()

    def _visit_node(context):
        if context.ast.shape is not None:
            raise ValueError('currently naively assumes this is performed before shape analysis')

        if is_array(context):
            visited_symbols.add(context.ast.attrib[0])

            node_symbol = select_array_node_symbol(context)
            if node_symbol.shape:
                for element in node_symbol.shape:
                    if is_symbolic_element(element):
                        visited_symbols.add(element.attrib[0])

            if node_symbol.value:
                for element in node_symbol.value:
                    if is_symbolic_element(element):
                        visited_symbols.add(element.attrib[0])
        return context

    node_traversal(context, _visit_node, traversal='postorder')
    return visited_symbols


def rename_node_symbols(context, symbol_mapping):
    def _rename_symbols(context):
        if is_array(context):
            return replace_node_attributes(context, (symbol_mapping[context.ast.attrib[0]],))
        return context

    context = node_traversal(context, _rename_symbols, traversal='postorder')
    return context.ast


def rename_symbol_table_symbols(symbol_table, symbol_mapping):
    new_symbol_table = {}
    for old_name, new_name in symbol_mapping.items():
        if old_name in symbol_table:
            new_symbol_table[new_name] = symbol_table[old_name]

    # rename symbols within SymbolNode
    for name, node_symbol in new_symbol_table.items():
        shape = None
        if node_symbol.shape is not None:
            shape = ()
            for element in node_symbol.shape:
                if is_symbolic_element(element):
                    shape = shape + (Node(element.symbol, element.shape, (symbol_mapping[element.attrib[0]],), ()),)
                else:
                    shape = shape + (element,)

        value = None
        if node_symbol.value is not None:
            value = ()
            for element in node_symbol.value:
                if is_symbolic_element(element):
                    value = value + (Node(element.symbol, element.shape, (symbol_mapping[element.attrib[0]],), ()),)
                else:
                    value = value + (element,)
        new_symbol_table[name] = SymbolNode(node_symbol.symbol, shape, node_symbol.type, value)
    return new_symbol_table


# joining symbolic tables
def join_symbol_tables(left_context, right_context):
    """Join two symbol tables together which requires rewriting both trees

    TODO: This function is ugly and could be simplified/broken into parts. It is needed by the array frontend.

    """
    counter = itertools.count()

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
    visited_symbols = referenced_node_symbols(left_context)
    left_symbol_mapping = _symbol_mapping(visited_symbols)

    visited_symbols = referenced_node_symbols(right_context)
    right_symbol_mapping = _symbol_mapping(visited_symbols)

    # check that user defined symbols match in both tables
    for symbol in (left_symbol_mapping.keys() & right_symbol_mapping.keys()):
        if not symbol.startswith('_') and left_context.symbol_table[symbol] != right_context.symbol_table[symbol]:
            raise ValueError(f'user defined symbols must match "{symbol}" {left_context.symbol_table[symbol]} != {right_context.symbol_table[symbol]}')

    # rename symbols in tree
    new_left_context = create_context(
        ast=rename_node_symbols(left_context, left_symbol_mapping),
        symbol_table=rename_symbol_table_symbols(left_context.symbol_table, left_symbol_mapping))

    new_right_context = create_context(
        ast=rename_node_symbols(right_context, right_symbol_mapping),
        symbol_table=rename_symbol_table_symbols(right_context.symbol_table, right_symbol_mapping))

    new_symbol_table = {**new_left_context.symbol_table, **new_right_context.symbol_table}

    return new_symbol_table, new_left_context, new_right_context


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
