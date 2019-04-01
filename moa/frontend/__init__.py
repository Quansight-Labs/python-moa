from .moa import MOAParser, MOALexer
from .array import LazyArray


def parse(source, frontend='moa'):
    if frontend == 'moa':
        parser = MOAParser()
        context = parser.parse(source)
    else:
        raise ValueError(f'frontend "{frontend}" not implemented')

    return context
