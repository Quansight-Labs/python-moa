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


def print_ast(node, vector_value=True):
    def _node_label(node):
        node_label = _NODE_LABEL_MAP[node.node_type]
        if node.shape:
            node_label += " <" + " ".join(str(_) for _ in node.shape) + ">"
        if is_vector(node) and node.value and vector_value:
            node_label += ': ' + " (" + " ".join(str(_) for _ in node.value) + ")"
        return node_label

    def _print_node(node, prefix=""):
        if is_unary_operation(node):
            print(prefix + "└──", _node_label(node.right_node))
            _print_node(node.right_node, prefix + "    ")
        elif is_binary_operation(node):
            print(prefix + "├──", _node_label(node.left_node))
            _print_node(node.left_node,  prefix + "│   ")
            print(prefix + "└──", _node_label(node.right_node))
            _print_node(node.right_node, prefix + "    ")

    print(_node_label(node))
    _print_node(node)



def visualize_ast(tree, comment='MOA AST', with_attrs=True):
    if graphviz is None:
        raise ImportError('The graphviz package is required to draw expressions')

    dot = graphviz.Digraph(comment=comment)
    counter = itertools.count()
    default_node_attr = dict(color='black', fillcolor='white', fontcolor='black')

    def _label_node(dot, node):
        unique_id = str(next(counter))

        labels = []
        if is_array(node):
            labels.append(f"Array {node.name}")
            shape = 'box'
        else: # operation
            labels.append(_NODE_LABEL_MAP[node.node_type])
            shape = 'ellipse'

        if node.shape:
            labels.append('ρ: &lt;' + ', '.join(str(_) for _ in node.shape) + '&gt;')
        if is_vector(node) and node.value:
            labels.append(" (" + ", ".join(str(_) for _ in node.value) + ")")

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

    def _visualize_node(dot, node):
        node_id = _label_node(dot, node)

        if is_unary_operation(node):
            right_node_id = _visualize_node(dot, node.right_node)
            dot.edge(node_id, right_node_id)
        elif is_binary_operation(node):
            left_node_id = _visualize_node(dot, node.left_node)
            dot.edge(node_id, left_node_id)
            right_node_id = _visualize_node(dot, node.right_node)
            dot.edge(node_id, right_node_id)

        return node_id

    _visualize_node(dot, tree)
    return dot
