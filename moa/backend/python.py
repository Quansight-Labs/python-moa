import ast
import astunparse

from ..ast import (
    MOANodeTypes, ArrayNode, postorder_replacement,
    has_symbolic_elements, is_symbolic_element
)


def python_backend(symbol_table, tree):
    """Convert MOA reduced AST to python source code

    """
    symbol_table, python_ast = postorder_replacement(symbol_table, tree, _ast_replacement)
    return python_ast


def generate_python_source(symbol_table, tree, materialize_scalars=False):
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

    if materialize_scalars:
        python_ast = ReplaceScalars().visit(python_ast)
        python_ast = ReplaceShapeIndex().visit(python_ast)

    return astunparse.unparse(python_ast)[:-1] # remove newline


def _ast_replacement(symbol_table, node):
    _NODE_AST_MAP = {
        MOANodeTypes.ARRAY: _ast_array,
        MOANodeTypes.INDEX: _ast_array,
        MOANodeTypes.FUNCTION: _ast_function,
        MOANodeTypes.CONDITION: _ast_condition,
        MOANodeTypes.IF: _ast_if,
        MOANodeTypes.ERROR: _ast_error,
        MOANodeTypes.ASSIGN: _ast_assignment,
        MOANodeTypes.INITIALIZE: _ast_initialize,
        MOANodeTypes.LOOP: _ast_loop,
        MOANodeTypes.SHAPE: _ast_shape,
        MOANodeTypes.DIM: _ast_dimension,
        MOANodeTypes.PSI: _ast_psi,
        MOANodeTypes.PLUS: _ast_plus_minus_times_divide,
        MOANodeTypes.MINUS: _ast_plus_minus_times_divide,
        MOANodeTypes.TIMES: _ast_plus_minus_times_divide,
        MOANodeTypes.DIVIDE: _ast_plus_minus_times_divide,
        MOANodeTypes.EQUAL: _ast_comparison_operations,
        MOANodeTypes.NOTEQUAL: _ast_comparison_operations,
        MOANodeTypes.LESSTHAN: _ast_comparison_operations,
        MOANodeTypes.LESSTHANEQUAL: _ast_comparison_operations,
        MOANodeTypes.GREATERTHAN: _ast_comparison_operations,
        MOANodeTypes.GREATERTHANEQUAL: _ast_comparison_operations,
        MOANodeTypes.AND: _ast_boolean_binary_operations,
        MOANodeTypes.OR: _ast_boolean_binary_operations,
        MOANodeTypes.NOT: _ast_boolean_unary_operations,
    }
    return _NODE_AST_MAP[node.node_type](symbol_table, node)


# helper
def _ast_element(symbol_table, element):
    if is_symbolic_element(element):
        _, symbolic_expression = _ast_replacement(symbol_table, element)
        return symbolic_expression
    else:
        return ast.Num(n=element)


def _ast_tuple(symbol_table, value):
    return ast.Tuple(elts=[_ast_element(symbol_table, element) for element in value])


# python elements
def _ast_psi(symbol_table, node):
    left_symbol_node = node.left_node.id
    return symbol_table, ast.Subscript(value=node.right_node,
                                       slice=ast.Index(value=_ast_tuple(symbol_table, symbol_table[left_symbol_node].value)),
                                       ctx=ast.Load())


def _ast_array(symbol_table, node):
    return symbol_table, ast.Name(id=node.symbol_node, ctx=ast.Load())


def _ast_function(symbol_table, node):
    return symbol_table, ast.FunctionDef(name='f',
                                         args=ast.arguments(args=[ast.arg(arg=arg, annotation=None) for arg in node.arguments],
                                                            vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
                                         body=[ast.Expr(value=child_node) for child_node in node.body] + [ast.Return(value=ast.Name(id=node.result))],
                                         decorator_list=[],
                                         returns=None)


def _ast_assignment(symbol_table, node):
    return symbol_table, ast.Assign(targets=[node.left_node], value=node.right_node)


def _ast_loop(symbol_table, node):
    symbol_node = symbol_table[node.symbol_node]
    return symbol_table, ast.For(target=ast.Name(id=node.symbol_node),
                                 iter=ast.Call(func=ast.Name(id='range'),
                                               args=[
                                                   _ast_element(symbol_table, symbol_node.value[0]),
                                                   _ast_element(symbol_table, symbol_node.value[1])
                                               ], keywords=[]), body=[ast.Expr(value=child_node) for child_node in node.body], orelse=[])


def _ast_error(symbol_table, node):
    return symbol_table, ast.Raise(exc=ast.Call(func=ast.Name(id='Exception'), args=[ast.Str(s=node.message)], keywords=[]), cause=None)


def _ast_initialize(symbol_table, node):
    return symbol_table, ast.Assign(targets=[ast.Name(id=node.symbol_node)], value=ast.Call(func=ast.Name(id='Array'), args=[_ast_tuple(symbol_table, node.shape)], keywords=[]))


def _ast_shape(symbol_table, node):
    return symbol_table, ast.Attribute(value=node.right_node, attr='shape', ctx=ast.Load())


def _ast_dimension(symbol_table, node):
    symbol_table, shape_ast = _ast_shape(symbol_table, node)
    return symbol_table, ast.Call(func=ast.Name(id='len', ctx=ast.Load()), args=[shape_ast], keywords=[])


def _ast_plus_minus_times_divide(symbol_table, node):
    binop_map = {
        MOANodeTypes.PLUS: ast.Add,
        MOANodeTypes.MINUS: ast.Sub,
        MOANodeTypes.TIMES: ast.Mult,
        MOANodeTypes.DIVIDE: ast.Div,
    }
    return symbol_table, ast.BinOp(left=node.left_node, op=binop_map[node.node_type](), right=node.right_node)


def _ast_if(symbol_table, node):
    return symbol_table, ast.If(test=node.condition_node, body=[ast.Expr(value=child_node) for child_node in node.body], orelse=[])


def _ast_condition(symbol_table, node):
    return symbol_table, ast.If(test=node.condition_node, body=[ast.Expr(value=node.right_node)], orelse=[])


def _ast_comparison_operations(symbol_table, node):
    comparision_map = {
        MOANodeTypes.EQUAL: ast.Eq,
        MOANodeTypes.NOTEQUAL: ast.NotEq,
        MOANodeTypes.LESSTHAN: ast.Lt,
        MOANodeTypes.LESSTHANEQUAL: ast.LtE,
        MOANodeTypes.GREATERTHAN: ast.Gt,
        MOANodeTypes.GREATERTHANEQUAL: ast.GtE,
    }
    return symbol_table, ast.Compare(left=node.left_node,
                                     ops=[comparision_map[node.node_type]()],
                                     comparators=[node.right_node])


def _ast_boolean_binary_operations(symbol_table, node):
    boolean_map = {
        MOANodeTypes.AND: ast.And,
        MOANodeTypes.OR: ast.Or
    }
    return symbol_table, ast.BoolOp(op=boolean_map[node.node_type](), values=[node.left_node, node.right_node])


def _ast_boolean_unary_operations(symbol_table, node):
    boolean_map = {
        MOANodeTypes.NOT: ast.Not
    }
    return symbol_table, ast.UnaryOp(op=boolean_map[node.node_type](), operand=node.right_node)
