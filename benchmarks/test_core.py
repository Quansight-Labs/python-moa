import pytest
import numpy
import numba
import torch
import tensorflow

from moa.frontend import LazyArray


@pytest.mark.benchmark(group="addition", warmup=True)
def test_moa_numba_addition(benchmark):
    n = 1000
    m = 1000

    expression = LazyArray(name='A', shape=('n', 'm')) + LazyArray(name='B', shape=('n', 'm'))

    local_dict = {}
    exec(expression.compile(backend='python', use_numba=True), globals(), local_dict)

    A = numpy.random.random((n, m))
    B = numpy.random.random((n, m))

    benchmark(local_dict['f'], A, B)


@pytest.mark.benchmark(group="addition")
def test_numpy_addition(benchmark):
    n = 1000
    m = 1000

    A = numpy.random.random((n, m))
    B = numpy.random.random((n, m))

    def _test():
        A + B

    benchmark(_test)


@pytest.mark.benchmark(group="addition")
def test_pytorch_addition(benchmark):
    n = 1000
    m = 1000

    A = torch.rand(n, m)
    B = torch.rand(n, m)

    def _test():
        torch.add(A, B)

    benchmark(_test)


@pytest.mark.benchmark(group="addition")
def test_tensorflow_addition(benchmark):
    n = 1000
    m = 1000

    A = tensorflow.random.uniform((n, m))
    B = tensorflow.random.uniform((n, m))

    session = tensorflow.Session()
    session.run(tensorflow.initialize_all_variables())

    result = tensorflow.math.add(A, B)

    def _test():
        session.run(result)

    benchmark(_test)


@pytest.mark.benchmark(group="addition_index", warmup=True)
def test_moa_numba_addition_index(benchmark):
    n = 1000
    m = 1000

    expression = (LazyArray(name='A', shape=('n', 'm')) + LazyArray(name='B', shape=('n', 'm')))[0]

    local_dict = {}
    exec(expression.compile(backend='python', use_numba=True), globals(), local_dict)

    A = numpy.random.random((n, m))
    B = numpy.random.random((n, m))

    benchmark(local_dict['f'], A, B)


@pytest.mark.benchmark(group="addition_index")
def test_numpy_addition_index(benchmark):
    n = 1000
    m = 1000

    A = numpy.random.random((n, m))
    B = numpy.random.random((n, m))

    def _test():
        A[0] + B[0]

    benchmark(_test)


@pytest.mark.benchmark(group="addition_index")
def test_pytorch_addition_index(benchmark):
    n = 1000
    m = 1000

    A = torch.rand(n, m)
    B = torch.rand(n, m)

    def _test():
        torch.add(A[0], B[0])

    benchmark(_test)


@pytest.mark.benchmark(group="addition_index")
def test_tensorflow_addition_index(benchmark):
    n = 1000
    m = 1000

    A = tensorflow.random.uniform((n, m))
    B = tensorflow.random.uniform((n, m))
    index = tensorflow.constant(0)

    session = tensorflow.Session()
    session.run(tensorflow.initialize_all_variables())

    result = tensorflow.gather(tensorflow.math.add(A, B), index)

    def _test():
        session.run(result)

    benchmark(_test)


@pytest.mark.benchmark(group="double_addition", warmup=True)
def test_moa_numba_double_addition(benchmark):
    n = 1000
    m = 1000

    expression = LazyArray(name='A', shape=('n', 'm')) + LazyArray(name='B', shape=('n', 'm')) + LazyArray(name='C', shape=('n', 'm'))

    local_dict = {}
    exec(expression.compile(backend='python', use_numba=True), globals(), local_dict)

    A = numpy.random.random((n, m))
    B = numpy.random.random((n, m))
    C = numpy.random.random((n, m))

    benchmark(local_dict['f'], A=A, B=B, C=C)


@pytest.mark.benchmark(group="double_addition")
def test_numpy_double_addition(benchmark):
    n = 1000
    m = 1000

    A = numpy.random.random((n, m))
    B = numpy.random.random((n, m))
    C = numpy.random.random((n, m))

    def _test():
        A + B + C

    benchmark(_test)


@pytest.mark.benchmark(group="double_addition")
def test_pytorch_double_addition(benchmark):
    n = 1000
    m = 1000

    A = torch.rand(n, m)
    B = torch.rand(n, m)
    C = torch.rand(n, m)

    def _test():
        torch.add(torch.add(A, B), C)

    benchmark(_test)


@pytest.mark.benchmark(group="double_addition")
def test_tensorflow_double_addition(benchmark):
    n = 1000
    m = 1000

    A = tensorflow.random.uniform((n, m))
    B = tensorflow.random.uniform((n, m))
    C = tensorflow.random.uniform((n, m))

    session = tensorflow.Session()
    session.run(tensorflow.initialize_all_variables())

    result = tensorflow.math.add(tensorflow.math.add(A, B), C)

    def _test():
        session.run(result)

    benchmark(_test)


@pytest.mark.benchmark(group="outer_product", warmup=True)
def test_moa_numba_outer_product(benchmark):
    n = 100
    m = 100

    expression = LazyArray(name='A', shape=('n', 'm')).outer('*', LazyArray(name='B', shape=('n', 'm')))

    local_dict = {}
    exec(expression.compile(backend='python', use_numba=True), globals(), local_dict)

    A = numpy.random.random((n, m))
    B = numpy.random.random((n, m))

    benchmark(local_dict['f'], A, B)


@pytest.mark.benchmark(group="outer_product")
def test_numpy_outer_product(benchmark):
    n = 100
    m = 100

    A = numpy.random.random((n, m))
    B = numpy.random.random((n, m))

    def _test():
        numpy.outer(A, B)

    benchmark(_test)


@pytest.mark.benchmark(group="reduce", warmup=True)
def test_moa_numba_reduce(benchmark):
    n = 1000
    m = 1000

    expression = LazyArray(name='A', shape=('n', 'm')).reduce('+')

    local_dict = {}
    exec(expression.compile(backend='python', use_numba=True), globals(), local_dict)

    A = numpy.random.random((n, m))

    benchmark(local_dict['f'], A)


@pytest.mark.benchmark(group="reduce")
def test_numpy_reduce(benchmark):
    n = 1000
    m = 1000

    A = numpy.random.random((n, m))

    def _test():
        A.sum()

    benchmark(_test)


@pytest.mark.benchmark(group="reduce")
def test_pytorch_reduce(benchmark):
    n = 1000
    m = 1000

    A = torch.rand(n, m)

    def _test():
        torch.sum(A)

    benchmark(_test)


@pytest.mark.benchmark(group="reduce")
def test_tensorflow_reduce(benchmark):
    n = 1000
    m = 1000

    A = tensorflow.random.uniform((n, m))

    session = tensorflow.Session()
    session.run(tensorflow.initialize_all_variables())

    result = tensorflow.math.reduce_sum(A)

    def _test():
        session.run(result)

    benchmark(_test)


@pytest.mark.benchmark(group="inner_product", warmup=True)
def test_moa_numba_inner_product(benchmark):
    n = 1000
    m = 1000

    _A = LazyArray(name='A', shape=('n', 'm'))
    _B = LazyArray(name='B', shape=('m', 'k'))
    expression = _A.inner('+', '*', _B)

    local_dict = {}
    exec(expression.compile(backend='python', use_numba=True), globals(), local_dict)

    A = numpy.random.random((n, m))
    B = numpy.random.random((n, m))

    benchmark(local_dict['f'], A, B)


@pytest.mark.benchmark(group="inner_product")
def test_numpy_inner_product(benchmark):
    n = 1000
    m = 1000

    A = numpy.random.random((n, m))
    B = numpy.random.random((n, m))

    def _test():
        A.dot(B)

    benchmark(_test)


@pytest.mark.benchmark(group="inner_product")
def test_pytorch_inner_product(benchmark):
    n = 1000
    m = 1000

    A = torch.rand(n, m)
    B = torch.rand(n, m)

    def _test():
        torch.mm(A, B)

    benchmark(_test)


@pytest.mark.benchmark(group="inner_product")
def test_tensorflow_inner_product(benchmark):
    n = 1000
    m = 1000

    A = tensorflow.random.uniform((n, m))
    B = tensorflow.random.uniform((n, m))

    session = tensorflow.Session()
    session.run(tensorflow.initialize_all_variables())

    result = tensorflow.linalg.matmul(A, B)

    def _test():
        session.run(result)

    benchmark(_test)
