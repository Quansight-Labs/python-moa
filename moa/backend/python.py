import ast

from ..ast import MOANodeTypes


def export_backend_python(tree):
    return _NODE_AST_MAP[tree.node_type](tree)


def _ast_psi(node):
    indicies = []
    for i in node.left_node.value:
        if isinstance(i, int):
            indicies.append(ast.Num(n=i))
        elif isinstance(i, str):
            indicies.append(ast.Str(s=i))

    array = _ast_array(node.right_node)
    return ast.Subscript(value=array,
                         slice=ast.Index(value=ast.Tuple(elts=indicies, ctx=ast.Load())),
                         ctx=ast.Load())


def _ast_array(node):
    return ast.Name(id=node.name, ctx=ast.Load())


def _ast_plus(node):
    left_ast = _NODE_AST_MAP[node.left_node.node_type](node.left_node)
    right_ast = _NODE_AST_MAP[node.right_node.node_type](node.right_node)

    return ast.BinOp(left=left_ast, op=ast.Add(), right=right_ast)


_NODE_AST_MAP = {
    MOANodeTypes.ARRAY: _ast_array,
    MOANodeTypes.PSI: _ast_psi,
    MOANodeTypes.PLUS: _ast_plus
}
