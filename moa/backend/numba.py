from .python import python_backend


def generate_numba_source(symbol_table, tree, materialize_scalars=False):
    python_ast = python_backend(symbol_table, tree)

    class ReplaceScalars(ast.NodeTransformer):
        def visit_Name(self, node):
            symbol_node = symbol_table.get(node.id)
            if symbol_node is not None and symbol_node.node_type != MOANodeTypes.INDEX and (symbol_node.shape == () and symbol_node.value is not None and not has_symbolic_elements(symbol_node.value)):
                return ast.Num(symbol_node.value[0])
            return node

    # TODO: this will no longer be necissary with psi reduction
    class ReplaceShapeIndex(ast.NodeTransformer):
        def visit_Subscript(self, node):
            if isinstance(node.value, ast.Attribute) and node.value.attr == 'shape':
                return ast.Subscript(value=node.value,
                                     slice=ast.Index(value=node.slice.value.elts[0]),
                                     ctx=ast.Load())
            return node

    class ReplaceNumba(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            raise NotImplemenetedError()

        def visit_Name(self, node):
            if node.id == 'Array':
                raise NotImplemenetedError()

    if materialize_scalars:
        python_ast = ReplaceScalars().visit(python_ast)
        python_ast = ReplaceShapeIndex().visit(python_ast)
        python_ast = ReplaceNumba().visit(python_ast)

    return astunparse.unparse(python_ast)[:-1] # remove newline
