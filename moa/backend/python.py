import ast
import astunparse

from ..ast import MOANodeTypes, postorder_replacement
from ..shape import has_symbolic_elements


def python_backend(symbol_table, tree):
    """Convert MOA reduced AST to python source code

    """
    symbol_table, python_ast = postorder_replacement(symbol_table, tree, _ast_replacement)
    return python_ast


def generate_python_source(symbol_table, tree, materialize_scalars=False):
    python_ast = python_backend(symbol_table, tree)

    class ReplaceScalars(ast.NodeTransformer):
        def visit_Name(self, node):
            symbol_node = symbol_table[node.id]
            if (symbol_node.shape == () and symbol_node.value is not None and not has_symbolic_elements(symbol_node.value)):
                return ast.Num(symbol_node.value[0])
            return node

    if materialize_scalars:
        python_ast = ReplaceScalars().visit(python_ast)

    return astunparse.unparse(python_ast)[:-1] # remove newline


def _ast_replacement(symbol_table, node):
    _NODE_AST_MAP = {
        MOANodeTypes.ARRAY: _ast_array,
        MOANodeTypes.PSI: _ast_psi,
        MOANodeTypes.PLUS: _ast_plus_minus_times_divide,
        MOANodeTypes.MINUS: _ast_plus_minus_times_divide,
        MOANodeTypes.TIMES: _ast_plus_minus_times_divide,
        MOANodeTypes.DIVIDE: _ast_plus_minus_times_divide,
        MOANodeTypes.CONDITION: _ast_condition,
        MOANodeTypes.EQUAL: _ast_comparison_operations,
        MOANodeTypes.NOTEQUAL: _ast_comparison_operations,
        MOANodeTypes.LESSTHAN: _ast_comparison_operations,
        MOANodeTypes.LESSTHANEQUAL: _ast_comparison_operations,
        MOANodeTypes.GREATERTHAN: _ast_comparison_operations,
        MOANodeTypes.GREATERTHANEQUAL: _ast_comparison_operations,
        MOANodeTypes.AND: _ast_boolean_operations,
        MOANodeTypes.OR: _ast_boolean_operations,
    }
    return _NODE_AST_MAP[node.node_type](symbol_table, node)


def _ast_psi(symbol_table, node):
    left_symbol_node = node.left_node.id
    indicies = [ast.Str(i) if isinstance(i, str) else ast.Num(i) for i in symbol_table[left_symbol_node].value]
    return symbol_table, ast.Subscript(value=node.right_node,
                                       slice=ast.Index(value=ast.Tuple(elts=indicies, ctx=ast.Load())),
                                       ctx=ast.Load())


def _ast_array(symbol_table, node):
    return symbol_table, ast.Name(id=node.symbol_node, ctx=ast.Load())


def _ast_plus_minus_times_divide(symbol_table, node):
    binop_map = {
        MOANodeTypes.PLUS: ast.Add,
        MOANodeTypes.MINUS: ast.Sub,
        MOANodeTypes.TIMES: ast.Mult,
        MOANodeTypes.DIVIDE: ast.Div,
    }
    return symbol_table, ast.BinOp(left=node.left_node, op=binop_map[node.node_type](), right=node.right_node)


def _ast_condition(symbol_table, node):
    print(node.left_node)
    print(node.right_node)
    return symbol_table, ast.If(test=node.left_node, body=[ast.Expr(value=node.right_node)], orelse=[])


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


def _ast_boolean_operations(symbol_table, node):
    boolean_map = {
        MOANodeTypes.AND: ast.And,
        MOANodeTypes.OR: ast.Or
    }
    return symbol_table, ast.BoolOp(op=boolean_map[node.node_type](), values=[node.left_node, node.right_node])
