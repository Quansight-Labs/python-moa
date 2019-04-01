import ast
import astunparse

from ..ast import (
    create_context,
    select_node,
    NodeSymbol, node_traversal,
    has_symbolic_elements, is_symbolic_element,
    select_array_node_symbol,
)


def python_backend(context):
    """Convert MOA reduced AST to python source code

    """
    context = node_traversal(context, _ast_replacement, traversal='postorder')
    return context.ast


def generate_python_source(context, materialize_scalars=False, use_numba=False):
    python_ast = python_backend(context)

    class ReplaceScalars(ast.NodeTransformer):
        def visit_Name(self, node):
            symbol_node = context.symbol_table.get(node.id)
            if symbol_node is not None and symbol_node.symbol != NodeSymbol.INDEX and (symbol_node.shape == () and symbol_node.value is not None and not has_symbolic_elements(symbol_node.value)):
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

    class ReplaceWithNumba(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            node.decorator_list = [ast.Name(id='numba.jit', ctx=ast.Load())]
            self.generic_visit(node)
            return node

        def visit_Name(self, node):
            if node.id == 'Array':
                node.id = 'numpy.zeros'
            return node

    if materialize_scalars:
        python_ast = ReplaceScalars().visit(python_ast)
        python_ast = ReplaceShapeIndex().visit(python_ast)
        if use_numba:
            python_ast = ReplaceWithNumba().visit(python_ast)

    return astunparse.unparse(python_ast)[:-1] # remove newline


def _ast_replacement(context):
    _NODE_AST_MAP = {
        (NodeSymbol.ARRAY,): _ast_array,
        (NodeSymbol.INDEX,): _ast_array,
        (NodeSymbol.FUNCTION,): _ast_function,
        (NodeSymbol.CONDITION,): _ast_condition,
        (NodeSymbol.BLOCK,): _ast_block,
        (NodeSymbol.ERROR,): _ast_error,
        (NodeSymbol.ASSIGN,): _ast_assignment,
        (NodeSymbol.INITIALIZE,): _ast_initialize,
        (NodeSymbol.LOOP,): _ast_loop,
        (NodeSymbol.SHAPE,): _ast_shape,
        (NodeSymbol.DIM,): _ast_dimension,
        (NodeSymbol.PSI,): _ast_psi,
        (NodeSymbol.PLUS,): _ast_plus_minus_times_divide,
        (NodeSymbol.MINUS,): _ast_plus_minus_times_divide,
        (NodeSymbol.TIMES,): _ast_plus_minus_times_divide,
        (NodeSymbol.DIVIDE,): _ast_plus_minus_times_divide,
        (NodeSymbol.EQUAL,): _ast_comparison_operations,
        (NodeSymbol.NOTEQUAL,): _ast_comparison_operations,
        (NodeSymbol.LESSTHAN,): _ast_comparison_operations,
        (NodeSymbol.LESSTHANEQUAL,): _ast_comparison_operations,
        (NodeSymbol.GREATERTHAN,): _ast_comparison_operations,
        (NodeSymbol.GREATERTHANEQUAL,): _ast_comparison_operations,
        (NodeSymbol.AND,): _ast_boolean_binary_operations,
        (NodeSymbol.OR,): _ast_boolean_binary_operations,
        (NodeSymbol.NOT,): _ast_boolean_unary_operations,
    }
    return _NODE_AST_MAP[context.ast.symbol](context)


# helper
def _ast_element(context, element):
    if is_symbolic_element(element):
        return _ast_replacement(create_context(ast=element, symbol_table=context.symbol_table)).ast
    else:
        return ast.Num(n=element)


def _ast_tuple(context, value):
    return ast.Tuple(elts=[_ast_element(context, element) for element in value])


# python elements
def _ast_psi(context):
    left_symbol_node = select_node(context, (0,)).ast.id
    return create_context(
        ast=ast.Subscript(value=select_node(context, (1,)).ast,
                          slice=ast.Index(value=_ast_tuple(context, context.symbol_table[left_symbol_node].value)),
                          ctx=ast.Load()),
        symbol_table=context.symbol_table)


def _ast_array(context):
    return create_context(
        ast=ast.Name(id=context.ast.attrib[0], ctx=ast.Load()),
        symbol_table=context.symbol_table)


def _ast_function(context):
    return create_context(
        ast=ast.FunctionDef(name='f',
                            args=ast.arguments(args=[ast.arg(arg=arg, annotation=None) for arg in context.ast.attrib[0]],
                                               vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
                            body=[ast.Expr(value=child_node) for child_node in context.ast.child] + [ast.Return(value=ast.Name(id=context.ast.attrib[1]))],
                            decorator_list=[],
                            returns=None),
        symbol_table=context.symbol_table)


def _ast_assignment(context):
    return create_context(
        ast=ast.Assign(targets=[select_node(context, (0,)).ast], value=select_node(context, (1,)).ast),
        symbol_table=context.symbol_table)


def _ast_loop(context):
    node_symbol = select_array_node_symbol(context)
    return create_context(
        ast=ast.For(target=ast.Name(id=context.ast.attrib[0]),
                iter=ast.Call(func=ast.Name(id='range'),
                              args=[
                                  _ast_element(context, node_symbol.value[0]),
                                  _ast_element(context, node_symbol.value[1]),
                                  _ast_element(context, node_symbol.value[2])
                              ], keywords=[]), body=select_node(context, (0,)).ast, orelse=[]),
        symbol_table=context.symbol_table)


def _ast_error(context):
    return create_context(
        ast=ast.Raise(exc=ast.Call(func=ast.Name(id='Exception'), args=[ast.Str(s=context.ast.attrib[0])], keywords=[]), cause=None),
        symbol_table=context.symbol_table)


def _ast_initialize(context):
    return create_context(
        ast=ast.Assign(targets=[ast.Name(id=context.ast.attrib[0])],
                       value=ast.Call(func=ast.Name(id='Array'),
                                      args=[_ast_tuple(context, context.ast.shape)],
                                      keywords=[])),
        symbol_table=context.symbol_table)


def _ast_shape(context):
    return create_context(
        ast=ast.Attribute(value=select_node(context, (0,)).ast, attr='shape', ctx=ast.Load()),
        symbol_table=context.symbol_table)


def _ast_dimension(context):
    return create_context(
        ast=ast.Call(func=ast.Name(id='len', ctx=ast.Load()), args=[_ast_shape(context).ast], keywords=[]),
        symbol_table=context.symbol_table)


def _ast_plus_minus_times_divide(context):
    binop_map = {
        (NodeSymbol.PLUS,): ast.Add,
        (NodeSymbol.MINUS,): ast.Sub,
        (NodeSymbol.TIMES,): ast.Mult,
        (NodeSymbol.DIVIDE,): ast.Div,
    }
    return create_context(
        ast=ast.BinOp(left=select_node(context, (0,)).ast, op=binop_map[context.ast.symbol](), right=select_node(context, (1,)).ast),
        symbol_table=context.symbol_table)


def _ast_block(context):
    return create_context(
        ast=[ast.Expr(value=child_node) for child_node in context.ast.child],
        symbol_table=context.symbol_table)


def _ast_condition(context):
    return create_context(
        ast=ast.If(test=select_node(context, (0,)).ast, body=select_node(context, (1,)).ast, orelse=[]),
        symbol_table=context.symbol_table)


def _ast_comparison_operations(context):
    comparision_map = {
        (NodeSymbol.EQUAL,): ast.Eq,
        (NodeSymbol.NOTEQUAL,): ast.NotEq,
        (NodeSymbol.LESSTHAN,): ast.Lt,
        (NodeSymbol.LESSTHANEQUAL,): ast.LtE,
        (NodeSymbol.GREATERTHAN,): ast.Gt,
        (NodeSymbol.GREATERTHANEQUAL,): ast.GtE,
    }
    return create_context(
        ast=ast.Compare(left=select_node(context, (0,)).ast,
                        ops=[comparision_map[context.ast.symbol]()],
                        comparators=[select_node(context, (1,)).ast]),
        symbol_table=context.symbol_table)


def _ast_boolean_binary_operations(context):
    boolean_map = {
        (NodeSymbol.AND,): ast.And,
        (NodeSymbol.OR,): ast.Or
    }
    return create_context(
        ast=ast.BoolOp(op=boolean_map[context.ast.symbol](), values=[
            select_node(context, (0,)).ast, select_node(context, (1,)).ast]),
        symbol_table=context.symbol_table)


def _ast_boolean_unary_operations(context):
    boolean_map = {
        (NodeSymbol.NOT,): ast.Not
    }
    return create_context(
        ast=ast.UnaryOp(op=boolean_map[context.ast.symbol](), operand=select_node(context, (0,)).ast),
        symbol_table=context.symbol_table)
