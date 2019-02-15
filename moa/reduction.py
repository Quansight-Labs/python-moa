import itertools


from .ast import MOANodeTypes, preorder_replacement


def create_index_node(


def reduction(tree):
    """Preorder traversal and replacement of ast tree

    In the future the symbol table will have to be constructed earlier
    for arrays and variables for shapes.
    """
    symbol_table = {}
    counter = itertools.counter()

    for dimension in tree.shape:
        symbol_name =
        symbol_table[


    patterns = {
        (MOANodeTypes.PSI


    }
