import itertools

try:
    import graphviz
except ImportError as e:
    graphviz = None


from .ast import (
    MOANodeTypes,
    is_array, is_unary_operation, is_binary_operation
)
from .shape import is_vector, is_symbolic_element
from .backend import generate_python_source


_NODE_LABEL_MAP = {
    #Symbols
    MOANodeTypes.ARRAY: "Array",
    # Control
    MOANodeTypes.FUNCTION: "function",
    MOANodeTypes.CONDITION: "condition",
    MOANodeTypes.LOOP: "loop",
    MOANodeTypes.ASSIGN: 'assign',
    # Unary
    MOANodeTypes.PLUSRED: "+red",
    MOANodeTypes.MINUSRED: "-red",
    MOANodeTypes.TIMESRED: "*red",
    MOANodeTypes.DIVIDERED: "/red",
    MOANodeTypes.IOTA: "iota(ι)",
    MOANodeTypes.DIM: "dim(δ)",
    MOANodeTypes.TAU: "tau(τ)",
    MOANodeTypes.SHAPE: "shape(ρ)",
    MOANodeTypes.RAV: "rav",
    MOANodeTypes.TRANSPOSE: "transpose(Ø)",
    MOANodeTypes.TRANSPOSEV: "transpose(Ø)",
    # Binary
    MOANodeTypes.PLUS: "+",
    MOANodeTypes.MINUS: "-",
    MOANodeTypes.TIMES: "*",
    MOANodeTypes.DIVIDE: "/",
    MOANodeTypes.PSI: "psi(Ψ)",
    MOANodeTypes.DIM: "dim(δ)",
    MOANodeTypes.TAU: "tau(τ)",
    MOANodeTypes.TAKE: "take(▵)",
    MOANodeTypes.DROP: "drop(▿)",
    MOANodeTypes.CAT: "cat(++)",
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


def _node_label(symbol_table, node):
    node_label = {
        'name': _NODE_LABEL_MAP[node.node_type],
    }

    if is_array(node) and symbol_table[node.symbol_node].shape is not None: # cannot assume that shape traversal has already happened and shape is defined
        symbol_node = symbol_table[node.symbol_node]
        node_label['name'] += f' {node.symbol_node}'
        if symbol_node.shape:
            node_label['shape'] = shape_string(symbol_table, symbol_node.shape)
        if is_vector(symbol_table, node) and symbol_node.value:
            node_label['value'] = value_string(symbol_table, symbol_node.value)
    elif node.node_type == MOANodeTypes.CONDITION:
        if node.shape:
            node_label['shape'] = shape_string(symbol_table, node.shape)
        node_label['value'] = generate_python_source(symbol_table, node.condition_node, materialize_scalars=True)
    elif node.node_type == MOANodeTypes.FUNCTION:
        if node.shape:
            node_label['shape'] = None
        node_label['value'] = value_string(symbol_table, node.arguments)
    else:
        if node.shape:
            node_label['shape'] = shape_string(symbol_table, node.shape)
    return node_label


def print_ast(symbol_table, node, vector_value=True):
    def _print_node_label(symbol_table, node):
        node_label = _node_label(symbol_table, node)
        label = '{name}'
        if 'shape' in node_label:
            label += ': {shape}'
        if 'value' in node_label:
            label += ' {value}'
        return label.format(**node_label)

    def _print_node(symbol_table, node, prefix=""):
        if is_unary_operation(node):
            print(prefix + "└──", _print_node_label(symbol_table, node.right_node))
            _print_node(symbol_table, node.right_node, prefix + "    ")

        elif is_binary_operation(node):
            print(prefix + "├──", _print_node_label(symbol_table, node.left_node))
            _print_node(symbol_table, node.left_node,  prefix + "│   ")
            print(prefix + "└──", _print_node_label(symbol_table, node.right_node))
            _print_node(symbol_table, node.right_node, prefix + "    ")

        elif node.node_type == MOANodeTypes.CONDITION:
            print(prefix + "└──", _print_node_label(symbol_table, node.right_node))
            _print_node(symbol_table, node.right_node, prefix + "    ")

        elif node.node_type in {MOANodeTypes.FUNCTION, MOANodeTypes.LOOP}:
            for child_node in node.body[:-1]:
                print(prefix + "├──", _print_node_label(symbol_table, child_node))
                _print_node(symbol_table, child_node,  prefix + "│   ")
            print(prefix + "└──", _print_node_label(symbol_table, node.body[-1]))
            _print_node(symbol_table, node.body[-1], prefix + "    ")

    print(_print_node_label(symbol_table, node))
    _print_node(symbol_table, node)


def visualize_ast(symbol_table, node, comment='MOA AST', with_attrs=True, vector_value=True):
    if graphviz is None:
        raise ImportError('The graphviz package is required to draw expressions')

    dot = graphviz.Digraph(comment=comment)
    counter = itertools.count()
    default_node_attr = dict(color='black', fillcolor='white', fontcolor='black')

    def _visualize_node_label(dot, symbol_table, node):
        unique_id = str(next(counter))

        node_label = _node_label(symbol_table, node)
        for key, value in node_label.items():
            node_label[key] = escape_dot_string(value)

        labels = []
        if is_array(node):
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

    def _visualize_node(dot, symbol_table, node):
        node_id = _visualize_node_label(dot, symbol_table, node)

        if is_unary_operation(node) or node.node_type == MOANodeTypes.CONDITION:
            right_node_id = _visualize_node(dot, symbol_table, node.right_node)
            dot.edge(node_id, right_node_id)

        elif is_binary_operation(node) or node.node_type == MOANodeTypes.ASSIGN:
            left_node_id = _visualize_node(dot, symbol_table, node.left_node)
            dot.edge(node_id, left_node_id)
            right_node_id = _visualize_node(dot, symbol_table, node.right_node)
            dot.edge(node_id, right_node_id)

        elif node.node_type in {MOANodeTypes.FUNCTION, MOANodeTypes.LOOP}:
            for child_node in node.body:
                child_node_id = _visualize_node(dot, symbol_table, child_node)
                dot.edge(node_id, child_node_id)

        return node_id

    _visualize_node(dot, symbol_table, node)
    return dot
