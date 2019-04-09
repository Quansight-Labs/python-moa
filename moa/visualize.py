import itertools

try:
    import graphviz
except ImportError as e:
    graphviz = None

from . import ast, backend

_NODE_LABEL_MAP = {
    #Symbols
    (ast.NodeSymbol.ARRAY,): "Array",
    # Control
    (ast.NodeSymbol.FUNCTION,): "function",
    (ast.NodeSymbol.CONDITION,): "condition",
    (ast.NodeSymbol.LOOP,): "loop",
    (ast.NodeSymbol.INITIALIZE,): 'initialize',
    (ast.NodeSymbol.ERROR,): 'error',
    (ast.NodeSymbol.BLOCK,): 'block',
    # Unary
    (ast.NodeSymbol.IOTA,): "iota(ι)",
    (ast.NodeSymbol.DIM,): "dim(δ)",
    (ast.NodeSymbol.TAU,): "tau(τ)",
    (ast.NodeSymbol.SHAPE,): "shape(ρ)",
    (ast.NodeSymbol.RAV,): "rav",
    (ast.NodeSymbol.TRANSPOSE,): "transpose(Ø)",
    (ast.NodeSymbol.TRANSPOSEV,): "transpose(Ø)",
    (ast.NodeSymbol.REDUCE, ast.NodeSymbol.PLUS): 'reduce (+)',
    (ast.NodeSymbol.REDUCE, ast.NodeSymbol.MINUS): 'reduce (-)',
    (ast.NodeSymbol.REDUCE, ast.NodeSymbol.TIMES): 'reduce (*)',
    (ast.NodeSymbol.REDUCE, ast.NodeSymbol.DIVIDE): 'reduce (/)',
    # Binary
    (ast.NodeSymbol.ASSIGN,): 'assign',
    (ast.NodeSymbol.PLUS,): "+",
    (ast.NodeSymbol.MINUS,): "-",
    (ast.NodeSymbol.TIMES,): "*",
    (ast.NodeSymbol.DIVIDE,): "/",
    (ast.NodeSymbol.PSI,): "psi(Ψ)",
    (ast.NodeSymbol.DIM,): "dim(δ)",
    (ast.NodeSymbol.TAU,): "tau(τ)",
    (ast.NodeSymbol.TAKE,): "take(▵)",
    (ast.NodeSymbol.DROP,): "drop(▿)",
    (ast.NodeSymbol.CAT,): "cat(++)",
    (ast.NodeSymbol.DOT, ast.NodeSymbol.PLUS): 'outer (+)',
    (ast.NodeSymbol.DOT, ast.NodeSymbol.MINUS): 'outer (-)',
    (ast.NodeSymbol.DOT, ast.NodeSymbol.TIMES): 'outer (*)',
    (ast.NodeSymbol.DOT, ast.NodeSymbol.DIVIDE): 'outer (/)',
    # messy representation
    (ast.NodeSymbol.DOT, ast.NodeSymbol.PLUS  , ast.NodeSymbol.PLUS): 'inner (+,+)',
    (ast.NodeSymbol.DOT, ast.NodeSymbol.MINUS , ast.NodeSymbol.PLUS): 'inner (-,+)',
    (ast.NodeSymbol.DOT, ast.NodeSymbol.TIMES , ast.NodeSymbol.PLUS): 'inner (*,+)',
    (ast.NodeSymbol.DOT, ast.NodeSymbol.DIVIDE, ast.NodeSymbol.PLUS): 'inner (/,+)',
    (ast.NodeSymbol.DOT, ast.NodeSymbol.PLUS  , ast.NodeSymbol.MINUS): 'inner (+,-)',
    (ast.NodeSymbol.DOT, ast.NodeSymbol.MINUS , ast.NodeSymbol.MINUS): 'inner (-,-)',
    (ast.NodeSymbol.DOT, ast.NodeSymbol.TIMES , ast.NodeSymbol.MINUS): 'inner (*,-)',
    (ast.NodeSymbol.DOT, ast.NodeSymbol.DIVIDE, ast.NodeSymbol.MINUS): 'inner (/,-)',
    (ast.NodeSymbol.DOT, ast.NodeSymbol.PLUS  , ast.NodeSymbol.TIMES): 'inner (+,*)',
    (ast.NodeSymbol.DOT, ast.NodeSymbol.MINUS , ast.NodeSymbol.TIMES): 'inner (-,*)',
    (ast.NodeSymbol.DOT, ast.NodeSymbol.TIMES , ast.NodeSymbol.TIMES): 'inner (*,*)',
    (ast.NodeSymbol.DOT, ast.NodeSymbol.DIVIDE, ast.NodeSymbol.TIMES): 'inner (/,*)',
    (ast.NodeSymbol.DOT, ast.NodeSymbol.PLUS  , ast.NodeSymbol.DIVIDE): 'inner (+,/)',
    (ast.NodeSymbol.DOT, ast.NodeSymbol.MINUS , ast.NodeSymbol.DIVIDE): 'inner (-,/)',
    (ast.NodeSymbol.DOT, ast.NodeSymbol.TIMES , ast.NodeSymbol.DIVIDE): 'inner (*,/)',
    (ast.NodeSymbol.DOT, ast.NodeSymbol.DIVIDE, ast.NodeSymbol.DIVIDE): 'inner (/,/)',
}


def stringify_elements(context, elements):
    strings = []
    for element in elements:
        if ast.is_symbolic_element(element):
            element_context = ast.create_context(ast=element, symbol_table=context.symbol_table)
            strings.append(backend.generate_python_source(element_context, materialize_scalars=True))
        else:
            strings.append(str(element))
    return strings


def symbolic_tuple_string(context, shape, start='(', end=')'):
    return start + " ".join(stringify_elements(context, shape)) + end


def escape_dot_string(string):
    return string.replace('<', '&lt;').replace('>', '&gt;')


def _node_label(context):
    node_label = {
        'name': _NODE_LABEL_MAP[context.ast.symbol],
    }
    # name
    if ast.is_array(context):
        node_label['name'] += f' {context.ast.attrib[0]}'

    # shape
    if ast.is_array(context):
        shape = ast.select_array_node_symbol(context).shape
        if shape is not None:
            node_label['shape'] = symbolic_tuple_string(context, shape, start='<', end='>')
    elif context.ast.shape is not None:
        node_label['shape'] = symbolic_tuple_string(context, context.ast.shape, start='<', end='>')

    # value
    if ast.is_array(context):
        value = ast.select_array_node_symbol(context).value
        if value is not None:
            node_label['value'] = symbolic_tuple_string(context, value, start='(', end=')')
    elif context.ast.symbol == (ast.NodeSymbol.ERROR,):
        message = context.ast.attrib[0]
        if message is not None:
            node_label['value'] = message
    elif context.ast.symbol in {(ast.NodeSymbol.LOOP,), (ast.NodeSymbol.INITIALIZE,)}:
        symbol_node = context.ast.attrib[0]
        if symbol_node is not None:
            node_label['value'] = symbol_node
    elif context.ast.symbol == (ast.NodeSymbol.CONDITION,):
        condition_context = ast.select_node(context, (0,))
        node_label['value'] = backend.generate_python_source(condition_context, materialize_scalars=True)
    elif context.ast.symbol == (ast.NodeSymbol.FUNCTION,):
        arguments, result = context.ast.attrib[0], context.ast.attrib[1]
        if arguments is not None and result is not None:
            node_label['value'] = symbolic_tuple_string(context, arguments, start='(', end=')') + ' -> ' + result
    elif context.ast.symbol[0] == ast.NodeSymbol.REDUCE:
        if context.ast.attrib:
            node_label['value'] = context.ast.attrib[0]

    return node_label


def print_ast(context, vector_value=True):
    def _print_node_label(context):
        node_label = _node_label(context)
        label = '{name}'
        if 'shape' in node_label:
            label += ': {shape}'
        if 'value' in node_label:
            label += ' {value}'
        return label.format(**node_label)

    def _print_node(context, prefix=""):
        if ast.num_node_children(context) == 0:
            return

        # no need to traverse condition node since converted to python source
        if context.ast.symbol == (ast.NodeSymbol.CONDITION,):
            child_context = ast.select_node(context, (1,))
            print(prefix + "└──", _print_node_label(child_context))
            _print_node(child_context, prefix + "    ")
            return

        for i in range(ast.num_node_children(context) - 1):
            child_context = ast.select_node(context, (i,))
            print(prefix + "├──", _print_node_label(child_context))
            _print_node(child_context,  prefix + "│   ")

        child_context = ast.select_node(context, (-1,))
        print(prefix + "└──", _print_node_label(child_context))
        _print_node(child_context, prefix + "    ")

    print(_print_node_label(context))
    _print_node(context)


def visualize_ast(context, comment='MOA AST', with_attrs=True, vector_value=True):
    if graphviz is None:
        raise ImportError('The graphviz package is required to draw expressions')

    dot = graphviz.Digraph(comment=comment)
    counter = itertools.count()
    default_node_attr = dict(color='black', fillcolor='white', fontcolor='black')

    def _visualize_node_label(dot, context):
        unique_id = str(next(counter))

        node_label = _node_label(context)
        for key, value in node_label.items():
            node_label[key] = escape_dot_string(value)

        labels = []
        if ast.is_array(context):
            shape = 'box'
        else: # operation
            shape = 'ellipse'

        if len(node_label) > 1:
            labels.append('<TR><TD>{}</TD></TR>'.format(node_label['name']))
            if 'shape' in node_label:
                labels.append('\n<TR><TD>{}</TD></TR>'.format(node_label['shape']))
            if 'value' in node_label:
                labels.append('\n<TR><TD>{}</TD></TR>'.format(node_label['value']))

            node_description = f'''<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
               {''.join(labels)}
            </TABLE>>'''
        else:
            node_description = node_label['name']

        dot.node(unique_id, label=node_description, shape=shape)
        return unique_id

    def _visualize_node(dot, context):
        node_id = _visualize_node_label(dot, context)

        # no need to traverse condition node since converted to python source
        if context.ast.symbol == (ast.NodeSymbol.CONDITION,):
            child_context = ast.select_node(context, (1,))
            child_node_id = _visualize_node(dot, child_context)
            dot.edge(node_id, child_node_id)
            return node_id

        for i in range(ast.num_node_children(context)):
            child_context = ast.select_node(context, (i,))
            child_node_id = _visualize_node(dot, child_context)
            dot.edge(node_id, child_node_id)

        return node_id

    _visualize_node(dot, context)
    return dot
