# storage shape for moving methods


# joining symbolic tables
def join_symbol_tables(left_symbol_table, left_tree, right_symbol_table, right_tree):
    """Join two symbol tables together which requires rewriting both trees

    TODO: This function is ugly and could be simplified/broken into parts. It is needed by the array frontend.

    """
    visited_symbols = set()
    counter = itertools.count()

    def _visit_node(symbol_table, node):
        if node.shape:
            raise ValueError('joining symbol tables currently naively assumes it is performed before shape analysis')

        if node.node_type == MOANodeTypes.ARRAY:
            visited_symbols.add(node.symbol_node)

            symbol_node = symbol_table[node.symbol_node]
            if symbol_node.shape:
                for element in symbol_node.shape:
                    if is_symbolic_element(element):
                        visited_symbols.add(element.symbol_node)

            if symbol_node.value:
                for element in symbol_node.value:
                    if is_symbolic_element(element):
                        visited_symbols.add(element.symbol_node)
        return symbol_table, node

    def _symbol_mapping(symbols):
        symbol_mapping = {}
        for symbol in symbols:
            if symbol.startswith('_i'):
                symbol_mapping[symbol] = f'_i{next(counter)}'
            elif symbol.startswith('_a'):
                symbol_mapping[symbol] = f'_a{next(counter)}'
            else:
                symbol_mapping[symbol] = symbol
        return symbol_mapping

    # discover used symbols and create symbol mapping
    node_traversal(left_symbol_table, left_tree, _visit_node, traversal='post')
    left_symbol_mapping = _symbol_mapping(visited_symbols)
    visited_symbols.clear()
    node_traversal(right_symbol_table, right_tree, _visit_node, traversal='post')
    right_symbol_mapping = _symbol_mapping(visited_symbols)

    # check that user defined symbols match in both tables
    for symbol in (left_symbol_mapping.keys() & right_symbol_mapping.keys()):
        if not symbol.startswith('_') and left_symbol_table[symbol] != right_symbol_table[symbol]:
            raise ValueError(f'user defined symbols must match "{symbol}" {left_symbol_table[symbol]} != {right_symbol_table[symbol]}')

    # rename symbols in tree
    symbol_mapping = {**left_symbol_mapping, **right_symbol_mapping}

    def _rename_symbols(symbol_table, node):
        if node.node_type == MOANodeTypes.ARRAY:
            node = Node(MOANodeTypes.ARRAY, None, symbol_mapping[node.symbol_node])
        return symbol_table, node

    new_left_symbol_table, new_left_tree = node_traversal(left_symbol_table, left_tree, _rename_symbols, traversal='post')
    new_right_symbol_table, new_right_tree = node_traversal(right_symbol_table, right_tree, _rename_symbols, traversal='post')

    # select subset of symbols from both symbol tables and rename
    new_symbol_table = {}
    for old_name, new_name in left_symbol_mapping.items():
        new_symbol_table[new_name] = new_left_symbol_table[old_name]
    for old_name, new_name in right_symbol_mapping.items():
        new_symbol_table[new_name] = new_right_symbol_table[old_name]

    # rename symbols within SymbolNode
    for name, symbol_node in new_symbol_table.items():
        shape = None
        if symbol_node.shape is not None:
            shape = ()
            for element in symbol_node.shape:
                if is_symbolic_element(element):
                    shape = shape + (Node(element.node_type, element.shape, symbol_mapping[element.symbol_node]),)
                else:
                    shape = shape + (element,)

        value = None
        if symbol_node.value is not None:
            value = ()
            for element in symbol_node.value:
                if is_symbolic_element(element):
                    value = value + (Node(element.node_type, element.shape, symbol_mapping[element.symbol_node]),)
                else:
                    value = value + (element,)
        new_symbol_table[name] = SymbolNode(MOANodeTypes.ARRAY, shape, value)

    return new_symbol_table, new_left_tree, new_right_tree
