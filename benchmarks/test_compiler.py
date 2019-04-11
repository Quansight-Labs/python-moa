from moa.frontend import LazyArray


def test_moa_compile_simple(benchmark):
    A = LazyArray(name='A', shape=('n', 'm'))
    B = LazyArray(name='B', shape=('k', 'l'))

    expression = A + B

    def _test():
        expression.compile(backend='python', use_numba=True)

    benchmark(_test)


def test_moa_compile_complex(benchmark):
    A = LazyArray(name='A', shape=('n', 'm'))
    B = LazyArray(name='B', shape=('k', 'l'))
    C = LazyArray(name='C', shape=(10, 5))

    expression = (A.inner('+', '*', B)).T[0] + C.reduce('+')

    def _test():
        expression.compile(backend='python', use_numba=True)

    benchmark(_test)
