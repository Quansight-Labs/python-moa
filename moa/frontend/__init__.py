from .array import LazyArray


def parse(source, frontend='moa'):
    if frontend == 'moa':
        from .moa import MOAParser, MOALexer
        parser = MOAParser()
        context = parser.parse(source)
    else:
        raise ValueError(f'frontend "{frontend}" not implemented')

    return context
