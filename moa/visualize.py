import itertools

try:
    import graphviz
except ImportError as e:
    graphviz = None

from . import ast
# from .shape import is_vector
# from .backend import generate_python_source

_NODE_LABEL_MAP = {
    #Symbols
    (ast.NodeSymbol.ARRAY,): "Array",
    # Control
    (ast.NodeSymbol.FUNCTION,): "function",
    (ast.NodeSymbol.CONDITION,): "condition",
    (ast.NodeSymbol.LOOP,): "loop",
    (ast.NodeSymbol.INITIALIZE,): 'initialize',
    (ast.NodeSymbol.ERROR,): 'error',
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
}


def stringify_elements(symbol_table, elements):
    strings = []
    for element in elements:
        if is_symbolic_element(element):
            strings.append(generate_python_source(symbol_table, element, materialize_scalars=True))
        else:
            strings.append(str(element))
    return strings
    shape_str = '<'


def shape_string(symbol_table, shape):
    return "<" + " ".join(stringify_elements(symbol_table, shape)) + ">"


def value_string(symbol_table, value):
    return "(" + " ".join(stringify_elements(symbol_table, value)) + ")"


def escape_dot_string(string):
    return string.replace('<', '&lt;').replace('>', '&gt;')


def _node_label(context):
    node_label = {
        'name': _NODE_LABEL_MAP[context.ast.symbol],
    }
    # if is_array(node) and symbol_table[node.symbol_node].shape is not None: # cannot assume that shape traversal has already happened and shape is defined
    #     symbol_node = symbol_table[node.symbol_node]
    #     node_label['name'] += f' {node.symbol_node}'
    #     if symbol_node.shape:
    #         node_label['shape'] = shape_string(symbol_table, symbol_node.shape)
    #     if is_vector(symbol_table, node) and symbol_node.value:
    #         node_label['value'] = value_string(symbol_table, symbol_node.value)

    # elif node.node_type == MOANodeTypes.ERROR:
    #     node_label['value'] = node.message

    # elif node.node_type in {MOANodeTypes.LOOP, MOANodeTypes.INITIALIZE}:
    #     if node.shape:
    #         node_label['shape'] = shape_string(symbol_table, node.shape)
    #     node_label['value'] = node.symbol_node

    # elif node.node_type in {MOANodeTypes.CONDITION, MOANodeTypes.IF}:
    #     if node.shape:
    #         node_label['shape'] = shape_string(symbol_table, node.shape)
    #     node_label['value'] = generate_python_source(symbol_table, node.condition_node, materialize_scalars=True)

    # elif node.node_type == MOANodeTypes.FUNCTION:
    #     if node.shape:
    #         node_label['shape'] = shape_string(symbol_table, node.shape)
    #     node_label['value'] = value_string(symbol_table, node.arguments) + ' -> ' + node.result

    # elif isinstance(node.node_type, tuple) and node.node_type[0] == MOANodeTypes.REDUCE:
    #     if node.shape:
    #         node_label['shape'] = shape_string(symbol_table, node.shape)
    #     if node.symbol_node:
    #         node_label['value'] = node.symbol_node

    # else:
    #     if node.shape:
    #         node_label['shape'] = shape_string(symbol_table, node.shape)
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

        for i in range(ast.num_node_children(context)):
            child_context = ast.select_node(context, (i,))
            child_node_id = _visualize_node(dot, child_context)
            dot.edge(node_id, child_node_id)

        return node_id

    _visualize_node(dot, context)
    return dot
