import itertools

try:
    import graphviz
except ImportError as e:
    graphviz = None


from .ast import (
    MOANodeTypes,
    is_array, is_unary_operation, is_binary_operation
)


_NODE_LABEL_MAP = {
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


def visualize_ast(tree, comment='MOA AST', with_attrs=True):
    if graphviz is None:
        raise ImportError('The graphviz package is required to draw expressions')

    dot = graphviz.Digraph(comment=comment)
    counter = itertools.count()
    default_node_attr = dict(color='black', fillcolor='white', fontcolor='black')

    def _label_node(dot, node):
        unique_id = str(next(counter))

        if is_array(node):
            node_label = f"Array {node.name}"
            shape = 'box'
        else: # operation
            node_label = _NODE_LABEL_MAP[node.node_type]
            shape = 'ellipse'

        if node.shape:
            shape_label = '&lt;' + ', '.join(str(_) for _ in node.shape) + '&gt;'
            node_description = f'''<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
              <TR><TD>{node_label}</TD></TR>
              <TR><TD>ρ: {shape_label}</TD></TR>
            </TABLE>>'''
        else:
            node_description = node_label
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
