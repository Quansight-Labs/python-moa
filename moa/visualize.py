import itertools

try:
    import graphviz
except ImportError as e:
    graphviz = None


from .ast import (
    MOANodeTypes,
    is_array, is_unary_operation, is_binary_operation
)
from .shape import is_vector


_NODE_LABEL_MAP = {
    MOANodeTypes.ARRAY: "Array",
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


def print_ast(symbol_table, node, vector_value=True):
    def _node_label(symbol_table, node):
        node_label = _NODE_LABEL_MAP[node.node_type]
        if is_array(node): # cannot assume that shape traversal has already happened
            symbol_node = symbol_table[node.symbol_node]
            node_label += f' {node.symbol_node}'
            if symbol_node.shape:
                node_label += " <" + " ".join(str(_) for _ in symbol_node.shape) + ">"
            if is_vector(symbol_table, node) and symbol_node.value and vector_value:
                node_label += ': ' + " (" + " ".join(str(_) for _ in symbol_node.value) + ")"
        else:
            if node.shape:
                node_label += " <" + " ".join(str(_) for _ in node.shape) + ">"
        return node_label

    def _print_node(symbol_table, node, prefix=""):
        if is_unary_operation(node):
            print(prefix + "└──", _node_label(symbol_table, node.right_node))
            _print_node(symbol_table, node.right_node, prefix + "    ")
        elif is_binary_operation(node):
            print(prefix + "├──", _node_label(symbol_table, node.left_node))
            _print_node(symbol_table, node.left_node,  prefix + "│   ")
            print(prefix + "└──", _node_label(symbol_table, node.right_node))
            _print_node(symbol_table, node.right_node, prefix + "    ")

    print(_node_label(symbol_table, node))
    _print_node(symbol_table, node)


def visualize_ast(symbol_table, node, comment='MOA AST', with_attrs=True, vector_value=True):
    if graphviz is None:
        raise ImportError('The graphviz package is required to draw expressions')

    dot = graphviz.Digraph(comment=comment)
    counter = itertools.count()
    default_node_attr = dict(color='black', fillcolor='white', fontcolor='black')

    def _label_node(dot, symbol_table, node):
        unique_id = str(next(counter))

        labels = []
        if is_array(node):
            labels.append(f"Array {node.symbol_node}")
            shape = 'box'

            symbol_node = symbol_table[node.symbol_node]
            if symbol_node.shape:
                labels.append('ρ: &lt;' + ', '.join(str(_) for _ in symbol_node.shape) + '&gt;')
            if is_vector(symbol_table, node) and symbol_node.value and vector_value:
                labels.append(" (" + ", ".join(str(_) for _ in symbol_node.value) + ")")
        else: # operation
            labels.append(_NODE_LABEL_MAP[node.node_type])
            shape = 'ellipse'

            if node.shape:
                labels.append('ρ: &lt;' + ', '.join(str(_) for _ in node.shape) + '&gt;')

        labels_str = '\n'.join('<TR><TD>{}</TD></TR>'.format(_) for _ in labels)
        if len(labels) == 1:
            node_description = labels[0]
        else:
            node_description = f'''<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
              {labels_str}
            </TABLE>>'''

        dot.node(unique_id, label=node_description, shape=shape)
        return unique_id

    def _visualize_node(dot, symbol_table, node):
        node_id = _label_node(dot, symbol_table, node)

        if is_unary_operation(node):
            right_node_id = _visualize_node(dot, symbol_table, node.right_node)
            dot.edge(node_id, right_node_id)
        elif is_binary_operation(node):
            left_node_id = _visualize_node(dot, symbol_table, node.left_node)
            dot.edge(node_id, left_node_id)
            right_node_id = _visualize_node(dot, symbol_table, node.right_node)
            dot.edge(node_id, right_node_id)

        return node_id

    _visualize_node(dot, symbol_table, node)
    return dot
