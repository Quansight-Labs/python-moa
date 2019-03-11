from .moa import MOAParser, MOALexer


def parse(source, frontend='moa'):
    if frontend == 'moa':
        parser = MOAParser()
        symbol_table, node = parser.parse(source)
    else:
        raise ValueError(f'frontend "{frontend}" not implemented')

    return symbol_table, node
